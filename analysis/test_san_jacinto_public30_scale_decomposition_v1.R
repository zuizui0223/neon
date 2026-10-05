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

OUT <- arg_value("--output", "results/san_jacinto_public30_scale_decomposition_v1.json")
CACHE <- arg_value("--cache", "/tmp/year_round_trap_data.csv")
NREPS <- as.integer(arg_value("--nreps", "5000"))
BASE_SEED <- as.integer(arg_value("--seed", "2026100504"))

URL <- "https://ndownloader.figshare.com/files/33058799"
SHA256 <- "ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
FOCAL <- c("CHFA","DKR","LAPM","PEER","PEMA","SKR")
SEASONS <- c("fall","winter","spring","summer")
FLAGS <- unlist(lapply(LETTERS[1:7], function(r) paste0(r,1:7)))

flag_xy <- function(flag) {
  c(match(substr(flag,1,1), LETTERS[1:7])-1L, as.integer(substr(flag,2,nchar(flag)))-1L)
}

d2 <- function(a,b) {
  aa <- flag_xy(a); bb <- flag_xy(b)
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
  x <- trimws(as.character(x))
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
  x <- trimws(as.character(x))
  fmts <- c("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%m-%d-%Y","%m-%d-%y")
  for (fmt in fmts) {
    d <- as.Date(x, format=fmt)
    if (!is.na(d)) return(d)
  }
  as.Date(NA)
}

seasonal_anchor <- function(flags) {
  if (!length(flags)) stop("empty anchor input")
  tab <- table(flags)
  cand <- sort(unique(flags))
  ss <- vapply(cand, function(cc) sum(vapply(flags, function(ff) d2(cc,ff), numeric(1))), numeric(1))
  freq <- as.numeric(tab[cand])
  ord <- order(ss, -freq, cand)
  cand[ord[1]]
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

prepare_representations <- function(raw) {
  # The published ALL-capture spatial matrix needs only species, grid, date
  # (to assign season), and trap flag. It must NOT condition on individual ID
  # or check time; those fields are required only for NIGHT-FIRST / ANCHOR.
  all_rows <- list()
  ordered_rows <- list()
  ka <- 0L
  ko <- 0L

  for (i in seq_len(nrow(raw))) {
    sp <- toupper(trimws(as.character(raw$species[i])))
    grid <- trimws(as.character(raw$grid[i]))
    uid <- trimws(as.character(raw$unique_ID[i]))
    date_s <- trimws(as.character(raw$date[i]))
    flag <- toupper(trimws(as.character(raw$flag[i])))
    dd <- parse_date(date_s)

    if (!(sp %in% FOCAL) || !nzchar(grid) || !nzchar(date_s) ||
        !(flag %in% FLAGS) || is.na(dd)) next

    m <- as.integer(format(dd, "%m"))
    seas <- season_from_month(m)

    ka <- ka + 1L
    all_rows[[ka]] <- data.frame(
      row_index=i, species=sp, grid=grid, date=date_s,
      season=seas, flag=flag, stringsAsFactors=FALSE
    )

    tt <- parse_time(raw$time[i])
    if (!nzchar(uid) || !is.finite(tt)) next

    ko <- ko + 1L
    ordered_rows[[ko]] <- data.frame(
      row_index=i, species=sp, grid=grid, uid=uid, date=date_s,
      season=seas, flag=flag, time=tt, stringsAsFactors=FALSE
    )
  }

  all <- do.call(rbind, all_rows)
  ordered <- do.call(rbind, ordered_rows)
  if (is.null(all) || !nrow(all)) stop("no valid focal spatial rows")
  if (is.null(ordered) || !nrow(ordered)) stop("no valid focal ordered rows")

  night_key <- paste(ordered$species, ordered$grid, ordered$uid, ordered$date, sep="|")
  spl <- split(seq_len(nrow(ordered)), night_key)
  first_idx <- vapply(spl, function(ii) {
    zz <- ordered[ii,,drop=FALSE]
    ii[order(zz$time, zz$row_index)[1]]
  }, integer(1))
  night_first <- ordered[first_idx,,drop=FALSE]
  rownames(night_first) <- NULL

  ind_key <- paste(night_first$species, night_first$grid, night_first$season, night_first$uid, sep="|")
  isp <- split(seq_len(nrow(night_first)), ind_key)
  anchor_rows <- vector("list", length(isp))
  jj <- 0L
  for (ii in isp) {
    z <- night_first[ii,,drop=FALSE]
    jj <- jj + 1L
    anchor_rows[[jj]] <- data.frame(
      species=z$species[1], grid=z$grid[1], season=z$season[1],
      uid=z$uid[1], flag=seasonal_anchor(z$flag),
      nights=nrow(z), stringsAsFactors=FALSE
    )
  }
  anchor <- do.call(rbind, anchor_rows)

  list(
    all=all[,c("species","grid","season","flag")],
    night_first=night_first[,c("species","grid","season","flag")],
    anchor=anchor[,c("species","grid","season","flag")],
    counts=list(
      valid_spatial_capture_rows=nrow(all),
      valid_ordered_capture_rows=nrow(ordered),
      nightly_first_rows=nrow(night_first),
      individual_anchors=nrow(anchor),
      multi_night_individuals=sum(anchor$nights >= 2)
    )
  )
}

build_matrix <- function(df, grid, season) {
  z <- df[df$grid == grid & df$season == season,,drop=FALSE]
  species <- FOCAL[FOCAL %in% unique(z$species)]
  if (length(species) < 3) return(NULL)
  mat <- matrix(0L, nrow=length(species), ncol=length(FLAGS),
                dimnames=list(species, FLAGS))
  if (nrow(z)) {
    for (i in seq_len(nrow(z))) mat[z$species[i], z$flag[i]] <- 1L
  }
  mat <- mat[rowSums(mat)>0, colSums(mat)>0, drop=FALSE]
  if (nrow(mat) < 3 || ncol(mat) < 1) return(NULL)
  mat
}

run_one <- function(mat, seed) {
  set.seed(seed)
  model <- EcoSimR::cooc_null_model(
    as.data.frame(mat),
    algo="sim9", metric="c_score",
    nReps=NREPS, burn_in=500,
    suppressProg=TRUE
  )
  obs <- as.numeric(model$Obs)
  sim <- as.numeric(model$Sim)
  mu <- mean(sim)
  ss <- sd(sim)
  q <- as.numeric(quantile(sim, c(0.025,0.975), names=FALSE, type=7))
  cls <- if (obs > q[2]) "segregated" else if (obs < q[1]) "aggregated" else "null"
  list(
    observed_c_score=obs,
    null_mean=mu,
    null_sd=ss,
    ses=if (is.finite(ss) && ss > 0) (obs-mu)/ss else NULL,
    null_q025=q[1],
    null_q975=q[2],
    classification=cls,
    row_totals=as.list(setNames(as.integer(rowSums(mat)), rownames(mat))),
    occupied_trap_columns=ncol(mat),
    column_richness_total=sum(colSums(mat)),
    seed=seed
  )
}

run_representation <- function(df, repr_name, repr_offset) {
  out <- list()
  idx <- 0L
  for (g in as.character(1:8)) {
    for (sidx in seq_along(SEASONS)) {
      seas <- SEASONS[sidx]
      idx <- idx + 1L
      mat <- build_matrix(df, g, seas)
      id <- paste(g, seas, sep="|")
      if (is.null(mat)) {
        out[[idx]] <- list(id=id, grid=g, season=seas, analyzable=FALSE)
      } else {
        seed <- BASE_SEED + repr_offset*1000L + as.integer(g)*10L + sidx
        rr <- run_one(mat, seed)
        out[[idx]] <- c(list(
          id=id, grid=g, season=seas, analyzable=TRUE,
          species=rownames(mat), species_count=nrow(mat)
        ), rr)
      }
    }
  }
  out
}

count_class <- function(res, cls) {
  sum(vapply(res, function(x) isTRUE(x$analyzable) && identical(x$classification,cls), logical(1)))
}

analyzable_count <- function(res) sum(vapply(res, function(x) isTRUE(x$analyzable), logical(1)))

sig_set <- function(res) vapply(res, function(x) if (isTRUE(x$analyzable) && identical(x$classification,"segregated")) x$id else NA_character_, character(1))
sig_set <- function(res) na.omit(sig_set(res))

ses_named <- function(res) {
  vals <- vapply(res, function(x) {
    if (!isTRUE(x$analyzable) || is.null(x$ses)) return(NA_real_)
    as.numeric(x$ses)
  }, numeric(1))
  ids <- vapply(res, function(x) x$id, character(1))
  setNames(vals, ids)
}

summarise_ses <- function(res) {
  x <- unname(ses_named(res))
  x <- x[is.finite(x)]
  list(mean=if(length(x)) mean(x) else NULL,
       median=if(length(x)) median(x) else NULL)
}

paired_cor <- function(a,b) {
  aa <- ses_named(a); bb <- ses_named(b)
  ids <- intersect(names(aa),names(bb))
  x <- aa[ids]; y <- bb[ids]
  keep <- is.finite(x) & is.finite(y)
  if (sum(keep)<3 || sd(x[keep])==0 || sd(y[keep])==0) return(NULL)
  unname(cor(x[keep],y[keep],method="pearson"))
}

if ("--self-test" %in% args) {
  stopifnot(season_from_month(9)=="fall", season_from_month(12)=="winter",
            season_from_month(3)=="spring", season_from_month(6)=="summer")
  stopifnot(parse_time("8:00")==20, parse_time("10:30")==22.5, parse_time("1:00")==25)
  stopifnot(seasonal_anchor(c("A1","A1","A3"))=="A1")
  stopifnot(seasonal_anchor(c("A1","A3"))=="A1")
  cat("self-test ok\n")
  quit(status=0)
}

raw <- download_source()
rep <- prepare_representations(raw)

message("Stage 4A: verify the fixed 30-unit public-data ALL reference")
all_res <- run_representation(rep$all, "all", 0L)
all_n <- analyzable_count(all_res)
all_seg <- count_class(all_res, "segregated")
all_agg <- count_class(all_res, "aggregated")
reference_pass <- identical(all_n,30L) && identical(all_seg,8L) && identical(all_agg,0L)

result <- list(
  schema="neon.san_jacinto_public30_scale_decomposition.v1",
  status=if(reference_pass) "public30_reference_passed_scale_decomposition_opened" else "stop_public30_reference_failed",
  source=list(
    figshare_doi="10.6084/m9.figshare.18295520.v1",
    file_id=33058799,
    sha256_verified=TRUE
  ),
  frozen_design="docs/SAN_JACINTO_TRANSITION_NICHE_EXPLORATION_V1.md",
  software=list(
    R=R.version.string,
    EcoSimR=as.character(packageVersion("EcoSimR")),
    n_replicates=NREPS,
    burn_in=500,
    algorithm="sim9",
    metric="c_score"
  ),
  support=rep$counts,
  reproduction=list(
    expected=list(grid_seasons=32, segregated=8, aggregated=0),
    observed=list(analyzable=all_n, segregated=all_seg, aggregated=all_agg),
    passed=repro_pass
  ),
  all_capture=all_res,
  claim_boundary=list(
    species_pair_decomposition_opened=FALSE,
    habitat_mechanism_identified=FALSE,
    competition_causally_identified=FALSE,
    alternative_thresholds_tried=FALSE
  )
)

if (repro_pass) {
  message("Stage 3B: same SIM9 null on NIGHT-FIRST and ANCHOR representations")
  first_res <- run_representation(rep$night_first, "night_first", 1L)
  anchor_res <- run_representation(rep$anchor, "anchor", 2L)

  sall <- as.character(sig_set(all_res))
  sfirst <- as.character(sig_set(first_res))
  sanchor <- as.character(sig_set(anchor_res))

  first_ret_n <- length(intersect(sall,sfirst))
  anchor_ret_n <- length(intersect(sall,sanchor))
  first_ret <- first_ret_n/length(sall)
  anchor_ret <- anchor_ret_n/length(sall)

  classification <- if (anchor_ret >= 0.75) {
    "point_anchor_sufficient"
  } else if (first_ret >= 0.75) {
    "between_night_footprint"
  } else {
    "within_night_records_materially_contribute"
  }

  result$night_first <- first_res
  result$anchor <- anchor_res
    reduced_support_pass <- identical(analyzable_count(first_res),30L) && identical(analyzable_count(anchor_res),30L)
  if (!reduced_support_pass) {
    result$status <- "stop_reduced_representation_support_loss"
  }
  result$scale_decomposition <- list(
    reduced_support_pass=reduced_support_pass,
    night_first_analyzable=analyzable_count(first_res),
    anchor_analyzable=analyzable_count(anchor_res),
    all_segregated_ids=sall,
    night_first_segregated_ids=sfirst,
    anchor_segregated_ids=sanchor,
    night_first_retained_all_significant_n=first_ret_n,
    night_first_retention_fraction=first_ret,
    anchor_retained_all_significant_n=anchor_ret_n,
    anchor_retention_fraction=anchor_ret,
    threshold=0.75,
    classification=classification
  )
  result$secondary <- list(
    ses_summary=list(
      all=summarise_ses(all_res),
      night_first=summarise_ses(first_res),
      anchor=summarise_ses(anchor_res)
    ),
    ses_correlation=list(
      all_vs_night_first=paired_cor(all_res,first_res),
      all_vs_anchor=paired_cor(all_res,anchor_res)
    ),
    newly_significant_outside_all=list(
      night_first=setdiff(sfirst,sall),
      anchor=setdiff(sanchor,sall)
    ),
    claim_status="descriptive_only"
  )
}

dir.create(dirname(OUT), recursive=TRUE, showWarnings=FALSE)
writeLines(toJSON(result, pretty=TRUE, auto_unbox=TRUE, digits=10, na="null"), OUT)
cat(toJSON(result$reproduction, pretty=TRUE, auto_unbox=TRUE), "\n")
if (!is.null(result$scale_decomposition)) {
  cat(toJSON(result$scale_decomposition, pretty=TRUE, auto_unbox=TRUE), "\n")
}
