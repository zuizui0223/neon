#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(secr)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
arg_value <- function(flag, default = NULL) {
  idx <- match(flag, args)
  if (is.na(idx)) return(default)
  if (idx == length(args)) stop(paste("missing value for", flag))
  args[[idx + 1]]
}

out_json <- arg_value("--output-json", "validation/san_jacinto_scr_sigma_v1/calibrated_simulation_result_v2.json")
out_cal_csv <- arg_value("--output-calibration-csv", "validation/san_jacinto_scr_sigma_v1/calibration_cells_v2.csv")
out_rep_csv <- arg_value("--output-replicates-csv", "validation/san_jacinto_scr_sigma_v1/calibrated_simulation_replicates_v2.csv")
cal_reps <- as.integer(arg_value("--calibration-reps", "12"))
effect_reps <- as.integer(arg_value("--effect-reps", "20"))

if (!is.finite(cal_reps) || cal_reps < 1) stop("invalid calibration reps")
if (!is.finite(effect_reps) || effect_reps < 1) stop("invalid effect reps")

SEED_CAL <- 202610030L
SEED_EFFECT <- 202610031L
SPACING <- 6.25
NIGHTS <- 3L
CHECKS <- 3L
DENSITY_PER_HA <- 40
MASK_BUFFER <- 100
MASK_SPACING <- 5
MATERIAL_THRESHOLD <- 0.10

TARGET_REPEAT <- mean(c(0.398, 0.355))
TARGET_SHIFT <- mean(c(0.7257731958762886, 0.6915887850467289))
TARGET_CHANGED_MEDIAN <- mean(c(14.0, 12.5))

SIGMA_GRID <- c(3.125, 4.0, 5.0, 6.25)
G0_GRID <- c(0.12, 0.16, 0.20)
HANDLING_RMS_GRID <- c(0, 12.5, 25.0)
HANDLING_PROB_GRID <- c(0.25, 0.50, 0.75, 1.00)

tr <- make.grid(nx = 7, ny = 7, spacing = SPACING, detector = "multi")
rownames(tr) <- as.character(seq_len(nrow(tr)))
mask <- make.mask(tr, buffer = MASK_BUFFER, spacing = MASK_SPACING)
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

simulate_raw <- function(seed, sigma_true, g0, handling_rms, handling_prob) {
  set.seed(seed)

  base_pop <- sim.popn(
    D = DENSITY_PER_HA,
    core = tr,
    buffer = MASK_BUFFER,
    Ndist = "poisson"
  )
  if (nrow(base_pop) < 20) stop("population unexpectedly small")

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

      idx <- unique(id_num)
      # A new handling response is drawn at each capture. If the animal does
      # not respond, it returns to its baseline centre; if it responds, the
      # transient centre is displaced for subsequent checks until another
      # capture changes the state or the night ends.
      current_pop[idx, c("x", "y")] <- base_pop[idx, c("x", "y")]
      if (handling_rms > 0 && handling_prob > 0) {
        move <- runif(length(idx)) < handling_prob
        movers <- idx[move]
        if (length(movers)) {
          sd_component <- handling_rms / sqrt(2)
          current_pop[movers, "x"] <- base_pop[movers, "x"] + rnorm(length(movers), 0, sd_component)
          current_pop[movers, "y"] <- base_pop[movers, "y"] + rnorm(length(movers), 0, sd_component)
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

observation_metrics <- function(raw) {
  if (!nrow(raw)) {
    return(c(
      captured_individual_nights = 0,
      repeat_individual_nights = 0,
      repeat_fraction = NA,
      shift_fraction_repeat = NA,
      median_first_last_m = NA,
      median_changed_first_last_m = NA
    ))
  }

  key <- paste(raw$ID, raw$night, sep = ":")
  groups <- split(seq_len(nrow(raw)), key)
  n_captured <- length(groups)
  repeat_groups <- groups[vapply(groups, length, integer(1)) >= 2]
  n_repeat <- length(repeat_groups)

  if (!n_repeat) {
    return(c(
      captured_individual_nights = n_captured,
      repeat_individual_nights = 0,
      repeat_fraction = 0,
      shift_fraction_repeat = NA,
      median_first_last_m = NA,
      median_changed_first_last_m = NA
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

  c(
    captured_individual_nights = n_captured,
    repeat_individual_nights = n_repeat,
    repeat_fraction = n_repeat / n_captured,
    shift_fraction_repeat = mean(spans >= SPACING - 1e-10),
    median_first_last_m = median(spans),
    median_changed_first_last_m = if (length(changed)) median(changed) else NA_real_
  )
}

calibration_parameter_grid <- function() {
  rows <- list()
  k <- 0L
  for (s in SIGMA_GRID) {
    for (g in G0_GRID) {
      # Zero-handling control appears once per sigma/g0 combination.
      k <- k + 1L
      rows[[k]] <- data.frame(
        sigma_true_m = s, g0 = g,
        handling_rms_m = 0, handling_prob = 0
      )
      for (h in HANDLING_RMS_GRID[HANDLING_RMS_GRID > 0]) {
        for (p in HANDLING_PROB_GRID) {
          k <- k + 1L
          rows[[k]] <- data.frame(
            sigma_true_m = s, g0 = g,
            handling_rms_m = h, handling_prob = p
          )
        }
      }
    }
  }
  do.call(rbind, rows)
}

safe_mean <- function(x) if (all(is.na(x))) NA_real_ else mean(x, na.rm = TRUE)
safe_median <- function(x) if (all(is.na(x))) NA_real_ else median(x, na.rm = TRUE)
safe_quantile <- function(x, p) {
  if (all(is.na(x))) return(NA_real_)
  as.numeric(quantile(x, probs = p, na.rm = TRUE, names = FALSE))
}

run_calibration <- function() {
  grid <- calibration_parameter_grid()
  summaries <- vector("list", nrow(grid))

  for (i in seq_len(nrow(grid))) {
    par <- grid[i, ]
    vals <- vector("list", cal_reps)
    for (r in seq_len(cal_reps)) {
      seed <- SEED_CAL + i * 100003L + r * 1009L
      raw <- simulate_raw(
        seed,
        sigma_true = par$sigma_true_m,
        g0 = par$g0,
        handling_rms = par$handling_rms_m,
        handling_prob = par$handling_prob
      )
      vals[[r]] <- observation_metrics(raw)
    }
    m <- do.call(rbind, vals)

    summaries[[i]] <- data.frame(
      sigma_true_m = par$sigma_true_m,
      g0 = par$g0,
      handling_rms_m = par$handling_rms_m,
      handling_prob = par$handling_prob,
      calibration_replicates = cal_reps,
      mean_repeat_fraction = safe_mean(m[, "repeat_fraction"]),
      mean_shift_fraction_repeat = safe_mean(m[, "shift_fraction_repeat"]),
      median_changed_first_last_m = safe_median(m[, "median_changed_first_last_m"]),
      median_all_first_last_m = safe_median(m[, "median_first_last_m"]),
      stringsAsFactors = FALSE
    )
  }

  out <- do.call(rbind, summaries)
  out$calibration_score <-
    ((out$mean_repeat_fraction - TARGET_REPEAT) / 0.10)^2 +
    ((out$mean_shift_fraction_repeat - TARGET_SHIFT) / 0.10)^2 +
    ((out$median_changed_first_last_m - TARGET_CHANGED_MEDIAN) / SPACING)^2

  out <- out[order(out$calibration_score), , drop = FALSE]
  rownames(out) <- NULL
  out
}

represent <- function(raw, mode = c("check", "first", "last")) {
  mode <- match.arg(mode)
  if (!nrow(raw)) return(raw)

  if (mode == "check") {
    out <- raw
    out$occasion <- out$check_occasion
    return(out)
  }

  key <- paste(raw$ID, raw$night, sep = ":")
  groups <- split(seq_len(nrow(raw)), key)
  pick <- vapply(groups, function(ii) {
    z <- raw[ii, , drop = FALSE]
    ord <- order(z$check)
    if (mode == "first") ii[ord[1]] else ii[ord[length(ord)]]
  }, integer(1))

  out <- raw[pick, , drop = FALSE]
  out$occasion <- out$night
  out
}

make_ch <- function(dat, mode) {
  if (!nrow(dat)) return(NULL)
  noc <- if (mode == "check") NIGHTS * CHECKS else NIGHTS
  capt <- data.frame(
    Session = 1,
    ID = dat$ID,
    Occasion = dat$occasion,
    TrapID = dat$trap
  )
  make.capthist(
    captures = capt,
    traps = tr,
    fmt = "trapID",
    noccasions = noc,
    bysession = TRUE,
    sortrows = TRUE
  )
}

fit_sigma <- function(dat, mode) {
  ch <- try(make_ch(dat, mode), silent = TRUE)
  if (inherits(ch, "try-error") || is.null(ch)) {
    return(list(ok = FALSE, sigma = NA_real_, n = 0L, error = "capthist"))
  }
  n_animals <- dim(ch)[1]
  if (!is.finite(n_animals) || n_animals < 8) {
    return(list(ok = FALSE, sigma = NA_real_, n = n_animals, error = "too_few_animals"))
  }

  fit <- try(
    secr.fit(
      ch,
      mask = mask,
      CL = TRUE,
      detectfn = "HN",
      model = list(g0 ~ 1, sigma ~ 1),
      trace = FALSE,
      ncores = 1
    ),
    silent = TRUE
  )
  if (inherits(fit, "try-error")) {
    return(list(ok = FALSE, sigma = NA_real_, n = n_animals, error = "fit_error"))
  }

  pr <- try(predict(fit, se.fit = FALSE), silent = TRUE)
  if (inherits(pr, "try-error") || !"sigma" %in% names(pr)) {
    return(list(ok = FALSE, sigma = NA_real_, n = n_animals, error = "predict_error"))
  }
  est <- as.numeric(pr$sigma[1])
  ok <- is.finite(est) && est > 0
  list(
    ok = ok,
    sigma = if (ok) est else NA_real_,
    n = n_animals,
    error = if (ok) "" else "nonfinite"
  )
}

one_effect_replicate <- function(seed, par, rep_id, selected_rank) {
  raw <- simulate_raw(
    seed,
    sigma_true = par$sigma_true_m,
    g0 = par$g0,
    handling_rms = par$handling_rms_m,
    handling_prob = par$handling_prob
  )
  om <- observation_metrics(raw)

  fc <- fit_sigma(represent(raw, "check"), "check")
  ff <- fit_sigma(represent(raw, "first"), "first")
  fl <- fit_sigma(represent(raw, "last"), "last")

  rel <- function(est) if (is.finite(est)) (est - par$sigma_true_m) / par$sigma_true_m else NA_real_
  pair <- function(a, b) if (is.finite(a) && is.finite(b) && b > 0) a / b - 1 else NA_real_

  data.frame(
    selected_rank = selected_rank,
    replicate = rep_id,
    seed = seed,
    sigma_true_m = par$sigma_true_m,
    g0 = par$g0,
    handling_rms_m = par$handling_rms_m,
    handling_prob = par$handling_prob,
    repeat_fraction = om["repeat_fraction"],
    shift_fraction_repeat = om["shift_fraction_repeat"],
    median_changed_first_last_m = om["median_changed_first_last_m"],
    check_ok = fc$ok,
    first_ok = ff$ok,
    last_ok = fl$ok,
    sigma_check_m = fc$sigma,
    sigma_first_m = ff$sigma,
    sigma_last_m = fl$sigma,
    rel_error_check = rel(fc$sigma),
    rel_error_first = rel(ff$sigma),
    rel_error_last = rel(fl$sigma),
    first_vs_check = pair(ff$sigma, fc$sigma),
    last_vs_check = pair(fl$sigma, fc$sigma),
    last_vs_first = pair(fl$sigma, ff$sigma),
    material_first_vs_check = abs(pair(ff$sigma, fc$sigma)) >= MATERIAL_THRESHOLD,
    material_last_vs_check = abs(pair(fl$sigma, fc$sigma)) >= MATERIAL_THRESHOLD,
    material_last_vs_first = abs(pair(fl$sigma, ff$sigma)) >= MATERIAL_THRESHOLD,
    check_error = fc$error,
    first_error = ff$error,
    last_error = fl$error,
    stringsAsFactors = FALSE
  )
}

summarise_effect_cell <- function(d) {
  data.frame(
    selected_rank = d$selected_rank[1],
    sigma_true_m = d$sigma_true_m[1],
    g0 = d$g0[1],
    handling_rms_m = d$handling_rms_m[1],
    handling_prob = d$handling_prob[1],
    n_replicates = nrow(d),
    check_fit_rate = mean(d$check_ok),
    first_fit_rate = mean(d$first_ok),
    last_fit_rate = mean(d$last_ok),
    mean_repeat_fraction = safe_mean(d$repeat_fraction),
    mean_shift_fraction_repeat = safe_mean(d$shift_fraction_repeat),
    median_changed_first_last_m = safe_median(d$median_changed_first_last_m),
    median_rel_error_check = safe_median(d$rel_error_check),
    median_rel_error_first = safe_median(d$rel_error_first),
    median_rel_error_last = safe_median(d$rel_error_last),
    q25_rel_error_check = safe_quantile(d$rel_error_check, 0.25),
    q75_rel_error_check = safe_quantile(d$rel_error_check, 0.75),
    q25_rel_error_first = safe_quantile(d$rel_error_first, 0.25),
    q75_rel_error_first = safe_quantile(d$rel_error_first, 0.75),
    q25_rel_error_last = safe_quantile(d$rel_error_last, 0.25),
    q75_rel_error_last = safe_quantile(d$rel_error_last, 0.75),
    median_first_vs_check = safe_median(d$first_vs_check),
    median_last_vs_check = safe_median(d$last_vs_check),
    median_last_vs_first = safe_median(d$last_vs_first),
    material_first_vs_check_fraction = safe_mean(d$material_first_vs_check),
    material_last_vs_check_fraction = safe_mean(d$material_last_vs_check),
    material_last_vs_first_fraction = safe_mean(d$material_last_vs_first),
    stringsAsFactors = FALSE
  )
}

message("Stage A: observation-process calibration only")
calibration <- run_calibration()
selected <- calibration[seq_len(min(3, nrow(calibration))), , drop = FALSE]
selected$selected_rank <- seq_len(nrow(selected))

message("Stage B: open downstream sigma only for automatically selected cells")
effect_rows <- list()
k <- 0L
for (i in seq_len(nrow(selected))) {
  par <- selected[i, ]
  for (r in seq_len(effect_reps)) {
    k <- k + 1L
    seed <- SEED_EFFECT + i * 1000003L + r * 1009L
    message(sprintf(
      "selected=%d sigma=%.3f g0=%.2f h=%.2f p=%.2f rep=%d/%d",
      i, par$sigma_true_m, par$g0, par$handling_rms_m, par$handling_prob,
      r, effect_reps
    ))
    effect_rows[[k]] <- one_effect_replicate(seed, par, r, i)
  }
}
effect_replicates <- do.call(rbind, effect_rows)

effect_split <- split(effect_replicates, effect_replicates$selected_rank)
effect_summary <- do.call(rbind, lapply(effect_split, summarise_effect_cell))
rownames(effect_summary) <- NULL

result <- list(
  schema = "neon.san_jacinto_scr_sigma_downstream_simulation.v2",
  frozen_design = "docs/SAN_JACINTO_SCR_SIGMA_CALIBRATED_SIMULATION_DESIGN_V2.md",
  package = list(secr_version = as.character(packageVersion("secr"))),
  constants = list(
    spacing_m = SPACING,
    nights = NIGHTS,
    checks_per_night = CHECKS,
    density_per_ha = DENSITY_PER_HA,
    mask_buffer_m = MASK_BUFFER,
    mask_spacing_m = MASK_SPACING,
    calibration_replicates_per_cell = cal_reps,
    downstream_replicates_per_selected_cell = effect_reps,
    material_relative_difference_threshold = MATERIAL_THRESHOLD
  ),
  calibration_targets = list(
    repeat_fraction = TARGET_REPEAT,
    shift_fraction_repeat = TARGET_SHIFT,
    median_changed_first_last_m = TARGET_CHANGED_MEDIAN
  ),
  claim_boundary = list(
    empirical_sigma_opened = FALSE,
    empirical_two_species_gate_remains_stopped = TRUE,
    calibration_used_downstream_sigma_outcomes = FALSE,
    all_three_selected_cells_reported = TRUE
  ),
  selected_calibration_cells = selected,
  downstream_cells = effect_summary,
  calibration_cells = calibration
)

dir.create(dirname(out_cal_csv), recursive = TRUE, showWarnings = FALSE)
write.csv(calibration, out_cal_csv, row.names = FALSE, na = "")

dir.create(dirname(out_rep_csv), recursive = TRUE, showWarnings = FALSE)
write.csv(effect_replicates, out_rep_csv, row.names = FALSE, na = "")

dir.create(dirname(out_json), recursive = TRUE, showWarnings = FALSE)
writeLines(
  toJSON(result, pretty = TRUE, auto_unbox = TRUE, digits = 10, na = "null"),
  out_json
)

cat("\nSelected calibration cells:\n")
print(selected)
cat("\nDownstream summaries:\n")
print(effect_summary)
