#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(secr)
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
out <- arg_value("--output","results/pema_scr_sigma_post_stop_exploratory_v1.json")
elig_path <- arg_value("--eligible","validation/san_jacinto_scr_sigma_v1/eligible_sessions_v1.csv")
cache <- arg_value("--cache","data/cache/san_jacinto/year_round_trap_data.csv")

url <- "https://ndownloader.figshare.com/files/33058799"
sha_expected <- "ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
flags <- as.vector(outer(LETTERS[1:7],1:7,paste0))

parse_date <- function(x) {
  out <- rep(as.Date(NA), length(x))
  for (i in seq_along(x)) {
    txt <- trimws(as.character(x[i]))
    sep <- if (grepl("/",txt,fixed=TRUE)) "/" else if (grepl("-",txt,fixed=TRUE)) "-" else NA_character_
    if (is.na(sep)) next
    p <- strsplit(txt,sep,fixed=TRUE)[[1]]
    if (length(p)!=3) next
    v <- suppressWarnings(as.integer(as.numeric(p)))
    if (any(is.na(v))) next
    if (v[1] > 1900) {
      yy <- v[1]; mm <- v[2]; dd <- v[3]
    } else {
      mm <- v[1]; dd <- v[2]; yy <- v[3]
      if (yy < 100) yy <- yy + 2000
    }
    out[i] <- as.Date(sprintf("%04d-%02d-%02d",yy,mm,dd))
  }
  out
}
parse_time <- function(x) {
  m <- regexec("^(\\d{1,2}):(\\d{2})$",trimws(as.character(x)))
  p <- regmatches(trimws(as.character(x)),m)
  ans <- rep(NA_real_,length(x))
  for (i in seq_along(p)) {
    if (length(p[[i]])!=3) next
    h <- as.integer(p[[i]][2]); mm <- as.integer(p[[i]][3])
    if (is.na(h)||is.na(mm)||mm>=60) next
    if (h>=7 && h<=11) h <- h+12
    else if (h==12) h <- 24
    else if (h>=0 && h<=6) h <- h+24
    else next
    ans[i] <- h + mm/60
  }
  ans
}

dir.create(dirname(cache),recursive=TRUE,showWarnings=FALSE)
if (!file.exists(cache)) {
  download.file(url,cache,mode="wb",quiet=TRUE)
}
sha_actual <- digest(cache,algo="sha256",file=TRUE,serialize=FALSE)
if (!identical(sha_actual,sha_expected)) stop(paste("checksum mismatch",sha_actual))

raw <- read.csv(cache,stringsAsFactors=FALSE,check.names=FALSE)
elig <- read.csv(elig_path,stringsAsFactors=FALSE,check.names=FALSE)
elig <- elig[elig$species=="PEMA" & as.logical(elig$eligible),,drop=FALSE]
if (nrow(elig)!=19) stop(paste("expected 19 eligible PEMA sessions; got",nrow(elig)))

# Build exact session-date map from the frozen support table.
session_meta <- list()
for (i in seq_len(nrow(elig))) {
  sid <- paste0("g",elig$grid[i],"_b",elig$bout_id[i])
  dates <- strsplit(elig$dates[i],";",fixed=TRUE)[[1]]
  session_meta[[sid]] <- list(
    grid=as.character(elig$grid[i]),
    bout=as.integer(elig$bout_id[i]),
    dates=dates
  )
}

# Prepare raw valid PEMA detections.
raw$.row <- seq_len(nrow(raw))
raw$.date <- format(parse_date(raw$date),"%Y-%m-%d")
raw$.time <- parse_time(raw$time)
raw$flag <- toupper(trimws(as.character(raw$flag)))
raw$unique_ID <- trimws(as.character(raw$unique_ID))
raw$grid <- trimws(as.character(raw$grid))
valid <- raw[
  trimws(as.character(raw$species))=="PEMA" &
  nzchar(raw$unique_ID) &
  raw$flag %in% flags &
  !is.na(raw$.date) &
  !is.na(raw$.time),
  ,drop=FALSE
]

make_traps <- function() {
  tr <- make.grid(nx=7,ny=7,spacing=6.25,detector="multi",origin=c(0,0))
  rownames(tr) <- flags
  tr
}

build_session <- function(sid,which=c("first","last")) {
  which <- match.arg(which)
  sm <- session_meta[[sid]]
  z <- valid[valid$grid==sm$grid & valid$.date %in% sm$dates,,drop=FALSE]
  if (!nrow(z)) stop(paste("no rows for",sid))
  # Occasion numbering follows the frozen chronological dates for this session.
  dates <- sort(unique(sm$dates))
  z$.occ <- match(z$.date,dates)
  key <- paste(z$unique_ID,z$.date,sep="::")
  split_idx <- split(seq_len(nrow(z)),key)
  pick <- vapply(split_idx,function(ii) {
    zz <- z[ii,,drop=FALSE]
    ord <- order(zz$.time,zz$.row)
    if (which=="first") ii[ord[1]] else ii[ord[length(ord)]]
  },integer(1))
  y <- z[unname(pick),,drop=FALSE]
  cap <- data.frame(
    Session=1,
    ID=y$unique_ID,
    Occasion=as.integer(y$.occ),
    TrapID=y$flag,
    stringsAsFactors=FALSE
  )
  ch <- make.capthist(
    captures=cap,
    traps=make_traps(),
    fmt="trapID",
    noccasions=length(dates),
    bysession=TRUE
  )
  session(ch) <- sid
  ch
}

sids <- names(session_meta)
first_list <- lapply(sids,build_session,which="first")
last_list <- lapply(sids,build_session,which="last")
names(first_list) <- names(last_list) <- sids

# Strict structural equality gate before opening fits.
for (i in seq_along(sids)) {
  a <- as.data.frame(first_list[[i]],fmt="trapID")
  b <- as.data.frame(last_list[[i]],fmt="trapID")
  ka <- sort(paste(a[,2],a[,3],sep="::"))
  kb <- sort(paste(b[,2],b[,3],sep="::"))
  if (!identical(ka,kb)) stop(paste("FIRST/LAST support differs in",sids[i]))
}

first_ms <- do.call(MS.capthist,first_list)
last_ms <- do.call(MS.capthist,last_list)
masks <- lapply(first_list,function(ch) make.mask(traps(ch),buffer=100,spacing=5))
sessioncov <- data.frame(
  grid=factor(vapply(session_meta,function(x)x$grid,character(1))),
  bout=factor(vapply(session_meta,function(x)as.character(x$bout),character(1))),
  row.names=sids
)

extract_sigma <- function(fit) {
  p <- predict(fit)
  frames <- if (is.data.frame(p)) list(p) else p
  vals <- list()
  for (x in frames) {
    if (!is.data.frame(x) || !("sigma" %in% rownames(x))) next
    vals[[length(vals)+1L]] <- x["sigma",,drop=FALSE]
  }
  if (!length(vals)) stop("sigma not found in prediction")
  est <- vapply(vals,function(x)as.numeric(x[1,"estimate"]),numeric(1))
  lcl_name <- intersect(c("lcl","lower","lower.CL"),colnames(vals[[1]]))
  ucl_name <- intersect(c("ucl","upper","upper.CL"),colnames(vals[[1]]))
  lcl <- if(length(lcl_name)) vapply(vals,function(x)as.numeric(x[1,lcl_name[1]]),numeric(1)) else rep(NA_real_,length(vals))
  ucl <- if(length(ucl_name)) vapply(vals,function(x)as.numeric(x[1,ucl_name[1]]),numeric(1)) else rep(NA_real_,length(vals))
  if (max(est)-min(est) > 1e-6*max(1,mean(est))) {
    stop("sigma unexpectedly varies among sessions")
  }
  list(estimate=mean(est),lcl=mean(lcl),ucl=mean(ucl))
}

fit_one <- function(ch,model,use_sessioncov=TRUE) {
  stack <- character()
  tryCatch({
    fit <- withCallingHandlers(
      secr.fit(
        ch,
        mask=masks,
        CL=TRUE,
        detectfn="HN",
        model=model,
        sessioncov=if (use_sessioncov) sessioncov else NULL,
        trace=FALSE,
        ncores=2
      ),
      error=function(e) {
        stack <<- vapply(sys.calls(), function(x) paste(deparse(x),collapse=" "), character(1))
      }
    )
    list(
      ok=TRUE,
      sigma=extract_sigma(fit),
      logLik=as.numeric(logLik(fit)),
      AIC=as.numeric(AIC(fit))
    )
  },error=function(e) list(
    ok=FALSE,
    error=conditionMessage(e),
    call_stack=stack
  ))
}

primary_model <- list(g0~b+grid+bout,sigma~1)
sensitivity_model <- list(g0~grid+bout,sigma~1)
null_model <- list(g0~1,sigma~1)

first_null <- fit_one(first_ms,null_model,use_sessioncov=FALSE)
last_null <- fit_one(last_ms,null_model,use_sessioncov=FALSE)
first_primary <- fit_one(first_ms,primary_model)
last_primary <- fit_one(last_ms,primary_model)
first_sens <- fit_one(first_ms,sensitivity_model)
last_sens <- fit_one(last_ms,sensitivity_model)

contrast <- function(a,b) {
  if (!isTRUE(a$ok) || !isTRUE(b$ok)) return(NULL)
  sf <- a$sigma$estimate; sl <- b$sigma$estimate
  list(
    sigma_first=sf,
    sigma_last=sl,
    sigma_ratio_last_over_first=sl/sf,
    relative_change=sl/sf-1,
    absolute_relative_change=abs(sl/sf-1),
    contextual_10pct_threshold_exceeded=abs(sl/sf-1)>=0.10
  )
}

result <- list(
  schema="neon.pema_scr_sigma.post_stop_exploratory.v1",
  status="post_stop_exploratory_only",
  binding_confirmatory_programme_decision="stop_scr_sigma_sensitivity_not_estimable",
  source_sha256=sha_actual,
  eligible_sessions=length(sids),
  eligible_session_ids=sids,
  eligible_grids=sort(unique(vapply(session_meta,function(x)x$grid,character(1)))),
  structure=list(
    first_class=class(first_ms),
    last_class=class(last_ms),
    first_session_names=as.character(session(first_ms)),
    last_session_names=as.character(session(last_ms)),
    first_session_count=length(first_ms),
    last_session_count=length(last_ms),
    mask_count=length(masks),
    mask_names=names(masks),
    sessioncov_rows=nrow(sessioncov),
    sessioncov_rownames=rownames(sessioncov),
    sessioncov_grid=as.character(sessioncov$grid),
    sessioncov_bout=as.character(sessioncov$bout)
  ),
  null_structure_check=list(
    model="g0 ~ 1; sigma ~ 1",
    first=first_null,
    last=last_null
  ),
  primary=list(
    model="g0 ~ b + grid + bout; sigma ~ 1",
    first=first_primary,
    last=last_primary,
    contrast=contrast(first_primary,last_primary)
  ),
  sensitivity_without_b=list(
    model="g0 ~ grid + bout; sigma ~ 1",
    first=first_sens,
    last=last_sens,
    contrast=contrast(first_sens,last_sens)
  ),
  guardrails=list(
    peER_fitted=FALSE,
    original_two_species_stop_relaxed=FALSE,
    result_confirmatory=FALSE
  )
)

dir.create(dirname(out),recursive=TRUE,showWarnings=FALSE)
write_json(result,out,pretty=TRUE,auto_unbox=TRUE,digits=10)
print(result)
