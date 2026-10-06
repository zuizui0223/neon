#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(secr)
  library(jsonlite)
})

arg_value <- function(flag, default=NULL) {
  args <- commandArgs(trailingOnly=TRUE)
  i <- match(flag,args)
  if (is.na(i)) return(default)
  if (i==length(args)) stop(paste("missing value for",flag))
  args[[i+1]]
}

source_path <- arg_value("--source")
eligible_path <- arg_value("--eligible")
sigma_json <- arg_value("--sigma-json")
out_json <- arg_value("--output-json","results/pema_stationary_displacement_null_v1.json")
out_csv <- arg_value("--output-csv","results/pema_stationary_displacement_null_replicates_v1.csv")
nrepl <- as.integer(arg_value("--nrepl","250"))
cores <- as.integer(arg_value("--cores","4"))
base_seed <- as.integer(arg_value("--seed","20261006"))

stopifnot(file.exists(source_path),file.exists(eligible_path),file.exists(sigma_json))
SPACING <- 6.25
BUFFER <- 100
DENSITY <- 1200
CHECKS <- 3
G0_VALUES <- c(0.08,0.15,0.25)

clean <- function(x) trimws(ifelse(is.na(x),"",as.character(x)))
parse_date <- function(x) {
  x <- clean(x); out <- as.Date(rep(NA_character_,length(x)))
  for (fmt in c("%m/%d/%Y","%Y-%m-%d","%m/%d/%y")) {
    miss <- is.na(out); if (!any(miss)) break
    suppressWarnings(out[miss] <- as.Date(x[miss],format=fmt))
  }
  out
}
parse_nocturnal_time <- function(x) {
  x <- clean(x); out <- rep(NA_real_,length(x))
  m <- regexec("^(\\d{1,2}):(\\d{2})$",x); p <- regmatches(x,m)
  for (i in seq_along(p)) {
    if (length(p[[i]])!=3) next
    h <- as.integer(p[[i]][2]); minute <- as.integer(p[[i]][3])
    if (is.na(h)||is.na(minute)||minute>=60) next
    if (h>=7 && h<=11) h <- h+12 else if (h==12) h <- 24 else if (h>=0 && h<=6) h <- h+24 else next
    out[i] <- h + minute/60
  }
  out
}

flags <- unlist(lapply(LETTERS[1:7],function(z)paste0(z,1:7)))
flag_xy <- function(flag) {
  flag <- toupper(clean(flag))
  row <- match(substr(flag,1,1),LETTERS[1:7])-1
  col <- suppressWarnings(as.integer(substr(flag,2,nchar(flag))))-1
  cbind(x=col*SPACING,y=row*SPACING)
}

raw <- read.csv(source_path,stringsAsFactors=FALSE,check.names=FALSE)
raw$.row <- seq_len(nrow(raw)); raw$.date <- parse_date(raw$date); raw$.time <- parse_nocturnal_time(raw$time)
all_dates <- sort(unique(raw$.date[!is.na(raw$.date)]))
gap <- c(0,as.integer(diff(all_dates)))
bout_id <- cumsum(c(TRUE,gap[-1]>7))
date_to_bout <- setNames(bout_id,as.character(all_dates))

elig <- read.csv(eligible_path,stringsAsFactors=FALSE)
elig$session_id <- paste0(elig$grid,":bout",elig$bout_id)
if (nrow(elig)!=19L) stop("expected 19 eligible sessions")

d <- raw[
  clean(raw$species)=="PEMA" &
  nzchar(clean(raw$unique_ID)) &
  toupper(clean(raw$flag)) %in% flags &
  !is.na(raw$.date) & is.finite(raw$.time),
  ,drop=FALSE
]
d$.grid <- clean(d$grid); d$.flag <- toupper(clean(d$flag))
d$.bout <- unname(date_to_bout[as.character(d$.date)])
d$.session_id <- paste0(d$.grid,":bout",d$.bout)
d <- d[d$.session_id %in% elig$session_id,,drop=FALSE]
if (!nrow(d)) stop("no PEMA rows in eligible sessions")

groups <- split(seq_len(nrow(d)),paste(d$.session_id,clean(d$unique_ID),as.character(d$.date),sep="||"))
emp_rows <- lapply(groups,function(ii){
  z <- d[ii,,drop=FALSE]; z <- z[order(z$.time,z$.row),,drop=FALSE]
  a <- flag_xy(z$.flag[1]); b <- flag_xy(z$.flag[nrow(z)])
  data.frame(n=nrow(z),dx=b[1,"x"]-a[1,"x"],dy=b[1,"y"]-a[1,"y"])
})
emp <- do.call(rbind,emp_rows)
emp_rep <- emp[emp$n>=2,,drop=FALSE]
if (nrow(emp_rep)<20) stop("too few empirical repeat nights")
metric <- function(x) {
  dist <- sqrt(x$dx^2+x$dy^2)
  list(
    n=nrow(x),
    axis_rms_m=sqrt(mean(c(x$dx^2,x$dy^2))),
    radial_rms_m=sqrt(mean(dist^2)),
    median_distance_m=median(dist),
    changed_fraction=mean(dist>=SPACING-1e-10),
    fraction_ge_2_spacings=mean(dist>=2*SPACING-1e-10)
  )
}
observed <- metric(emp_rep)
observed$captured_individual_nights <- nrow(emp)
observed$repeat_fraction <- nrow(emp_rep)/nrow(emp)

sig <- read_json(sigma_json,simplifyVector=TRUE)
s_first <- as.numeric(sig$primary_model$first$sigma_m)
s_last <- as.numeric(sig$primary_model$last$sigma_m)
SIGMAS <- sort(unique(c(s_last,(s_last+s_first)/2,s_first)))
names(SIGMAS) <- NULL

tr <- make.grid(nx=7,ny=7,spacing=SPACING,detector="multi",ID="numy",leadingzero=FALSE)
trxy <- as.matrix(tr)[,1:2,drop=FALSE]; colnames(trxy)<-c("x","y")
core <- as.data.frame(trxy)

records_from_ch <- function(ch,check) {
  ids <- as.character(animalID(ch,names=TRUE))
  k <- as.integer(trap(ch,names=FALSE))
  if (!length(ids)) return(data.frame(ID=character(),check=integer(),trap=integer()))
  data.frame(ID=ids,check=rep.int(check,length(ids)),trap=k,stringsAsFactors=FALSE)
}

simulate_one <- function(sigma,g0,seed,target_n) {
  set.seed(seed)
  pop <- sim.popn(D=DENSITY,core=core,buffer=BUFFER,model2D="poisson",Ndist="poisson",seed=seed)
  pieces <- vector("list",CHECKS)
  for (cc in seq_len(CHECKS)) {
    ch <- sim.capthist(
      tr,popn=pop,detectfn="HN",detectpar=list(g0=g0,sigma=sigma),
      noccasions=1,renumber=FALSE,seed=seed+cc*1009L
    )
    pieces[[cc]] <- records_from_ch(ch,cc)
  }
  rec <- do.call(rbind,pieces)
  if (!nrow(rec)) return(NULL)
  gs <- split(rec,paste0(rec$ID))
  rows <- lapply(gs,function(z){
    z <- z[order(z$check),,drop=FALSE]
    if (nrow(z)<2) return(NULL)
    a <- trxy[z$trap[1],]; b <- trxy[z$trap[nrow(z)],]
    data.frame(dx=b["x"]-a["x"],dy=b["y"]-a["y"])
  })
  rows <- rows[!vapply(rows,is.null,logical(1))]
  if (!length(rows)) return(NULL)
  rr <- do.call(rbind,rows)
  if (nrow(rr)<target_n) return(NULL)
  rr <- rr[sample.int(nrow(rr),target_n,replace=FALSE),,drop=FALSE]
  m <- metric(rr)
  data.frame(
    axis_rms_m=m$axis_rms_m,
    radial_rms_m=m$radial_rms_m,
    median_distance_m=m$median_distance_m,
    changed_fraction=m$changed_fraction,
    fraction_ge_2_spacings=m$fraction_ge_2_spacings
  )
}

grid <- expand.grid(
  sigma=SIGMAS,g0=G0_VALUES,replicate=seq_len(nrepl),
  KEEP.OUT.ATTRS=FALSE,stringsAsFactors=FALSE
)
grid$seed <- base_seed + seq_len(nrow(grid))*7919L

run_task <- function(i) {
  z <- grid[i,,drop=FALSE]
  ans <- simulate_one(z$sigma,z$g0,z$seed,observed$n)
  if (is.null(ans)) {
    return(data.frame(sigma=z$sigma,g0=z$g0,replicate=z$replicate,success=FALSE,
      axis_rms_m=NA,radial_rms_m=NA,median_distance_m=NA,changed_fraction=NA,fraction_ge_2_spacings=NA))
  }
  cbind(data.frame(sigma=z$sigma,g0=z$g0,replicate=z$replicate,success=TRUE),ans)
}

if (.Platform$OS.type=="unix" && cores>1) {
  pieces <- parallel::mclapply(seq_len(nrow(grid)),run_task,mc.cores=cores,mc.preschedule=FALSE)
} else pieces <- lapply(seq_len(nrow(grid)),run_task)
res <- do.call(rbind,pieces)

summarize_cell <- function(z) {
  ok <- z[z$success,,drop=FALSE]
  qs <- function(v) as.numeric(quantile(v,c(.025,.5,.975),na.rm=TRUE,names=FALSE,type=8))
  a <- qs(ok$axis_rms_m); r <- qs(ok$radial_rms_m); cfr <- qs(ok$changed_fraction)
  data.frame(
    sigma=z$sigma[1],g0=z$g0[1],n=nrow(z),n_success=nrow(ok),
    axis_q025=a[1],axis_median=a[2],axis_q975=a[3],
    radial_q025=r[1],radial_median=r[2],radial_q975=r[3],
    changed_q025=cfr[1],changed_median=cfr[2],changed_q975=cfr[3],
    axis_upper_tail_p=mean(ok$axis_rms_m>=observed$axis_rms_m),
    changed_upper_tail_p=mean(ok$changed_fraction>=observed$changed_fraction),
    observed_axis_within_95=(observed$axis_rms_m>=a[1] && observed$axis_rms_m<=a[3]),
    observed_axis_exceeds_q975=(observed$axis_rms_m>a[3]),
    observed_changed_exceeds_q975=(observed$changed_fraction>cfr[3])
  )
}
key <- interaction(res$sigma,res$g0,drop=TRUE,lex.order=TRUE)
summ <- do.call(rbind,lapply(split(res,key),summarize_cell)); rownames(summ)<-NULL
primary_sigma <- mean(c(s_first,s_last))
primary_idx <- which.min(abs(summ$sigma-primary_sigma)+100*abs(summ$g0-0.15))
primary <- summ[primary_idx,,drop=FALSE]

out <- list(
  schema="neon.pema_stationary_displacement_null.v1",
  generated_at_utc=format(Sys.time(),tz="UTC",usetz=TRUE),
  status="post_result_stationary_scr_displacement_diagnostic",
  empirical_scope=list(
    species="PEMA",
    eligible_sessions=19,
    sigma_source="same frozen 19-session PEMA post-stop SCR fit",
    repeat_nights=observed$n
  ),
  observed=observed,
  sigma_anchors_m=list(first=s_first,last=s_last,midpoint=primary_sigma),
  design=list(
    trap_grid="7x7",
    spacing_m=SPACING,
    checks_per_night=CHECKS,
    detector="multi",
    detectfn="HN",
    density_per_ha=DENSITY,
    buffer_m=BUFFER,
    g0_sensitivity=G0_VALUES,
    nrepl_per_cell=nrepl,
    matched_repeat_nights_per_replicate=observed$n,
    state_process="fixed activity centre; independent stationary checks; no within-night state shift"
  ),
  cells=summ,
  primary_cell=primary,
  conclusion=list(
    observed_exceeds_primary_stationary_975=as.logical(primary$observed_axis_exceeds_q975[1]),
    observed_axis_within_primary_95=as.logical(primary$observed_axis_within_95[1]),
    observed_exceeds_any_stationary_975=as.logical(any(summ$observed_axis_exceeds_q975)),
    observed_exceeds_all_stationary_975=as.logical(all(summ$observed_axis_exceeds_q975)),
    interpretation="Tests whether empirical first-to-last displacement is unusually large relative to a fixed-centre stationary SCR observation process; it does not prove time-reversal symmetry or identify handling effects."
  ),
  package_versions=list(R=as.character(getRversion()),secr=as.character(packageVersion("secr")),jsonlite=as.character(packageVersion("jsonlite")))
)

dir.create(dirname(out_json),recursive=TRUE,showWarnings=FALSE)
dir.create(dirname(out_csv),recursive=TRUE,showWarnings=FALSE)
write_json(out,out_json,pretty=TRUE,auto_unbox=TRUE,na="null")
write.csv(res,out_csv,row.names=FALSE)
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,na="null"),"\n")
