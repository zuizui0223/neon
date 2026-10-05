#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(EcoSimR)
  library(jsonlite)
  library(digest)
})

args <- commandArgs(trailingOnly=TRUE)
arg_value <- function(flag, default=NULL) {
  i <- match(flag,args)
  if (is.na(i)) return(default)
  if (i==length(args)) stop(paste("missing value for",flag))
  args[[i+1]]
}

OUT <- arg_value("--output","results/san_jacinto_public_data_scale_decomposition_v1.json")
CACHE <- arg_value("--cache","/tmp/year_round_trap_data.csv")
NREPS <- as.integer(arg_value("--nreps","5000"))
BASE_SEED <- as.integer(arg_value("--seed","2026100504"))

URL <- "https://ndownloader.figshare.com/files/33058799"
SHA256 <- "ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
FOCAL <- c("CHFA","DKR","LAPM","PEER","PEMA","SKR")
SEASONS <- c("fall","winter","spring","summer")
FLAGS <- unlist(lapply(LETTERS[1:7], function(r) paste0(r,1:7)))
EXCLUDED <- c("3|winter","7|winter")

flag_xy <- function(flag) {
  c(match(substr(flag,1,1),LETTERS[1:7])-1L,
    as.integer(substr(flag,2,nchar(flag)))-1L)
}
d2 <- function(a,b) {
  aa<-flag_xy(a); bb<-flag_xy(b)
  sum((aa-bb)^2)
}
season_from_month <- function(m) {
  if (m %in% c(8,9,10)) return("fall")
  if (m %in% c(11,12,1)) return("winter")
  if (m %in% c(2,3,4)) return("spring")
  if (m %in% c(5,6,7)) return("summer")
  stop("bad month")
}
parse_time <- function(x) {
  x<-trimws(as.character(x))
  if (!grepl("^[0-9]{1,2}:[0-9]{2}$",x)) return(NA_real_)
  z<-strsplit(x,":",fixed=TRUE)[[1]]
  h<-as.integer(z[1]); minute<-as.integer(z[2])
  if (is.na(h)||is.na(minute)||minute>=60) return(NA_real_)
  if (h>=7 && h<=11) h<-h+12
  else if (h==12) h<-24
  else if (h>=0 && h<=6) h<-h+24
  else return(NA_real_)
  h+minute/60
}
parse_date <- function(x) {
  x<-trimws(as.character(x))
  for (fmt in c("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%m-%d-%Y","%m-%d-%y")) {
    d<-as.Date(x,format=fmt)
    if (!is.na(d)) return(d)
  }
  as.Date(NA)
}
seasonal_anchor <- function(flags) {
  tab<-table(flags); cand<-sort(unique(flags))
  ss<-vapply(cand,function(cc) sum(vapply(flags,function(ff)d2(cc,ff),numeric(1))),numeric(1))
  freq<-as.numeric(tab[cand])
  cand[order(ss,-freq,cand)[1]]
}
sha256sum <- function(path) {
  digest::digest(file=path, algo="sha256", serialize=FALSE)
}
download_source <- function() {
  dir.create(dirname(CACHE),recursive=TRUE,showWarnings=FALSE)
  download.file(URL,CACHE,mode="wb",quiet=TRUE)
  actual<-sha256sum(CACHE)
  if (!identical(actual,SHA256)) stop(paste("source checksum mismatch",actual))
  read.csv(CACHE,stringsAsFactors=FALSE,check.names=FALSE)
}

prepare_representations <- function(raw) {
  all_rows<-list(); ordered_rows<-list(); ka<-0L; ko<-0L
  for (i in seq_len(nrow(raw))) {
    sp<-toupper(trimws(as.character(raw$species[i])))
    grid<-trimws(as.character(raw$grid[i]))
    uid<-trimws(as.character(raw$unique_ID[i]))
    date_s<-trimws(as.character(raw$date[i]))
    flag<-toupper(trimws(as.character(raw$flag[i])))
    dd<-parse_date(date_s)
    if (!(sp %in% FOCAL) || !nzchar(grid) || !nzchar(date_s) ||
        !(flag %in% FLAGS) || is.na(dd)) next
    seas<-season_from_month(as.integer(format(dd,"%m")))
    ka<-ka+1L
    all_rows[[ka]]<-data.frame(
      row_index=i,species=sp,grid=grid,date=date_s,season=seas,flag=flag,
      stringsAsFactors=FALSE
    )
    tt<-parse_time(raw$time[i])
    if (!nzchar(uid) || !is.finite(tt)) next
    ko<-ko+1L
    ordered_rows[[ko]]<-data.frame(
      row_index=i,species=sp,grid=grid,uid=uid,date=date_s,season=seas,
      flag=flag,time=tt,stringsAsFactors=FALSE
    )
  }
  all<-do.call(rbind,all_rows)
  ordered<-do.call(rbind,ordered_rows)

  night_key<-paste(ordered$species,ordered$grid,ordered$uid,ordered$date,sep="|")
  spl<-split(seq_len(nrow(ordered)),night_key)
  first_idx<-vapply(spl,function(ii){
    z<-ordered[ii,,drop=FALSE]
    ii[order(z$time,z$row_index)[1]]
  },integer(1))
  night_first<-ordered[first_idx,,drop=FALSE]
  rownames(night_first)<-NULL

  ind_key<-paste(night_first$species,night_first$grid,night_first$season,night_first$uid,sep="|")
  isp<-split(seq_len(nrow(night_first)),ind_key)
  anchors<-vector("list",length(isp)); j<-0L
  for (ii in isp) {
    z<-night_first[ii,,drop=FALSE]; j<-j+1L
    anchors[[j]]<-data.frame(
      species=z$species[1],grid=z$grid[1],season=z$season[1],uid=z$uid[1],
      flag=seasonal_anchor(z$flag),nights=nrow(z),stringsAsFactors=FALSE
    )
  }
  anchor<-do.call(rbind,anchors)

  list(
    all=all[,c("species","grid","season","flag")],
    night_first=night_first[,c("species","grid","season","flag")],
    anchor=anchor[,c("species","grid","season","flag")],
    support=list(
      valid_spatial_capture_rows=nrow(all),
      valid_ordered_capture_rows=nrow(ordered),
      nightly_first_rows=nrow(night_first),
      individual_anchors=nrow(anchor),
      multi_night_individuals=sum(anchor$nights>=2)
    )
  )
}

build_matrix <- function(df,grid,seas) {
  z<-df[df$grid==grid & df$season==seas,,drop=FALSE]
  spp<-FOCAL[FOCAL %in% unique(z$species)]
  if (length(spp)<2) return(NULL)
  m<-matrix(0L,nrow=length(spp),ncol=length(FLAGS),dimnames=list(spp,FLAGS))
  if (nrow(z)) for(i in seq_len(nrow(z))) m[z$species[i],z$flag[i]]<-1L
  m<-m[rowSums(m)>0,colSums(m)>0,drop=FALSE]
  if(nrow(m)<2 || ncol(m)<1) return(NULL)
  m
}

community_c_score <- function(mat) {
  pairs <- combn(seq_len(nrow(mat)), 2)
  vals <- apply(pairs, 2, function(ii) {
    a <- mat[ii[1],]
    b <- mat[ii[2],]
    ra <- sum(a)
    rb <- sum(b)
    shared <- sum(a == 1 & b == 1)
    (ra - shared) * (rb - shared)
  })
  mean(vals)
}

has_fixed_fixed_switch <- function(mat) {
  if (nrow(mat) < 2 || ncol(mat) < 2) return(FALSE)
  for (i in seq_len(nrow(mat)-1L)) {
    for (j in (i+1L):nrow(mat)) {
      a_only <- any(mat[i,] == 1 & mat[j,] == 0)
      b_only <- any(mat[i,] == 0 & mat[j,] == 1)
      if (a_only && b_only) return(TRUE)
    }
  }
  FALSE
}

run_one <- function(mat,seed) {
  if (nrow(mat)<3) stop("Stage 4 fixed universe requires >=3 species per ALL unit")

  # A binary matrix with no switchable 2x2 checkerboard has a unique
  # realization under its fixed row and column margins (Ferrers/threshold
  # case). SIM9 therefore has a point-mass null distribution. Current
  # EcoSimR's recursive trade search can overflow on this exact edge case,
  # so return the mathematically equivalent degenerate fixed-fixed null.
  if (!has_fixed_fixed_switch(mat)) {
    obs <- community_c_score(mat)
    return(list(
      observed_c_score=obs,null_mean=obs,null_sd=0,
      ses=NULL,null_q025=obs,null_q975=obs,classification="null",
      row_totals=as.list(setNames(as.integer(rowSums(mat)),rownames(mat))),
      occupied_trap_columns=ncol(mat),
      column_richness_total=sum(colSums(mat)),seed=seed,
      degenerate_fixed_fixed_exact=TRUE
    ))
  }

  set.seed(seed)
  mod<-EcoSimR::cooc_null_model(
    as.data.frame(mat),algo="sim9",metric="c_score",
    nReps=NREPS,burn_in=500,suppressProg=TRUE
  )
  obs<-as.numeric(mod$Obs); sim<-as.numeric(mod$Sim)
  mu<-mean(sim); s<-sd(sim)
  q<-as.numeric(quantile(sim,c(.025,.975),names=FALSE,type=7))
  cls<-if(obs>q[2])"segregated" else if(obs<q[1])"aggregated" else "null"
  list(
    observed_c_score=obs,null_mean=mu,null_sd=s,
    ses=if(is.finite(s)&&s>0)(obs-mu)/s else NULL,
    null_q025=q[1],null_q975=q[2],classification=cls,
    row_totals=as.list(setNames(as.integer(rowSums(mat)),rownames(mat))),
    occupied_trap_columns=ncol(mat),
    column_richness_total=sum(colSums(mat)),seed=seed
  )
}

fixed_units <- function(all_df) {
  ids<-character()
  for(g in as.character(1:8)) for(seas in SEASONS) {
    id<-paste(g,seas,sep="|")
    m<-build_matrix(all_df,g,seas)
    if(!is.null(m) && nrow(m)>=3) ids<-c(ids,id)
  }
  ids
}

run_rep <- function(df,repr,offset,unit_ids) {
  out<-vector("list",length(unit_ids))
  for(i in seq_along(unit_ids)) {
    parts<-strsplit(unit_ids[i],"\\|")[[1]]
    g<-parts[1]; seas<-parts[2]
    m<-build_matrix(df,g,seas)
    if(is.null(m) || nrow(m)<3) {
      out[[i]]<-list(id=unit_ids[i],grid=g,season=seas,analyzable=FALSE,
                     reason="reduced_representation_has_fewer_than_3_species")
      next
    }
    sidx<-match(seas,SEASONS)
    seed<-BASE_SEED+offset*1000L+as.integer(g)*10L+sidx
    message(sprintf("%s %s: species=%d traps=%d switchable=%s",repr,unit_ids[i],nrow(m),ncol(m),has_fixed_fixed_switch(m)))
    rr<-run_one(m,seed)
    out[[i]]<-c(list(id=unit_ids[i],grid=g,season=seas,analyzable=TRUE,
                     species=rownames(m),species_count=nrow(m)),rr)
  }
  out
}

count_class <- function(x,cls) sum(vapply(x,function(z)isTRUE(z$analyzable)&&identical(z$classification,cls),logical(1)))
sig_ids <- function(x) vapply(x,function(z) if(isTRUE(z$analyzable)&&identical(z$classification,"segregated")) z$id else NA_character_,character(1))
sig_ids <- function(x) as.character(na.omit(sig_ids(x)))
ses_named <- function(x) {
  v<-vapply(x,function(z) if(!isTRUE(z$analyzable)||is.null(z$ses)) NA_real_ else as.numeric(z$ses),numeric(1))
  setNames(v,vapply(x,function(z)z$id,character(1)))
}
ses_summary <- function(x) {
  v<-unname(ses_named(x)); v<-v[is.finite(v)]
  list(mean=if(length(v))mean(v) else NULL,median=if(length(v))median(v) else NULL)
}
ses_cor <- function(a,b) {
  aa<-ses_named(a); bb<-ses_named(b); ids<-intersect(names(aa),names(bb))
  x<-aa[ids]; y<-bb[ids]; keep<-is.finite(x)&is.finite(y)
  if(sum(keep)<3 || sd(x[keep])==0 || sd(y[keep])==0) return(NULL)
  unname(cor(x[keep],y[keep]))
}
row_and_col_delta <- function(ref,reduced) {
  ids<-vapply(ref,function(z)z$id,character(1))
  out<-list()
  for(id in ids) {
    a<-ref[[match(id,ids)]]
    b<-reduced[[match(id,vapply(reduced,function(z)z$id,character(1)))]]
    out[[id]]<-list(
      reduced_analyzable=isTRUE(b$analyzable),
      all_species_count=a$species_count,
      reduced_species_count=if(isTRUE(b$analyzable))b$species_count else NULL,
      all_occupied_traps=a$occupied_trap_columns,
      reduced_occupied_traps=if(isTRUE(b$analyzable))b$occupied_trap_columns else NULL,
      all_row_totals=a$row_totals,
      reduced_row_totals=if(isTRUE(b$analyzable))b$row_totals else NULL
    )
  }
  out
}

if("--self-test" %in% args) {
  stopifnot(season_from_month(9)=="fall",season_from_month(12)=="winter",
            season_from_month(3)=="spring",season_from_month(6)=="summer")
  stopifnot(parse_time("8:00")==20,parse_time("1:00")==25)
  stopifnot(seasonal_anchor(c("A1","A1","A3"))=="A1")
  cat("self-test ok\n"); quit(status=0)
}

raw<-download_source()
rep<-prepare_representations(raw)
units<-fixed_units(rep$all)

# Stage-4 universe was frozen from support counts only.
if(length(units)!=30L) stop(paste("public-data supported universe changed:",length(units)))
if(!setequal(setdiff(as.vector(outer(as.character(1:8),SEASONS,paste,sep="|")),units),EXCLUDED)) {
  stop("excluded grid-seasons differ from frozen Stage-4 universe")
}

message("Stage 4A: verify 30-unit ALL reference")
all_res<-run_rep(rep$all,"all",0L,units)
all_ok<-sum(vapply(all_res,function(z)isTRUE(z$analyzable),logical(1)))==30L
all_seg<-count_class(all_res,"segregated")
all_agg<-count_class(all_res,"aggregated")
reference_pass<-all_ok && identical(all_seg,8L) && identical(all_agg,0L)

result<-list(
  schema="neon.san_jacinto_public_data_scale_decomposition.v1",
  status=if(reference_pass)"all_reference_passed_reduced_representations_opened" else "stop_all_reference_failed",
  frozen_design="docs/SAN_JACINTO_TRANSITION_NICHE_EXPLORATION_V1.md",
  source=list(figshare_doi="10.6084/m9.figshare.18295520.v1",file_id=33058799,sha256_verified=TRUE),
  software=list(R=R.version.string,EcoSimR=as.character(packageVersion("EcoSimR")),
                n_replicates=NREPS,burn_in=500,algorithm="sim9",metric="c_score"),
  support=rep$support,
  fixed_universe=list(
    eligible_grid_seasons=units,
    excluded_grid_seasons=EXCLUDED,
    eligibility="ALL-capture public-data matrix has >=3 focal species"
  ),
  all_reference=list(
    expected=list(analyzable=30,segregated=8,aggregated=0),
    observed=list(analyzable=sum(vapply(all_res,function(z)isTRUE(z$analyzable),logical(1))),
                  segregated=all_seg,aggregated=all_agg),
    passed=reference_pass,
    units=all_res
  ),
  claim_boundary=list(
    stage3_32_unit_reproduction_reclassified=FALSE,
    habitat_mechanism_identified=FALSE,
    competition_causally_identified=FALSE,
    species_pair_decomposition_opened=FALSE,
    alternative_retention_thresholds_tried=FALSE
  )
)

if(reference_pass) {
  message("Stage 4B: open NIGHT-FIRST and ANCHOR under same SIM9 null")
  first_res<-run_rep(rep$night_first,"night_first",1L,units)
  anchor_res<-run_rep(rep$anchor,"anchor",2L,units)

  sall<-sig_ids(all_res); sfirst<-sig_ids(first_res); sanchor<-sig_ids(anchor_res)
  if(length(sall)!=8L) stop("ALL reference significant set changed")
  f_n<-length(intersect(sall,sfirst)); a_n<-length(intersect(sall,sanchor))
  f_frac<-f_n/8; a_frac<-a_n/8
  scale_class<-if(a_n>=6L)"point_anchor_sufficient" else if(f_n>=6L)"between_night_footprint" else "within_night_records_materially_contribute"

  result$status<-"stage4_complete"
  result$night_first<-first_res
  result$anchor<-anchor_res
  result$primary<-list(
    all_reference_segregated_ids=sall,
    night_first_retained_ids=intersect(sall,sfirst),
    night_first_lost_ids=setdiff(sall,sfirst),
    anchor_retained_ids=intersect(sall,sanchor),
    anchor_lost_ids=setdiff(sall,sanchor),
    night_first_retained_n=f_n,
    night_first_retention_fraction=f_frac,
    anchor_retained_n=a_n,
    anchor_retention_fraction=a_frac,
    required_retention_n=6,
    classification=scale_class
  )
  result$secondary<-list(
    classification_counts=list(
      all=list(segregated=count_class(all_res,"segregated"),aggregated=count_class(all_res,"aggregated"),null=count_class(all_res,"null")),
      night_first=list(segregated=count_class(first_res,"segregated"),aggregated=count_class(first_res,"aggregated"),null=count_class(first_res,"null")),
      anchor=list(segregated=count_class(anchor_res,"segregated"),aggregated=count_class(anchor_res,"aggregated"),null=count_class(anchor_res,"null"))
    ),
    ses_summary=list(all=ses_summary(all_res),night_first=ses_summary(first_res),anchor=ses_summary(anchor_res)),
    ses_correlation=list(all_vs_night_first=ses_cor(all_res,first_res),all_vs_anchor=ses_cor(all_res,anchor_res)),
    newly_significant_outside_all=list(night_first=setdiff(sfirst,sall),anchor=setdiff(sanchor,sall)),
    support_changes=list(night_first=row_and_col_delta(all_res,first_res),anchor=row_and_col_delta(all_res,anchor_res)),
    claim_status="descriptive_only"
  )
}

dir.create(dirname(OUT),recursive=TRUE,showWarnings=FALSE)
writeLines(toJSON(result,pretty=TRUE,auto_unbox=TRUE,digits=10,na="null"),OUT)
cat(toJSON(result$all_reference[c("expected","observed","passed")],pretty=TRUE,auto_unbox=TRUE),"\n")
if(!is.null(result$primary)) cat(toJSON(result$primary,pretty=TRUE,auto_unbox=TRUE),"\n")
