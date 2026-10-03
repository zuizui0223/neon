#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(secr)
  library(jsonlite)
})

# End-to-end simulation for temporal aggregation of repeated live-trap checks.
# Scientific design is frozen in:
# docs/SCR_TEMPORAL_AGGREGATION_SIGMA_SIMULATION_DESIGN_V1.md

args <- commandArgs(trailingOnly = TRUE)
arg_value <- function(flag, default = NULL) {
  i <- match(flag, args)
  if (is.na(i)) return(default)
  if (i == length(args)) stop(flag, " requires a value")
  args[[i + 1]]
}

out_json <- arg_value("--output-json", "results/scr_temporal_aggregation_sigma_v1.json")
out_csv <- arg_value("--output-csv", "results/scr_temporal_aggregation_sigma_replicates_v1.csv")
replicates <- as.integer(arg_value("--replicates", "20"))
seed0 <- as.integer(arg_value("--seed", "20261003"))

if (!is.finite(replicates) || replicates < 1) stop("replicates must be >= 1")
setNumThreads(1)

spacing_m <- 6.25
sigma_true <- 12.5
nights <- 5L
checks_per_night <- 4L
nocc <- nights * checks_per_night
g0_onecheck <- 0.15
lambda0_onecheck <- -log(1 - g0_onecheck)

trp <- make.grid(
  nx = 7, ny = 7, spacing = spacing_m,
  detector = "multi"
)
msk <- make.mask(trp, buffer = 100, spacing = 5)

# ---------- deterministic fixed-detector closure calculation ----------

hn_prob <- function(d, g0, sigma) {
  g0 * exp(-(d^2) / (2 * sigma^2))
}

hhn_prob <- function(d, lambda0, sigma) {
  1 - exp(-lambda0 * exp(-(d^2) / (2 * sigma^2)))
}

hn_aggregated <- function(d, g0, sigma, K) {
  1 - (1 - hn_prob(d, g0, sigma))^K
}

hhn_aggregated <- function(d, lambda0, sigma, K) {
  1 - exp(-K * lambda0 * exp(-(d^2) / (2 * sigma^2)))
}

hn_effective_sigma <- function(g0, sigma, K) {
  if (K == 1L) return(sigma)
  q0 <- hn_aggregated(0, g0, sigma, K)
  target <- q0 * exp(-0.5)
  f <- function(d) hn_aggregated(d, g0, sigma, K) - target
  uniroot(f, interval = c(0, 10 * sigma))$root
}

closure_rows <- list()
kk <- 1L
for (K in c(1L, 2L, 4L, 8L)) {
  for (p0 in c(0.05, 0.15, 0.30, 0.50)) {
    lam0 <- -log(1 - p0)
    dgrid <- seq(0, 4 * sigma_true, length.out = 401)
    hhn_a <- hhn_aggregated(dgrid, lam0, sigma_true, K)
    hhn_b <- hhn_prob(dgrid, K * lam0, sigma_true)
    s_eff <- hn_effective_sigma(p0, sigma_true, K)
    closure_rows[[kk]] <- data.frame(
      checks = K,
      onecheck_centre_probability = p0,
      hn_effective_sigma_m = s_eff,
      hn_effective_sigma_ratio = s_eff / sigma_true,
      hhn_max_abs_closure_error = max(abs(hhn_a - hhn_b)),
      stringsAsFactors = FALSE
    )
    kk <- kk + 1L
  }
}
closure_df <- do.call(rbind, closure_rows)

# Frozen deterministic checks.
stopifnot(
  all(abs(closure_df$hn_effective_sigma_ratio[closure_df$checks == 1] - 1) < 1e-8),
  all(closure_df$hn_effective_sigma_ratio[closure_df$checks > 1] > 1),
  max(closure_df$hhn_max_abs_closure_error) < 1e-12
)

# ---------- capthist helpers ----------

capthist_records <- function(ch) {
  z <- as.data.frame(ch, fmt = "trapID")
  if (nrow(z) == 0L) {
    return(data.frame(
      session = character(), id = character(), occasion = integer(),
      trap = integer(), stringsAsFactors = FALSE
    ))
  }
  if (ncol(z) < 4L) stop("unexpected capthist data-frame format")
  z <- z[, 1:4, drop = FALSE]
  names(z) <- c("session", "id", "occasion", "trap")
  z$id <- as.character(z$id)
  z$occasion <- as.integer(z$occasion)

  trap_names <- rownames(as.data.frame(traps(ch)))
  if (is.numeric(z$trap)) {
    z$trap <- as.integer(z$trap)
  } else {
    trap_chr <- as.character(z$trap)
    trap_int <- suppressWarnings(as.integer(trap_chr))
    if (anyNA(trap_int)) {
      trap_int <- match(trap_chr, trap_names)
    }
    z$trap <- trap_int
  }
  if (anyNA(z$trap)) stop("could not map exported trap IDs to detector indices")
  z
}

records_to_capthist <- function(z, trp, noccasions) {
  if (nrow(z) == 0L) stop("cannot construct capthist from zero detections")
  captures <- data.frame(
    session = 1,
    id = z$id,
    occasion = as.integer(z$occasion),
    trap = as.integer(z$trap),
    stringsAsFactors = FALSE
  )
  make.capthist(
    captures = captures,
    traps = trp,
    fmt = "trapID",
    noccasions = noccasions,
    bysession = FALSE,
    sortrows = TRUE
  )
}

nearest_trap <- function(x, y, trap_xy) {
  which.min((trap_xy[, 1] - x)^2 + (trap_xy[, 2] - y)^2)
}

perturb_after_first <- function(ch, checks_per_night, move_prob, radial_median_m, seed) {
  if (move_prob <= 0 || radial_median_m <= 0) return(ch)

  z <- capthist_records(ch)
  if (nrow(z) == 0L) return(ch)
  z$night <- ((z$occasion - 1L) %/% checks_per_night) + 1L

  trap_xy <- as.matrix(as.data.frame(traps(ch))[, c("x", "y")])
  component_sd <- radial_median_m / sqrt(2 * log(2))

  set.seed(seed)
  keys <- interaction(z$id, z$night, drop = TRUE, lex.order = TRUE)
  idxs <- split(seq_len(nrow(z)), keys)

  for (idx in idxs) {
    if (length(idx) < 2L) next
    ord <- idx[order(z$occasion[idx])]
    if (runif(1) >= move_prob) next

    dx <- rnorm(1, 0, component_sd)
    dy <- rnorm(1, 0, component_sd)
    later <- ord[-1L]

    for (j in later) {
      old <- z$trap[j]
      xnew <- trap_xy[old, 1] + dx
      ynew <- trap_xy[old, 2] + dy
      z$trap[j] <- nearest_trap(xnew, ynew, trap_xy)
    }
  }

  records_to_capthist(z, traps(ch), nocc)
}

fit_sigma <- function(ch, detectfn, mask) {
  model <- if (detectfn == "HN") {
    list(g0 ~ 1, sigma ~ 1)
  } else if (detectfn == "HHN") {
    list(lambda0 ~ 1, sigma ~ 1)
  } else {
    stop("unsupported detectfn")
  }

  fit <- try(
    suppressWarnings(
      secr.fit(
        ch,
        model = model,
        mask = mask,
        CL = TRUE,
        detectfn = detectfn,
        trace = FALSE,
        biasLimit = NA
      )
    ),
    silent = TRUE
  )
  if (inherits(fit, "try-error")) {
    return(list(success = FALSE, sigma = NA_real_, message = as.character(fit)))
  }

  pred <- try(predict(fit), silent = TRUE)
  if (inherits(pred, "try-error") || is.list(pred)) {
    return(list(success = FALSE, sigma = NA_real_, message = "predict failed"))
  }
  rn <- rownames(pred)
  ii <- which(rn == "sigma")
  if (length(ii) != 1L || !"estimate" %in% colnames(pred)) {
    return(list(success = FALSE, sigma = NA_real_, message = "sigma row missing"))
  }
  est <- as.numeric(pred[ii, "estimate"])
  ok <- is.finite(est) && est > 0
  list(success = ok, sigma = if (ok) est else NA_real_, message = if (ok) "" else "invalid sigma")
}

fit_representation <- function(ch, detectfn, representation) {
  target <- switch(
    representation,
    CHECK = ch,
    FIRST = reduce(
      ch, by = checks_per_night, select = "first",
      outputdetector = "multi", dropunused = FALSE, verify = TRUE
    ),
    LAST = reduce(
      ch, by = checks_per_night, select = "last",
      outputdetector = "multi", dropunused = FALSE, verify = TRUE
    ),
    stop("unknown representation")
  )
  fit_sigma(target, detectfn, msk)
}

simulate_one <- function(seed, detectfn, perturbation) {
  detectpar <- if (detectfn == "HN") {
    list(g0 = g0_onecheck, sigma = sigma_true)
  } else {
    list(lambda0 = lambda0_onecheck, sigma = sigma_true)
  }

  raw <- sim.capthist(
    trp,
    popn = list(D = 10, buffer = 100, Ndist = "poisson"),
    detectfn = detectfn,
    detectpar = detectpar,
    noccasions = nocc,
    seed = seed
  )

  if (nrow(raw) < 5L) {
    return(data.frame(
      detectfn = detectfn, perturbation = perturbation,
      representation = c("CHECK", "FIRST", "LAST"),
      success = FALSE, sigma_hat = NA_real_,
      sigma_relative_error = NA_real_,
      detected_animals = nrow(raw),
      stringsAsFactors = FALSE
    ))
  }

  move_prob <- if (perturbation == "NONE") 0 else 0.70
  move_median <- if (perturbation == "NONE") 0 else 13.0
  ch <- perturb_after_first(
    raw,
    checks_per_night = checks_per_night,
    move_prob = move_prob,
    radial_median_m = move_median,
    seed = seed + 700001L
  )

  rows <- lapply(c("CHECK", "FIRST", "LAST"), function(repname) {
    a <- fit_representation(ch, detectfn, repname)
    data.frame(
      detectfn = detectfn,
      perturbation = perturbation,
      representation = repname,
      success = a$success,
      sigma_hat = a$sigma,
      sigma_relative_error = if (a$success) (a$sigma - sigma_true) / sigma_true else NA_real_,
      detected_animals = nrow(ch),
      stringsAsFactors = FALSE
    )
  })
  do.call(rbind, rows)
}

# ---------- run primary end-to-end experiment ----------

all_rows <- list()
rr <- 1L
scenario_index <- 0L
for (detectfn in c("HN", "HHN")) {
  for (perturbation in c("NONE", "SAN_JACINTO")) {
    scenario_index <- scenario_index + 1L
    for (r in seq_len(replicates)) {
      seed <- seed0 + scenario_index * 100000L + r * 1009L
      z <- simulate_one(seed, detectfn, perturbation)
      z$replicate <- r
      z$seed <- seed
      all_rows[[rr]] <- z
      rr <- rr + 1L
    }
  }
}
rep_df <- do.call(rbind, all_rows)

summarise_cell <- function(z) {
  ok <- z[z$success & is.finite(z$sigma_hat), , drop = FALSE]
  if (nrow(ok) == 0L) {
    return(data.frame(
      detectfn = z$detectfn[1],
      perturbation = z$perturbation[1],
      representation = z$representation[1],
      n = nrow(z), fit_success_fraction = 0,
      median_sigma_hat = NA_real_, mean_sigma_hat = NA_real_,
      median_sigma_relative_error = NA_real_,
      mean_sigma_relative_error = NA_real_,
      rmse_sigma = NA_real_, q10_sigma_hat = NA_real_, q90_sigma_hat = NA_real_,
      stringsAsFactors = FALSE
    ))
  }
  data.frame(
    detectfn = z$detectfn[1],
    perturbation = z$perturbation[1],
    representation = z$representation[1],
    n = nrow(z),
    fit_success_fraction = nrow(ok) / nrow(z),
    median_sigma_hat = median(ok$sigma_hat),
    mean_sigma_hat = mean(ok$sigma_hat),
    median_sigma_relative_error = median(ok$sigma_relative_error),
    mean_sigma_relative_error = mean(ok$sigma_relative_error),
    rmse_sigma = sqrt(mean((ok$sigma_hat - sigma_true)^2)),
    q10_sigma_hat = unname(quantile(ok$sigma_hat, 0.10)),
    q90_sigma_hat = unname(quantile(ok$sigma_hat, 0.90)),
    stringsAsFactors = FALSE
  )
}

cell_key <- interaction(
  rep_df$detectfn, rep_df$perturbation, rep_df$representation,
  drop = TRUE, lex.order = TRUE
)
summary_df <- do.call(rbind, lapply(split(rep_df, cell_key), summarise_cell))
row.names(summary_df) <- NULL

all_primary_fit_success_ge_080 <- all(summary_df$fit_success_fraction >= 0.80)
closure_predictions_pass <- (
  all(closure_df$hn_effective_sigma_ratio[closure_df$checks > 1] > 1) &&
  max(closure_df$hhn_max_abs_closure_error) < 1e-12
)

result <- list(
  schema = "neon.scr_temporal_aggregation_sigma_simulation.v1",
  generated_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
  secr_version = as.character(packageVersion("secr")),
  design = list(
    detector = "multi",
    grid = "7x7",
    spacing_m = spacing_m,
    mask_buffer_m = 100,
    mask_spacing_m = 5,
    nights = nights,
    checks_per_night = checks_per_night,
    sigma_true_m = sigma_true,
    onecheck_centre_probability = g0_onecheck,
    hn_g0 = g0_onecheck,
    hhn_lambda0 = lambda0_onecheck,
    density_per_ha = 10,
    perturbations = list(
      NONE = list(move_probability = 0, radial_median_m = 0),
      SAN_JACINTO = list(move_probability = 0.70, radial_median_m = 13.0)
    ),
    replicates_per_detectfn_perturbation = replicates,
    seed = seed0
  ),
  fixed_detector_closure = closure_df,
  end_to_end_summary = summary_df,
  gates = list(
    closure_predictions_pass = closure_predictions_pass,
    all_primary_fit_success_ge_0_80 = all_primary_fit_success_ge_080,
    figure2_replacement_eligible = closure_predictions_pass && all_primary_fit_success_ge_080
  ),
  empirical_sigma_gate_reopened = FALSE,
  claim_boundary = list(
    hhn_closure_applies_to_fixed_detector_repeated_exposure = TRUE,
    hhn_closure_does_not_guarantee_first_last_multidetector_invariance = TRUE,
    postcapture_perturbation_is_sensitivity_not_natural_movement = TRUE
  )
)

dir.create(dirname(out_json), recursive = TRUE, showWarnings = FALSE)
dir.create(dirname(out_csv), recursive = TRUE, showWarnings = FALSE)
write.csv(rep_df, out_csv, row.names = FALSE)
write_json(result, out_json, pretty = TRUE, auto_unbox = TRUE, digits = 10)

cat(toJSON(result$gates, auto_unbox = TRUE, pretty = TRUE), "\n")
cat(toJSON(summary_df, dataframe = "rows", auto_unbox = TRUE, pretty = TRUE, digits = 6), "\n")
