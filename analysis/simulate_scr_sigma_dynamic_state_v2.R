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
out_json <- arg_value("--output-json", "results/scr_sigma_dynamic_state_v2.json")
out_csv <- arg_value("--output-csv", "results/scr_sigma_dynamic_state_replicates_v2.csv")
nrepl <- as.integer(arg_value("--nrepl", "24"))
cores <- as.integer(arg_value("--cores", "2"))
base_seed <- as.integer(arg_value("--seed", "20261003"))

if (is.null(source_path) || !file.exists(source_path)) stop("--source must exist")
if (!is.finite(nrepl) || nrepl < 2) stop("nrepl must be >=2")
if (!is.finite(cores) || cores < 1) stop("cores must be >=1")

SPACING <- 6.25
SIGMAS <- c(6.25, 12.5, 25.0)
G0 <- 0.15
DENSITY <- 60
BUFFER <- 100
NIGHTS <- 3
CHECKS_PER_NIGHT <- 3
SPECIES <- c("PEMA", "PEER")
SHIFT_MULTIPLIERS <- c(0, 0.5, 1.0, 1.5)

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
  if (!all(required %in% names(dat))) stop("source file missing required columns")
  dat$.row <- seq_len(nrow(dat))
  dat$species <- trimws(as.character(dat$species))
  dat$grid <- trimws(as.character(dat$grid))
  dat$unique_ID <- trimws(as.character(dat$unique_ID))
  dat$date <- trimws(as.character(dat$date))
  dat$flag <- toupper(trimws(as.character(dat$flag)))
  dat$.time <- parse_nocturnal_time(dat$time)
  keep <- dat$species %in% SPECIES &
    nzchar(dat$grid) & nzchar(dat$unique_ID) & nzchar(dat$date) &
    grepl("^[A-G][1-7]$", dat$flag) & is.finite(dat$.time)
  dat <- dat[keep, , drop = FALSE]
  dat$.key <- paste(dat$species, dat$grid, dat$unique_ID, dat$date, sep = "||")
  groups <- split(dat, dat$.key)
  rows <- lapply(groups, function(g) {
    g <- g[order(g$.time, g$.row), , drop = FALSE]
    xy1 <- flag_xy(g$flag[1])
    xy2 <- flag_xy(g$flag[nrow(g)])
    data.frame(
      species = g$species[1],
      n_records = nrow(g),
      dx = xy2[1,"x"] - xy1[1,"x"],
      dy = xy2[1,"y"] - xy1[1,"y"],
      distance = sqrt((xy2[1,"x"]-xy1[1,"x"])^2 + (xy2[1,"y"]-xy1[1,"y"])^2),
      stringsAsFactors = FALSE
    )
  })
  nights <- do.call(rbind, rows)
  repeat_nights <- nights[nights$n_records >= 2, , drop = FALSE]
  changed <- repeat_nights[repeat_nights$distance >= SPACING - 1e-10, , drop = FALSE]
  if (nrow(nights) != 1520L || nrow(repeat_nights) != 592L || nrow(changed) != 426L) {
    stop("empirical calibration counts do not reproduce frozen results")
  }
  list(
    vectors = as.matrix(changed[,c("dx","dy"),drop=FALSE]),
    repeat_fraction = nrow(repeat_nights)/nrow(nights),
    changed_given_repeat = nrow(changed)/nrow(repeat_nights),
    effective_transition_fraction = nrow(changed)/nrow(nights),
    changed_rms_m = sqrt(mean(changed$distance^2)),
    changed_median_m = median(changed$distance)
  )
}

kernel <- build_empirical_kernel(source_path)
SHIFT_PROB <- kernel$changed_given_repeat

tr <- make.grid(nx=7, ny=7, spacing=SPACING, detector="multi", ID="numy", leadingzero=FALSE)
trxy <- as.matrix(tr)[,1:2,drop=FALSE]
colnames(trxy) <- c("x","y")
fitmask <- make.mask(tr, buffer=BUFFER, spacing=5)
core <- as.data.frame(trxy)

records_from_capthist <- function(ch, global_occasion) {
  ids <- as.character(animalID(ch, names=TRUE))
  k <- as.integer(trap(ch, names=FALSE))
  if (!length(ids)) {
    return(data.frame(ID=character(), occasion=integer(), trap=integer()))
  }
  data.frame(
    ID=ids,
    occasion=rep.int(as.integer(global_occasion), length(ids)),
    trap=k,
    stringsAsFactors=FALSE
  )
}

make_ch <- function(records, noccasions) {
  if (!nrow(records)) stop("zero detections")
  make.capthist(
    data.frame(
      session=1,
      ID=as.character(records$ID),
      occasion=as.integer(records$occasion),
      trap=as.integer(records$trap),
      stringsAsFactors=FALSE
    ),
    traps=tr, fmt="trapID", noccasions=noccasions, bysession=FALSE
  )
}

collapse_records <- function(check_records, method=c("first","last")) {
  method <- match.arg(method)
  x <- check_records
  x$night <- ((x$occasion - 1L) %/% CHECKS_PER_NIGHT) + 1L
  groups <- split(x, paste(x$ID,x$night,sep="||"))
  out <- lapply(groups, function(g) {
    g <- g[order(g$occasion),,drop=FALSE]
    z <- if (method=="first") g[1,,drop=FALSE] else g[nrow(g),,drop=FALSE]
    data.frame(ID=z$ID, occasion=z$night, trap=z$trap, stringsAsFactors=FALSE)
  })
  do.call(rbind,out)
}

night_diagnostics <- function(records) {
  x <- records
  x$night <- ((x$occasion - 1L) %/% CHECKS_PER_NIGHT) + 1L
  groups <- split(x, paste(x$ID,x$night,sep="||"))
  rows <- lapply(groups, function(g) {
    g <- g[order(g$occasion),,drop=FALSE]
    first <- g[1,,drop=FALSE]
    last <- g[nrow(g),,drop=FALSE]
    p1 <- trxy[first$trap,]
    p2 <- trxy[last$trap,]
    d <- sqrt(sum((p2-p1)^2))
    data.frame(
      detections=nrow(g),
      repeated=nrow(g)>=2,
      changed=(nrow(g)>=2 && d>=SPACING-1e-10),
      first_last_distance_m=d
    )
  })
  z <- do.call(rbind, rows)
  repeated <- z[z$repeated,,drop=FALSE]
  changed <- repeated[repeated$changed,,drop=FALSE]
  list(
    captured_nights=nrow(z),
    repeat_nights=nrow(repeated),
    repeat_fraction=if(nrow(z)) nrow(repeated)/nrow(z) else NA_real_,
    changed_repeat_nights=nrow(changed),
    changed_fraction_given_repeat=if(nrow(repeated)) nrow(changed)/nrow(repeated) else NA_real_,
    changed_median_distance_m=if(nrow(changed)) median(changed$first_last_distance_m) else NA_real_,
    changed_rms_distance_m=if(nrow(changed)) sqrt(mean(changed$first_last_distance_m^2)) else NA_real_
  )
}

fit_sigma <- function(ch) {
  fit <- tryCatch(
    suppressWarnings(secr.fit(
      ch,
      model=list(g0~b, sigma~1),
      CL=TRUE,
      mask=fitmask,
      detectfn="HN",
      trace=FALSE,
      biasLimit=NA,
      ncores=1
    )),
    error=function(e)e
  )
  if (inherits(fit,"error")) {
    return(data.frame(success=FALSE,sigma_hat=NA_real_,lcl=NA_real_,ucl=NA_real_,error=conditionMessage(fit)))
  }
  pr <- tryCatch(predict(fit, realnames="sigma"), error=function(e)e)
  if (inherits(pr,"error")) {
    return(data.frame(success=FALSE,sigma_hat=NA_real_,lcl=NA_real_,ucl=NA_real_,error=conditionMessage(pr)))
  }
  z <- if ("sigma" %in% rownames(pr)) pr["sigma",,drop=FALSE] else pr[1,,drop=FALSE]
  est <- as.numeric(z$estimate[1]); lo <- as.numeric(z$lcl[1]); hi <- as.numeric(z$ucl[1])
  ok <- is.finite(est) && est>0 && is.finite(lo) && is.finite(hi)
  data.frame(success=ok,sigma_hat=if(ok)est else NA_real_,lcl=if(ok)lo else NA_real_,ucl=if(ok)hi else NA_real_,error=if(ok)"" else "non-finite prediction")
}

apply_shift <- function(state, ids, multiplier) {
  if (multiplier <= 0 || !length(ids)) return(state)
  for (id in ids) {
    if (runif(1) >= SHIFT_PROB) next
    idx <- match(as.character(id), rownames(state))
    if (is.na(idx)) stop("captured ID not found in population")
    v <- kernel$vectors[sample.int(nrow(kernel$vectors),1L),] * multiplier
    state[idx,"x"] <- state[idx,"x"] + v[1]
    state[idx,"y"] <- state[idx,"y"] + v[2]
  }
  state
}

simulate_dynamic_records <- function(sigma_true, multiplier, seed) {
  set.seed(seed)
  basepop <- sim.popn(
    D=DENSITY, core=core, buffer=BUFFER, model2D="poisson",
    Ndist="poisson", seed=seed
  )
  all_records <- list(); oi <- 1L
  for (night in seq_len(NIGHTS)) {
    state <- basepop
    shifted_ids <- character()
    for (check in seq_len(CHECKS_PER_NIGHT)) {
      occ <- (night-1L)*CHECKS_PER_NIGHT + check
      ch <- sim.capthist(
        tr, popn=state,
        detectfn="HN", detectpar=list(g0=G0,sigma=sigma_true),
        noccasions=1, renumber=FALSE,
        seed=seed + night*1009L + check*101L
      )
      rec <- records_from_capthist(ch, occ)
      if (nrow(rec)) {
        all_records[[oi]] <- rec; oi <- oi+1L
        newly <- setdiff(unique(rec$ID), shifted_ids)
        if (length(newly)) {
          state <- apply_shift(state, newly, multiplier)
          shifted_ids <- union(shifted_ids, newly)
        }
      }
    }
  }
  if (!length(all_records)) stop("replicate yielded zero detections")
  do.call(rbind, all_records)
}

fit_encodings <- function(records, sigma_true, multiplier, replicate_id) {
  first <- collapse_records(records,"first")
  last <- collapse_records(records,"last")
  datasets <- list(
    CHECK=make_ch(records,NIGHTS*CHECKS_PER_NIGHT),
    FIRST=make_ch(first,NIGHTS),
    LAST=make_ch(last,NIGHTS)
  )
  rows <- lapply(names(datasets), function(method) {
    f <- fit_sigma(datasets[[method]])
    cbind(data.frame(
      shift_multiplier=multiplier,
      replicate=replicate_id,
      sigma_true=sigma_true,
      method=method,
      stringsAsFactors=FALSE
    ),f)
  })
  do.call(rbind,rows)
}

task_grid <- expand.grid(
  sigma_true=SIGMAS,
  shift_multiplier=SHIFT_MULTIPLIERS,
  replicate=seq_len(nrepl),
  KEEP.OUT.ATTRS=FALSE,
  stringsAsFactors=FALSE
)
task_grid$seed <- base_seed + seq_len(nrow(task_grid))*10007L

run_task <- function(i) {
  task <- task_grid[i,,drop=FALSE]
  rec <- simulate_dynamic_records(task$sigma_true, task$shift_multiplier, task$seed)
  list(
    fits=fit_encodings(rec,task$sigma_true,task$shift_multiplier,task$replicate),
    calibration=cbind(
      data.frame(
        shift_multiplier=task$shift_multiplier,
        replicate=task$replicate,
        sigma_true=task$sigma_true
      ),
      as.data.frame(night_diagnostics(rec))
    )
  )
}

if (.Platform$OS.type=="unix" && cores>1) {
  pieces <- parallel::mclapply(seq_len(nrow(task_grid)),run_task,mc.cores=cores,mc.preschedule=FALSE)
} else {
  pieces <- lapply(seq_len(nrow(task_grid)),run_task)
}

fits <- do.call(rbind,lapply(pieces,`[[`,"fits"))
cal <- do.call(rbind,lapply(pieces,`[[`,"calibration"))
fits$relative_bias <- (fits$sigma_hat-fits$sigma_true)/fits$sigma_true
fits$covered95 <- with(fits,success & lcl<=sigma_true & ucl>=sigma_true)

summarize_group <- function(g) {
  ok <- g[g$success,,drop=FALSE]
  data.frame(
    n=nrow(g),
    n_success=nrow(ok),
    failure_fraction=1-nrow(ok)/nrow(g),
    median_sigma_hat=if(nrow(ok))median(ok$sigma_hat) else NA_real_,
    mean_sigma_hat=if(nrow(ok))mean(ok$sigma_hat) else NA_real_,
    median_relative_bias=if(nrow(ok))median(ok$relative_bias) else NA_real_,
    mean_relative_bias=if(nrow(ok))mean(ok$relative_bias) else NA_real_,
    coverage95=if(nrow(ok))mean(ok$covered95) else NA_real_
  )
}

gkey <- interaction(fits$shift_multiplier,fits$sigma_true,fits$method,drop=TRUE,lex.order=TRUE)
summary_df <- do.call(rbind,lapply(split(fits,gkey),function(g){
  cbind(g[1,c("shift_multiplier","sigma_true","method"),drop=FALSE],summarize_group(g))
}))
rownames(summary_df)<-NULL

cellkey <- interaction(fits$shift_multiplier,fits$sigma_true,drop=TRUE,lex.order=TRUE)
paired <- do.call(rbind,lapply(split(fits,cellkey),function(g){
  ms <- split(g,g$method)
  ids <- Reduce(intersect,lapply(ms[c("CHECK","FIRST","LAST")],function(z)z$replicate[z$success]))
  if(!length(ids))return(NULL)
  val <- function(m)setNames(ms[[m]]$sigma_hat,ms[[m]]$replicate)[as.character(ids)]
  cc<-val("CHECK"); ff<-val("FIRST"); ll<-val("LAST")
  data.frame(
    shift_multiplier=g$shift_multiplier[1],
    sigma_true=g$sigma_true[1],
    n_paired=length(ids),
    median_last_first_ratio=median(ll/ff),
    median_check_first_ratio=median(cc/ff),
    median_check_last_ratio=median(cc/ll)
  )
}))
rownames(paired)<-NULL

ckey <- interaction(cal$shift_multiplier,cal$sigma_true,drop=TRUE,lex.order=TRUE)
cal_summary <- do.call(rbind,lapply(split(cal,ckey),function(g){
  data.frame(
    shift_multiplier=g$shift_multiplier[1],
    sigma_true=g$sigma_true[1],
    mean_repeat_fraction=mean(g$repeat_fraction,na.rm=TRUE),
    mean_changed_fraction_given_repeat=mean(g$changed_fraction_given_repeat,na.rm=TRUE),
    median_changed_distance_m=median(g$changed_median_distance_m,na.rm=TRUE),
    median_changed_rms_m=median(g$changed_rms_distance_m,na.rm=TRUE)
  )
}))
rownames(cal_summary)<-NULL

null_summary <- summary_df[summary_df$shift_multiplier==0,,drop=FALSE]
max_null_bias <- max(abs(null_summary$median_relative_bias),na.rm=TRUE)

out <- list(
  schema="neon.scr_sigma_dynamic_state_robustness.v2",
  generated_at_utc=format(Sys.time(),tz="UTC",usetz=TRUE),
  seed=base_seed,
  nrepl_per_cell=nrepl,
  secr_version=as.character(packageVersion("secr")),
  design=list(
    trap_grid="7x7",
    spacing_m=SPACING,
    nights=NIGHTS,
    checks_per_night=CHECKS_PER_NIGHT,
    g0=G0,
    density_per_ha=DENSITY,
    buffer_m=BUFFER,
    sigma_true_m=SIGMAS,
    shift_probability_after_first_capture=SHIFT_PROB,
    empirical_shift_vector_rms_m=kernel$changed_rms_m,
    shift_multipliers=SHIFT_MULTIPLIERS,
    generator="sequential independent secr checks on a persistent within-night state centre; state centre may shift once after first capture",
    fit_model="CL=TRUE; HN; g0~b; sigma~1"
  ),
  empirical_anchor=list(
    repeat_fraction=kernel$repeat_fraction,
    changed_fraction_given_repeat=kernel$changed_given_repeat,
    effective_transition_fraction=kernel$effective_transition_fraction,
    changed_rms_m=kernel$changed_rms_m,
    changed_median_m=kernel$changed_median_m
  ),
  summaries=summary_df,
  paired_contrasts=paired,
  calibration=cal_summary,
  diagnostic_checks=list(
    zero_shift_max_abs_median_relative_bias=max_null_bias,
    zero_shift_within_10pct=max_null_bias<0.10,
    v1_conditional_record_expansion_used=FALSE,
    empirical_real_data_sigma_opened=FALSE
  )
)

dir.create(dirname(out_json),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(out_csv),recursive=TRUE,showWarnings=FALSE)
write_json(out,out_json,pretty=TRUE,auto_unbox=TRUE,na="null")
write.csv(fits,out_csv,row.names=FALSE)

cat(toJSON(list(
  design=out$design,
  diagnostic_checks=out$diagnostic_checks,
  calibration=cal_summary,
  summaries=summary_df,
  paired_contrasts=paired
),pretty=TRUE,auto_unbox=TRUE,na="null"))
cat("\n")
