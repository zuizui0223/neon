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
out_json <- arg_value("--output-json", "results/scr_sigma_consequence_simulation_v1.json")
out_csv <- arg_value("--output-csv", "results/scr_sigma_consequence_replicates_v1.csv")
nrepl <- as.integer(arg_value("--nrepl", "40"))
cores <- as.integer(arg_value("--cores", "2"))
base_seed <- as.integer(arg_value("--seed", "20261001"))

if (is.null(source_path) || !file.exists(source_path)) {
  stop("--source must point to the frozen San Jacinto capture CSV")
}
if (!is.finite(nrepl) || nrepl < 2) stop("nrepl must be >=2")
if (!is.finite(cores) || cores < 1) stop("cores must be >=1")

SPACING <- 6.25
SIGMAS <- c(6.25, 12.5, 25.0)
G0 <- 0.15
ORIGINAL_DENSITY <- 20
DENSITY <- 60
BUFFER <- 100
NIGHTS <- 3
CHECKS_PER_NIGHT <- 3
SPECIES <- c("PEMA", "PEER")

parse_nocturnal_time <- function(x) {
  x <- trimws(as.character(x))
  out <- rep(NA_real_, length(x))
  ok <- grepl("^\\d{1,2}:\\d{2}$", x)
  if (!any(ok)) return(out)
  parts <- strsplit(x[ok], ":", fixed = TRUE)
  h <- as.integer(vapply(parts, `[[`, character(1), 1))
  m <- as.integer(vapply(parts, `[[`, character(1), 2))
  good <- !is.na(h) & !is.na(m) & m < 60
  hh <- rep(NA_real_, length(h))
  hh[good & h >= 7 & h <= 11] <- h[good & h >= 7 & h <= 11] + 12
  hh[good & h == 12] <- 24
  hh[good & h >= 0 & h <= 6] <- h[good & h >= 0 & h <= 6] + 24
  vals <- hh + m / 60
  out[which(ok)] <- vals
  out
}

flag_xy <- function(flag) {
  flag <- toupper(trimws(as.character(flag)))
  row <- match(substr(flag, 1, 1), LETTERS[1:7]) - 1
  col <- suppressWarnings(as.integer(substr(flag, 2, nchar(flag)))) - 1
  cbind(x = col * SPACING, y = row * SPACING)
}

build_empirical_kernel <- function(path) {
  dat <- read.csv(path, stringsAsFactors = FALSE, check.names = FALSE)
  required <- c("species", "grid", "unique_ID", "date", "flag", "time")
  if (!all(required %in% names(dat))) {
    stop("source file missing required columns")
  }
  dat$.row <- seq_len(nrow(dat))
  dat$species <- trimws(as.character(dat$species))
  dat$grid <- trimws(as.character(dat$grid))
  dat$unique_ID <- trimws(as.character(dat$unique_ID))
  dat$date <- trimws(as.character(dat$date))
  dat$flag <- toupper(trimws(as.character(dat$flag)))
  dat$.time <- parse_nocturnal_time(dat$time)
  valid_flag <- grepl("^[A-G][1-7]$", dat$flag)
  keep <- dat$species %in% SPECIES &
    nzchar(dat$grid) & nzchar(dat$unique_ID) & nzchar(dat$date) &
    valid_flag & is.finite(dat$.time)
  dat <- dat[keep, , drop = FALSE]
  dat$.key <- paste(dat$species, dat$grid, dat$unique_ID, dat$date, sep = "||")
  groups <- split(dat, dat$.key)

  rows <- lapply(groups, function(g) {
    ord <- order(g$.time, g$.row)
    g <- g[ord, , drop = FALSE]
    first <- g[1, , drop = FALSE]
    last <- g[nrow(g), , drop = FALSE]
    xy1 <- flag_xy(first$flag)
    xy2 <- flag_xy(last$flag)
    data.frame(
      species = first$species,
      n_records = nrow(g),
      first_flag = first$flag,
      last_flag = last$flag,
      dx = xy2[1, "x"] - xy1[1, "x"],
      dy = xy2[1, "y"] - xy1[1, "y"],
      distance = sqrt(
        (xy2[1, "x"] - xy1[1, "x"])^2 +
        (xy2[1, "y"] - xy1[1, "y"])^2
      ),
      stringsAsFactors = FALSE
    )
  })
  nights <- do.call(rbind, rows)
  repeat_nights <- nights[nights$n_records >= 2, , drop = FALSE]
  changed <- repeat_nights[repeat_nights$distance >= SPACING - 1e-10, , drop = FALSE]

  by_species <- lapply(SPECIES, function(sp) {
    nsp <- nights[nights$species == sp, , drop = FALSE]
    rsp <- repeat_nights[repeat_nights$species == sp, , drop = FALSE]
    csp <- changed[changed$species == sp, , drop = FALSE]
    list(
      all_valid_captured_nights = nrow(nsp),
      repeat_capture_nights = nrow(rsp),
      changed_repeat_nights = nrow(csp),
      repeat_fraction = nrow(rsp) / nrow(nsp),
      changed_fraction_given_repeat = nrow(csp) / nrow(rsp),
      changed_median_distance_m = median(csp$distance),
      changed_q90_distance_m = as.numeric(quantile(csp$distance, 0.90, names = FALSE)),
      changed_rms_distance_m = sqrt(mean(csp$distance^2))
    )
  })
  names(by_species) <- SPECIES

  if (by_species$PEMA$all_valid_captured_nights != 1219L ||
      by_species$PEMA$repeat_capture_nights != 485L ||
      by_species$PEMA$changed_repeat_nights != 352L) {
    stop("PEMA calibration counts do not reproduce frozen results")
  }
  if (by_species$PEER$all_valid_captured_nights != 301L ||
      by_species$PEER$repeat_capture_nights != 107L ||
      by_species$PEER$changed_repeat_nights != 74L) {
    stop("PEER calibration counts do not reproduce frozen results")
  }

  repeat_p <- nrow(repeat_nights) / nrow(nights)
  change_p <- nrow(changed) / nrow(repeat_nights)

  list(
    nights = nights,
    repeat_nights = repeat_nights,
    changed = changed,
    vectors = as.matrix(changed[, c("dx", "dy"), drop = FALSE]),
    repeat_probability = repeat_p,
    change_probability_given_repeat = change_p,
    species = by_species,
    pooled = list(
      all_valid_captured_nights = nrow(nights),
      repeat_capture_nights = nrow(repeat_nights),
      changed_repeat_nights = nrow(changed),
      repeat_probability = repeat_p,
      change_probability_given_repeat = change_p,
      changed_median_distance_m = median(changed$distance),
      changed_q90_distance_m = as.numeric(quantile(changed$distance, 0.90, names = FALSE)),
      changed_rms_distance_m = sqrt(mean(changed$distance^2)),
      effective_transition_probability = nrow(changed) / nrow(nights)
    )
  )
}

kernel <- build_empirical_kernel(source_path)

# Continuous dense-detector second-moment benchmark for an isotropic random
# transition vector H. For random transition length R and overall transition
# probability q, Cov(H) contributes q E[R^2] / 2 per spatial axis.
q_transition <- kernel$pooled$effective_transition_probability
r2_transition <- mean(kernel$changed$distance^2)
analytic_benchmark <- lapply(SIGMAS, function(sigma_true) {
  ratio <- sqrt(1 + q_transition * r2_transition / (2 * sigma_true^2))
  list(
    sigma_true_m = sigma_true,
    predicted_sigma_ratio = ratio,
    predicted_relative_inflation = ratio - 1
  )
})

tr <- make.grid(nx = 7, ny = 7, spacing = SPACING, detector = "multi", ID = "numy", leadingzero = FALSE)
trxy <- as.matrix(tr)
if (ncol(trxy) < 2) stop("unexpected trap coordinate object")
trxy <- trxy[, 1:2, drop = FALSE]
colnames(trxy) <- c("x", "y")
coord_key <- function(x, y) sprintf("%.6f,%.6f", x, y)
trap_lookup <- setNames(seq_len(nrow(trxy)), coord_key(trxy[,1], trxy[,2]))
fitmask <- make.mask(tr, buffer = BUFFER, spacing = 5)

records_from_capthist <- function(ch) {
  ids <- as.character(animalID(ch, names = TRUE))
  occ <- as.integer(occasion(ch))
  k <- as.integer(trap(ch, names = FALSE))
  if (!length(ids)) {
    return(data.frame(ID=character(), occasion=integer(), trap=integer()))
  }
  data.frame(
    ID = ids,
    occasion = occ,
    trap = k,
    stringsAsFactors = FALSE
  )
}

make_ch <- function(records, noccasions) {
  if (nrow(records) == 0) stop("cannot make capthist with zero detections")
  captures <- data.frame(
    session = 1,
    ID = as.character(records$ID),
    occasion = as.integer(records$occasion),
    trap = as.integer(records$trap),
    stringsAsFactors = FALSE
  )
  make.capthist(
    captures,
    traps = tr,
    fmt = "trapID",
    noccasions = noccasions,
    bysession = FALSE
  )
}

collapse_records <- function(check_records, method = c("first", "last")) {
  method <- match.arg(method)
  if (nrow(check_records) == 0) return(check_records)
  x <- check_records
  x$night <- ((x$occasion - 1L) %/% CHECKS_PER_NIGHT) + 1L
  key <- paste(x$ID, x$night, sep = "||")
  groups <- split(x, key)
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

jump_destination <- function(origin_trap, vectors, max_tries = 100L) {
  origin <- trxy[origin_trap, ]
  for (i in seq_len(max_tries)) {
    v <- vectors[sample.int(nrow(vectors), 1L), ]
    target <- origin + v
    key <- coord_key(target[1], target[2])
    if (key %in% names(trap_lookup)) {
      return(unname(trap_lookup[[key]]))
    }
  }
  # Deterministic fallback: choose a non-origin trap nearest to a sampled empirical distance.
  target_d <- sqrt(sum(vectors[sample.int(nrow(vectors), 1L), ]^2))
  d <- sqrt((trxy[,1] - origin[1])^2 + (trxy[,2] - origin[2])^2)
  candidates <- which(seq_along(d) != origin_trap)
  candidates[which.min(abs(d[candidates] - target_d))]
}

transition_check_records <- function(base_ch, orientation, seed) {
  if (!orientation %in% c("POST", "PRE")) stop("bad orientation")
  set.seed(seed)
  base <- records_from_capthist(base_ch)
  if (nrow(base) == 0) stop("base simulation yielded zero captures")
  out <- list()
  diagnostics <- list()
  oi <- 1L
  di <- 1L

  for (r in seq_len(nrow(base))) {
    id <- base$ID[r]
    night <- base$occasion[r]
    canonical <- base$trap[r]
    repeated <- runif(1) < kernel$repeat_probability
    changed <- FALSE
    displaced <- canonical

    if (repeated && runif(1) < kernel$change_probability_given_repeat) {
      displaced <- jump_destination(canonical, kernel$vectors)
      changed <- displaced != canonical
    }

    if (!repeated) {
      ck <- sample.int(CHECKS_PER_NIGHT, 1L)
      out[[oi]] <- data.frame(
        ID=id,
        occasion=(night - 1L) * CHECKS_PER_NIGHT + ck,
        trap=canonical,
        stringsAsFactors=FALSE
      )
      oi <- oi + 1L
    } else {
      if (orientation == "POST") {
        first_trap <- canonical
        last_trap <- displaced
      } else {
        first_trap <- displaced
        last_trap <- canonical
      }
      out[[oi]] <- data.frame(
        ID=id,
        occasion=(night - 1L) * CHECKS_PER_NIGHT + 1L,
        trap=first_trap,
        stringsAsFactors=FALSE
      )
      oi <- oi + 1L
      out[[oi]] <- data.frame(
        ID=id,
        occasion=(night - 1L) * CHECKS_PER_NIGHT + 3L,
        trap=last_trap,
        stringsAsFactors=FALSE
      )
      oi <- oi + 1L

      xy1 <- trxy[first_trap,]
      xy2 <- trxy[last_trap,]
      diagnostics[[di]] <- data.frame(
        repeated=TRUE,
        changed=changed,
        distance=sqrt(sum((xy2 - xy1)^2))
      )
      di <- di + 1L
    }
  }

  records <- do.call(rbind, out)
  diag <- if (length(diagnostics)) do.call(rbind, diagnostics) else
    data.frame(repeated=logical(), changed=logical(), distance=numeric())
  list(records=records, diagnostics=diag, base_captured_nights=nrow(base))
}

fit_sigma <- function(ch, sigma_true) {
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
      success=FALSE,
      sigma_hat=NA_real_,
      sigma_se=NA_real_,
      lcl=NA_real_,
      ucl=NA_real_,
      error=conditionMessage(fit),
      stringsAsFactors=FALSE
    ))
  }
  pr <- tryCatch(predict(fit, realnames = "sigma"), error=function(e) e)
  if (inherits(pr, "error")) {
    return(data.frame(
      success=FALSE,
      sigma_hat=NA_real_,
      sigma_se=NA_real_,
      lcl=NA_real_,
      ucl=NA_real_,
      error=conditionMessage(pr),
      stringsAsFactors=FALSE
    ))
  }
  if ("sigma" %in% rownames(pr)) z <- pr["sigma", , drop = FALSE] else z <- pr[1, , drop = FALSE]
  est <- as.numeric(z$estimate[1])
  se <- as.numeric(z$SE.estimate[1])
  lcl <- as.numeric(z$lcl[1])
  ucl <- as.numeric(z$ucl[1])

  # Numerical-validity repair added after a QA audit found two pathological
  # fits with enormous sigma estimates but an impossible reported SE of zero.
  # The scientific generator, cells, seeds and effect thresholds are unchanged.
  # A fitted sigma is counted as successful only when both the point estimate
  # and its Hessian-based uncertainty are finite and the sigma SE is positive.
  fit_code <- if (!is.null(fit$fit$code)) {
    as.integer(fit$fit$code)
  } else if (!is.null(fit$fit$convergence)) {
    as.integer(fit$fit$convergence)
  } else {
    NA_integer_
  }
  fit_code_ok <- if (is.na(fit_code)) NA else fit_code <= 2L
  ok <- is.finite(est) && est > 0 &&
    is.finite(se) && se > 0 &&
    is.finite(lcl) && is.finite(ucl) &&
    ucl > lcl
  issue <- if (ok) "" else paste(
    c(
      if (!is.finite(est) || est <= 0) "invalid_sigma" else NULL,
      if (!is.finite(se) || se <= 0) "invalid_sigma_se" else NULL,
      if (!is.finite(lcl) || !is.finite(ucl) || ucl <= lcl) "invalid_sigma_ci" else NULL
    ),
    collapse = ";"
  )
  data.frame(
    success=ok,
    sigma_hat=if (ok) est else NA_real_,
    sigma_se=if (ok) se else NA_real_,
    lcl=if (ok) lcl else NA_real_,
    ucl=if (ok) ucl else NA_real_,
    optimizer_code=fit_code,
    optimizer_code_ok=fit_code_ok,
    error=issue,
    stringsAsFactors=FALSE
  )
}

fit_three_encodings <- function(check_records, sigma_true, family, orientation, replicate_id) {
  first_records <- collapse_records(check_records, "first")
  last_records <- collapse_records(check_records, "last")
  datasets <- list(
    CHECK = make_ch(check_records, NIGHTS * CHECKS_PER_NIGHT),
    FIRST = make_ch(first_records, NIGHTS),
    LAST = make_ch(last_records, NIGHTS)
  )
  rows <- lapply(names(datasets), function(method) {
    f <- fit_sigma(datasets[[method]], sigma_true)
    cbind(
      data.frame(
        family=family,
        orientation=orientation,
        replicate=replicate_id,
        sigma_true=sigma_true,
        method=method,
        stringsAsFactors=FALSE
      ),
      f
    )
  })
  do.call(rbind, rows)
}

stationary_task <- function(sigma_true, replicate_id, seed) {
  ch <- sim.capthist(
    tr,
    popn = list(D = DENSITY, buffer = BUFFER),
    detectfn = "HN",
    detectpar = list(g0 = G0, sigma = sigma_true),
    noccasions = NIGHTS * CHECKS_PER_NIGHT,
    seed = seed
  )
  rec <- records_from_capthist(ch)
  fit_three_encodings(rec, sigma_true, "stationary_null", "NONE", replicate_id)
}

transition_task <- function(sigma_true, orientation, replicate_id, seed) {
  base <- sim.capthist(
    tr,
    popn = list(D = DENSITY, buffer = BUFFER),
    detectfn = "HN",
    detectpar = list(g0 = G0, sigma = sigma_true),
    noccasions = NIGHTS,
    seed = seed
  )
  built <- transition_check_records(base, orientation, seed + 7919L)
  fits <- fit_three_encodings(
    built$records, sigma_true, "empirical_transition", orientation, replicate_id
  )
  diag <- built$diagnostics
  calibration <- data.frame(
    family="empirical_transition",
    orientation=orientation,
    replicate=replicate_id,
    sigma_true=sigma_true,
    base_captured_nights=built$base_captured_nights,
    repeat_nights=nrow(diag),
    repeat_fraction=if (built$base_captured_nights > 0) nrow(diag) / built$base_captured_nights else NA_real_,
    changed_repeat_nights=sum(diag$changed),
    changed_fraction=if (nrow(diag) > 0) mean(diag$changed) else NA_real_,
    changed_median_distance_m=if (any(diag$changed)) median(diag$distance[diag$changed]) else NA_real_,
    changed_q90_distance_m=if (any(diag$changed)) as.numeric(quantile(diag$distance[diag$changed], .90, names=FALSE)) else NA_real_,
    stringsAsFactors=FALSE
  )
  list(fits=fits, calibration=calibration)
}

tasks <- list()
ti <- 1L
for (s in SIGMAS) {
  for (r in seq_len(nrepl)) {
    tasks[[ti]] <- list(
      type="stationary",
      sigma=s,
      orientation="NONE",
      replicate=r,
      seed=base_seed + ti * 1009L
    )
    ti <- ti + 1L
  }
}
for (s in SIGMAS) {
  for (o in c("POST", "PRE")) {
    for (r in seq_len(nrepl)) {
      tasks[[ti]] <- list(
        type="transition",
        sigma=s,
        orientation=o,
        replicate=r,
        seed=base_seed + ti * 1009L
      )
      ti <- ti + 1L
    }
  }
}

run_task <- function(task) {
  if (task$type == "stationary") {
    list(
      fits=stationary_task(task$sigma, task$replicate, task$seed),
      calibration=NULL
    )
  } else {
    transition_task(task$sigma, task$orientation, task$replicate, task$seed)
  }
}

if (.Platform$OS.type == "unix" && cores > 1) {
  pieces <- parallel::mclapply(tasks, run_task, mc.cores = cores, mc.preschedule = FALSE)
} else {
  pieces <- lapply(tasks, run_task)
}

fits <- do.call(rbind, lapply(pieces, `[[`, "fits"))
cal_pieces <- Filter(Negate(is.null), lapply(pieces, `[[`, "calibration"))
calibration_reps <- if (length(cal_pieces)) do.call(rbind, cal_pieces) else data.frame()

fits$relative_bias <- (fits$sigma_hat - fits$sigma_true) / fits$sigma_true
fits$covered95 <- with(fits, success & lcl <= sigma_true & ucl >= sigma_true)
fits$relative_ci_width <- with(fits, (ucl - lcl) / sigma_true)

summarize_group <- function(g) {
  ok <- g[g$success, , drop=FALSE]
  if (nrow(ok) == 0) {
    return(data.frame(
      n=nrow(g), n_success=0, failure_fraction=1,
      mean_sigma_hat=NA, median_sigma_hat=NA,
      mean_relative_bias=NA, median_relative_bias=NA,
      rmse=NA, coverage95=NA, median_relative_ci_width=NA,
      fraction_abs_bias_ge_10pct=NA
    ))
  }
  data.frame(
    n=nrow(g),
    n_success=nrow(ok),
    failure_fraction=1 - nrow(ok)/nrow(g),
    mean_sigma_hat=mean(ok$sigma_hat),
    median_sigma_hat=median(ok$sigma_hat),
    mean_relative_bias=mean(ok$relative_bias),
    median_relative_bias=median(ok$relative_bias),
    rmse=sqrt(mean((ok$sigma_hat - ok$sigma_true)^2)),
    coverage95=mean(ok$covered95),
    median_relative_ci_width=median(ok$relative_ci_width),
    fraction_abs_bias_ge_10pct=mean(abs(ok$relative_bias) >= 0.10)
  )
}

group_key <- interaction(
  fits$family, fits$orientation, fits$sigma_true, fits$method,
  drop=TRUE, lex.order=TRUE
)
sum_parts <- lapply(split(fits, group_key), function(g) {
  headrow <- g[1, c("family","orientation","sigma_true","method"), drop=FALSE]
  cbind(headrow, summarize_group(g))
})
summary_df <- do.call(rbind, sum_parts)
rownames(summary_df) <- NULL

paired_contrasts <- function(g) {
  methods <- split(g, g$method)
  needed <- c("CHECK","FIRST","LAST")
  if (!all(needed %in% names(methods))) return(NULL)
  ids <- Reduce(intersect, lapply(methods[needed], function(z) z$replicate[z$success]))
  if (!length(ids)) return(NULL)
  val <- function(m) {
    z <- methods[[m]]
    setNames(z$sigma_hat, z$replicate)[as.character(ids)]
  }
  check <- val("CHECK"); first <- val("FIRST"); last <- val("LAST")
  data.frame(
    n_paired=length(ids),
    median_last_first_ratio=median(last/first),
    median_check_first_ratio=median(check/first),
    median_check_last_ratio=median(check/last),
    fraction_last_first_diff_ge_10pct=mean(abs(last/first - 1) >= .10),
    fraction_check_first_diff_ge_10pct=mean(abs(check/first - 1) >= .10),
    fraction_check_last_diff_ge_10pct=mean(abs(check/last - 1) >= .10)
  )
}

cell_key <- interaction(
  fits$family, fits$orientation, fits$sigma_true,
  drop=TRUE, lex.order=TRUE
)
pair_parts <- lapply(split(fits, cell_key), function(g) {
  z <- paired_contrasts(g)
  if (is.null(z)) return(NULL)
  headrow <- g[1, c("family","orientation","sigma_true"), drop=FALSE]
  cbind(headrow, z)
})
pair_parts <- Filter(Negate(is.null), pair_parts)
paired_df <- if (length(pair_parts)) do.call(rbind, pair_parts) else data.frame()
if (nrow(paired_df)) rownames(paired_df) <- NULL

calibration_summary <- NULL
if (nrow(calibration_reps)) {
  ck <- interaction(
    calibration_reps$orientation,
    calibration_reps$sigma_true,
    drop=TRUE, lex.order=TRUE
  )
  cps <- lapply(split(calibration_reps, ck), function(g) {
    data.frame(
      orientation=g$orientation[1],
      sigma_true=g$sigma_true[1],
      mean_repeat_fraction=mean(g$repeat_fraction, na.rm=TRUE),
      mean_changed_fraction=mean(g$changed_fraction, na.rm=TRUE),
      median_of_changed_medians_m=median(g$changed_median_distance_m, na.rm=TRUE),
      median_of_changed_q90_m=median(g$changed_q90_distance_m, na.rm=TRUE)
    )
  })
  calibration_summary <- do.call(rbind, cps)
  rownames(calibration_summary) <- NULL
}

stationary_summary <- summary_df[summary_df$family == "stationary_null", , drop=FALSE]
stationary_max_abs_median_bias <- max(abs(stationary_summary$median_relative_bias), na.rm=TRUE)

out <- list(
  schema="neon.scr_sigma_consequence_simulation.v1",
  generated_at_utc=format(Sys.time(), tz="UTC", usetz=TRUE),
  seed=base_seed,
  nrepl_per_cell=nrepl,
  secr_version=as.character(packageVersion("secr")),
  design=list(
    trap_grid="7x7",
    spacing_m=SPACING,
    checks_per_night=CHECKS_PER_NIGHT,
    nights=NIGHTS,
    g0=G0,
    density_per_ha=DENSITY,
    original_density_per_ha=ORIGINAL_DENSITY,
    estimability_repair="density_only_20_to_60_animals_per_ha",
    buffer_m=BUFFER,
    sigma_true_m=SIGMAS,
    fit_model="CL=TRUE; HN; g0~b; sigma~1",
    numerical_success_rule="finite positive sigma; finite positive sigma SE; finite ordered CI"
  ),
  empirical_anchor=list(
    source_sha256="ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301",
    species=kernel$species,
    pooled=kernel$pooled
  ),
  analytic_second_moment_benchmark=analytic_benchmark,
  summaries=summary_df,
  paired_contrasts=paired_df,
  transition_calibration=calibration_summary,
  diagnostic_checks=list(
    stationary_max_abs_median_relative_bias=stationary_max_abs_median_bias,
    stationary_null_within_10pct=stationary_max_abs_median_bias < 0.10,
    empirical_real_data_sigma_opened=FALSE,
    numerical_validity_repair="positive sigma SE and ordered finite CI required; generator and seeds unchanged"
  )
)

dir.create(dirname(out_json), recursive=TRUE, showWarnings=FALSE)
dir.create(dirname(out_csv), recursive=TRUE, showWarnings=FALSE)
write_json(out, out_json, pretty=TRUE, auto_unbox=TRUE, na="null")
write.csv(fits, out_csv, row.names=FALSE)

cat(toJSON(list(
  empirical_anchor=kernel$pooled,
  diagnostic_checks=out$diagnostic_checks,
  summaries=summary_df,
  paired_contrasts=paired_df,
  transition_calibration=calibration_summary
), pretty=TRUE, auto_unbox=TRUE, na="null"))
cat("\n")
