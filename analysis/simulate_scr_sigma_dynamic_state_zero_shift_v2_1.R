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

out_json <- arg_value("--output-json", "results/scr_sigma_dynamic_state_zero_shift_v2_1.json")
out_csv <- arg_value("--output-csv", "results/scr_sigma_dynamic_state_zero_shift_replicates_v2_1.csv")
nrepl <- as.integer(arg_value("--nrepl", "96"))
cores <- as.integer(arg_value("--cores", "4"))
base_seed <- as.integer(arg_value("--seed", "20261005"))

if (!is.finite(nrepl) || nrepl < 2) stop("nrepl must be >=2")
if (!is.finite(cores) || cores < 1) stop("cores must be >=1")

SPACING <- 6.25
SIGMAS <- c(6.25, 12.5, 25.0)
G0 <- 0.15
DENSITY <- 60
BUFFER <- 100
NIGHTS <- 3
CHECKS_PER_NIGHT <- 3

tr <- make.grid(
  nx = 7, ny = 7, spacing = SPACING,
  detector = "multi", ID = "numy", leadingzero = FALSE
)
fitmask <- make.mask(tr, buffer = BUFFER, spacing = 5)
core <- as.data.frame(as.matrix(tr)[, 1:2, drop = FALSE])

records_from_capthist <- function(ch, global_occasion) {
  ids <- as.character(animalID(ch, names = TRUE))
  k <- as.integer(trap(ch, names = FALSE))
  if (!length(ids)) {
    return(data.frame(ID=character(), occasion=integer(), trap=integer()))
  }
  data.frame(
    ID = ids,
    occasion = rep.int(as.integer(global_occasion), length(ids)),
    trap = k,
    stringsAsFactors = FALSE
  )
}

make_ch <- function(records, noccasions) {
  if (!nrow(records)) stop("zero detections")
  make.capthist(
    data.frame(
      session = 1,
      ID = as.character(records$ID),
      occasion = as.integer(records$occasion),
      trap = as.integer(records$trap),
      stringsAsFactors = FALSE
    ),
    traps = tr,
    fmt = "trapID",
    noccasions = noccasions,
    bysession = FALSE
  )
}

collapse_records <- function(check_records, method = c("first", "last")) {
  method <- match.arg(method)
  x <- check_records
  x$night <- ((x$occasion - 1L) %/% CHECKS_PER_NIGHT) + 1L
  groups <- split(x, paste(x$ID, x$night, sep = "||"))
  out <- lapply(groups, function(g) {
    g <- g[order(g$occasion), , drop = FALSE]
    z <- if (method == "first") g[1, , drop = FALSE] else g[nrow(g), , drop = FALSE]
    data.frame(
      ID = z$ID,
      occasion = z$night,
      trap = z$trap,
      stringsAsFactors = FALSE
    )
  })
  do.call(rbind, out)
}

fit_sigma <- function(ch) {
  fit <- tryCatch(
    suppressWarnings(
      secr.fit(
        ch,
        model = list(g0 ~ b, sigma ~ 1),
        CL = TRUE,
        mask = fitmask,
        detectfn = "HN",
        trace = FALSE,
        biasLimit = NA,
        ncores = 1
      )
    ),
    error = function(e) e
  )
  if (inherits(fit, "error")) {
    return(data.frame(
      success=FALSE, sigma_hat=NA_real_, lcl=NA_real_, ucl=NA_real_,
      error=conditionMessage(fit), stringsAsFactors=FALSE
    ))
  }
  pr <- tryCatch(predict(fit, realnames = "sigma"), error = function(e) e)
  if (inherits(pr, "error")) {
    return(data.frame(
      success=FALSE, sigma_hat=NA_real_, lcl=NA_real_, ucl=NA_real_,
      error=conditionMessage(pr), stringsAsFactors=FALSE
    ))
  }
  z <- if ("sigma" %in% rownames(pr)) pr["sigma", , drop=FALSE] else pr[1, , drop=FALSE]
  est <- as.numeric(z$estimate[1])
  lo <- as.numeric(z$lcl[1])
  hi <- as.numeric(z$ucl[1])
  ok <- is.finite(est) && est > 0 && is.finite(lo) && is.finite(hi)
  data.frame(
    success=ok,
    sigma_hat=if (ok) est else NA_real_,
    lcl=if (ok) lo else NA_real_,
    ucl=if (ok) hi else NA_real_,
    error=if (ok) "" else "non-finite prediction",
    stringsAsFactors=FALSE
  )
}

simulate_static_sequential_records <- function(sigma_true, seed) {
  set.seed(seed)
  pop <- sim.popn(
    D = DENSITY,
    core = core,
    buffer = BUFFER,
    model2D = "poisson",
    Ndist = "poisson",
    seed = seed
  )

  all_records <- list()
  oi <- 1L
  for (night in seq_len(NIGHTS)) {
    for (check in seq_len(CHECKS_PER_NIGHT)) {
      occ <- (night - 1L) * CHECKS_PER_NIGHT + check
      ch <- sim.capthist(
        tr,
        popn = pop,
        detectfn = "HN",
        detectpar = list(g0 = G0, sigma = sigma_true),
        noccasions = 1,
        renumber = FALSE,
        seed = seed + night * 1009L + check * 101L
      )
      rec <- records_from_capthist(ch, occ)
      if (nrow(rec)) {
        all_records[[oi]] <- rec
        oi <- oi + 1L
      }
    }
  }
  if (!length(all_records)) stop("replicate yielded zero detections")
  do.call(rbind, all_records)
}

fit_encodings <- function(records, sigma_true, replicate_id) {
  first <- collapse_records(records, "first")
  last <- collapse_records(records, "last")
  datasets <- list(
    CHECK = make_ch(records, NIGHTS * CHECKS_PER_NIGHT),
    FIRST = make_ch(first, NIGHTS),
    LAST = make_ch(last, NIGHTS)
  )
  rows <- lapply(names(datasets), function(method) {
    f <- fit_sigma(datasets[[method]])
    cbind(
      data.frame(
        replicate = replicate_id,
        sigma_true = sigma_true,
        method = method,
        stringsAsFactors = FALSE
      ),
      f
    )
  })
  do.call(rbind, rows)
}

tasks <- expand.grid(
  sigma_true = SIGMAS,
  replicate = seq_len(nrepl),
  KEEP.OUT.ATTRS = FALSE,
  stringsAsFactors = FALSE
)
tasks$seed <- base_seed + seq_len(nrow(tasks)) * 10007L

run_task <- function(i) {
  task <- tasks[i, , drop=FALSE]
  rec <- simulate_static_sequential_records(task$sigma_true, task$seed)
  fit_encodings(rec, task$sigma_true, task$replicate)
}

if (.Platform$OS.type == "unix" && cores > 1) {
  pieces <- parallel::mclapply(
    seq_len(nrow(tasks)),
    run_task,
    mc.cores = cores,
    mc.preschedule = FALSE
  )
} else {
  pieces <- lapply(seq_len(nrow(tasks)), run_task)
}

fits <- do.call(rbind, pieces)
fits$relative_bias <- (fits$sigma_hat - fits$sigma_true) / fits$sigma_true
fits$covered95 <- with(fits, success & lcl <= sigma_true & ucl >= sigma_true)

summarize_group <- function(g) {
  ok <- g[g$success, , drop=FALSE]
  data.frame(
    n = nrow(g),
    n_success = nrow(ok),
    failure_fraction = 1 - nrow(ok) / nrow(g),
    median_sigma_hat = if (nrow(ok)) median(ok$sigma_hat) else NA_real_,
    mean_sigma_hat = if (nrow(ok)) mean(ok$sigma_hat) else NA_real_,
    median_relative_bias = if (nrow(ok)) median(ok$relative_bias) else NA_real_,
    mean_relative_bias = if (nrow(ok)) mean(ok$relative_bias) else NA_real_,
    coverage95 = if (nrow(ok)) mean(ok$covered95) else NA_real_
  )
}

gkey <- interaction(fits$sigma_true, fits$method, drop=TRUE, lex.order=TRUE)
summary_df <- do.call(rbind, lapply(split(fits, gkey), function(g) {
  cbind(
    g[1, c("sigma_true", "method"), drop=FALSE],
    summarize_group(g)
  )
}))
rownames(summary_df) <- NULL

cellkey <- interaction(fits$sigma_true, drop=TRUE, lex.order=TRUE)
paired <- do.call(rbind, lapply(split(fits, cellkey), function(g) {
  ms <- split(g, g$method)
  ids <- Reduce(
    intersect,
    lapply(ms[c("CHECK","FIRST","LAST")], function(z) z$replicate[z$success])
  )
  if (!length(ids)) return(NULL)
  val <- function(m) setNames(ms[[m]]$sigma_hat, ms[[m]]$replicate)[as.character(ids)]
  cc <- val("CHECK")
  ff <- val("FIRST")
  ll <- val("LAST")
  data.frame(
    sigma_true = g$sigma_true[1],
    n_paired = length(ids),
    median_last_first_ratio = median(ll / ff),
    median_check_first_ratio = median(cc / ff),
    median_check_last_ratio = median(cc / ll)
  )
}))
rownames(paired) <- NULL

max_abs_median_bias <- max(abs(summary_df$median_relative_bias), na.rm=TRUE)
max_abs_last_first_deviation <- max(abs(paired$median_last_first_ratio - 1), na.rm=TRUE)

out <- list(
  schema = "neon.scr_sigma_dynamic_state_zero_shift_diagnostic.v2_1",
  generated_at_utc = format(Sys.time(), tz="UTC", usetz=TRUE),
  seed = base_seed,
  nrepl_per_sigma = nrepl,
  secr_version = as.character(packageVersion("secr")),
  design = list(
    trap_grid = "7x7",
    spacing_m = SPACING,
    nights = NIGHTS,
    checks_per_night = CHECKS_PER_NIGHT,
    g0 = G0,
    density_per_ha = DENSITY,
    buffer_m = BUFFER,
    sigma_true_m = SIGMAS,
    shift_multiplier = 0,
    generator = "sequential independent static SCR checks with no state shift",
    fit_model = "CL=TRUE; HN; g0~b; sigma~1"
  ),
  summaries = summary_df,
  paired_contrasts = paired,
  diagnostic_checks = list(
    frozen_bias_threshold = 0.10,
    max_abs_median_relative_bias = max_abs_median_bias,
    zero_shift_gate_passed = max_abs_median_bias < 0.10,
    max_abs_median_last_first_ratio_deviation = max_abs_last_first_deviation,
    nonzero_shift_cells_run = FALSE,
    empirical_real_data_sigma_opened = FALSE
  )
)

dir.create(dirname(out_json), recursive=TRUE, showWarnings=FALSE)
dir.create(dirname(out_csv), recursive=TRUE, showWarnings=FALSE)
write_json(out, out_json, pretty=TRUE, auto_unbox=TRUE, na="null")
write.csv(fits, out_csv, row.names=FALSE)

cat(toJSON(out, pretty=TRUE, auto_unbox=TRUE, na="null"))
cat("\n")
