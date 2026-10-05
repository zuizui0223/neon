#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(EcoSimR)
  library(jsonlite)
})

args <- commandArgs(trailingOnly=TRUE)
arg_value <- function(flag, default=NULL) {
  i <- match(flag,args)
  if (is.na(i)) return(default)
  if (i==length(args)) stop(paste("missing value for",flag))
  args[[i+1]]
}

OUT <- arg_value("--output","results/san_jacinto_cross_season_turnover_v1.json")
CACHE <- arg_value("--cache","/tmp/year_round_trap_data.csv")
SUPPORT <- arg_value("--support","results/san_jacinto_cross_season_turnover_support_v1.json")
NREPS <- as.integer(arg_value("--nreps","10000"))
BURN <- as.integer(arg_value("--burn","500"))
BASE_SEED <- as.integer(arg_value("--seed","2026100509"))

URL <- "https://ndownloader.figshare.com/files/33058799"
SHA256 <- "ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
FOCAL <- c("CHFA","DKR","LAPM","PEER","PEMA","SKR")
FLAGS <- unlist(lapply(LETTERS[1:7],function(r)paste0(r,1:7)))

clean <- function(x) trimws(as.character(x))
parse_time <- function(x) {
  x <- clean(x)
  if (!grepl("^[0-9]{1,2}:[0-9]{2}$",x)) return(NA_real_)
  z <- strsplit(x,":",fixed=TRUE)[[1]]
  h <- as.integer(z[1]); minute <- as.integer(z[2])
  if (is.na(h)||is.na(minute)||minute>=60) return(NA_real_)
  if (h>=7 && h<=11) h <- h+12
  else if (h==12) h <- 24
  else if (h>=0 && h<=6) h <- h+24
  else return(NA_real_)
  h+minute/60
}
parse_date <- function(x) {
  x <- clean(x)
  fmts <- c("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%m-%d-%Y","%m-%d-%y")
  for (fmt in fmts) {
    d <- as.Date(x,format=fmt)
    if (!is.na(d)) return(d)
  }
  as.Date(NA)
}
season_from_month <- function(m) {
  if (m %in% c(8,9,10)) return("fall")
  if (m %in% c(11,12,1)) return("winter")
  if (m %in% c(2,3,4)) return("spring")
  if (m %in% c(5,6,7)) return("summer")
  stop("bad month")
}
sha256sum <- function(path) {
  out <- system2("sha256sum",path,stdout=TRUE)
  sub(" .*","",out[1])
}
download_source <- function() {
  dir.create(dirname(CACHE),recursive=TRUE,showWarnings=FALSE)
  download.file(URL,CACHE,mode="wb",quiet=TRUE)
  actual <- sha256sum(CACHE)
  if (!identical(actual,SHA256)) stop(paste("source checksum mismatch",actual))
  read.csv(CACHE,stringsAsFactors=FALSE,check.names=FALSE)
}
nightly_first_rows <- function(raw) {
  rows <- list(); k <- 0L
  for (i in seq_len(nrow(raw))) {
    sp <- toupper(clean(raw$species[i])); grid <- clean(raw$grid[i])
    uid <- clean(raw$unique_ID[i]); date_s <- clean(raw$date[i])
    flag <- toupper(clean(raw$flag[i])); tt <- parse_time(raw$time[i]); dd <- parse_date(date_s)
    if (!(sp %in% FOCAL)||!nzchar(grid)||!nzchar(uid)||!(flag %in% FLAGS)||!is.finite(tt)||is.na(dd)) next
    k <- k+1L
    rows[[k]] <- data.frame(
      row_index=i,species=sp,grid=grid,uid=uid,date=date_s,date_obj=dd,
      season=season_from_month(as.integer(format(dd,"%m"))),
      flag=flag,time=tt,stringsAsFactors=FALSE
    )
  }
  x <- do.call(rbind,rows)
  key <- paste(x$species,x$grid,x$uid,x$date,sep="|")
  spl <- split(seq_len(nrow(x)),key)
  idx <- vapply(spl,function(ii){
    z <- x[ii,,drop=FALSE]
    ii[order(z$time,z$row_index)[1]]
  },integer(1))
  y <- x[idx,,drop=FALSE]; rownames(y)<-NULL; y
}
matched_overlap <- function(A,B) {
  stopifnot(identical(dim(A),dim(B)))
  sum((A>0)&(B>0))
}
build_matrix <- function(z,species) {
  m <- matrix(0L,nrow=length(species),ncol=length(FLAGS),dimnames=list(species,FLAGS))
  zz <- z[z$species %in% species,,drop=FALSE]
  if (nrow(zz)) for (i in seq_len(nrow(zz))) m[zz$species[i],zz$flag[i]] <- 1L
  m
}
parse_unit_id <- function(id) {
  p <- strsplit(id,"|",fixed=TRUE)[[1]]
  ss <- strsplit(p[2],"->",fixed=TRUE)[[1]]
  list(grid=p[1],a=ss[1],b=ss[2])
}
prepare_unit <- function(nf,support_unit) {
  id <- support_unit$id
  p <- parse_unit_id(id)
  za0 <- nf[nf$grid==p$grid & nf$season==p$a,,drop=FALSE]
  zb0 <- nf[nf$grid==p$grid & nf$season==p$b,,drop=FALSE]
  akey <- unique(paste(za0$species,za0$uid,sep="|"))
  bkey <- unique(paste(zb0$species,zb0$uid,sep="|"))
  bridge <- intersect(akey,bkey)
  za <- za0[!(paste(za0$species,za0$uid,sep="|") %in% bridge),,drop=FALSE]
  zb <- zb0[!(paste(zb0$species,zb0$uid,sep="|") %in% bridge),,drop=FALSE]
  eligible <- FOCAL[vapply(FOCAL,function(sp){
    length(unique(za$uid[za$species==sp]))>=2 &&
      length(unique(zb$uid[zb$species==sp]))>=2
  },logical(1))]
  frozen <- unlist(support_unit$common_species_ge2_individuals_each,use.names=FALSE)
  if (!identical(sort(eligible),sort(frozen))) {
    stop(paste("support mismatch",id,paste(eligible,collapse=","),paste(frozen,collapse=",")))
  }
  if (length(eligible)<3) stop(paste("ineligible frozen unit",id))
  A <- build_matrix(za,eligible)
  B <- build_matrix(zb,eligible)
  active <- colSums(B)>0
  A <- A[,active,drop=FALSE]
  B <- B[,active,drop=FALSE]
  list(
    id=id,grid=p$grid,season_a=p$a,season_b=p$b,species=eligible,
    bridge_n=length(bridge),
    a_individuals=setNames(vapply(eligible,function(sp)length(unique(za$uid[za$species==sp])),integer(1)),eligible),
    b_individuals=setNames(vapply(eligible,function(sp)length(unique(zb$uid[zb$species==sp])),integer(1)),eligible),
    a_records=sum(za$species %in% eligible),b_records=sum(zb$species %in% eligible),
    A=A,B=B
  )
}
run_null <- function(unit,seed) {
  A <- unit$A; B <- unit$B
  obs <- matched_overlap(A,B)
  set.seed(seed)
  msim <- B
  for (i in seq_len(BURN)) msim <- EcoSimR::sim9_single(msim)
  sim <- numeric(NREPS)
  for (i in seq_len(NREPS)) {
    msim <- EcoSimR::sim9_single(msim)
    sim[i] <- matched_overlap(A,msim)
  }
  mu <- mean(sim); ss <- sd(sim)
  z <- if(is.finite(ss)&&ss>0)(obs-mu)/ss else NA_real_
  p <- (1+sum(sim>=obs))/(NREPS+1)
  list(obs=obs,mu=mu,sd=ss,z=z,p=p,null=sim)
}
exact_signflip <- function(grid_means) {
  g <- length(grid_means)
  if (!g) return(list(p=NA_real_,patterns=0L))
  obs <- mean(grid_means)
  patterns <- 2^g
  vals <- numeric(patterns)
  for (mask in 0:(patterns-1)) {
    signs <- ifelse(bitwAnd(mask,bitwShiftL(1L,0:(g-1)))>0,1,-1)
    vals[mask+1] <- mean(grid_means*signs)
  }
  list(p=sum(vals>=obs-1e-15)/patterns,patterns=patterns,null=vals)
}

if ("--self-test" %in% args) {
  A <- matrix(c(1,0,1,0,1,0),nrow=2,byrow=TRUE)
  B <- matrix(c(1,1,0,0,1,0),nrow=2,byrow=TRUE)
  stopifnot(matched_overlap(A,B)==2)
  sf <- exact_signflip(c(1,2,3))
  stopifnot(sf$patterns==8)
  cat("self-test ok\n")
  quit(status=0)
}

support <- fromJSON(SUPPORT,simplifyVector=FALSE)
support_units <- support$units
eligible_support <- support_units[vapply(support_units,function(u)length(unlist(u$common_species_ge2_individuals_each))>=3,logical(1))]
if (length(eligible_support)!=10) stop(paste("expected 10 frozen support units, got",length(eligible_support)))

raw <- download_source()
nf <- nightly_first_rows(raw)
units <- lapply(eligible_support,function(u)prepare_unit(nf,u))

unit_results <- list(); null_vectors <- list()
for (i in seq_along(units)) {
  u <- units[[i]]; seed <- BASE_SEED+i
  message(sprintf("Stage9 cross-season turnover unit %s",u$id))
  rr <- run_null(u,seed); null_vectors[[u$id]] <- rr$null
  unit_results[[i]] <- list(
    id=u$id,grid=u$grid,season_a=u$season_a,season_b=u$season_b,
    species=u$species,species_count=length(u$species),
    bridge_individuals_removed=u$bridge_n,
    season_a_exclusive_individuals_by_species=as.list(u$a_individuals),
    season_b_exclusive_individuals_by_species=as.list(u$b_individuals),
    season_a_records=u$a_records,season_b_records=u$b_records,
    observed_matched_species_trap_overlap=rr$obs,
    null_mean=rr$mu,null_sd=rr$sd,
    z=if(is.finite(rr$z))rr$z else NULL,
    p_upper=rr$p,seed=seed
  )
}

informative <- unit_results[vapply(unit_results,function(x)!is.null(x$z)&&is.finite(x$z),logical(1))]
informative_n <- length(informative)
positive_n <- sum(vapply(informative,function(x)x$z>0,logical(1)))

if (informative_n) {
  ids <- vapply(informative,function(x)x$id,character(1))
  zobs <- vapply(informative,function(x)x$z,numeric(1))
  mus <- setNames(vapply(informative,function(x)x$null_mean,numeric(1)),ids)
  sds <- setNames(vapply(informative,function(x)x$null_sd,numeric(1)),ids)
  Tobs <- mean(zobs)
  Tnull <- numeric(NREPS)
  for (b in seq_len(NREPS)) {
    Tnull[b] <- mean(vapply(ids,function(id)(null_vectors[[id]][b]-mus[[id]])/sds[[id]],numeric(1)))
  }
  pglobal <- (1+sum(Tnull>=Tobs))/(NREPS+1)
  ngm <- mean(Tnull); ngs <- sd(Tnull)
} else {
  Tobs <- pglobal <- ngm <- ngs <- NA_real_
}

grid_names <- sort(unique(vapply(informative,function(x)x$grid,character(1))))
grid_means <- setNames(vapply(grid_names,function(g){
  mean(vapply(informative[vapply(informative,function(x)x$grid==g,logical(1))],function(x)x$z,numeric(1)))
},numeric(1)),grid_names)
grid_positive <- sum(grid_means>0)
sf <- exact_signflip(grid_means)

unit_pass <- informative_n>=8 && positive_n>=7 && is.finite(Tobs)&&Tobs>0 && is.finite(pglobal)&&pglobal<0.05
grid_pass <- length(grid_means)==6 && grid_positive>=5 && is.finite(sf$p)&&sf$p<0.05
supported <- unit_pass && grid_pass

decision <- if (supported) {
  "support_cross_season_species_template_reassembly"
} else if (unit_pass && !grid_pass) {
  "unit_level_cross_season_signal_not_grid_robust"
} else {
  "stop_cross_season_template_reassembly_claim"
}

result <- list(
  schema="neon.san_jacinto_cross_season_turnover.v1",
  status="stage9_frozen_test_complete",
  frozen_design="docs/SAN_JACINTO_TRANSITION_NICHE_EXPLORATION_V1.md",
  support_artifact="results/san_jacinto_cross_season_turnover_support_v1.json",
  source=list(figshare_doi="10.6084/m9.figshare.18295520.v1",file_id=33058799,sha256_verified=TRUE),
  software=list(R=R.version.string,EcoSimR=as.character(packageVersion("EcoSimR")),n_replicates=NREPS,burn_in=BURN),
  design=list(
    representation="NIGHT-FIRST",
    season_pairs=c("fall->winter","winter->spring","spring->summer"),
    bridge_rule="remove from both seasons every species x individual observed in both seasons",
    species_eligibility=">=2 distinct season-A-exclusive and >=2 distinct season-B-exclusive individuals",
    unit_eligibility=">=3 eligible focal species",
    frozen_units=vapply(units,function(u)u$id,character(1)),
    statistic="matched species x trap recurrence across adjacent seasons with disjoint individuals",
    null="season A fixed; season B fixed-fixed curveball preserving season-B species occupancies and trap richness"
  ),
  primary=list(
    frozen_units=length(units),
    informative_nonzero_null_sd=informative_n,
    positive_z_units=positive_n,
    global_mean_standardized_cross_season_recurrence=if(is.finite(Tobs))Tobs else NULL,
    null_global_mean=if(is.finite(ngm))ngm else NULL,
    null_global_sd=if(is.finite(ngs))ngs else NULL,
    one_sided_monte_carlo_p_upper=if(is.finite(pglobal))pglobal else NULL,
    unit_level_criterion_pass=unit_pass,
    physical_grids=length(grid_means),
    grid_mean_z=as.list(grid_means),
    positive_grid_means=grid_positive,
    exact_grid_signflip_p_upper=if(is.finite(sf$p))sf$p else NULL,
    exact_grid_signflip_patterns=sf$patterns,
    physical_grid_criterion_pass=grid_pass,
    decision=decision
  ),
  units=unit_results,
  claim_boundary=list(
    habitat_mechanism_identified=FALSE,
    competition_causally_identified=FALSE,
    nonadjacent_seasons_opened=FALSE,
    species_pair_decomposition_opened=FALSE,
    one_individual_threshold_used=FALSE,
    alternative_overlap_metric_opened=FALSE
  )
)

dir.create(dirname(OUT),recursive=TRUE,showWarnings=FALSE)
writeLines(toJSON(result,pretty=TRUE,auto_unbox=TRUE,digits=10,na="null"),OUT)
cat(toJSON(result$primary,pretty=TRUE,auto_unbox=TRUE,digits=10,na="null"),"\n")
