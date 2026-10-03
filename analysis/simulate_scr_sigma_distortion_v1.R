#!/usr/bin/env Rscript

# San Jacinto temporal positional aliasing:
# generative SCR simulation of downstream sigma distortion.
#
# AI assistance disclosure: drafted/refactored with OpenAI ChatGPT (GPT-5.6 Sol,
# October 2026); scientific interpretation and repository use remain under
# author responsibility.

suppressPackageStartupMessages({
  library(secr)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)

arg_value <- function(flag, default = NULL) {
  hit <- which(args == flag)
  if (length(hit) == 0) return(default)
  if (hit[length(hit)] == length(args)) stop(flag, " requires a value")
  args[hit[length(hit)] + 1]
}

mode <- arg_value("--mode", "smoke")
output_json <- arg_value("--output-json", "results/scr_sigma_distortion_simulation_v1.json")
output_csv <- arg_value("--output-csv", "results/scr_sigma_distortion_replicates_v1.csv")
seed0 <- as.integer(arg_value("--seed", "20261003"))

if (!mode %in% c("smoke", "full")) stop("mode must be smoke or full")

SPACING <- 6.25
NX <- 7
NY <- 7
NIGHTS <- 5
CHECKS <- 4
N_ANIMALS <- 120
MASK_BUFFER <- 100

PROFILES <- data.frame(
  profile = c("PEMA_like", "PEER_like"),
  g0 = c(0.09, 0.08),
  stringsAsFactors = FALSE
)

SIGMAS <- c(5.0, 10.0, 15.0)
RHOS <- c(0.0, 0.5, 1.0)
JITTERS <- c(0.0, 1.5, 3.125, 6.25, 12.5)

if (mode == "smoke") {
  # Debug only: one empirical-like profile, one generating sigma, and three
  # mechanistic cells. This subset was fixed in code before simulated sigma
  # effects were inspected.
  PROFILES <- PROFILES[PROFILES$profile == "PEMA_like", , drop = FALSE]
  SIGMAS <- c(5.0)
  RHOS <- c(0.0, 1.0)
  JITTERS <- c(0.0, 1.5, 12.5)
  N_REP <- 3L
} else {
  N_REP <- 100L
}

setNumThreads(2)

trap_index <- function(traps_obj, trap_id) {
  ids <- rownames(traps_obj)
  z <- match(as.character(trap_id), ids)
  if (anyNA(z)) {
    z2 <- suppressWarnings(as.integer(as.character(trap_id)))
    use <- is.na(z) & !is.na(z2) & z2 >= 1 & z2 <= nrow(traps_obj)
    z[use] <- z2[use]
  }
  if (anyNA(z)) stop("could not map TrapID to detector index")
  z
}

make_design <- function() {
  make.grid(
    nx = NX,
    ny = NY,
    spacing = SPACING,
    detector = "multi",
    ID = "numeric",
    centre = TRUE
  )
}

new_population <- function(traps_obj, seed) {
  p <- sim.popn(
    D = 1,
    core = traps_obj,
    buffer = MASK_BUFFER,
    Ndist = "specified",
    Nbuffer = N_ANIMALS,
    covariates = NULL,
    seed = seed
  )
  rownames(p) <- sprintf("A%03d", seq_len(nrow(p)))
  p
}

simulate_raw <- function(traps_obj, sigma_true, g0, rho, jitter_sd, seed) {
  set.seed(seed)
  base <- new_population(traps_obj, seed = seed + 17L)
  raw_parts <- list()
  part_i <- 0L

  for (night in seq_len(NIGHTS)) {
    current <- base
    handled <- setNames(rep(FALSE, nrow(base)), rownames(base))

    for (check in seq_len(CHECKS)) {
      one <- sim.capthist(
        traps = traps_obj,
        popn = current,
        detectfn = "HN",
        detectpar = list(g0 = g0, sigma = sigma_true),
        noccasions = 1,
        renumber = FALSE
      )

      if (nrow(one) == 0) next

      d <- as.data.frame(one, fmt = "trapID")
      if (nrow(d) == 0) next
      names(d)[1:4] <- c("Session", "ID", "Occasion", "TrapID")
      d$ID <- as.character(d$ID)
      d$TrapID <- as.character(d$TrapID)
      d$night <- night
      d$check <- check
      d$Occasion <- (night - 1L) * CHECKS + check

      part_i <- part_i + 1L
      raw_parts[[part_i]] <- d[, c("Session", "ID", "Occasion", "TrapID", "night", "check")]

      ids <- unique(d$ID)
      newly <- ids[!handled[ids]]
      if (length(newly) == 0) next

      first_rows <- d[match(newly, d$ID), , drop = FALSE]
      tidx <- trap_index(traps_obj, first_rows$TrapID)
      pidx <- match(newly, rownames(base))
      if (anyNA(pidx)) stop("captured ID not found in simulated population")

      current[pidx, "x"] <-
        (1 - rho) * base[pidx, "x"] +
        rho * traps_obj[tidx, "x"] +
        rnorm(length(pidx), mean = 0, sd = jitter_sd)
      current[pidx, "y"] <-
        (1 - rho) * base[pidx, "y"] +
        rho * traps_obj[tidx, "y"] +
        rnorm(length(pidx), mean = 0, sd = jitter_sd)

      handled[newly] <- TRUE
    }
  }

  if (length(raw_parts) == 0) {
    return(data.frame(
      Session = numeric(0), ID = character(0), Occasion = integer(0),
      TrapID = character(0), night = integer(0), check = integer(0)
    ))
  }

  raw <- do.call(rbind, raw_parts)
  raw <- raw[order(raw$ID, raw$night, raw$check), , drop = FALSE]
  rownames(raw) <- NULL
  raw
}

collapse_nights <- function(raw, which = c("FIRST", "LAST")) {
  which <- match.arg(which)
  if (nrow(raw) == 0) return(raw)
  key <- paste(raw$ID, raw$night, sep = "::")
  keep <- if (which == "FIRST") !duplicated(key) else !duplicated(key, fromLast = TRUE)
  out <- raw[keep, , drop = FALSE]
  out$Occasion <- out$night
  out <- out[order(out$ID, out$Occasion), , drop = FALSE]
  rownames(out) <- NULL
  out
}

build_capthist <- function(raw, traps_obj, nocc) {
  if (nrow(raw) == 0) stop("no detections")
  capt <- data.frame(
    Session = 1,
    AnimalID = as.character(raw$ID),
    Occasion = as.integer(raw$Occasion),
    TrapID = trap_index(traps_obj, raw$TrapID)
  )
  make.capthist(
    captures = capt,
    traps = traps_obj,
    fmt = "trapID",
    noccasions = nocc,
    bysession = TRUE
  )
}

fit_sigma <- function(ch, sigma_true) {
  tryCatch({
    fit <- secr.fit(
      capthist = ch,
      model = list(g0 = ~ b, sigma = ~ 1),
      CL = TRUE,
      detectfn = "HN",
      buffer = MASK_BUFFER,
      trace = FALSE
    )
    pred <- predict(fit)
    if (!("sigma" %in% rownames(pred))) stop("sigma absent from predict()")
    est <- as.numeric(pred["sigma", "estimate"])
    lcl <- as.numeric(pred["sigma", "lcl"])
    ucl <- as.numeric(pred["sigma", "ucl"])
    data.frame(
      fit_ok = TRUE,
      sigma_hat = est,
      sigma_lcl = lcl,
      sigma_ucl = ucl,
      rel_error = (est - sigma_true) / sigma_true,
      covers_true = lcl <= sigma_true && sigma_true <= ucl,
      stringsAsFactors = FALSE
    )
  }, error = function(e) {
    data.frame(
      fit_ok = FALSE,
      sigma_hat = NA_real_,
      sigma_lcl = NA_real_,
      sigma_ucl = NA_real_,
      rel_error = NA_real_,
      covers_true = NA,
      stringsAsFactors = FALSE
    )
  })
}

observation_metrics <- function(raw, traps_obj) {
  if (nrow(raw) == 0) {
    return(list(
      observed_nights = 0L,
      repeat_nights = 0L,
      repeat_fraction = NA_real_,
      one_spacing_shift_fraction = NA_real_,
      median_first_last_span_m = NA_real_
    ))
  }

  groups <- split(raw, paste(raw$ID, raw$night, sep = "::"))
  observed_nights <- length(groups)
  spans <- c()

  for (g in groups) {
    if (nrow(g) < 2) next
    g <- g[order(g$check), , drop = FALSE]
    ii <- trap_index(traps_obj, c(g$TrapID[1], g$TrapID[nrow(g)]))
    dx <- traps_obj[ii[1], "x"] - traps_obj[ii[2], "x"]
    dy <- traps_obj[ii[1], "y"] - traps_obj[ii[2], "y"]
    spans <- c(spans, sqrt(dx * dx + dy * dy))
  }

  repeat_nights <- length(spans)
  list(
    observed_nights = observed_nights,
    repeat_nights = repeat_nights,
    repeat_fraction = if (observed_nights > 0) repeat_nights / observed_nights else NA_real_,
    one_spacing_shift_fraction = if (repeat_nights > 0) mean(spans >= SPACING - 1e-12) else NA_real_,
    median_first_last_span_m = if (repeat_nights > 0) median(spans) else NA_real_
  )
}

one_replicate <- function(profile, g0, sigma_true, rho, jitter_sd, rep_id, seed) {
  traps_obj <- make_design()
  raw <- simulate_raw(
    traps_obj = traps_obj,
    sigma_true = sigma_true,
    g0 = g0,
    rho = rho,
    jitter_sd = jitter_sd,
    seed = seed
  )

  om <- observation_metrics(raw, traps_obj)
  first_raw <- collapse_nights(raw, "FIRST")
  last_raw <- collapse_nights(raw, "LAST")

  reps <- list(
    FIRST = list(raw = first_raw, nocc = NIGHTS),
    LAST = list(raw = last_raw, nocc = NIGHTS),
    CHECK = list(raw = raw, nocc = NIGHTS * CHECKS)
  )

  out <- list()
  for (nm in names(reps)) {
    rr <- reps[[nm]]
    fitrow <- tryCatch({
      ch <- build_capthist(rr$raw, traps_obj, rr$nocc)
      fit_sigma(ch, sigma_true)
    }, error = function(e) {
      data.frame(
        fit_ok = FALSE,
        sigma_hat = NA_real_,
        sigma_lcl = NA_real_,
        sigma_ucl = NA_real_,
        rel_error = NA_real_,
        covers_true = NA,
        stringsAsFactors = FALSE
      )
    })

    out[[nm]] <- cbind(
      data.frame(
        profile = profile,
        g0 = g0,
        sigma_true_m = sigma_true,
        rho_release_location = rho,
        release_jitter_sd_m = jitter_sd,
        replicate = rep_id,
        seed = seed,
        representation = nm,
        detections = nrow(rr$raw),
        observed_nights = om$observed_nights,
        repeat_nights = om$repeat_nights,
        repeat_fraction = om$repeat_fraction,
        one_spacing_shift_fraction = om$one_spacing_shift_fraction,
        median_first_last_span_m = om$median_first_last_span_m,
        stringsAsFactors = FALSE
      ),
      fitrow
    )
  }

  do.call(rbind, out)
}

quant <- function(x, p) {
  x <- x[is.finite(x)]
  if (!length(x)) return(NA_real_)
  as.numeric(quantile(x, probs = p, names = FALSE, type = 7))
}

summarise_results <- function(rows) {
  keycols <- c(
    "profile", "g0", "sigma_true_m", "rho_release_location",
    "release_jitter_sd_m"
  )
  cellkey <- interaction(rows[, keycols], drop = TRUE, lex.order = TRUE)
  cells <- split(rows, cellkey)

  summary_rows <- lapply(cells, function(g) {
    first <- g[g$representation == "FIRST", , drop = FALSE]
    last <- g[g$representation == "LAST", , drop = FALSE]
    check <- g[g$representation == "CHECK", , drop = FALSE]

    merge_one <- function(a, b, suffix_a, suffix_b) {
      merge(
        a[, c("replicate", "sigma_hat", "fit_ok")],
        b[, c("replicate", "sigma_hat", "fit_ok")],
        by = "replicate",
        suffixes = c(suffix_a, suffix_b)
      )
    }

    fl <- merge_one(first, last, "_FIRST", "_LAST")
    fc <- merge_one(first, check, "_FIRST", "_CHECK")

    fl_ratio <- with(
      fl,
      ifelse(fit_ok_FIRST & fit_ok_LAST, sigma_hat_LAST / sigma_hat_FIRST, NA_real_)
    )
    fc_ratio <- with(
      fc,
      ifelse(fit_ok_FIRST & fit_ok_CHECK, sigma_hat_CHECK / sigma_hat_FIRST, NA_real_)
    )

    one <- g[1, keycols, drop = FALSE]
    data.frame(
      one,
      n_replicates = length(unique(g$replicate)),
      repeat_fraction_mean = mean(g$repeat_fraction[g$representation == "FIRST"], na.rm = TRUE),
      shift_fraction_mean = mean(g$one_spacing_shift_fraction[g$representation == "FIRST"], na.rm = TRUE),
      median_span_m_median = median(g$median_first_last_span_m[g$representation == "FIRST"], na.rm = TRUE),
      first_fit_rate = mean(first$fit_ok),
      last_fit_rate = mean(last$fit_ok),
      check_fit_rate = mean(check$fit_ok),
      first_rel_error_median = median(first$rel_error, na.rm = TRUE),
      last_rel_error_median = median(last$rel_error, na.rm = TRUE),
      check_rel_error_median = median(check$rel_error, na.rm = TRUE),
      first_coverage = mean(first$covers_true, na.rm = TRUE),
      last_coverage = mean(last$covers_true, na.rm = TRUE),
      check_coverage = mean(check$covers_true, na.rm = TRUE),
      last_first_ratio_median = median(fl_ratio, na.rm = TRUE),
      last_first_ratio_q025 = quant(fl_ratio, 0.025),
      last_first_ratio_q975 = quant(fl_ratio, 0.975),
      check_first_ratio_median = median(fc_ratio, na.rm = TRUE),
      check_first_ratio_q025 = quant(fc_ratio, 0.025),
      check_first_ratio_q975 = quant(fc_ratio, 0.975),
      material_first_last = abs(median(fl_ratio, na.rm = TRUE) - 1) >= 0.10,
      stringsAsFactors = FALSE
    )
  })

  out <- do.call(rbind, summary_rows)
  rownames(out) <- NULL
  out[order(
    out$profile, out$sigma_true_m, out$rho_release_location,
    out$release_jitter_sd_m
  ), , drop = FALSE]
}

grid <- expand.grid(
  profile = PROFILES$profile,
  sigma_true_m = SIGMAS,
  rho_release_location = RHOS,
  release_jitter_sd_m = JITTERS,
  stringsAsFactors = FALSE
)

# Avoid duplicate zero-control cells that differ only in rho when there is no
# post-capture displacement to the release location. rho still matters at
# jitter=0, so all frozen cells are retained.
rows <- list()
ri <- 0L
cell_index <- 0L

for (gi in seq_len(nrow(grid))) {
  cell_index <- cell_index + 1L
  profile <- grid$profile[gi]
  g0 <- PROFILES$g0[match(profile, PROFILES$profile)]
  sigma_true <- grid$sigma_true_m[gi]
  rho <- grid$rho_release_location[gi]
  jitter <- grid$release_jitter_sd_m[gi]

  for (rep_id in seq_len(N_REP)) {
    ri <- ri + 1L
    seed <- seed0 + cell_index * 100000L + rep_id
    message(
      "cell ", cell_index, "/", nrow(grid),
      " rep ", rep_id, "/", N_REP,
      " profile=", profile,
      " sigma=", sigma_true,
      " rho=", rho,
      " jitter=", jitter
    )
    rows[[ri]] <- one_replicate(
      profile = profile,
      g0 = g0,
      sigma_true = sigma_true,
      rho = rho,
      jitter_sd = jitter,
      rep_id = rep_id,
      seed = seed
    )
  }
}

replicates <- do.call(rbind, rows)
summary_table <- summarise_results(replicates)

# Mandatory implementation gate: in the exact static-control cell, FIRST and
# LAST must not show a large systematic divergence. For smoke runs the Monte
# Carlo sample is intentionally tiny, so this is recorded rather than used to
# abort. The full run applies the pre-frozen 10% boundary.
control <- summary_table[
  summary_table$rho_release_location == 0 &
  summary_table$release_jitter_sd_m == 0,
  , drop = FALSE
]

control_pass <- if (nrow(control) == 0) FALSE else all(
  abs(control$last_first_ratio_median - 1) < 0.10,
  na.rm = TRUE
)

if (mode == "full" && !control_pass) {
  stop("negative-control gate failed: systematic FIRST/LAST distortion")
}

dir.create(dirname(output_csv), recursive = TRUE, showWarnings = FALSE)
write.csv(replicates, output_csv, row.names = FALSE)

result <- list(
  schema = "neon.san_jacinto_scr_sigma_distortion_simulation.result.v1",
  mode = mode,
  seed = seed0,
  package_versions = list(
    R = paste(R.version$major, R.version$minor, sep = "."),
    secr = as.character(packageVersion("secr"))
  ),
  design = list(
    trap_spacing_m = SPACING,
    nx = NX,
    ny = NY,
    nights = NIGHTS,
    checks_per_night = CHECKS,
    n_animals = N_ANIMALS,
    mask_buffer_m = MASK_BUFFER,
    replicates_per_cell = N_REP
  ),
  negative_control_pass = control_pass,
  summary = summary_table,
  simulated_sigma_effects_inspected = TRUE,
  empirical_sigma_effects_opened = FALSE,
  real_data_sigma_gate_remains_stopped = TRUE
)

dir.create(dirname(output_json), recursive = TRUE, showWarnings = FALSE)
write_json(result, output_json, pretty = TRUE, auto_unbox = TRUE, digits = 10)

print(summary_table)
