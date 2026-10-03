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

out_json <- arg_value("--output-json", "validation/san_jacinto_scr_sigma_v1/simulation_result_v1.json")
out_csv  <- arg_value("--output-csv",  "validation/san_jacinto_scr_sigma_v1/simulation_replicates_v1.csv")
reps <- as.integer(arg_value("--reps", "8"))
if (!is.finite(reps) || reps < 1) stop("--reps must be a positive integer")

SEED0 <- 20261003L
SPACING <- 6.25
NIGHTS <- 3L
CHECKS <- 3L
G0 <- 0.20
DENSITY_PER_HA <- 20
MASK_BUFFER <- 100
MASK_SPACING <- 5
TRUE_SIGMAS <- c(6.25, 12.5, 25.0)
HANDLING_RMS <- c(0, 6.25, 12.5, 25.0)
MATERIAL_THRESHOLD <- 0.10

# San Jacinto held-out observation-process values already opened before this
# simulation design. They are used only to label an empirically relevant scale.
EMP_SHIFT <- mean(c(0.7257731958762886, 0.6915887850467289))
EMP_MEDIAN_SPAN <- mean(c(8.838834764831844, 6.25))

tr <- make.grid(nx = 7, ny = 7, spacing = SPACING, detector = "multi")
rownames(tr) <- as.character(seq_len(nrow(tr)))
mask <- make.mask(tr, buffer = MASK_BUFFER, spacing = MASK_SPACING)
trap_xy <- as.data.frame(tr)

assert_protocol <- function() {
  stopifnot(nrow(tr) == 49)
  ux <- sort(unique(round(trap_xy$x, 8)))
  uy <- sort(unique(round(trap_xy$y, 8)))
  stopifnot(length(ux) == 7, length(uy) == 7)
  stopifnot(all(abs(diff(ux) - SPACING) < 1e-8))
  stopifnot(all(abs(diff(uy) - SPACING) < 1e-8))
}
assert_protocol()

trap_index_from_df <- function(df) {
  vals <- as.character(df$TrapID)
  idx <- match(vals, rownames(tr))
  if (anyNA(idx)) {
    num <- suppressWarnings(as.integer(vals))
    use <- is.na(idx) & !is.na(num) & num >= 1 & num <= nrow(tr)
    idx[use] <- num[use]
  }
  if (anyNA(idx)) stop("could not map one or more TrapID values to detector index")
  idx
}

simulate_raw <- function(seed, sigma_true, handling_rms) {
  set.seed(seed)
  base_pop <- sim.popn(
    D = DENSITY_PER_HA,
    core = tr,
    buffer = MASK_BUFFER,
    Ndist = "poisson"
  )
  if (nrow(base_pop) < 20) stop("simulated population unexpectedly small")

  rows <- list()
  k <- 0L

  for (night in seq_len(NIGHTS)) {
    # Handling displacement is transient within a night; each new night starts
    # from the baseline activity-centre state.
    current_pop <- base_pop

    for (check in seq_len(CHECKS)) {
      ch <- sim.capthist(
        traps = tr,
        popn = current_pop,
        detectfn = "HN",
        detectpar = list(g0 = G0, sigma = sigma_true),
        noccasions = 1,
        renumber = FALSE
      )
      # A valid check may have zero captures.  Some secr versions do not
      # coerce a zero-animal capthist cleanly with as.data.frame(), so retain
      # the occasion as a zero-detection check and skip conversion.
      nch <- dim(ch)[1]
      if (is.null(nch) || nch == 0) next

      d <- as.data.frame(ch, fmt = "trapID")

      if (nrow(d) > 0) {
        if (!all(c("ID", "TrapID") %in% names(d))) {
          stop("unexpected capthist dataframe schema")
        }
        id_num <- suppressWarnings(as.integer(as.character(d$ID)))
        if (anyNA(id_num)) stop("population IDs were not retained as numeric row indices")
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

        if (handling_rms > 0) {
          # Isotropic Gaussian displacement whose RMS radial magnitude equals
          # handling_rms: component SD = handling_rms / sqrt(2).
          component_sd <- handling_rms / sqrt(2)
          idx <- unique(id_num)
          current_pop[idx, "x"] <- base_pop[idx, "x"] + rnorm(length(idx), 0, component_sd)
          current_pop[idx, "y"] <- base_pop[idx, "y"] + rnorm(length(idx), 0, component_sd)
        } else {
          idx <- unique(id_num)
          current_pop[idx, c("x", "y")] <- base_pop[idx, c("x", "y")]
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
    return(list(
      captured_individual_nights = 0L,
      repeat_individual_nights = 0L,
      repeat_fraction = NA_real_,
      shift_fraction_repeat = NA_real_,
      median_first_last_m = NA_real_
    ))
  }

  key <- paste(raw$ID, raw$night, sep = ":")
  groups <- split(seq_len(nrow(raw)), key)
  n_captured <- length(groups)
  repeat_idx <- groups[vapply(groups, function(ii) length(ii) >= 2, logical(1))]
  n_repeat <- length(repeat_idx)

  if (!n_repeat) {
    return(list(
      captured_individual_nights = n_captured,
      repeat_individual_nights = 0L,
      repeat_fraction = 0,
      shift_fraction_repeat = NA_real_,
      median_first_last_m = NA_real_
    ))
  }

  spans <- vapply(repeat_idx, function(ii) {
    z <- raw[ii, , drop = FALSE]
    z <- z[order(z$check), , drop = FALSE]
    a <- trap_xy[z$trap[1], c("x", "y")]
    b <- trap_xy[z$trap[nrow(z)], c("x", "y")]
    sqrt((a$x - b$x)^2 + (a$y - b$y)^2)
  }, numeric(1))

  list(
    captured_individual_nights = n_captured,
    repeat_individual_nights = n_repeat,
    repeat_fraction = n_repeat / n_captured,
    shift_fraction_repeat = mean(spans >= SPACING - 1e-10),
    median_first_last_m = median(spans)
  )
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
  noc <- if (mode == "check") NIGHTS * CHECKS else NIGHTS
  if (!nrow(dat)) return(NULL)
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
    return(list(ok = FALSE, sigma = NA_real_, g0 = NA_real_, n = 0L, error = "capthist"))
  }

  n_animals <- dim(ch)[1]
  if (!is.finite(n_animals) || n_animals < 8) {
    return(list(ok = FALSE, sigma = NA_real_, g0 = NA_real_, n = n_animals, error = "too_few_animals"))
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
    return(list(ok = FALSE, sigma = NA_real_, g0 = NA_real_, n = n_animals, error = "fit_error"))
  }

  pr <- try(predict(fit, se.fit = FALSE), silent = TRUE)
  if (inherits(pr, "try-error") || !all(c("g0", "sigma") %in% names(pr))) {
    return(list(ok = FALSE, sigma = NA_real_, g0 = NA_real_, n = n_animals, error = "predict_error"))
  }

  sigma_hat <- as.numeric(pr$sigma[1])
  g0_hat <- as.numeric(pr$g0[1])
  ok <- is.finite(sigma_hat) && sigma_hat > 0 && is.finite(g0_hat) && g0_hat > 0 && g0_hat < 1
  list(
    ok = ok,
    sigma = if (ok) sigma_hat else NA_real_,
    g0 = if (ok) g0_hat else NA_real_,
    n = n_animals,
    error = if (ok) "" else "nonfinite_or_boundary"
  )
}

one_replicate <- function(seed, sigma_true, handling_rms, rep_id) {
  raw <- simulate_raw(seed, sigma_true, handling_rms)
  om <- observation_metrics(raw)

  dc <- represent(raw, "check")
  df <- represent(raw, "first")
  dl <- represent(raw, "last")

  fc <- fit_sigma(dc, "check")
  ff <- fit_sigma(df, "first")
  fl <- fit_sigma(dl, "last")

  rel <- function(est) if (is.finite(est)) (est - sigma_true) / sigma_true else NA_real_
  pairrel <- function(a, b) if (is.finite(a) && is.finite(b) && b > 0) a / b - 1 else NA_real_

  data.frame(
    seed = seed,
    replicate = rep_id,
    sigma_true_m = sigma_true,
    sigma_true_spacings = sigma_true / SPACING,
    handling_rms_m = handling_rms,
    handling_rms_spacings = handling_rms / SPACING,
    raw_detections = nrow(raw),
    captured_individual_nights = om$captured_individual_nights,
    repeat_individual_nights = om$repeat_individual_nights,
    repeat_fraction = om$repeat_fraction,
    shift_fraction_repeat = om$shift_fraction_repeat,
    median_first_last_m = om$median_first_last_m,
    check_ok = fc$ok,
    first_ok = ff$ok,
    last_ok = fl$ok,
    check_n = fc$n,
    first_n = ff$n,
    last_n = fl$n,
    sigma_check_m = fc$sigma,
    sigma_first_m = ff$sigma,
    sigma_last_m = fl$sigma,
    rel_error_check = rel(fc$sigma),
    rel_error_first = rel(ff$sigma),
    rel_error_last = rel(fl$sigma),
    abs_rel_error_check = abs(rel(fc$sigma)),
    abs_rel_error_first = abs(rel(ff$sigma)),
    abs_rel_error_last = abs(rel(fl$sigma)),
    first_vs_check = pairrel(ff$sigma, fc$sigma),
    last_vs_check = pairrel(fl$sigma, fc$sigma),
    last_vs_first = pairrel(fl$sigma, ff$sigma),
    material_first_vs_check = abs(pairrel(ff$sigma, fc$sigma)) >= MATERIAL_THRESHOLD,
    material_last_vs_check = abs(pairrel(fl$sigma, fc$sigma)) >= MATERIAL_THRESHOLD,
    material_last_vs_first = abs(pairrel(fl$sigma, ff$sigma)) >= MATERIAL_THRESHOLD,
    check_error = fc$error,
    first_error = ff$error,
    last_error = fl$error,
    stringsAsFactors = FALSE
  )
}

safe_mean <- function(x) if (all(is.na(x))) NA_real_ else mean(x, na.rm = TRUE)
safe_median <- function(x) if (all(is.na(x))) NA_real_ else median(x, na.rm = TRUE)
safe_quantile <- function(x, p) {
  if (all(is.na(x))) return(NA_real_)
  as.numeric(quantile(x, probs = p, na.rm = TRUE, names = FALSE))
}

summarise_cell <- function(d) {
  data.frame(
    sigma_true_m = d$sigma_true_m[1],
    handling_rms_m = d$handling_rms_m[1],
    n_replicates = nrow(d),
    check_fit_rate = mean(d$check_ok),
    first_fit_rate = mean(d$first_ok),
    last_fit_rate = mean(d$last_ok),
    mean_repeat_fraction = safe_mean(d$repeat_fraction),
    mean_shift_fraction_repeat = safe_mean(d$shift_fraction_repeat),
    median_first_last_m = safe_median(d$median_first_last_m),
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

rows <- list()
counter <- 0L
for (s in TRUE_SIGMAS) {
  for (h in HANDLING_RMS) {
    for (r in seq_len(reps)) {
      counter <- counter + 1L
      seed <- SEED0 + counter * 1009L
      message(sprintf("cell sigma=%.2f handling=%.2f rep=%d/%d", s, h, r, reps))
      rows[[counter]] <- one_replicate(seed, s, h, r)
    }
  }
}
replicates <- do.call(rbind, rows)

split_key <- interaction(replicates$sigma_true_m, replicates$handling_rms_m, drop = TRUE)
cell_list <- split(replicates, split_key)
summary_rows <- do.call(rbind, lapply(cell_list, summarise_cell))
rownames(summary_rows) <- NULL

# Descriptive empirical-scale match based only on observation-process outputs.
score <- abs(summary_rows$mean_shift_fraction_repeat - EMP_SHIFT) / 0.10 +
  abs(summary_rows$median_first_last_m - EMP_MEDIAN_SPAN) / SPACING
if (all(!is.finite(score))) {
  matched <- NULL
} else {
  j <- which.min(ifelse(is.finite(score), score, Inf))
  matched <- as.list(summary_rows[j, , drop = FALSE])
  matched$match_score <- score[j]
  matched$empirical_target_shift_fraction <- EMP_SHIFT
  matched$empirical_target_median_span_m <- EMP_MEDIAN_SPAN
}

# Negative-control summary is a required model check.
zero <- summary_rows[summary_rows$handling_rms_m == 0, , drop = FALSE]
negative_control <- list(
  cells = nrow(zero),
  max_abs_median_rel_error_check = if (nrow(zero)) max(abs(zero$median_rel_error_check), na.rm = TRUE) else NA_real_,
  max_abs_median_first_vs_check = if (nrow(zero)) max(abs(zero$median_first_vs_check), na.rm = TRUE) else NA_real_,
  max_abs_median_last_vs_check = if (nrow(zero)) max(abs(zero$median_last_vs_check), na.rm = TRUE) else NA_real_,
  max_abs_median_last_vs_first = if (nrow(zero)) max(abs(zero$median_last_vs_first), na.rm = TRUE) else NA_real_
)

result <- list(
  schema = "neon.san_jacinto_scr_sigma_downstream_simulation.v1",
  frozen_design = "docs/SAN_JACINTO_SCR_SIGMA_SIMULATION_DESIGN_V1.md",
  package = list(secr_version = as.character(packageVersion("secr"))),
  constants = list(
    spacing_m = SPACING,
    nights = NIGHTS,
    checks_per_night = CHECKS,
    g0 = G0,
    density_per_ha = DENSITY_PER_HA,
    mask_buffer_m = MASK_BUFFER,
    mask_spacing_m = MASK_SPACING,
    true_sigma_m = TRUE_SIGMAS,
    handling_rms_m = HANDLING_RMS,
    material_relative_difference_threshold = MATERIAL_THRESHOLD,
    replicates_per_cell = reps
  ),
  claim_boundary = list(
    empirical_sigma_opened = FALSE,
    empirical_two_species_gate_remains_stopped = TRUE,
    simulation_is_downstream_sensitivity_not_empirical_effect_estimate = TRUE
  ),
  empirical_observation_scale = list(
    mean_heldout_shift_fraction = EMP_SHIFT,
    mean_heldout_median_span_m = EMP_MEDIAN_SPAN
  ),
  negative_control = negative_control,
  empirically_scale_matched_cell = matched,
  cells = summary_rows
)

dir.create(dirname(out_csv), recursive = TRUE, showWarnings = FALSE)
write.csv(replicates, out_csv, row.names = FALSE, na = "")

dir.create(dirname(out_json), recursive = TRUE, showWarnings = FALSE)
writeLines(toJSON(result, pretty = TRUE, auto_unbox = TRUE, digits = 10, na = "null"), out_json)

print(summary_rows)
cat("\nNegative control:\n")
print(negative_control)
cat("\nEmpirically scale-matched cell:\n")
print(matched)
