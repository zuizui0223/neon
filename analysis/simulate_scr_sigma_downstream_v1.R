#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(secr)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
arg_value <- function(flag, default = NULL) {
  i <- match(flag, args)
  if (is.na(i)) return(default)
  if (i == length(args)) stop(paste("missing value after", flag))
  args[[i + 1]]
}

out_json <- arg_value("--output-json", "results/scr_sigma_downstream_simulation_v1.json")
out_csv <- arg_value("--output-csv", "results/scr_sigma_downstream_simulation_replicates_v1.csv")
reps <- as.integer(arg_value("--replicates", "12"))
seed_base <- as.integer(arg_value("--seed", "20261001"))

if (!is.finite(reps) || reps < 1) stop("replicates must be >=1")

spacing <- 6.25
nx <- 7
ny <- 7
nights <- 5
checks_per_night <- 4
n_population <- 350
buffer <- 100
lambda0 <- 0.10
response_probability <- 0.70
sigma_spacing <- c(0.5, 1, 2)
shift_spacing <- c(0, 1, 2, 3)
practical_threshold <- 0.10

tr <- make.grid(nx = nx, ny = ny, spacing = spacing, detector = "multi")
trdf <- as.data.frame(tr)
mask <- make.mask(tr, buffer = buffer, spacing = spacing, type = "traprect")

xmin <- min(trdf$x) - buffer
xmax <- max(trdf$x) + buffer
ymin <- min(trdf$y) - buffer
ymax <- max(trdf$y) + buffer

simulate_records <- function(seed, sigma_true, shift_m) {
  set.seed(seed)
  ac <- cbind(
    runif(n_population, xmin, xmax),
    runif(n_population, ymin, ymax)
  )

  rows <- vector("list", n_population * nights * checks_per_night)
  z <- 0L

  for (i in seq_len(n_population)) {
    for (night in seq_len(nights)) {
      offset <- c(0, 0)
      response_drawn <- FALSE

      for (check in seq_len(checks_per_night)) {
        effective <- ac[i, ] + offset
        dx <- trdf$x - effective[1]
        dy <- trdf$y - effective[2]
        d2 <- dx * dx + dy * dy
        lambda <- lambda0 * exp(-d2 / (2 * sigma_true * sigma_true))
        Lambda <- sum(lambda)

        if (Lambda > 0 && runif(1) < (1 - exp(-Lambda))) {
          trap_index <- sample.int(nrow(trdf), size = 1L, prob = lambda)
          z <- z + 1L
          rows[[z]] <- data.frame(
            id = as.character(i),
            night = night,
            check = check,
            check_occasion = (night - 1L) * checks_per_night + check,
            trap = trap_index,
            x = trdf$x[trap_index],
            y = trdf$y[trap_index],
            stringsAsFactors = FALSE
          )

          if (!response_drawn) {
            response_drawn <- TRUE
            if (shift_m > 0 && runif(1) < response_probability) {
              theta <- runif(1, 0, 2 * pi)
              offset <- shift_m * c(cos(theta), sin(theta))
            }
          }
        }
      }
    }
  }

  if (z == 0L) {
    return(data.frame(
      id = character(), night = integer(), check = integer(),
      check_occasion = integer(), trap = integer(),
      x = numeric(), y = numeric()
    ))
  }
  do.call(rbind, rows[seq_len(z)])
}

collapse_nightly <- function(records, which = c("first", "last")) {
  which <- match.arg(which)
  if (nrow(records) == 0) return(records)
  ord <- order(records$id, records$night, records$check)
  x <- records[ord, , drop = FALSE]
  key <- paste(x$id, x$night, sep = "::")
  keep <- if (which == "first") !duplicated(key) else !duplicated(key, fromLast = TRUE)
  y <- x[keep, , drop = FALSE]
  y$occasion <- y$night
  y
}

observation_summary <- function(records) {
  if (nrow(records) == 0) {
    return(list(
      detected_nights = 0L,
      repeat_capture_nights = 0L,
      repeat_capture_fraction = NA_real_,
      material_shift_fraction = NA_real_,
      median_span_m = NA_real_,
      median_changed_span_m = NA_real_
    ))
  }

  keys <- unique(paste(records$id, records$night, sep = "::"))
  spans <- numeric()
  for (k in keys) {
    parts <- strsplit(k, "::", fixed = TRUE)[[1]]
    g <- records[records$id == parts[1] & records$night == as.integer(parts[2]), , drop = FALSE]
    if (nrow(g) >= 2) {
      g <- g[order(g$check), , drop = FALSE]
      d <- sqrt((g$x[1] - g$x[nrow(g)])^2 + (g$y[1] - g$y[nrow(g)])^2)
      spans <- c(spans, d)
    }
  }

  changed <- spans[spans >= spacing - 1e-12]
  list(
    detected_nights = length(keys),
    repeat_capture_nights = length(spans),
    repeat_capture_fraction = if (length(keys)) length(spans) / length(keys) else NA_real_,
    material_shift_fraction = if (length(spans)) mean(spans >= spacing - 1e-12) else NA_real_,
    median_span_m = if (length(spans)) median(spans) else NA_real_,
    median_changed_span_m = if (length(changed)) median(changed) else NA_real_
  )
}

to_capthist <- function(records, representation) {
  if (nrow(records) == 0) return(NULL)
  if (representation == "CHECK") {
    dat <- data.frame(
      session = 1,
      id = records$id,
      occasion = records$check_occasion,
      trap = records$trap
    )
    no <- nights * checks_per_night
  } else if (representation == "FIRST") {
    x <- collapse_nightly(records, "first")
    dat <- data.frame(session = 1, id = x$id, occasion = x$occasion, trap = x$trap)
    no <- nights
  } else if (representation == "LAST") {
    x <- collapse_nightly(records, "last")
    dat <- data.frame(session = 1, id = x$id, occasion = x$occasion, trap = x$trap)
    no <- nights
  } else stop("unknown representation")
  make.capthist(dat, traps = tr, fmt = "trapID", noccasions = no)
}

fit_sigma <- function(records, representation) {
  ch <- tryCatch(to_capthist(records, representation), error = function(e) e)
  if (inherits(ch, "error") || is.null(ch)) {
    return(list(status = "capthist_fail", sigma = NA_real_, message = if (inherits(ch, "error")) conditionMessage(ch) else "no detections"))
  }

  fit <- tryCatch(
    suppressWarnings(
      secr.fit(
        capthist = ch,
        model = list(lambda0 ~ 1, sigma ~ 1),
        mask = mask,
        CL = TRUE,
        detectfn = "HHN",
        trace = FALSE,
        verify = TRUE
      )
    ),
    error = function(e) e
  )
  if (inherits(fit, "error")) {
    return(list(status = "fit_fail", sigma = NA_real_, message = conditionMessage(fit)))
  }

  dp <- tryCatch(detectpar(fit), error = function(e) e)
  if (inherits(dp, "error") || is.null(dp$sigma) || !is.finite(as.numeric(dp$sigma))) {
    return(list(status = "extract_fail", sigma = NA_real_, message = if (inherits(dp, "error")) conditionMessage(dp) else "sigma unavailable"))
  }

  list(status = "ok", sigma = as.numeric(dp$sigma), message = "")
}

scenario_grid <- expand.grid(
  sigma_spacing = sigma_spacing,
  shift_spacing = shift_spacing,
  KEEP.OUT.ATTRS = FALSE,
  stringsAsFactors = FALSE
)
scenario_grid <- scenario_grid[order(scenario_grid$sigma_spacing, scenario_grid$shift_spacing), , drop = FALSE]

out_rows <- list()
row_i <- 0L
scenario_i <- 0L

for (s in seq_len(nrow(scenario_grid))) {
  scenario_i <- scenario_i + 1L
  sig_sp <- scenario_grid$sigma_spacing[s]
  sh_sp <- scenario_grid$shift_spacing[s]
  sigma_true <- sig_sp * spacing
  shift_m <- sh_sp * spacing

  for (r in seq_len(reps)) {
    seed <- seed_base + scenario_i * 100000L + r
    records <- simulate_records(seed, sigma_true, shift_m)
    obs <- observation_summary(records)

    fit_check <- fit_sigma(records, "CHECK")
    fit_first <- fit_sigma(records, "FIRST")
    fit_last <- fit_sigma(records, "LAST")

    sig_check <- fit_check$sigma
    sig_first <- fit_first$sigma
    sig_last <- fit_last$sigma

    row_i <- row_i + 1L
    out_rows[[row_i]] <- data.frame(
      scenario = scenario_i,
      replicate = r,
      seed = seed,
      sigma_spacing = sig_sp,
      sigma_true_m = sigma_true,
      shift_spacing = sh_sp,
      shift_m = shift_m,
      response_probability = response_probability,
      n_raw_detections = nrow(records),
      n_detected_individuals = length(unique(records$id)),
      detected_nights = obs$detected_nights,
      repeat_capture_nights = obs$repeat_capture_nights,
      repeat_capture_fraction = obs$repeat_capture_fraction,
      material_shift_fraction = obs$material_shift_fraction,
      median_span_m = obs$median_span_m,
      median_changed_span_m = obs$median_changed_span_m,
      check_status = fit_check$status,
      first_status = fit_first$status,
      last_status = fit_last$status,
      check_message = fit_check$message,
      first_message = fit_first$message,
      last_message = fit_last$message,
      sigma_check_m = sig_check,
      sigma_first_m = sig_first,
      sigma_last_m = sig_last,
      relative_bias_check = (sig_check - sigma_true) / sigma_true,
      relative_bias_first = (sig_first - sigma_true) / sigma_true,
      relative_bias_last = (sig_last - sigma_true) / sigma_true,
      delta_first_check = (sig_first - sig_check) / sig_check,
      delta_last_check = (sig_last - sig_check) / sig_check,
      delta_last_first = (sig_last - sig_first) / sig_first,
      stringsAsFactors = FALSE
    )
  }
}

raw <- do.call(rbind, out_rows)

finite_mean <- function(x) {
  x <- x[is.finite(x)]
  if (!length(x)) return(NA_real_)
  mean(x)
}
finite_median <- function(x) {
  x <- x[is.finite(x)]
  if (!length(x)) return(NA_real_)
  median(x)
}
rmse <- function(est, truth) {
  ok <- is.finite(est) & is.finite(truth)
  if (!any(ok)) return(NA_real_)
  sqrt(mean((est[ok] - truth[ok])^2))
}
frac_material <- function(x) {
  x <- x[is.finite(x)]
  if (!length(x)) return(NA_real_)
  mean(abs(x) >= practical_threshold)
}

summaries <- list()
for (sc in unique(raw$scenario)) {
  x <- raw[raw$scenario == sc, , drop = FALSE]
  ok3 <- x$check_status == "ok" & x$first_status == "ok" & x$last_status == "ok"
  mean_shift <- finite_mean(x$material_shift_fraction)
  mean_changed <- finite_mean(x$median_changed_span_m)
  empirical_scale_region <- is.finite(mean_shift) && is.finite(mean_changed) &&
    mean_shift >= 0.60 && mean_shift <= 0.80 &&
    (mean_changed / spacing) >= 1.5 && (mean_changed / spacing) <= 2.5

  summaries[[length(summaries) + 1L]] <- list(
    scenario = sc,
    sigma_spacing = x$sigma_spacing[1],
    sigma_true_m = x$sigma_true_m[1],
    shift_spacing = x$shift_spacing[1],
    shift_m = x$shift_m[1],
    response_probability = response_probability,
    replicates = nrow(x),
    successful_three_way_fits = sum(ok3),
    fit_failure_fraction_check = mean(x$check_status != "ok"),
    fit_failure_fraction_first = mean(x$first_status != "ok"),
    fit_failure_fraction_last = mean(x$last_status != "ok"),
    mean_repeat_capture_fraction = finite_mean(x$repeat_capture_fraction),
    mean_material_shift_fraction = mean_shift,
    mean_median_span_m = finite_mean(x$median_span_m),
    mean_median_changed_span_m = mean_changed,
    empirical_scale_region = empirical_scale_region,
    mean_relative_bias_check = finite_mean(x$relative_bias_check),
    mean_relative_bias_first = finite_mean(x$relative_bias_first),
    mean_relative_bias_last = finite_mean(x$relative_bias_last),
    median_relative_bias_check = finite_median(x$relative_bias_check),
    median_relative_bias_first = finite_median(x$relative_bias_first),
    median_relative_bias_last = finite_median(x$relative_bias_last),
    median_abs_relative_bias_check = finite_median(abs(x$relative_bias_check)),
    median_abs_relative_bias_first = finite_median(abs(x$relative_bias_first)),
    median_abs_relative_bias_last = finite_median(abs(x$relative_bias_last)),
    rmse_check_m = rmse(x$sigma_check_m, x$sigma_true_m),
    rmse_first_m = rmse(x$sigma_first_m, x$sigma_true_m),
    rmse_last_m = rmse(x$sigma_last_m, x$sigma_true_m),
    median_delta_first_check = finite_median(x$delta_first_check[ok3]),
    median_delta_last_check = finite_median(x$delta_last_check[ok3]),
    median_delta_last_first = finite_median(x$delta_last_first[ok3]),
    frac_abs_delta_first_check_ge_10pct = frac_material(x$delta_first_check[ok3]),
    frac_abs_delta_last_check_ge_10pct = frac_material(x$delta_last_check[ok3]),
    frac_abs_delta_last_first_ge_10pct = frac_material(x$delta_last_first[ok3])
  )
}

summary_df <- do.call(rbind, lapply(summaries, function(z) {
  as.data.frame(z, stringsAsFactors = FALSE)
}))

stationary <- summary_df[summary_df$shift_spacing == 0, , drop = FALSE]
empirical_like <- summary_df[summary_df$empirical_scale_region %in% TRUE, , drop = FALSE]

result <- list(
  schema = "neon.scr_sigma_downstream_simulation.result.v1",
  generated_at = format(Sys.time(), tz = "UTC", usetz = TRUE),
  locked_design = list(
    seed_base = seed_base,
    replicates_per_cell = reps,
    trap_spacing_m = spacing,
    detector_grid = c(nx = nx, ny = ny),
    nights = nights,
    checks_per_night = checks_per_night,
    exact_population_n = n_population,
    buffer_m = buffer,
    lambda0 = lambda0,
    detectfn = "HHN",
    response_probability = response_probability,
    sigma_spacing = sigma_spacing,
    shift_spacing = shift_spacing,
    practical_relative_change_threshold = practical_threshold
  ),
  interpretation_guardrails = list(
    check_is_data_preserving_comparator_not_gold_standard_under_shift = TRUE,
    h_zero_is_stationary_scr_null = TRUE,
    post_release_shift_is_sensitivity_mechanism_not_empirical_handling_effect_estimate = TRUE,
    empirical_first_last_sigma_used_for_tuning = FALSE
  ),
  scenario_summaries = summaries,
  stationary_null_summaries = jsonlite::fromJSON(jsonlite::toJSON(stationary, dataframe = "rows", na = "null")),
  empirical_scale_summaries = jsonlite::fromJSON(jsonlite::toJSON(empirical_like, dataframe = "rows", na = "null"))
)

dir.create(dirname(out_csv), recursive = TRUE, showWarnings = FALSE)
dir.create(dirname(out_json), recursive = TRUE, showWarnings = FALSE)
write.csv(raw, out_csv, row.names = FALSE, na = "")
write_json(result, out_json, pretty = TRUE, auto_unbox = TRUE, na = "null")

cat(toJSON(list(
  n_scenarios = length(summaries),
  n_replicates = nrow(raw),
  stationary_cells = nrow(stationary),
  empirical_scale_cells = nrow(empirical_like),
  successful_three_way_fits = sum(
    raw$check_status == "ok" & raw$first_status == "ok" & raw$last_status == "ok"
  )
), pretty = TRUE, auto_unbox = TRUE), "\n")
