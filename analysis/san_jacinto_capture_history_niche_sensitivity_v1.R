suppressPackageStartupMessages({
  library(EcoSimR)
  library(jsonlite)
})

args <- commandArgs(trailingOnly=TRUE)
input_csv <- args[[1]]
out_json <- args[[2]]
nreps_temporal <- if (length(args)>=3) as.integer(args[[3]]) else 5000L
nreps_spatial <- if (length(args)>=4) as.integer(args[[4]]) else 5000L
seed <- if (length(args)>=5) as.integer(args[[5]]) else 20261007L

SPECIES <- c("CHFA","PEMA","DKR","PEER","LAPM","SKR")
BINS <- c("early","middle","late")
FLAGS <- unlist(lapply(LETTERS[1:7],function(x)paste0(x,1:7)))

clean <- function(x) trimws(ifelse(is.na(x),"",as.character(x)))
up <- function(x) toupper(clean(x))

season_of <- function(x) {
  d <- as.Date(x,format="%m/%d/%y")
  m <- as.integer(format(d,"%m"))
  ifelse(m %in% c(8,9,10),"Fall",
  ifelse(m %in% c(11,12,1),"Winter",
  ifelse(m %in% c(2,3,4),"Spring","Summer")))
}

bin_rank <- function(x) match(tolower(clean(x)),BINS)

noct_time <- function(x) {
  z <- clean(x)
  m <- regexec("^(\\d{1,2}):(\\d{2})$",z)
  p <- regmatches(z,m)
  out <- rep(Inf,length(z))
  for(i in seq_along(p)){
    if(length(p[[i]])!=3) next
    h <- as.integer(p[[i]][2]); mm <- as.integer(p[[i]][3])
    if(h>=7 && h<=11) h<-h+12 else if(h==12) h<-24 else if(h>=0 && h<=6) h<-h+24 else next
    out[i]<-h+mm/60
  }
  out
}

identity_key <- function(d) {
  uid <- up(d$unique_ID)
  left <- up(d$left_tag); right <- up(d$right_tag); vie <- up(d$VIE)
  out <- rep("",nrow(d))
  i <- nzchar(uid)
  out[i] <- paste(up(d$species[i]),uid[i],sep="|")
  j <- !i & (nzchar(left)|nzchar(right))
  out[j] <- paste0(up(d$species[j]),"|TAG:",left[j],"/",right[j])
  k <- !i & !j & nzchar(vie)
  out[k] <- paste0(up(d$species[k]),"|VIE:",vie[k])
  out
}

raw <- read.csv(input_csv,stringsAsFactors=FALSE,check.names=FALSE)
raw$.row <- seq_len(nrow(raw))
raw$species <- up(raw$species)
raw$grid <- clean(raw$grid)
raw$flag <- up(raw$flag)
raw$time_bin <- tolower(clean(raw$time_bin))
raw$season <- season_of(raw$date)
raw$.bin_rank <- bin_rank(raw$time_bin)
raw$.time <- noct_time(raw$time)

d <- raw[
  raw$species %in% SPECIES &
  raw$flag %in% FLAGS &
  raw$time_bin %in% BINS &
  nzchar(raw$grid) &
  !is.na(raw$season),
  ,drop=FALSE
]

# Sensitivity representation: one capture per identifiable individual per grid-night,
# retaining the earliest observed check. Unidentifiable records are retained rather
# than guessed to be recaptures.
d$.id <- identity_key(d)
key <- ifelse(
  nzchar(d$.id),
  paste(d$grid,clean(d$date),d$.id,sep="||"),
  paste0("UNRESOLVED||",d$.row)
)
groups <- split(seq_len(nrow(d)),key)
keep <- vapply(groups,function(ii){
  z <- d[ii,,drop=FALSE]
  ii[order(z$.bin_rank,z$.time,z$.row)[1]]
},integer(1))
d_first <- d[sort(keep),,drop=FALSE]

cscore_obs <- function(mat) {
  spp <- rownames(mat)
  vals <- c()
  if(nrow(mat)<2) return(NA_real_)
  for(i in seq_len(nrow(mat)-1)) for(j in (i+1):nrow(mat)){
    A <- which(mat[i,]>0); B <- which(mat[j,]>0)
    S <- length(intersect(A,B))
    vals <- c(vals,(length(A)-S)*(length(B)-S))
  }
  mean(vals)
}

cz_obs <- function(mat) {
  p <- mat/rowSums(mat)
  vals <- c()
  if(nrow(p)<2) return(NA_real_)
  for(i in seq_len(nrow(p)-1)) for(j in (i+1):nrow(p)){
    vals <- c(vals,1-0.5*sum(abs(p[i,]-p[j,])))
  }
  mean(vals)
}

build_spatial <- function(z) {
  spp <- SPECIES[SPECIES %in% z$species]
  m <- matrix(0L,nrow=length(spp),ncol=length(FLAGS),dimnames=list(spp,FLAGS))
  for(i in seq_len(nrow(z))) m[z$species[i],z$flag[i]] <- 1L
  # EcoSimR sim9 does not need empty columns; remove only if present.
  m[,colSums(m)>0,drop=FALSE]
}

build_temporal <- function(z) {
  spp <- SPECIES[SPECIES %in% z$species]
  m <- matrix(0L,nrow=length(spp),ncol=3,dimnames=list(spp,BINS))
  for(i in seq_len(nrow(z))) m[z$species[i],z$time_bin[i]] <- m[z$species[i],z$time_bin[i]] + 1L
  m
}

run_null <- function(mat,type,nreps,local_seed) {
  set.seed(local_seed)
  if(type=="spatial"){
    obs <- cscore_obs(mat)
    fit <- cooc_null_model(
      as.data.frame(mat),algo="sim9",metric="c_score",
      nReps=nreps,burn_in=500,suppressProg=TRUE
    )
  } else {
    obs <- cz_obs(mat)
    fit <- niche_null_model(
      as.data.frame(mat),algo="ra3",metric="czekanowski",
      nReps=nreps,suppressProg=TRUE
    )
  }
  sim <- as.numeric(fit$Sim)
  q <- as.numeric(quantile(sim,c(.025,.975),names=FALSE,type=8))
  ses <- (obs-mean(sim))/sd(sim)
  status <- if(obs>q[2]) {
    if(type=="spatial") "segregated" else "aggregated"
  } else if(obs<q[1]) {
    if(type=="spatial") "aggregated" else "segregated"
  } else "null"
  list(
    observed=obs,
    null_mean=mean(sim),
    null_sd=sd(sim),
    q025=q[1],q975=q[2],
    ses=ses,
    status=status,
    p_lower=mean(sim<=obs),
    p_upper=mean(sim>=obs),
    nreps=length(sim)
  )
}

units <- expand.grid(
  grid=sort(unique(d$grid)),
  season=c("Fall","Winter","Spring","Summer"),
  stringsAsFactors=FALSE
)

results <- list()
for(ii in seq_len(nrow(units))){
  g <- units$grid[ii]; s <- units$season[ii]
  a <- d[d$grid==g & d$season==s,,drop=FALSE]
  b <- d_first[d_first$grid==g & d_first$season==s,,drop=FALSE]
  if(!nrow(a)||!nrow(b)) next
  spa <- build_spatial(a); spb <- build_spatial(b)
  tea <- build_temporal(a); teb <- build_temporal(b)
  # Deterministic seeds by lane/unit.
  ss <- seed + ii*10000L
  results[[paste(g,s,sep="|")]] <- list(
    grid=g,season=s,
    captures_all=nrow(a),captures_first_only=nrow(b),
    species_all=rownames(spa),species_first_only=rownames(spb),
    spatial=list(
      all=run_null(spa,"spatial",nreps_spatial,ss+1L),
      first_only=run_null(spb,"spatial",nreps_spatial,ss+2L)
    ),
    temporal=list(
      all=run_null(tea,"temporal",nreps_temporal,ss+3L),
      first_only=run_null(teb,"temporal",nreps_temporal,ss+4L)
    )
  )
}

summarize_status <- function(axis,lane) {
  x <- vapply(results,function(z)z[[axis]][[lane]]$status,character(1))
  as.list(table(factor(x,levels=c("segregated","aggregated","null"))))
}

changed <- function(axis) {
  sum(vapply(results,function(z)z[[axis]]$all$status != z[[axis]]$first_only$status,logical(1)))
}

delta_ses <- function(axis) {
  x <- vapply(results,function(z)z[[axis]]$first_only$ses-z[[axis]]$all$ses,numeric(1))
  list(
    mean=mean(x),median=median(x),
    q025=as.numeric(quantile(x,.025,type=8)),
    q975=as.numeric(quantile(x,.975,type=8)),
    min=min(x),max=max(x)
  )
}

out <- list(
  schema="neon.san_jacinto_capture_history_niche_sensitivity.v1",
  status="post_result_ecological_sensitivity_not_causal_decontamination",
  source_sha256_expected="ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301",
  design=list(
    focal_species=SPECIES,
    original_spatial_null="EcoSimR sim9 + c_score",
    original_temporal_null="EcoSimR ra3 + czekanowski",
    spatial_nreps=nreps_spatial,
    temporal_nreps=nreps_temporal,
    first_only_rule="retain earliest capture per identifiable individual x grid x night; unresolved identities retained",
    purpose="measure propagation of within-night recapture history into published community-level niche indices"
  ),
  support=list(
    capture_rows_main_six=nrow(d),
    first_only_rows=nrow(d_first),
    rows_removed=nrow(d)-nrow(d_first),
    fraction_removed=(nrow(d)-nrow(d_first))/nrow(d),
    grid_seasons=length(results)
  ),
  reproduction=list(
    published_spatial_segregated_grid_seasons=8,
    published_temporal_aggregated_grid_seasons=7,
    all_capture_spatial_status_counts=summarize_status("spatial","all"),
    all_capture_temporal_status_counts=summarize_status("temporal","all")
  ),
  sensitivity=list(
    first_only_spatial_status_counts=summarize_status("spatial","first_only"),
    first_only_temporal_status_counts=summarize_status("temporal","first_only"),
    spatial_classification_changes=changed("spatial"),
    temporal_classification_changes=changed("temporal"),
    spatial_delta_ses=delta_ses("spatial"),
    temporal_delta_ses=delta_ses("temporal")
  ),
  units=results,
  claim_boundary=list(
    causal_measurement_effect_identified=FALSE,
    first_only_is_unmanipulated_behavior=FALSE,
    original_analysis_invalidated=FALSE,
    interpretation="This sensitivity asks whether within-night recapture history propagates into community niche indices. Removing later within-night captures changes the representation and sample size; it is not a causal correction for trapping."
  ),
  package_versions=list(
    R=as.character(getRversion()),
    EcoSimR=as.character(packageVersion("EcoSimR")),
    jsonlite=as.character(packageVersion("jsonlite"))
  )
)

dir.create(dirname(out_json),recursive=TRUE,showWarnings=FALSE)
write_json(out,out_json,pretty=TRUE,auto_unbox=TRUE,na="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,na="null"),"\n")
