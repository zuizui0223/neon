suppressPackageStartupMessages({
  library(secr)
  library(jsonlite)
})

# Post-stop exploratory analysis. The earlier two-species confirmatory SCR gate
# remains stopped and is not modified by this script.
# AI assistance disclosure: drafted with OpenAI ChatGPT (GPT-5.6 Sol,
# October 2026); author remains responsible for verification and interpretation.

args <- commandArgs(trailingOnly = TRUE)
input_csv <- args[[1]]
support_json <- args[[2]]
out_json <- args[[3]]

spacing <- 6.25
buffer_m <- 100
mask_spacing_m <- 5

clean <- function(x) trimws(ifelse(is.na(x), "", as.character(x)))

parse_date <- function(x) {
  x <- clean(x)
  out <- as.Date(rep(NA_character_, length(x)))
  fmts <- c("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y")
  for (fmt in fmts) {
    miss <- is.na(out)
    if (!any(miss)) break
    suppressWarnings(out[miss] <- as.Date(x[miss], format = fmt))
  }
  out
}

parse_nocturnal_time <- function(x) {
  x <- clean(x)
  m <- regexec("^(\\d{1,2}):(\\d{2})$", x)
  p <- regmatches(x, m)
  out <- rep(NA_real_, length(x))
  for (i in seq_along(p)) {
    if (length(p[[i]]) != 3) next
    h <- as.integer(p[[i]][2]); minute <- as.integer(p[[i]][3])
    if (is.na(h) || is.na(minute) || minute >= 60) next
    if (h >= 7 && h <= 11) h <- h + 12
    else if (h == 12) h <- 24
    else if (h >= 0 && h <= 6) h <- h + 24
    else next
    out[i] <- h + minute / 60
  }
  out
}

raw <- read.csv(input_csv, stringsAsFactors = FALSE, check.names = FALSE)
raw$.row_index <- seq_len(nrow(raw))
raw$.date <- parse_date(raw$date)

all_dates <- sort(unique(raw$.date[!is.na(raw$.date)]))
if (length(all_dates) == 0) stop("no valid dates")
gap <- c(0, as.integer(diff(all_dates)))
bout_id <- cumsum(c(TRUE, gap[-1] > 7))
date_to_bout <- setNames(bout_id, as.character(all_dates))

flags <- unlist(lapply(LETTERS[1:7], function(z) paste0(z, 1:7)))
flag_to_trap <- setNames(seq_along(flags), flags)

d <- raw[
  clean(raw$species) == "PEMA" &
  nzchar(clean(raw$unique_ID)) &
  clean(raw$flag) %in% flags &
  !is.na(raw$.date),
  , drop = FALSE
]
d$.time <- parse_nocturnal_time(d$time)
d <- d[!is.na(d$.time), , drop = FALSE]
d$.grid <- clean(d$grid)
d$.flag <- clean(d$flag)
d$.bout <- unname(date_to_bout[as.character(d$.date)])
d$.session_id <- paste0(d$.grid, ":bout", d$.bout)

support <- read_json(support_json, simplifyVector = TRUE)
eligible <- support$species$PEMA$eligible_session_ids
if (length(eligible) != 19L) {
  stop("expected 19 frozen PEMA eligible sessions, found ", length(eligible))
}
d <- d[d$.session_id %in% eligible, , drop = FALSE]
if (nrow(d) == 0L) stop("no PEMA rows in frozen eligible sessions")

session_order <- eligible
session_meta <- do.call(rbind, lapply(session_order, function(s) {
  bits <- strsplit(s, ":bout", fixed = TRUE)[[1]]
  data.frame(session_id = s, grid = bits[1], bout = as.integer(bits[2]),
             stringsAsFactors = FALSE)
}))
session_meta$session <- seq_len(nrow(session_meta))

# Occasion numbers are chronological dates within each session.
occasion_map <- list()
for (s in session_order) {
  dates <- sort(unique(d$.date[d$.session_id == s]))
  occasion_map[[s]] <- setNames(seq_along(dates), as.character(dates))
}

reduce_locations <- function(which = c("first", "last")) {
  which <- match.arg(which)
  key <- interaction(d$.session_id, clean(d$unique_ID), as.character(d$.date),
                     drop = TRUE)
  groups <- split(seq_len(nrow(d)), key)
  rows <- lapply(groups, function(ii) {
    z <- d[ii, , drop = FALSE]
    ord <- order(z$.time, z$.row_index)
    z <- z[ord, , drop = FALSE]
    pick <- if (which == "first") z[1, , drop = FALSE] else z[nrow(z), , drop = FALSE]
    ss <- match(pick$.session_id, session_order)
    occ <- unname(occasion_map[[pick$.session_id]][as.character(pick$.date)])
    data.frame(
      session = ss,
      ID = clean(pick$unique_ID),
      occasion = as.integer(occ),
      trap = unname(flag_to_trap[pick$.flag]),
      stringsAsFactors = FALSE
    )
  })
  out <- do.call(rbind, rows)
  out[order(out$session, out$ID, out$occasion), , drop = FALSE]
}

first_dat <- reduce_locations("first")
last_dat <- reduce_locations("last")

key_cols <- c("session", "ID", "occasion")
fk <- do.call(paste, c(first_dat[key_cols], sep = "|"))
lk <- do.call(paste, c(last_dat[key_cols], sep = "|"))
if (!identical(fk, lk)) stop("FIRST/LAST observation keys differ")

make_trap <- function(nocc) {
  tr <- make.grid(nx = 7, ny = 7, spacing = spacing, detector = "multi", ID = "numy", leadingzero = FALSE)
  usage(tr) <- matrix(1, nrow = nrow(tr), ncol = nocc)
  tr
}

session_nocc <- vapply(session_order, function(s) length(occasion_map[[s]]), integer(1))
traplist <- lapply(session_nocc, make_trap)

make_ch <- function(dat) {
  make.capthist(
    dat,
    traps = traplist,
    fmt = "trapID",
    noccasions = session_nocc
  )
}

ch_first <- make_ch(first_dat)
ch_last <- make_ch(last_dat)

# secr::secr.fit verifies a user-supplied mask before it reaches the
# multi-session class-normalization block. Construct masks from the fitted
# capthist trap layouts, then explicitly mark the list as a multi-session
# mask so verify.mask dispatches correctly.
masklist <- lapply(
  traps(ch_first),
  function(tr) make.mask(tr, buffer = buffer_m, spacing = mask_spacing_m,
                         type = "trapbuffer")
)
class(masklist) <- c("mask", "list")
names(masklist) <- session(ch_first)
stopifnot(identical(names(masklist), session(ch_first)))
stopifnot(!verify(masklist, report = 1)$errors)

sessioncov <- data.frame(
  grid = factor(session_meta$grid),
  bout = factor(session_meta$bout)
)
rownames(sessioncov) <- session(ch_first)
stopifnot(nrow(sessioncov) == length(session(ch_first)))

extract_sigma <- function(fit) {
  pr <- predict(fit)
  idx <- which(rownames(pr) == "sigma")
  if (length(idx) != 1L) idx <- grep("^sigma", rownames(pr))
  if (length(idx) < 1L) stop("sigma prediction row not found")
  r <- pr[idx[1], , drop = FALSE]
  list(
    estimate = as.numeric(r[1, "estimate"]),
    SE = if ("SE.estimate" %in% colnames(r)) as.numeric(r[1, "SE.estimate"]) else NA_real_,
    lcl = if ("lcl" %in% colnames(r)) as.numeric(r[1, "lcl"]) else NA_real_,
    ucl = if ("ucl" %in% colnames(r)) as.numeric(r[1, "ucl"]) else NA_real_
  )
}

fit_pair <- function(model_name, formula_g0) {
  fit_one <- function(ch) {
    secr.fit(
      ch, mask = masklist, CL = TRUE, detectfn = "HN",
      model = list(g0 = formula_g0, sigma = ~1),
      sessioncov = sessioncov,
      trace = FALSE, verify = TRUE
    )
  }
  f <- fit_one(ch_first)
  l <- fit_one(ch_last)
  sf <- extract_sigma(f)
  sl <- extract_sigma(l)
  list(
    model = model_name,
    first = sf,
    last = sl,
    sigma_ratio_last_first = sl$estimate / sf$estimate,
    relative_change = (sl$estimate - sf$estimate) / sf$estimate,
    abs_relative_change_ge_10pct =
      abs((sl$estimate - sf$estimate) / sf$estimate) >= 0.10,
    AIC_first = as.numeric(suppressWarnings(AIC(f, criterion = "AIC"))[1, "AIC"]),
    AIC_last = as.numeric(suppressWarnings(AIC(l, criterion = "AIC"))[1, "AIC"])
  )
}

models <- list(
  primary = fit_pair("g0 ~ b + grid + bout", ~ b + grid + bout),
  no_behaviour = fit_pair("g0 ~ grid + bout", ~ grid + bout),
  constant_g0 = fit_pair("g0 ~ 1", ~ 1)
)

out <- list(
  schema = "neon.san_jacinto_scr_sigma_pema_post_stop.v1",
  status = "post_stop_exploratory",
  confirmatory_two_species_gate_remains =
    "stop_scr_sigma_sensitivity_not_estimable",
  species = "PEMA",
  scientific_name = "Peromyscus maniculatus",
  frozen_eligible_sessions = length(eligible),
  frozen_eligible_grids = length(unique(session_meta$grid)),
  first_last_keys_identical = identical(fk, lk),
  first_observations = nrow(first_dat),
  last_observations = nrow(last_dat),
  models = models,
  empirical_claim_boundary = list(
    replaces_failed_confirmatory_gate = FALSE,
    determines_correct_representative_location = FALSE,
    universal_bias_direction = FALSE
  ),
  package_versions = list(
    R = as.character(getRversion()),
    secr = as.character(packageVersion("secr")),
    jsonlite = as.character(packageVersion("jsonlite"))
  )
)

dir.create(dirname(out_json), recursive = TRUE, showWarnings = FALSE)
write_json(out, out_json, auto_unbox = TRUE, pretty = TRUE, na = "null")
cat(toJSON(out, auto_unbox = TRUE, pretty = TRUE, na = "null"), "\n")
