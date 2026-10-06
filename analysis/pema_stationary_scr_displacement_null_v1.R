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
bootstrap_csv <- arg_value("--bootstrap-csv", "results/pema_stationary_scr_displacement_null_bootstrap_v1.csv")
base_seed <- as.integer(arg_value("--seed", "20261006"))
target_repeat <- as.integer(arg_value("--target-repeat", "2500"))
nboot <- as.integer(arg_value("--nboot", "2000"))

if (is.null(source_path) || !file.exists(source_path)) stop("--source must exist")
if (!is.finite(target_repeat) || target_repeat < 485) stop("target-repeat must be >=485")
if (!is.finite(nboot) || nboot < 200) stop("nboot must be >=200")

SPACING <- 6.25
BUFFER <- 100
DENSITY <- 60
CHECKS <- 3
OBS_N <- 485L
SIGMAS <- c(7.7806, 8.5625, 8.8515, 9.7559)
G0S <- c(0.03, 0.06, 0.10, 0.15, 0.25)

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
  out[which(ok)] <- hh + m / 60
  out
}

flag_xy <- function(flag) {
  flag <- toupper(trimws(as.character(flag)))
  row <- match(substr(flag, 1, 1), LETTERS[1:7]) - 1
  col <- suppressWarnings(as.integer(substr(flag, 2, nchar(flag)))) - 1
  cbind(x = col * SPACING, y = row * SPACING)
}

summarize_vectors <- function(dx, dy) {
  d <- sqrt(dx^2 + dy^2)
  c(
    changed_fraction = mean(d >= SPACING - 1e-10),
    vector_rms_m = sqrt(mean(d^2)),
    axis_rms_m = sqrt(mean((dx^2 + dy^2) / 2)),
    median_distance_m = median(d),
    q90_distance_m = as.numeric(quantile(d, 0.90, names = FALSE, type = 8)),
    mean_dx_m = mean(dx),
    mean_dy_m = mean(dy),
    mean_vector_magnitude_m = sqrt(mean(dx)^2 + mean(dy)^2)
  )
}

empirical_repeat_vectors <- function(path) {
  dat <- read.csv(path, stringsAsFactors = FALSE, check.names = FALSE)
  req <- c("species","grid","unique_ID","date","flag","time")
  if (!all(req %in% names(dat))) stop("source missing required columns")
  dat$.row <- seq_len(nrow(dat))
  dat$species <- trimws(as.character(dat$species))
  dat$grid <- trimws(as.character(dat$grid))
  dat$unique_ID <- trimws(as.character(dat$unique_ID))
  dat$date <- trimws(as.character(dat$date))
  dat$flag <- toupper(trimws(as.character(dat$flag)))
  dat$.time <- parse_nocturnal_time(dat$time)
  keep <- dat$species == "PEMA" &
    nzchar(dat$grid) & nzchar(dat$unique_ID) & nzchar(dat$date) &
    grepl("^[A-G][1-7]$", dat$flag) & is.finite(dat$.time)
  dat <- dat[keep,,drop=FALSE]
  dat$.key <- paste(dat$grid, dat$unique_ID, dat$date, sep="||")
  groups <- split(dat, dat$.key)
  rows <- lapply(groups, function(g) {
    g <- g[order(g$.time, g$.row),,drop=FALSE]
    if (nrow(g) < 2) return(NULL)
    p1 <- flag_xy(g$flag[1])
    p2 <- flag_xy(g$flag[nrow(g)])
    data.frame(
      dx = p2[1,"x"] - p1[1,"x"],
      dy = p2[1,"y"] - p1[1,"y"],
      stringsAsFactors = FALSE
    )
  })
  z <- do.call(rbind, rows)
  if (is.null(z) || nrow(z) != OBS_N) stop("expected 485 PEMA repeat nights")
  z
}

emp <- empirical_repeat_vectors(source_path)
emp_summary <- summarize_vectors(emp$dx, emp$dy)

tr <- make.grid(nx=7, ny=7, spacing=SPACING, detector="multi", ID="numy", leadingzero=FALSE)
trxy <- as.matrix(tr)[,1:2,drop=FALSE]
colnames(trxy) <- c("x","y")
core <- as.data.frame(trxy)

records_from_one_check <- function(ch, check_index) {
  ids <- as.character(animalID(ch, names=TRUE))
  k <- as.integer(trap(ch, names=FALSE))
  if (!length(ids)) return(data.frame(ID=character(),check=integer(),trap=integer()))
  data.frame(ID=ids, check=rep.int(check_index,length(ids)), trap=k, stringsAsFactors=FALSE)
}

simulate_one_night <- function(sigma, g0, seed) {
  set.seed(seed)
  pop <- sim.popn(
    D=DENSITY, core=core, buffer=BUFFER, model2D="poisson",
    Ndist="poisson", seed=seed
  )
  recs <- vector("list", CHECKS)
  for (check in seq_len(CHECKS)) {
    ch <- sim.capthist(
      tr, popn=pop, detectfn="HN",
      detectpar=list(g0=g0, sigma=sigma),
      noccasions=1, renumber=FALSE,
      seed=seed + check*1009L
    )
    recs[[check]] <- records_from_one_check(ch, check)
  }
  x <- do.call(rbind,recs)
  if (!nrow(x)) return(list(captured=0L, repeat=data.frame(dx=numeric(),dy=numeric())))
  groups <- split(x, x$ID)
  out <- lapply(groups, function(g) {
    g <- g[order(g$check),,drop=FALSE]
    if (nrow(g) < 2) return(NULL)
    p1 <- trxy[g$trap[1],]
    p2 <- trxy[g$trap[nrow(g)],]
    data.frame(dx=p2[1]-p1[1],dy=p2[2]-p1[2])
  })
  rep <- do.call(rbind,out)
  if (is.null(rep)) rep <- data.frame(dx=numeric(),dy=numeric())
  list(captured=length(groups), repeat=rep)
}

run_cell <- function(sigma, g0, cell_seed) {
  pooled <- data.frame(dx=numeric(),dy=numeric())
  captured_total <- 0L
  nights <- 0L
  while (nrow(pooled) < target_repeat) {
    nights <- nights + 1L
    z <- simulate_one_night(sigma,g0,cell_seed + nights*100003L)
    captured_total <- captured_total + z$captured
    if (nrow(z$repeat)) pooled <- rbind(pooled,z$repeat)
    if (nights > 5000L) stop("failed to accumulate repeat nights")
  }
  pooled <- pooled[seq_len(target_repeat),,drop=FALSE]
  null_summary <- summarize_vectors(pooled$dx,pooled$dy)
  repeat_fraction <- target_repeat / captured_total

  set.seed(cell_seed + 9000001L)
  boot <- matrix(NA_real_, nrow=nboot, ncol=length(emp_summary))
  colnames(boot) <- names(emp_summary)
  for (b in seq_len(nboot)) {
    ii <- sample.int(nrow(pooled), OBS_N, replace=TRUE)
    boot[b,] <- summarize_vectors(pooled$dx[ii], pooled$dy[ii])
  }
  comp <- lapply(seq_along(emp_summary), function(j) {
    vals <- boot[,j]
    obs <- unname(emp_summary[j])
    data.frame(
      sigma_m=sigma,g0=g0,metric=names(emp_summary)[j],
      observed=obs,
      null_p2.5=as.numeric(quantile(vals,.025,names=FALSE,type=8)),
      null_median=median(vals),
      null_p97.5=as.numeric(quantile(vals,.975,names=FALSE,type=8)),
      p_ge_observed=mean(vals>=obs),
      p_le_observed=mean(vals<=obs),
      observed_inside_95=obs>=quantile(vals,.025,names=FALSE,type=8) &&
                         obs<=quantile(vals,.975,names=FALSE,type=8),
      stringsAsFactors=FALSE
    )
  })
  comp <- do.call(rbind,comp)
  boot_long <- do.call(rbind,lapply(seq_len(nboot),function(b){
    data.frame(sigma_m=sigma,g0=g0,bootstrap=b,
               metric=colnames(boot),value=as.numeric(boot[b,]),
               stringsAsFactors=FALSE)
  }))
  list(
    cell=data.frame(
      sigma_m=sigma,g0=g0,simulated_nights=nights,
      captured_animal_nights=captured_total,
      repeat_animal_nights=target_repeat,
      repeat_fraction=repeat_fraction,
      null_changed_fraction=unname(null_summary["changed_fraction"]),
      null_vector_rms_m=unname(null_summary["vector_rms_m"]),
      null_axis_rms_m=unname(null_summary["axis_rms_m"]),
      null_median_distance_m=unname(null_summary["median_distance_m"]),
      null_q90_distance_m=unname(null_summary["q90_distance_m"]),
      null_mean_vector_magnitude_m=unname(null_summary["mean_vector_magnitude_m"])
    ),
    comparison=comp,
    bootstrap=boot_long
  )
}

grid <- expand.grid(sigma_m=SIGMAS,g0=G0S,KEEP.OUT.ATTRS=FALSE,stringsAsFactors=FALSE)
pieces <- vector("list",nrow(grid))
for (i in seq_len(nrow(grid))) {
  message("cell ",i,"/",nrow(grid)," sigma=",grid$sigma_m[i]," g0=",grid$g0[i])
  pieces[[i]] <- run_cell(grid$sigma_m[i],grid$g0[i],base_seed+i*10000019L)
}

cells <- do.call(rbind,lapply(pieces,`[[`,"cell"))
comparisons <- do.call(rbind,lapply(pieces,`[[`,"comparison"))
boots <- do.call(rbind,lapply(pieces,`[[`,"bootstrap"))

emp_repeat_fraction <- 485/1219
cells$repeat_fraction_abs_error <- abs(cells$repeat_fraction-emp_repeat_fraction)
closest <- cells[order(cells$repeat_fraction_abs_error),,drop=FALSE][1:min(5,nrow(cells)),]

metric_pass <- aggregate(
  observed_inside_95 ~ metric,
  data=comparisons,
  FUN=function(x)c(n_inside=sum(x),n_cells=length(x),fraction_inside=mean(x))
)

out <- list(
  schema="neon.pema_stationary_scr_displacement_null.v1",
  generated_at_utc=format(Sys.time(),tz="UTC",usetz=TRUE),
  seed=base_seed,
  design=list(
    trap_grid="7x7",spacing_m=SPACING,checks_per_night=CHECKS,
    density_per_ha=DENSITY,buffer_m=BUFFER,
    sigma_m=SIGMAS,g0=G0S,target_repeat_nights_per_cell=target_repeat,
    bootstrap_draws_per_cell=nboot,bootstrap_sample_size=OBS_N,
    generator="static activity centre within night; three independent secr checks; no state shift"
  ),
  empirical=list(
    repeat_nights=OBS_N,
    captured_individual_nights=1219,
    repeat_fraction=emp_repeat_fraction,
    summary=as.list(emp_summary)
  ),
  cells=cells,
  comparisons=comparisons,
  closest_cells_by_repeat_fraction=closest,
  interpretation=list(
    displacement_metrics_inside_null_cells=lapply(split(comparisons,comparisons$metric),function(z)sum(z$observed_inside_95)),
    total_cells=nrow(cells),
    claim_boundary="Reference diagnostic only; same data informed sigma bracket. Does not identify handling effects or prove exchangeability."
  ),
  package_versions=list(R=as.character(getRversion()),secr=as.character(packageVersion("secr")),jsonlite=as.character(packageVersion("jsonlite")))
)

dir.create(dirname(out_json),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(out_csv),recursive=TRUE,showWarnings=FALSE)
write_json(out,out_json,pretty=TRUE,auto_unbox=TRUE,na="null")
write.csv(cells,out_csv,row.names=FALSE)
write.csv(boots,bootstrap_csv,row.names=FALSE)
cat(toJSON(list(empirical=out$empirical,closest_cells=closest,interpretation=out$interpretation),pretty=TRUE,auto_unbox=TRUE))
cat("\n")
