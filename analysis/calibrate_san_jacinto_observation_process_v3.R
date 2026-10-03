#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(secr)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
arg_value <- function(flag, default = NULL) {
  i <- match(flag, args)
  if (is.na(i)) return(default)
  if (i == length(args)) stop(paste("missing value for", flag))
  args[[i + 1]]
}

out_json <- arg_value(
  "--output-json",
  "validation/san_jacinto_scr_sigma_v1/observation_calibration_v3.json"
)
out_search_csv <- arg_value(
  "--output-search-csv",
  "validation/san_jacinto_scr_sigma_v1/observation_calibration_search_v3.csv"
)
out_validation_csv <- arg_value(
  "--output-validation-csv",
  "validation/san_jacinto_scr_sigma_v1/observation_calibration_validation_v3.csv"
)
search_reps <- as.integer(arg_value("--search-reps", "12"))
validation_reps <- as.integer(arg_value("--validation-reps", "50"))

if (!is.finite(search_reps) || search_reps < 1) stop("invalid search reps")
if (!is.finite(validation_reps) || validation_reps < 1) stop("invalid validation reps")

SEED_SEARCH <- 2026100300L
SEED_VALIDATION <- 2026100400L
SPACING <- 6.25
NIGHTS <- 3L
CHECKS <- 3L
DENSITY_PER_HA <- 60
SIGMA_GRID <- c(3.125, 4.0, 5.0, 6.25)
G0_GRID <- c(0.12, 0.16, 0.20)
HANDLING_RMS_GRID <- c(6.25, 12.5, 18.75, 25.0)
RESPONSE_PROB_GRID <- c(0.10, 0.25, 0.50, 0.75)

TARGET_REPEAT <- 0.3765
TARGET_SHIFT <- mean(c(0.7257731958762886, 0.6915887850467289))
TARGET_ALL_MEDIAN <- mean(c(8.838834764831844, 6.25))
TARGET_CHANGED_MEDIAN <- mean(c(14.0, 12.5))

REPEAT_LO <- 0.3265
REPEAT_HI <- 0.4265
SHIFT_LO <- TARGET_SHIFT - 0.05
SHIFT_HI <- TARGET_SHIFT + 0.05
ALL_MEDIAN_LO <- 6.25
ALL_MEDIAN_HI <- 8.84
CHANGED_MEDIAN_LO <- 12.5
CHANGED_MEDIAN_HI <- 14.0

tr <- make.grid(nx = 7, ny = 7, spacing = SPACING, detector = "multi")
rownames(tr) <- as.character(seq_len(nrow(tr)))
trap_xy <- as.data.frame(tr)

stopifnot(nrow(tr) == 49)
stopifnot(length(unique(trap_xy$x)) == 7)
stopifnot(length(unique(trap_xy$y)) == 7)

trap_index_from_df <- function(df) {
  vals <- as.character(df$TrapID)
  idx <- match(vals, rownames(tr))
  if (anyNA(idx)) {
    num <- suppressWarnings(as.integer(vals))
    use <- is.na(idx) & !is.na(num) & num >= 1 & num <= nrow(tr)
    idx[use] <- num[use]
  }
  if (anyNA(idx)) stop("could not map TrapID")
  idx
}

simulate_raw <- function(seed, sigma_true, g0, handling_rms, response_prob) {
  set.seed(seed)
  base_pop <- sim.popn(
    D = DENSITY_PER_HA,
    core = tr,
    buffer = 100,
    Ndist = "poisson"
  )
  if (nrow(base_pop) < 20) stop("simulated population unexpectedly small")

  rows <- list()
  k <- 0L

  for (night in seq_len(NIGHTS)) {
    current_pop <- base_pop

    for (check in seq_len(CHECKS)) {
      ch <- sim.capthist(
        traps = tr,
        popn = current_pop,
        detectfn = "HN",
        detectpar = list(g0 = g0, sigma = sigma_true),
        noccasions = 1,
        renumber = FALSE
      )

      nch <- dim(ch)[1]
      if (is.null(nch) || nch == 0) next

      d <- as.data.frame(ch, fmt = "trapID")
      if (!nrow(d)) next
      if (!all(c("ID", "TrapID") %in% names(d))) stop("unexpected capthist schema")

      id_num <- suppressWarnings(as.integer(as.character(d$ID)))
      if (anyNA(id_num)) stop("population IDs not retained")
      if (anyDuplicated(id_num)) stop("exclusive multi detector produced duplicate animal within check")
      trap_idx <- trap_index_from_df(d)

      k <- k + 1L
      rows[[k]] <- data.frame(
        ID = id_num,
        night = night,
        check = check,
        check_occasion = (night - 1L) * CHECKS + check,
        trap = trap_idx,
        stringsAsFactors = FALSE
      )

      # First restore captured animals to the baseline state. A stochastic
      # response then moves some of them relative to the detector where they
      # were physically captured and released.
      current_pop[id_num, c("x", "y")] <- base_pop[id_num, c("x", "y")]

      if (handling_rms > 0 && response_prob > 0) {
        respond <- runif(length(id_num)) < response_prob
        if (any(respond)) {
          ids <- id_num[respond]
          tix <- trap_idx[respond]
          component_sd <- handling_rms / sqrt(2)
          current_pop[ids, "x"] <- trap_xy$x[tix] + rnorm(length(ids), 0, component_sd)
          current_pop[ids, "y"] <- trap_xy$y[tix] + rnorm(length(ids), 0, component_sd)
        }
      }
    }
  }

  if (!length(rows)) {
    return(data.frame(
      ID = integer(), night = integer(), check = integer(),
      check_occasion = integer(), trap = integer()
    ))
  }
  do.call(rbind, rows)
}

observation_record <- function(raw) {
  if (!nrow(raw)) {
    return(list(
      captured_nights = 0L,
      repeat_nights = 0L,
      shift_nights = 0L,
      all_spans = numeric(),
      changed_spans = numeric()
    ))
  }

  key <- paste(raw$ID, raw$night, sep = ":")
  groups <- split(seq_len(nrow(raw)), key)
  repeat_groups <- groups[vapply(groups, length, integer(1)) >= 2]

  if (!length(repeat_groups)) {
    return(list(
      captured_nights = length(groups),
      repeat_nights = 0L,
      shift_nights = 0L,
      all_spans = numeric(),
      changed_spans = numeric()
    ))
  }

  spans <- vapply(repeat_groups, function(ii) {
    z <- raw[ii, , drop = FALSE]
    z <- z[order(z$check), , drop = FALSE]
    a <- trap_xy[z$trap[1], c("x", "y")]
    b <- trap_xy[z$trap[nrow(z)], c("x", "y")]
    sqrt((a$x - b$x)^2 + (a$y - b$y)^2)
  }, numeric(1))

  changed <- spans[spans >= SPACING - 1e-10]
  list(
    captured_nights = length(groups),
    repeat_nights = length(repeat_groups),
    shift_nights = length(changed),
    all_spans = spans,
    changed_spans = changed
  )
}

parameter_grid <- function() {
  out <- list()
  k <- 0L
  for (s in SIGMA_GRID) {
    for (g in G0_GRID) {
      k <- k + 1L
      out[[k]] <- data.frame(
        sigma_true_m = s,
        g0 = g,
        handling_rms_m = 0,
        response_prob = 0
      )
      for (h in HANDLING_RMS_GRID) {
        for (p in RESPONSE_PROB_GRID) {
          k <- k + 1L
          out[[k]] <- data.frame(
            sigma_true_m = s,
            g0 = g,
            handling_rms_m = h,
            response_prob = p
          )
        }
      }
    }
  }
  ans <- do.call(rbind, out)
  rownames(ans) <- NULL
  stopifnot(nrow(ans) == 204)
  ans
}

ranking_score <- function(q_repeat, q_shift, med_all, med_changed) {
  if (any(!is.finite(c(q_repeat, q_shift, med_all, med_changed)))) return(Inf)
  ((q_repeat - TARGET_REPEAT) / 0.05)^2 +
    ((q_shift - TARGET_SHIFT) / 0.05)^2 +
    ((med_all - TARGET_ALL_MEDIAN) / (8.838834764831844 - 6.25))^2 +
    ((med_changed - TARGET_CHANGED_MEDIAN) / 1.5)^2
}

summarise_parameter <- function(par, reps, seed_base, cell_id) {
  captured_total <- 0L
  repeat_total <- 0L
  shift_total <- 0L
  all_spans <- numeric()
  changed_spans <- numeric()

  for (r in seq_len(reps)) {
    seed <- seed_base + cell_id * 100003L + r * 1009L
    raw <- simulate_raw(
      seed,
      sigma_true = par$sigma_true_m,
      g0 = par$g0,
      handling_rms = par$handling_rms_m,
      response_prob = par$response_prob
    )
    rec <- observation_record(raw)
    captured_total <- captured_total + rec$captured_nights
    repeat_total <- repeat_total + rec$repeat_nights
    shift_total <- shift_total + rec$shift_nights
    all_spans <- c(all_spans, rec$all_spans)
    changed_spans <- c(changed_spans, rec$changed_spans)
  }

  q_repeat <- if (captured_total > 0) repeat_total / captured_total else NA_real_
  q_shift <- if (repeat_total > 0) shift_total / repeat_total else NA_real_
  med_all <- if (length(all_spans)) median(all_spans) else NA_real_
  med_changed <- if (length(changed_spans)) median(changed_spans) else NA_real_

  data.frame(
    sigma_true_m = par$sigma_true_m,
    g0 = par$g0,
    handling_rms_m = par$handling_rms_m,
    response_prob = par$response_prob,
    replicates = reps,
    captured_individual_nights = captured_total,
    repeat_individual_nights = repeat_total,
    shifted_repeat_nights = shift_total,
    repeat_fraction = q_repeat,
    shift_fraction_repeat = q_shift,
    median_all_first_last_m = med_all,
    median_changed_first_last_m = med_changed,
    ranking_score = ranking_score(q_repeat, q_shift, med_all, med_changed),
    stringsAsFactors = FALSE
  )
}

grid <- parameter_grid()

message("Stage A1: observation-only search across 204 cells")
search_rows <- vector("list", nrow(grid))
for (i in seq_len(nrow(grid))) {
  if (i %% 10 == 0) message(sprintf("search cell %d/%d", i, nrow(grid)))
  search_rows[[i]] <- summarise_parameter(
    grid[i, , drop = FALSE],
    reps = search_reps,
    seed_base = SEED_SEARCH,
    cell_id = i
  )
}
search <- do.call(rbind, search_rows)
search <- search[order(search$ranking_score), , drop = FALSE]
rownames(search) <- NULL
search$search_rank <- seq_len(nrow(search))

advance_n <- min(12L, nrow(search))
advanced <- search[seq_len(advance_n), , drop = FALSE]

message("Stage A2: independent validation of top 12 cells")
validation_rows <- vector("list", advance_n)
for (j in seq_len(advance_n)) {
  par <- advanced[j, c("sigma_true_m", "g0", "handling_rms_m", "response_prob")]
  validation_rows[[j]] <- summarise_parameter(
    par,
    reps = validation_reps,
    seed_base = SEED_VALIDATION,
    cell_id = j
  )
  validation_rows[[j]]$a1_search_rank <- advanced$search_rank[j]
}
validation <- do.call(rbind, validation_rows)

validation$passes_repeat <- with(
  validation,
  repeat_fraction >= REPEAT_LO & repeat_fraction <= REPEAT_HI
)
validation$passes_shift <- with(
  validation,
  shift_fraction_repeat >= SHIFT_LO & shift_fraction_repeat <= SHIFT_HI
)
validation$passes_all_median <- with(
  validation,
  median_all_first_last_m >= ALL_MEDIAN_LO &
    median_all_first_last_m <= ALL_MEDIAN_HI
)
validation$passes_changed_median <- with(
  validation,
  median_changed_first_last_m >= CHANGED_MEDIAN_LO &
    median_changed_first_last_m <= CHANGED_MEDIAN_HI
)
validation$passes_all <- with(
  validation,
  passes_repeat & passes_shift & passes_all_median & passes_changed_median
)

validation <- validation[order(validation$ranking_score), , drop = FALSE]
rownames(validation) <- NULL
validation$validation_rank <- seq_len(nrow(validation))

passing <- validation[validation$passes_all, , drop = FALSE]
if (nrow(passing) > 3) passing <- passing[seq_len(3), , drop = FALSE]

decision <- if (nrow(passing) > 0) {
  "authorize_v3_downstream_freeze"
} else {
  "stop_v3_no_observation_process_match"
}

result <- list(
  schema = "neon.san_jacinto_observation_calibration.v3",
  frozen_design = "docs/SAN_JACINTO_OBSERVATION_CALIBRATION_V3.md",
  secr_version = as.character(packageVersion("secr")),
  protocol = list(
    spacing_m = SPACING,
    nights = NIGHTS,
    checks_per_night = CHECKS,
    density_per_ha = DENSITY_PER_HA,
    release_centred_transient_state = TRUE
  ),
  targets = list(
    repeat_fraction = TARGET_REPEAT,
    shift_fraction_repeat = TARGET_SHIFT,
    median_all_first_last_m = TARGET_ALL_MEDIAN,
    median_changed_first_last_m = TARGET_CHANGED_MEDIAN
  ),
  hard_validation_bounds = list(
    repeat_fraction = c(REPEAT_LO, REPEAT_HI),
    shift_fraction_repeat = c(SHIFT_LO, SHIFT_HI),
    median_all_first_last_m = c(ALL_MEDIAN_LO, ALL_MEDIAN_HI),
    median_changed_first_last_m = c(CHANGED_MEDIAN_LO, CHANGED_MEDIAN_HI)
  ),
  grid = list(
    candidate_cells = nrow(grid),
    search_replicates_per_cell = search_reps,
    validation_candidates = advance_n,
    validation_replicates_per_cell = validation_reps
  ),
  decision = list(
    value = decision,
    passing_validation_cells = nrow(validation[validation$passes_all, , drop = FALSE]),
    downstream_cells_frozen_now = FALSE
  ),
  claim_boundary = list(
    scr_models_fit = 0,
    empirical_sigma_opened = FALSE,
    v1_v2_sigma_results_not_used_for_v3_cell_selection = TRUE,
    downstream_sigma_results_generated = FALSE
  ),
  passing_cells_for_later_freeze = passing,
  validation_cells = validation,
  top_search_cells = search[seq_len(min(20L, nrow(search))), , drop = FALSE]
)

dir.create(dirname(out_search_csv), recursive = TRUE, showWarnings = FALSE)
write.csv(search, out_search_csv, row.names = FALSE, na = "")

dir.create(dirname(out_validation_csv), recursive = TRUE, showWarnings = FALSE)
write.csv(validation, out_validation_csv, row.names = FALSE, na = "")

dir.create(dirname(out_json), recursive = TRUE, showWarnings = FALSE)
writeLines(
  toJSON(result, pretty = TRUE, auto_unbox = TRUE, digits = 10, na = "null"),
  out_json
)

cat("\nDecision:\n")
print(result$decision)
cat("\nPassing cells:\n")
print(passing)
cat("\nValidation cells:\n")
print(validation)
