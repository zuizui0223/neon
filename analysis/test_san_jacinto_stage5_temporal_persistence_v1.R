#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(EcoSimR)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
arg_value <- function(flag, default = NULL) {
  i <- match(flag, args)
  if (is.na(i)) return(default)
  if (i == length(args)) stop(paste("missing value for", flag))
  args[[i + 1]]
}

OUT <- arg_value("--output", "results/san_jacinto_stage5_temporal_persistence_v1.json")
CACHE <- arg_value("--cache", "/tmp/year_round_trap_data.csv")
NREPS <- as.integer(arg_value("--nreps", "5000"))
BURN <- as.integer(arg_value("--burn", "500"))
BASE_SEED <- as.integer(arg_value("--seed", "2026100505"))

URL <- "https://ndownloader.figshare.com/files/33058799"
SHA256 <- "ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
FOCAL <- c("CHFA","DKR","LAPM","PEER","PEMA","SKR")
FLAGS <- unlist(lapply(LETTERS[1:7], function(r) paste0(r,1:7)))
EXCLUDED <- c("3|winter","7|winter")
REFERENCE <- c(
  "1|summer",
  "4|fall","4|winter","4|spring","4|summer",
  "6|fall","6|winter","6|summer"
)

clean <- function(x) trimws(as.character(x))

parse_time <- function(x) {
  x <- clean(x)
  if (!grepl("^[0-9]{1,2}:[0-9]{2}$", x)) return(NA_real_)
  z <- strsplit(x, ":", fixed=TRUE)[[1]]
  h <- as.integer(z[1]); minute <- as.integer(z[2])
  if (is.na(h) || is.na(minute) || minute >= 60) return(NA_real_)
  if (h >= 7 && h <= 11) h <- h + 12
  else if (h == 12) h <- 24
  else if (h >= 0 && h <= 6) h <- h + 24
  else return(NA_real_)
  h + minute/60
}

parse_date <- function(x) {
  x <- clean(x)
  fmts <- c("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%m-%d-%Y","%m-%d-%y")
  for (fmt in fmts) {
    d <- as.Date(x, format=fmt)
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
  out <- system2("sha256sum", path, stdout=TRUE)
  sub(" .*", "", out[1])
}

download_source <- function() {
  dir.create(dirname(CACHE), recursive=TRUE, showWarnings=FALSE)
  download.file(URL, CACHE, mode="wb", quiet=TRUE)
  actual <- sha256sum(CACHE)
  if (!identical(actual, SHA256)) stop(paste("source checksum mismatch", actual))
  read.csv(CACHE, stringsAsFactors=FALSE, check.names=FALSE)
}

nightly_first_rows <- function(raw) {
  rows <- list()
  k <- 0L
  for (i in seq_len(nrow(raw))) {
    sp <- toupper(clean(raw$species[i]))
    grid <- clean(raw$grid[i])
    uid <- clean(raw$unique_ID[i])
    date_s <- clean(raw$date[i])
    flag <- toupper(clean(raw$flag[i]))
    tt <- parse_time(raw$time[i])
    dd <- parse_date(date_s)
    if (!(sp %in% FOCAL) || !nzchar(grid) || !nzchar(uid) ||
        !(flag %in% FLAGS) || !is.finite(tt) || is.na(dd)) next
    k <- k + 1L
    rows[[k]] <- data.frame(
      row_index=i, species=sp, grid=grid, uid=uid, date=date_s,
      date_obj=dd, season=season_from_month(as.integer(format(dd,"%m"))),
      flag=flag, time=tt, stringsAsFactors=FALSE
    )
  }
  x <- do.call(rbind, rows)
  key <- paste(x$species,x$grid,x$uid,x$date,sep="|")
  spl <- split(seq_len(nrow(x)), key)
  idx <- vapply(spl,function(ii) {
    z <- x[ii,,drop=FALSE]
    ii[order(z$time,z$row_index)[1]]
  },integer(1))
  y <- x[idx,,drop=FALSE]
  rownames(y) <- NULL
  y
}

split_unit_dates <- function(z) {
  dates <- sort(unique(z$date_obj))
  n <- length(dates)
  h <- floor(n/2)
  if (n %% 2 == 0) {
    early <- dates[seq_len(h)]
    late <- dates[(h+1):n]
    middle <- as.Date(NA)
  } else {
    early <- dates[seq_len(h)]
    late <- dates[(h+2):n]
    middle <- dates[h+1]
  }
  list(early=early,late=late,middle=middle)
}

build_half_matrix <- function(z, species, dates) {
  zz <- z[z$species %in% species & z$date_obj %in% dates,,drop=FALSE]
  m <- matrix(0L,nrow=length(species),ncol=length(FLAGS),
              dimnames=list(species,FLAGS))
  if (nrow(zz)) {
    for (i in seq_len(nrow(zz))) m[zz$species[i],zz$flag[i]] <- 1L
  }
  m
}

matched_overlap <- function(E,L) {
  stopifnot(identical(dim(E),dim(L)))
  sum((E>0) & (L>0))
}

prepare_unit <- function(nf, grid, season) {
  id <- paste(grid,season,sep="|")
  if (id %in% EXCLUDED) return(NULL)
  z <- nf[nf$grid==grid & nf$season==season,,drop=FALSE]
  if (!nrow(z)) return(NULL)
  spl <- split_unit_dates(z)

  ez <- z[z$date_obj %in% spl$early,,drop=FALSE]
  lz <- z[z$date_obj %in% spl$late,,drop=FALSE]
  common <- intersect(unique(ez$species),unique(lz$species))
  eligible <- FOCAL[FOCAL %in% common]
  eligible <- eligible[vapply(eligible,function(sp) {
    sum(ez$species==sp)>=2 && sum(lz$species==sp)>=2
  },logical(1))]
  if (length(eligible)<3) return(NULL)

  E <- build_half_matrix(z,eligible,spl$early)
  L <- build_half_matrix(z,eligible,spl$late)

  late_cols <- colSums(L)>0
  E <- E[,late_cols,drop=FALSE]
  L <- L[,late_cols,drop=FALSE]

  list(
    id=id,grid=grid,season=season,species=eligible,
    early_dates=as.character(spl$early),
    late_dates=as.character(spl$late),
    discarded_middle_date=if(is.na(spl$middle)) NULL else as.character(spl$middle),
    early_records=sum(ez$species %in% eligible),
    late_records=sum(lz$species %in% eligible),
    E=E,L=L
  )
}

run_null <- function(unit, seed) {
  E <- unit$E
  L <- unit$L
  obs <- matched_overlap(E,L)
  set.seed(seed)
  msim <- L
  for (i in seq_len(BURN)) msim <- EcoSimR::sim9_single(msim)
  sim <- numeric(NREPS)
  for (i in seq_len(NREPS)) {
    msim <- EcoSimR::sim9_single(msim)
    sim[i] <- matched_overlap(E,msim)
  }
  mu <- mean(sim)
  ss <- sd(sim)
  z <- if(is.finite(ss) && ss>0) (obs-mu)/ss else NA_real_
  p <- (1 + sum(sim >= obs)) / (NREPS + 1)
  list(
    observed_overlap=obs,
    null_mean=mu,
    null_sd=ss,
    z=if(is.finite(z)) z else NULL,
    p_upper=p,
    null=sim
  )
}

if ("--self-test" %in% args) {
  E <- matrix(c(1,0,1,0,1,0),nrow=2,byrow=TRUE)
  L <- matrix(c(1,1,0,0,1,0),nrow=2,byrow=TRUE)
  stopifnot(matched_overlap(E,L)==2)
  cat("self-test ok\n")
  quit(status=0)
}

raw <- download_source()
nf <- nightly_first_rows(raw)

units <- list()
kk <- 0L
for (g in as.character(1:8)) {
  for (sea in c("fall","winter","spring","summer")) {
    u <- prepare_unit(nf,g,sea)
    if (!is.null(u)) {
      kk <- kk+1L
      units[[kk]] <- u
    }
  }
}

unit_results <- list()
null_vectors <- list()
for (i in seq_along(units)) {
  u <- units[[i]]
  seed <- BASE_SEED + i
  message(sprintf("Stage5 persistence unit %s",u$id))
  rr <- run_null(u,seed)
  null_vectors[[u$id]] <- rr$null
  unit_results[[i]] <- list(
    id=u$id,grid=u$grid,season=u$season,
    stage4_reference=u$id %in% REFERENCE,
    species=u$species,species_count=length(u$species),
    early_nights=length(u$early_dates),
    late_nights=length(u$late_dates),
    discarded_middle_date=u$discarded_middle_date,
    early_records=u$early_records,late_records=u$late_records,
    early_row_totals=as.list(setNames(as.integer(rowSums(u$E)),u$species)),
    late_row_totals=as.list(setNames(as.integer(rowSums(u$L)),u$species)),
    late_occupied_traps=ncol(u$L),
    late_column_richness_total=sum(colSums(u$L)),
    observed_matched_species_trap_overlap=rr$observed_overlap,
    null_mean=rr$null_mean,
    null_sd=rr$null_sd,
    z=rr$z,
    p_upper=rr$p_upper,
    seed=seed
  )
}

primary_idx <- which(vapply(unit_results,function(x) isTRUE(x$stage4_reference),logical(1)))
primary <- unit_results[primary_idx]
if (length(primary)!=8) stop(paste("expected 8 reference units, got",length(primary)))

informative_ids <- vapply(primary,function(x) {
  if (!is.null(x$z) && is.finite(x$z)) x$id else NA_character_
},character(1))
informative_ids <- informative_ids[!is.na(informative_ids)]

if (length(informative_ids)) {
  zobs <- vapply(informative_ids,function(id) {
    unit_results[[which(vapply(unit_results,function(x) x$id==id,logical(1)))[1]]]$z
  },numeric(1))
  Tobs <- mean(zobs)

  mus <- setNames(vapply(informative_ids,function(id) {
    unit_results[[which(vapply(unit_results,function(x) x$id==id,logical(1)))[1]]]$null_mean
  },numeric(1)),informative_ids)
  sds <- setNames(vapply(informative_ids,function(id) {
    unit_results[[which(vapply(unit_results,function(x) x$id==id,logical(1)))[1]]]$null_sd
  },numeric(1)),informative_ids)

  Tnull <- numeric(NREPS)
  for (b in seq_len(NREPS)) {
    Tnull[b] <- mean(vapply(informative_ids,function(id) {
      (null_vectors[[id]][b]-mus[[id]])/sds[[id]]
    },numeric(1)))
  }
  pglobal <- (1+sum(Tnull>=Tobs))/(NREPS+1)
  null_global_mean <- mean(Tnull)
  null_global_sd <- sd(Tnull)
} else {
  Tobs <- pglobal <- null_global_mean <- null_global_sd <- NA_real_
}

positive_n <- sum(vapply(primary,function(x) !is.null(x$z) && is.finite(x$z) && x$z>0,logical(1)))
informative_n <- length(informative_ids)
supported <- informative_n>=6 && positive_n>=6 && is.finite(Tobs) && Tobs>0 && is.finite(pglobal) && pglobal<0.05

all_z <- vapply(unit_results,function(x) if(is.null(x$z)) NA_real_ else as.numeric(x$z),numeric(1))
ref_z <- all_z[vapply(unit_results,function(x) isTRUE(x$stage4_reference),logical(1))]
nonref_z <- all_z[!vapply(unit_results,function(x) isTRUE(x$stage4_reference),logical(1))]

result <- list(
  schema="neon.san_jacinto_stage5_temporal_persistence.v1",
  status="stage5_frozen_test_complete",
  frozen_design="docs/SAN_JACINTO_TRANSITION_NICHE_EXPLORATION_V1.md",
  source=list(figshare_doi="10.6084/m9.figshare.18295520.v1",file_id=33058799,sha256_verified=TRUE),
  software=list(R=R.version.string,EcoSimR=as.character(packageVersion("EcoSimR")),n_replicates=NREPS,burn_in=BURN),
  design=list(
    representation="NIGHT-FIRST only",
    split="chronological equal early/late halves of unique calendar nights; discard middle date if odd",
    species_eligibility="present in both halves and >=2 NIGHT-FIRST records in each half",
    statistic="sum of matched species x trap incidences recurring in EARLY and LATE",
    null="EARLY fixed; LATE randomized by EcoSimR sim9_single preserving LATE row and column totals",
    primary_units=REFERENCE
  ),
  primary=list(
    reference_units=8,
    informative_nonzero_null_sd=informative_n,
    positive_z_units=positive_n,
    global_mean_standardized_persistence=Tobs,
    null_global_mean=null_global_mean,
    null_global_sd=null_global_sd,
    one_sided_monte_carlo_p_upper=pglobal,
    required_informative_units=6,
    required_positive_units=6,
    alpha=0.05,
    decision=if(supported) "support_persistent_species_specific_multi_night_footprints" else "stop_persistent_footprint_claim"
  ),
  secondary=list(
    eligible_public_units=length(unit_results),
    positive_z_units=sum(is.finite(all_z) & all_z>0,na.rm=TRUE),
    mean_z=if(any(is.finite(all_z))) mean(all_z[is.finite(all_z)]) else NULL,
    median_z=if(any(is.finite(all_z))) median(all_z[is.finite(all_z)]) else NULL,
    reference_mean_z=if(any(is.finite(ref_z))) mean(ref_z[is.finite(ref_z)]) else NULL,
    nonreference_mean_z=if(any(is.finite(nonref_z))) mean(nonref_z[is.finite(nonref_z)]) else NULL,
    claim_status="descriptive_only"
  ),
  units=unit_results,
  claim_boundary=list(
    habitat_mechanism_identified=FALSE,
    competition_causally_identified=FALSE,
    individual_home_range_persistence_proven=FALSE,
    species_pair_decomposition_opened=FALSE,
    broader_22_unit_set_can_rescue_primary=FALSE
  )
)

dir.create(dirname(OUT),recursive=TRUE,showWarnings=FALSE)
writeLines(toJSON(result,pretty=TRUE,auto_unbox=TRUE,digits=10,na="null"),OUT)
cat(toJSON(result$primary,pretty=TRUE,auto_unbox=TRUE,digits=10,na="null"),"\n")
