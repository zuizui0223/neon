#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(secr)
  library(jsonlite)
})

arg_value <- function(flag, default = NULL) {
  args <- commandArgs(trailingOnly = TRUE)
  i <- match(flag, args)
  if (is.na(i)) return(default)
  if (i == length(args)) stop(paste("missing value for", flag))
  args[[i + 1]]
}

source_path <- arg_value("--source")
out_json <- arg_value("--output-json", "results/pema_stationary_scr_displacement_null_v1.json")
out_csv <- arg_value("--output-csv", "results/pema_stationary_scr_displacement_null_cells_v1.csv")
target_repeat_pool <- as.integer(arg_value("--target-repeat-pool", "2500"))
nboot <- as.integer(arg_value("--nboot", "2000"))
cores <- as.integer(arg_value("--cores", "4"))
base_seed <- as.integer(arg_value("--seed", "20261006"))

if (is.null(source_path) || !file.exists(source_path)) stop("--source must exist")
if (target_repeat_pool < 1000) stop("target repeat pool must be >=1000")
if (nboot < 500) stop("nboot must be >=500")
if (cores < 1) stop("cores must be >=1")

SPACING <- 6.25
BUFFER <- 100
DENSITY <- 60
CHECKS <- 3
SIGMAS <- c(7.7806, 8.5625, 8.8515, 9.7559)
G0S <- c(0.03, 0.06, 0.10, 0.15, 0.25)
OBS_REPEAT_N <- 485L
OBS_CAPTURED_N <- 1219L

clean <- function(x) trimws(ifelse(is.na(x), "", as.character(x)))

parse_nocturnal_time <- function(x) {
  x <- clean(x)
  m <- regexec("^(\\d{1,2}):(\\d{2})$", x)
  p <- regmatches(x, m)
  out <- rep(NA_real_, length(x))
  for (i in seq_along(p)) {
    if (length(p[[i]]) != 3) next
    h <- as.integer(p[[i]][2])
    minute <- as.integer(p[[i]][3])
    if (is.na(h) || is.na(minute) || minute >= 60) next
    if (h >= 7 && h <= 11) h <- h + 12
    else if (h == 12) h <- 24
    else if (h >= 0 && h <= 6) h <- h + 24
    else next
    out[i] <- h + minute / 60
  }
  out
}

flag_xy <- function(flag) {
  flag <- toupper(clean(flag))
  row <- match(substr(flag, 1, 1), LETTERS[1:7]) - 1
  col <- suppressWarnings(as.integer(substr(flag, 2, nchar(flag)))) - 1
  cbind(x = col * SPACING, y = row * SPACING)
}

metric_summary <- function(dx, dy) {
  d <- sqrt(dx^2 + dy^2)
  list(
    n = length(d),
    changed_fraction = mean(d >= SPACING - 1e-10),
    vector_rms_m = sqrt(mean(d^2)),
    axis_rms_m = sqrt(mean(d^2) / 2),
    median_distance_m = as.numeric(median(d)),
    q90_distance_m = as.numeric(quantile(d, 0.90, names = FALSE, type = 7)),
    mean_dx_m = mean(dx),
    mean_dy_m = mean(dy),
    mean_vector_magnitude_m = sqrt(mean(dx)^2 + mean(dy)^2)
  )
}

build_empirical <- function(path) {
  dat <- read.csv(path, stringsAsFactors = FALSE, check.names = FALSE)
  required <- c("species", "grid", "unique_ID", "date", "flag", "time")
  if (!all(required %in% names(dat))) stop("source file missing required columns")

  dat$.row <- seq_len(nrow(dat))
  dat$species <- clean(dat$species)
  dat$grid <- clean(dat$grid)
  dat$unique_ID <- clean(dat$unique_ID)
  dat$date <- clean(dat$date)
  dat$flag <- toupper(clean(dat$flag))
  dat$.time <- parse_nocturnal_time(dat$time)

  keep <- dat$species == "PEMA" &
    nzchar(dat$grid) & nzchar(dat$unique_ID) & nzchar(dat$date) &
    grepl("^[A-G][1-7]$", dat$flag) & is.finite(dat$.time)
  dat <- dat[keep, , drop = FALSE]
  dat$.key <- paste(dat$grid, dat$unique_ID, dat$date, sep = "||")
  groups <- split(dat, dat$.key)

  rows <- lapply(groups, function(g) {
    g <- g[order(g$.time, g$.row), , drop = FALSE]
    xy1 <- flag_xy(g$flag[1])
    xy2 <- flag_xy(g$flag[nrow(g)])
    data.frame(
      detections = nrow(g),
      dx = xy2[1, "x"] - xy1[1, "x"],
      dy = xy2[1, "y"] - xy1[1, "y"],
      stringsAsFactors = FALSE
    )
  })
  nights <- do.call(rbind, rows)
  repeat <- nights[nights$detections >= 2, , drop = FALSE]

  if (nrow(nights) != OBS_CAPTURED_N) {
    stop("PEMA valid captured-night count mismatch: ", nrow(nights), " != ", OBS_CAPTURED_N)
  }
  if (nrow(repeat) != OBS_REPEAT_N) {
    stop("PEMA repeat-night count mismatch: ", nrow(repeat), " != ", OBS_REPEAT_N)
  }

  list(
    captured_nights = nrow(nights),
    repeat_nights = nrow(repeat),
    repeat_fraction = nrow(repeat) / nrow(nights),
    metrics = metric_summary(repeat$dx, repeat$dy),
    rows = repeat
  )
}

empirical <- build_empirical(source_path)

tr <- make.grid(
  nx = 7, ny = 7, spacing = SPACING,
  detector = "multi", ID = "numy", leadingzero = FALSE
)
trxy <- as.matrix(tr)[, 1:2, drop = FALSE]
colnames(trxy) <- c("x", "y")
core <- as.data.frame(trxy)

records_from_one_check <- function(ch, check_index) {
  ids <- as.character(animalID(ch, names = TRUE))
  k <- as.integer(trap(ch, names = FALSE))
  if (!length(ids)) {
    return(data.frame(ID = character(), check = integer(), trap = integer()))
  }
  data.frame(
    ID = ids,
    check = rep.int(as.integer(check_index), length(ids)),
    trap = k,
    stringsAsFactors = FALSE
  )
}

simulate_one_night <- function(sigma, g0, seed) {
  pop <- sim.popn(
    D = DENSITY,
    core = core,
    buffer = BUFFER,
    model2D = "poisson",
    Ndist = "poisson",
    seed = seed
  )

  recs <- list()
  oi <- 1L
  for (check in seq_len(CHECKS)) {
    ch <- sim.capthist(
      tr,
      popn = pop,
      detectfn = "HN",
      detectpar = list(g0 = g0, sigma = sigma),
      noccasions = 1,
      renumber = FALSE,
      seed = seed + check * 1009L
    )
    z <- records_from_one_check(ch, check)
    if (nrow(z)) {
      recs[[oi]] <- z
      oi <- oi + 1L
    }
  }

  if (!length(recs)) {
    return(list(
      captured_nights = 0L,
      repeat_rows = data.frame(dx = numeric(), dy = numeric())
    ))
  }

  x <- do.call(rbind, recs)
  groups <- split(x, x$ID)
  out <- lapply(groups, function(g) {
    g <- g[order(g$check), , drop = FALSE]
    if (nrow(g) < 2) return(NULL)
    p1 <- trxy[g$trap[1], ]
    p2 <- trxy[g$trap[nrow(g)], ]
    data.frame(
      dx = p2[1, "x"] - p1[1, "x"],
      dy = p2[1, "y"] - p1[1, "y"],
      stringsAsFactors = FALSE
    )
  })
  out <- Filter(Negate(is.null), out)
  repeat_rows <- if (length(out)) do.call(rbind, out) else data.frame(dx = numeric(), dy = numeric())

  list(
    captured_nights = length(groups),
    repeat_rows = repeat_rows
  )
}

bootstrap_metrics <- function(pool, nboot, sample_n, seed) {
  set.seed(seed)
  metrics <- c(
    "changed_fraction", "vector_rms_m", "axis_rms_m",
    "median_distance_m", "q90_distance_m", "mean_vector_magnitude_m"
  )
  mat <- matrix(NA_real_, nrow = nboot, ncol = length(metrics))
  colnames(mat) <- metrics

  for (b in seq_len(nboot)) {
    ii <- sample.int(nrow(pool), sample_n, replace = TRUE)
    s <- metric_summary(pool$dx[ii], pool$dy[ii])
    mat[b, ] <- unlist(s[metrics], use.names = FALSE)
  }
  mat
}

summarize_boot <- function(mat, observed_metrics) {
  out <- list()
  for (metric in colnames(mat)) {
    vals <- mat[, metric]
    obs <- as.numeric(observed_metrics[[metric]])
    qs <- as.numeric(quantile(vals, c(0.025, 0.5, 0.975), names = FALSE, type = 7))
    out[[metric]] <- list(
      observed = obs,
      null_q025 = qs[1],
      null_median = qs[2],
      null_q975 = qs[3],
      tail_ge_observed = mean(vals >= obs),
      tail_le_observed = mean(vals <= obs),
      observed_inside_null95 = obs >= qs[1] && obs <= qs[3]
    )
  }
  out
}

run_cell <- function(cell_index, sigma, g0) {
  seed0 <- base_seed + cell_index * 1000003L
  repeat_parts <- list()
  captured_total <- 0L
  repeat_total <- 0L
  night <- 0L

  while (repeat_total < target_repeat_pool) {
    night <- night + 1L
    if (night > 10000L) stop("failed to accumulate repeat pool")
    z <- simulate_one_night(
      sigma = sigma,
      g0 = g0,
      seed = seed0 + night * 7919L
    )
    captured_total <- captured_total + z$captured_nights
    if (nrow(z$repeat_rows)) {
      repeat_parts[[length(repeat_parts) + 1L]] <- z$repeat_rows
      repeat_total <- repeat_total + nrow(z$repeat_rows)
    }
  }

  pool <- do.call(rbind, repeat_parts)
  boot <- bootstrap_metrics(
    pool = pool,
    nboot = nboot,
    sample_n = OBS_REPEAT_N,
    seed = seed0 + 900000001L
  )

  list(
    sigma_m = sigma,
    g0 = g0,
    nights_simulated = night,
    captured_nights = captured_total,
    repeat_nights = nrow(pool),
    repeat_fraction = nrow(pool) / captured_total,
    repeat_fraction_abs_diff_from_empirical = abs(nrow(pool) / captured_total - empirical$repeat_fraction),
    pooled_repeat_metrics = metric_summary(pool$dx, pool$dy),
    bootstrap_reference = summarize_boot(boot, empirical$metrics)
  )
}

grid <- expand.grid(
  sigma_m = SIGMAS,
  g0 = G0S,
  KEEP.OUT.ATTRS = FALSE,
  stringsAsFactors = FALSE
)

runner <- function(i) {
  run_cell(
    cell_index = i,
    sigma = grid$sigma_m[i],
    g0 = grid$g0[i]
  )
}

if (.Platform$OS.type == "unix" && cores > 1L) {
  cells <- parallel::mclapply(
    seq_len(nrow(grid)),
    runner,
    mc.cores = cores,
    mc.preschedule = FALSE
  )
} else {
  cells <- lapply(seq_len(nrow(grid)), runner)
}

repeat_diff <- vapply(cells, function(x) x$repeat_fraction_abs_diff_from_empirical, numeric(1))
closest_order <- order(repeat_diff)
closest <- cells[closest_order[seq_len(min(5L, length(cells)))]]

primary_metrics <- c("changed_fraction", "vector_rms_m", "axis_rms_m", "median_distance_m", "q90_distance_m")
inside_matrix <- sapply(cells, function(cell) {
  vapply(primary_metrics, function(m) cell$bootstrap_reference[[m]]$observed_inside_null95, logical(1))
})
if (is.null(dim(inside_matrix))) {
  inside_matrix <- matrix(inside_matrix, nrow = length(primary_metrics))
}
rownames(inside_matrix) <- primary_metrics

out <- list(
  schema = "neon.pema_stationary_scr_displacement_null.v1",
  date = "2026-10-06",
  status = "post_result_stationary_reference_diagnostic",
  source_sha256 = "ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301",
  empirical = list(
    species = "PEMA",
    scientific_name = "Peromyscus maniculatus",
    captured_nights = empirical$captured_nights,
    repeat_nights = empirical$repeat_nights,
    repeat_fraction = empirical$repeat_fraction,
    metrics = empirical$metrics
  ),
  design = list(
    detector_grid = "7x7 multi-catch",
    spacing_m = SPACING,
    checks_per_night = CHECKS,
    activity_centre = "fixed within night",
    check_process = "independent static SCR checks",
    detectfn = "HN",
    density_per_ha = DENSITY,
    buffer_m = BUFFER,
    sigma_m = SIGMAS,
    g0 = G0S,
    target_repeat_pool_per_cell = target_repeat_pool,
    bootstrap_samples = nboot,
    bootstrap_sample_size = OBS_REPEAT_N,
    state_shift = FALSE
  ),
  cells = cells,
  closest_cells_by_repeat_fraction = closest,
  robustness = list(
    primary_metrics = primary_metrics,
    number_of_cells = length(cells),
    cells_with_observed_inside_null95 = setNames(
      as.list(rowSums(inside_matrix)),
      primary_metrics
    ),
    note = "g0 cells are sensitivity references; no cell is selected using displacement outcomes"
  ),
  claim_boundary = list(
    allowed = "assess whether observed PEMA within-night displacement scale exceeds a static time-reversal-symmetric SCR reference over the empirical sigma bracket",
    not_allowed = c(
      "infer handling causation",
      "replace the stopped two-species SCR gate",
      "choose FIRST or LAST as biologically correct",
      "treat the ordered-transition stress test as an empirical bias estimate",
      "claim full temporal exchangeability"
    )
  ),
  package_versions = list(
    R = as.character(getRversion()),
    secr = as.character(packageVersion("secr")),
    jsonlite = as.character(packageVersion("jsonlite"))
  )
)

cell_rows <- do.call(rbind, lapply(cells, function(cell) {
  base <- data.frame(
    sigma_m = cell$sigma_m,
    g0 = cell$g0,
    nights_simulated = cell$nights_simulated,
    captured_nights = cell$captured_nights,
    repeat_nights = cell$repeat_nights,
    repeat_fraction = cell$repeat_fraction,
    repeat_fraction_abs_diff_from_empirical = cell$repeat_fraction_abs_diff_from_empirical
  )
  for (metric in names(cell$bootstrap_reference)) {
    z <- cell$bootstrap_reference[[metric]]
    base[[paste0(metric, "_observed")]] <- z$observed
    base[[paste0(metric, "_null_q025")]] <- z$null_q025
    base[[paste0(metric, "_null_median")]] <- z$null_median
    base[[paste0(metric, "_null_q975")]] <- z$null_q975
    base[[paste0(metric, "_tail_ge")]] <- z$tail_ge_observed
    base[[paste0(metric, "_tail_le")]] <- z$tail_le_observed
    base[[paste0(metric, "_inside95")]] <- z$observed_inside_null95
  }
  base
}))

dir.create(dirname(out_json), recursive = TRUE, showWarnings = FALSE)
dir.create(dirname(out_csv), recursive = TRUE, showWarnings = FALSE)
write_json(out, out_json, pretty = TRUE, auto_unbox = TRUE, na = "null")
write.csv(cell_rows, out_csv, row.names = FALSE)

cat(toJSON(list(
  empirical = out$empirical,
  closest_cells_by_repeat_fraction = closest,
  robustness = out$robustness
), pretty = TRUE, auto_unbox = TRUE, na = "null"))
cat("\n")
