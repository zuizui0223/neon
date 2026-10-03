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

out_json <- arg_value("--output-json", "results/scr_temporal_collapse_pilot_v1.json")
out_csv <- arg_value("--output-csv", "results/scr_temporal_collapse_pilot_replicates_v1.csv")
replicates <- as.integer(arg_value("--replicates", "6"))
seed0 <- as.integer(arg_value("--seed", "20261003"))

spacing_m <- 6.25
nights <- 3L
true_sigma <- 12.5
centre_p <- 0.15
density <- 30
pop_buffer <- 100
mask_buffer <- 75

tr <- make.grid(
  nx = 7, ny = 7, spacing = spacing_m,
  detector = "multi", origin = c(0, 0)
)
mk <- make.mask(tr, buffer = mask_buffer, spacing = 5)

trap_index <- function(x, tr) {
  z <- as.character(x)
  rn <- rownames(tr)
  out <- match(z, rn)
  bad <- is.na(out)
  if (any(bad)) {
    suppressWarnings(num <- as.integer(z[bad]))
    out[bad] <- num
  }
  if (any(is.na(out)) || any(out < 1) || any(out > nrow(tr))) {
    stop("could not map exported TrapID to detector index")
  }
  out
}

capture_frame <- function(ch, checks) {
  d <- as.data.frame(ch, fmt = "trapID")
  names(d)[1:4] <- c("Session", "ID", "Occasion", "TrapID")
  d$Occasion <- as.integer(d$Occasion)
  d$TrapNum <- trap_index(d$TrapID, tr)
  d$Night <- ((d$Occasion - 1L) %/% checks) + 1L
  d$Check <- ((d$Occasion - 1L) %% checks) + 1L
  d
}

collapse_history <- function(d, which = c("first", "last"), checks) {
  which <- match.arg(which)
  if (nrow(d) == 0) stop("no detections")
  ord <- order(d$ID, d$Night, d$Occasion)
  d <- d[ord, , drop = FALSE]
  key <- paste(d$ID, d$Night, sep = "::")
  idx_by <- split(seq_len(nrow(d)), key)
  chosen <- vapply(idx_by, function(ii) {
    if (which == "first") ii[[1]] else ii[[length(ii)]]
  }, integer(1))
  z <- d[unname(chosen), , drop = FALSE]
  z <- z[order(z$ID, z$Night), , drop = FALSE]
  captures <- data.frame(
    Session = 1,
    ID = as.character(z$ID),
    Occasion = as.integer(z$Night),
    TrapID = as.integer(z$TrapNum)
  )
  make.capthist(
    captures = captures,
    traps = tr,
    fmt = "trapID",
    noccasions = nights,
    bysession = TRUE
  )
}

repeat_night_summary <- function(d) {
  if (nrow(d) == 0) {
    return(list(repeat_nights = 0L, material_shift_fraction = NA_real_,
                changed_median_m = NA_real_))
  }
  xy <- as.data.frame(tr)[, c("x", "y"), drop = FALSE]
  key <- paste(d$ID, d$Night, sep = "::")
  groups <- split(seq_len(nrow(d)), key)
  dist <- c()
  for (ii in groups) {
    if (length(ii) < 2) next
    zz <- d[ii, , drop = FALSE]
    zz <- zz[order(zz$Occasion), , drop = FALSE]
    a <- xy[zz$TrapNum[[1]], ]
    b <- xy[zz$TrapNum[[nrow(zz)]], ]
    dist <- c(dist, sqrt((a$x - b$x)^2 + (a$y - b$y)^2))
  }
  if (!length(dist)) {
    return(list(repeat_nights = 0L, material_shift_fraction = NA_real_,
                changed_median_m = NA_real_))
  }
  changed <- dist > 1e-12
  list(
    repeat_nights = length(dist),
    material_shift_fraction = mean(dist >= spacing_m - 1e-12),
    changed_median_m = if (any(changed)) median(dist[changed]) else 0
  )
}

fit_sigma <- function(ch, detectfn, binomN = NULL) {
  ans <- tryCatch({
    fit <- secr.fit(
      ch,
      mask = mk,
      CL = TRUE,
      detectfn = detectfn,
      binomN = binomN,
      trace = FALSE,
      ncores = 1
    )
    p <- predict(fit)
    if (!("sigma" %in% rownames(p))) stop("sigma row absent from predict(fit)")
    list(
      ok = TRUE,
      sigma = unname(p["sigma", "estimate"]),
      logLik = as.numeric(logLik(fit))
    )
  }, error = function(e) {
    list(ok = FALSE, sigma = NA_real_, logLik = NA_real_,
         error = conditionMessage(e))
  })
  ans
}

simulate_one <- function(detectfn, checks, rep_id, seed) {
  if (detectfn == "HN") {
    detectpar <- list(g0 = centre_p, sigma = true_sigma)
  } else if (detectfn == "HHN") {
    detectpar <- list(lambda0 = -log(1 - centre_p), sigma = true_sigma)
  } else stop("unsupported detectfn")

  ch <- sim.capthist(
    tr,
    popn = list(D = density, buffer = pop_buffer),
    detectfn = detectfn,
    detectpar = detectpar,
    noccasions = nights * checks,
    seed = seed
  )
  d <- capture_frame(ch, checks)
  first_ch <- collapse_history(d, "first", checks)
  last_ch <- collapse_history(d, "last", checks)
  count_ch <- tryCatch(
    reduce(
      ch,
      by = checks,
      outputdetector = "count",
      dropunused = FALSE
    ),
    error = function(e) e
  )

  f_check <- fit_sigma(ch, detectfn)
  f_first <- fit_sigma(first_ch, detectfn)
  f_last <- fit_sigma(last_ch, detectfn)
  f_count <- if (inherits(count_ch, "error")) {
    list(ok = FALSE, sigma = NA_real_, logLik = NA_real_,
         error = conditionMessage(count_ch))
  } else {
    fit_sigma(count_ch, detectfn, binomN = 1)
  }
  rs <- repeat_night_summary(d)

  data.frame(
    detectfn = detectfn,
    checks_per_night = checks,
    replicate = rep_id,
    seed = seed,
    true_sigma = true_sigma,
    centre_detection_probability = centre_p,
    animals_detected = length(unique(d$ID)),
    detections = nrow(d),
    repeat_nights = rs$repeat_nights,
    material_shift_fraction = rs$material_shift_fraction,
    changed_median_m = rs$changed_median_m,
    check_fit_ok = f_check$ok,
    first_fit_ok = f_first$ok,
    last_fit_ok = f_last$ok,
    count_fit_ok = f_count$ok,
    sigma_check = f_check$sigma,
    sigma_first = f_first$sigma,
    sigma_last = f_last$sigma,
    sigma_count = f_count$sigma,
    relerr_check = f_check$sigma / true_sigma - 1,
    relerr_first = f_first$sigma / true_sigma - 1,
    relerr_last = f_last$sigma / true_sigma - 1,
    relerr_count = f_count$sigma / true_sigma - 1,
    first_vs_check = f_first$sigma / f_check$sigma - 1,
    last_vs_check = f_last$sigma / f_check$sigma - 1,
    count_vs_check = f_count$sigma / f_check$sigma - 1,
    last_vs_first = f_last$sigma / f_first$sigma - 1,
    stringsAsFactors = FALSE
  )
}

rows <- list()
k <- 0L
for (detectfn in c("HN", "HHN")) {
  for (checks in 1:4) {
    for (r in seq_len(replicates)) {
      k <- k + 1L
      s <- seed0 + k * 1009L
      message(sprintf(
        "cell detectfn=%s checks=%d replicate=%d/%d seed=%d",
        detectfn, checks, r, replicates, s
      ))
      rows[[k]] <- simulate_one(detectfn, checks, r, s)
    }
  }
}
res <- do.call(rbind, rows)

safe_mean <- function(x) {
  x <- x[is.finite(x)]
  if (!length(x)) return(NA_real_)
  mean(x)
}
safe_median <- function(x) {
  x <- x[is.finite(x)]
  if (!length(x)) return(NA_real_)
  median(x)
}

keys <- unique(res[, c("detectfn", "checks_per_night")])
summary_rows <- list()
for (i in seq_len(nrow(keys))) {
  a <- keys[i, ]
  z <- res[
    res$detectfn == a$detectfn &
      res$checks_per_night == a$checks_per_night, ,
    drop = FALSE
  ]
  summary_rows[[i]] <- data.frame(
    detectfn = a$detectfn,
    checks_per_night = a$checks_per_night,
    replicates = nrow(z),
    all_four_fit_fraction = mean(z$check_fit_ok & z$first_fit_ok & z$last_fit_ok & z$count_fit_ok),
    mean_relerr_check = safe_mean(z$relerr_check),
    mean_relerr_first = safe_mean(z$relerr_first),
    mean_relerr_last = safe_mean(z$relerr_last),
    mean_relerr_count = safe_mean(z$relerr_count),
    mean_first_vs_check = safe_mean(z$first_vs_check),
    mean_last_vs_check = safe_mean(z$last_vs_check),
    mean_count_vs_check = safe_mean(z$count_vs_check),
    mean_last_vs_first = safe_mean(z$last_vs_first),
    mean_repeat_nights = safe_mean(z$repeat_nights),
    mean_material_shift_fraction = safe_mean(z$material_shift_fraction),
    median_changed_median_m = safe_median(z$changed_median_m),
    stringsAsFactors = FALSE
  )
}
summ <- do.call(rbind, summary_rows)

pilot <- list(
  schema = "neon.scr_temporal_collapse.pilot.v1",
  frozen_settings = list(
    nights = nights,
    checks_per_night = 1:4,
    detector = "multi",
    grid = "7x7",
    spacing_m = spacing_m,
    true_sigma_m = true_sigma,
    centre_detection_probability_per_check = centre_p,
    density_animals_per_ha = density,
    population_buffer_m = pop_buffer,
    fit_mask_buffer_m = mask_buffer,
    likelihood = "conditional",
    generating_detection_functions = c("HN", "HHN"),
    fitted_detection_function = "matched_to_generator",
    handling_displacement = "none"
  ),
  empirical_calibration_band = list(
    repeat_night_material_shift_fraction = c(0.69, 0.73),
    changed_night_median_distance_m = c(12.5, 14.0)
  ),
  summary = unname(split(summ, seq_len(nrow(summ)))),
  interpretation_guardrails = list(
    empirical_sigma_effect_opened = FALSE,
    empirical_scr_stop_gate_relaxed = FALSE,
    pilot_is_final_monte_carlo = FALSE
  )
)

dir.create(dirname(out_json), recursive = TRUE, showWarnings = FALSE)
write_json(pilot, out_json, pretty = TRUE, auto_unbox = TRUE, digits = 10)
write.csv(res, out_csv, row.names = FALSE)
print(summ)
