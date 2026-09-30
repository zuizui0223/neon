suppressPackageStartupMessages({
  library(secr)
  library(jsonlite)
})

# AI assistance disclosure: this exploratory simulation was drafted with
# OpenAI ChatGPT (GPT-5.6 Sol, October 2026) and remains under author
# responsibility. The empirical SCR effect gate remains stopped.

args <- commandArgs(trailingOnly = TRUE)
out_json <- if (length(args) >= 1) args[[1]] else "results/san_jacinto_scr_sigma_simulation_pilot_v1.json"
out_csv  <- if (length(args) >= 2) args[[2]] else "results/san_jacinto_scr_sigma_simulation_pilot_v1.csv"
n_reps   <- if (length(args) >= 3) as.integer(args[[3]]) else 8L

set.seed(20261001)

spacing <- 6.25
nx <- 7L
ny <- 7L
n_sessions <- 4L
n_animals <- 300L
n_nights <- 3L
checks_per_night <- 3L
sigma_true <- 11.0
g0_true <- 0.04
mask_buffer <- 100
mask_spacing <- 10

# Pooled already-opened San Jacinto targets.
target <- list(
  repeat_fraction = 592 / 1520,
  changed_fraction_given_repeat = 426 / 592,
  median_span_m = 8.838834764831844,
  changed_median_span_m = 12.5
)

make_base_traps <- function(check_level = FALSE) {
  tr <- make.grid(nx = nx, ny = ny, spacing = spacing, detector = "multi")
  if (check_level) {
    # 3 checks, closed separator, 3 checks, closed separator, 3 checks.
    u <- matrix(1, nrow = nrow(tr), ncol = 11)
    u[, c(4, 8)] <- 0
    usage(tr) <- u
  } else {
    usage(tr) <- matrix(1, nrow = nrow(tr), ncol = n_nights)
  }
  tr
}

trap_xy <- as.data.frame(make_base_traps(FALSE))[, c("x", "y"), drop = FALSE]
center_mask <- as.data.frame(
  make.mask(make_base_traps(FALSE), buffer = mask_buffer,
            spacing = mask_spacing, type = "trapbuffer")
)[, c("x", "y"), drop = FALSE]

draw_capture <- function(cx, cy, previous_trap = NA_integer_,
                         recapture_factor = 1) {
  d2 <- (trap_xy$x - cx)^2 + (trap_xy$y - cy)^2
  gj <- g0_true * exp(-d2 / (2 * sigma_true^2))
  if (!is.na(previous_trap)) {
    gj[previous_trap] <- min(0.999999, gj[previous_trap] * recapture_factor)
  }

  # Multi-catch competing-risk representation: detector-specific hazards sum.
  hj <- -log1p(-pmin(gj, 0.999999))
  H <- sum(hj)
  if (!is.finite(H) || H <= 0 || runif(1) >= 1 - exp(-H)) {
    return(NA_integer_)
  }
  sample.int(length(hj), size = 1L, prob = hj)
}

simulate_session <- function(session_id, recapture_factor) {
  centre_idx <- sample(
    seq_len(nrow(center_mask)),
    n_animals,
    replace = n_animals > nrow(center_mask)
  )
  centres <- center_mask[centre_idx, , drop = FALSE]

  rows <- vector("list", n_animals * n_nights * checks_per_night)
  z <- 0L

  for (i in seq_len(n_animals)) {
    id <- sprintf("S%02d_A%04d", session_id, i)
    for (night in seq_len(n_nights)) {
      previous_trap <- NA_integer_
      occs <- switch(
        as.character(night),
        "1" = c(1L, 2L, 3L),
        "2" = c(5L, 6L, 7L),
        "3" = c(9L, 10L, 11L)
      )
      for (j in seq_len(checks_per_night)) {
        trap <- draw_capture(
          centres$x[i], centres$y[i],
          previous_trap = previous_trap,
          recapture_factor = recapture_factor
        )
        if (!is.na(trap)) {
          z <- z + 1L
          rows[[z]] <- data.frame(
            session = session_id,
            ID = id,
            occasion = occs[j],
            night = night,
            check = j,
            trap = trap,
            stringsAsFactors = FALSE
          )
          previous_trap <- trap
        } else {
          # Bk is transient: no capture on the immediately preceding check
          # removes the local response on the next check.
          previous_trap <- NA_integer_
        }
      }
    }
  }
  if (z == 0L) {
    return(data.frame(
      session = integer(), ID = character(), occasion = integer(),
      night = integer(), check = integer(), trap = integer()
    ))
  }
  do.call(rbind, rows[seq_len(z)])
}

simulate_dataset <- function(recapture_factor) {
  parts <- lapply(seq_len(n_sessions), simulate_session,
                  recapture_factor = recapture_factor)
  do.call(rbind, parts)
}

night_summaries <- function(records) {
  if (nrow(records) == 0L) {
    return(list(
      observed_nights = 0L, repeat_nights = 0L,
      repeat_fraction = NA_real_, changed_fraction = NA_real_,
      median_span_m = NA_real_, changed_median_span_m = NA_real_
    ))
  }

  key <- interaction(records$session, records$ID, records$night, drop = TRUE)
  groups <- split(records, key)
  spans <- c()
  observed <- length(groups)
  repeat_n <- 0L

  for (g in groups) {
    g <- g[order(g$occasion, g$trap), , drop = FALSE]
    if (nrow(g) < 2L) next
    repeat_n <- repeat_n + 1L
    a <- trap_xy[g$trap[1], ]
    b <- trap_xy[g$trap[nrow(g)], ]
    spans <- c(spans, sqrt((a$x - b$x)^2 + (a$y - b$y)^2))
  }

  changed <- spans[spans > 1e-12]
  list(
    observed_nights = observed,
    repeat_nights = repeat_n,
    repeat_fraction = if (observed) repeat_n / observed else NA_real_,
    changed_fraction = if (length(spans)) mean(spans > 1e-12) else NA_real_,
    median_span_m = if (length(spans)) median(spans) else NA_real_,
    changed_median_span_m = if (length(changed)) median(changed) else NA_real_
  )
}

night_reduction <- function(records, which = c("first", "last")) {
  which <- match.arg(which)
  key <- interaction(records$session, records$ID, records$night, drop = TRUE)
  groups <- split(records, key)
  picked <- lapply(groups, function(g) {
    ord <- order(g$occasion, g$trap)
    g <- g[ord, , drop = FALSE]
    if (which == "first") g[1, , drop = FALSE] else g[nrow(g), , drop = FALSE]
  })
  x <- do.call(rbind, picked)
  x$occasion <- x$night
  x[, c("session", "ID", "occasion", "trap"), drop = FALSE]
}

make_check_capthist <- function(records) {
  traps <- lapply(seq_len(n_sessions), function(i) make_base_traps(TRUE))
  make.capthist(
    records[, c("session", "ID", "occasion", "trap"), drop = FALSE],
    traps = traps, fmt = "trapID",
    noccasions = rep(11L, n_sessions)
  )
}

make_night_capthist <- function(records, which) {
  traps <- lapply(seq_len(n_sessions), function(i) make_base_traps(FALSE))
  red <- night_reduction(records, which)
  make.capthist(
    red, traps = traps, fmt = "trapID",
    noccasions = rep(n_nights, n_sessions)
  )
}

make_masks <- function(capthist) {
  lapply(
    traps(capthist),
    function(tr) make.mask(tr, buffer = mask_buffer,
                           spacing = mask_spacing, type = "trapbuffer")
  )
}

fit_one <- function(capthist, behaviour = FALSE) {
  mdl <- if (behaviour) list(g0 ~ Bk, sigma ~ 1) else list(g0 ~ 1, sigma ~ 1)
  masks <- make_masks(capthist)

  fit <- tryCatch(
    secr.fit(
      capthist, mask = masks, CL = TRUE, detectfn = "HN",
      model = mdl, trace = FALSE, verify = FALSE
    ),
    error = function(e) e
  )
  if (inherits(fit, "error")) {
    return(list(ok = FALSE, sigma = NA_real_, aic = NA_real_,
                error = conditionMessage(fit)))
  }

  pr <- predict(fit)
  ridx <- which(rownames(pr) == "sigma")
  if (length(ridx) != 1L) {
    ridx <- grep("^sigma", rownames(pr))
  }
  sigma_hat <- if (length(ridx) >= 1L) as.numeric(pr[ridx[1], "estimate"]) else NA_real_
  aa <- suppressWarnings(AIC(fit, criterion = "AIC"))
  aic_value <- if ("AIC" %in% colnames(aa)) as.numeric(aa[1, "AIC"]) else NA_real_
  list(
    ok = is.finite(sigma_hat),
    sigma = sigma_hat,
    aic = aic_value,
    error = if (is.finite(sigma_hat)) "" else "sigma row not found"
  )
}

run_replicate <- function(regime, recapture_factor, rep_id) {
  records <- simulate_dataset(recapture_factor)
  cal <- night_summaries(records)

  check_ch <- make_check_capthist(records)
  first_ch <- make_night_capthist(records, "first")
  last_ch <- make_night_capthist(records, "last")

  check_naive <- fit_one(check_ch, behaviour = FALSE)
  check_bk <- fit_one(check_ch, behaviour = TRUE)
  first_fit <- fit_one(first_ch, behaviour = FALSE)
  last_fit <- fit_one(last_ch, behaviour = FALSE)

  data.frame(
    regime = regime,
    replicate = rep_id,
    recapture_factor = recapture_factor,
    observed_nights = cal$observed_nights,
    repeat_nights = cal$repeat_nights,
    repeat_fraction = cal$repeat_fraction,
    changed_fraction = cal$changed_fraction,
    median_span_m = cal$median_span_m,
    changed_median_span_m = cal$changed_median_span_m,
    sigma_true = sigma_true,
    sigma_check_naive = check_naive$sigma,
    sigma_check_Bk = check_bk$sigma,
    sigma_night_first = first_fit$sigma,
    sigma_night_last = last_fit$sigma,
    ratio_check_naive_true = check_naive$sigma / sigma_true,
    ratio_check_Bk_true = check_bk$sigma / sigma_true,
    ratio_first_check_Bk = first_fit$sigma / check_bk$sigma,
    ratio_last_check_Bk = last_fit$sigma / check_bk$sigma,
    ratio_last_first = last_fit$sigma / first_fit$sigma,
    aic_check_naive = check_naive$aic,
    aic_check_Bk = check_bk$aic,
    all_fits_ok = check_naive$ok && check_bk$ok && first_fit$ok && last_fit$ok,
    error_check_naive = check_naive$error,
    error_check_Bk = check_bk$error,
    error_first = first_fit$error,
    error_last = last_fit$error,
    stringsAsFactors = FALSE
  )
}

regimes <- list(
  no_dependence = 1,
  san_jacinto_like_local_response = 10
)

rows <- list()
z <- 0L
for (regime in names(regimes)) {
  for (rep_id in seq_len(n_reps)) {
    message("running ", regime, " replicate ", rep_id, "/", n_reps)
    z <- z + 1L
    rows[[z]] <- run_replicate(regime, regimes[[regime]], rep_id)
  }
}
res <- do.call(rbind, rows)

dir.create(dirname(out_csv), recursive = TRUE, showWarnings = FALSE)
write.csv(res, out_csv, row.names = FALSE)

summarise_regime <- function(x) {
  good <- x[is.finite(x$sigma_check_Bk) & is.finite(x$sigma_night_first) &
              is.finite(x$sigma_night_last), , drop = FALSE]
  med <- function(v) if (length(v)) median(v, na.rm = TRUE) else NA_real_
  mn <- function(v) if (length(v)) mean(v, na.rm = TRUE) else NA_real_
  list(
    replicates = nrow(x),
    successful_replicates = nrow(good),
    calibration = list(
      mean_repeat_fraction = mn(x$repeat_fraction),
      mean_changed_fraction = mn(x$changed_fraction),
      median_of_median_span_m = med(x$median_span_m),
      median_of_changed_median_span_m = med(x$changed_median_span_m)
    ),
    sigma = list(
      median_check_naive = med(x$sigma_check_naive),
      median_check_Bk = med(x$sigma_check_Bk),
      median_night_first = med(x$sigma_night_first),
      median_night_last = med(x$sigma_night_last),
      median_ratio_check_naive_true = med(x$ratio_check_naive_true),
      median_ratio_check_Bk_true = med(x$ratio_check_Bk_true),
      median_ratio_first_check_Bk = med(x$ratio_first_check_Bk),
      median_ratio_last_check_Bk = med(x$ratio_last_check_Bk),
      median_ratio_last_first = med(x$ratio_last_first),
      fraction_first_ge_10pct_from_check_Bk =
        mn(abs(x$ratio_first_check_Bk - 1) >= 0.10),
      fraction_last_ge_10pct_from_check_Bk =
        mn(abs(x$ratio_last_check_Bk - 1) >= 0.10),
      fraction_check_naive_ge_10pct_from_true =
        mn(abs(x$ratio_check_naive_true - 1) >= 0.10),
      fraction_check_Bk_ge_10pct_from_true =
        mn(abs(x$ratio_check_Bk_true - 1) >= 0.10)
    )
  )
}

summary <- list(
  schema = "neon.san_jacinto_scr_sigma_simulation_pilot.v1",
  seed = 20261001,
  n_reps_per_regime = n_reps,
  design = list(
    grid = "7x7",
    trap_spacing_m = spacing,
    nights_per_session = n_nights,
    checks_per_night = checks_per_night,
    sessions_per_replicate = n_sessions,
    activity_centres_per_session = n_animals,
    sigma_true_m = sigma_true,
    g0_true = g0_true,
    mask_buffer_m = mask_buffer,
    mask_spacing_m = mask_spacing,
    material_relative_change = 0.10
  ),
  empirical_targets = target,
  regimes = lapply(names(regimes), function(nm) {
    c(list(name = nm, local_recapture_factor = regimes[[nm]]),
      summarise_regime(res[res$regime == nm, , drop = FALSE]))
  }),
  claim_boundary = list(
    empirical_sigma_opened = FALSE,
    simulation_is_exploratory = TRUE,
    local_response_is_a_generative_calibration_device_not_a_causal_claim = TRUE,
    primary_question = paste(
      "whether nightly collapse or naive check-level occasioning changes",
      "sigma relative to a dependence-aware check-level analysis"
    )
  ),
  package_versions = list(
    R = as.character(getRversion()),
    secr = as.character(packageVersion("secr")),
    jsonlite = as.character(packageVersion("jsonlite"))
  )
)

dir.create(dirname(out_json), recursive = TRUE, showWarnings = FALSE)
write_json(summary, out_json, auto_unbox = TRUE, pretty = TRUE, na = "null")
cat(toJSON(summary, auto_unbox = TRUE, pretty = TRUE, na = "null"), "\n")
