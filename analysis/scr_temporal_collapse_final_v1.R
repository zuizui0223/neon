#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(secr)
  library(jsonlite)
})

args <- commandArgs(trailingOnly=TRUE)
arg_value <- function(flag, default=NULL) {
  i <- match(flag,args)
  if (is.na(i)) return(default)
  if (i==length(args)) stop(paste("missing value for",flag))
  args[[i+1]]
}
lock_path <- arg_value("--lock","validation/scr_temporal_collapse_final_lock_v1.json")
out_json <- arg_value("--output-json","results/scr_temporal_collapse_final_v1.json")
out_csv <- arg_value("--output-csv","results/scr_temporal_collapse_final_replicates_v1.csv")
seed0 <- as.integer(arg_value("--seed","20261003"))
reps_override <- arg_value("--replicates",NULL)

lock <- fromJSON(lock_path,simplifyVector=FALSE)
if (lock$state!="frozen_before_downstream_sigma_effects") stop("final lock is not frozen")
if (isTRUE(lock$downstream_sigma_effects_inspected)) stop("lock says effects already inspected")
G <- lock$generator
reps <- if (is.null(reps_override)) as.integer(lock$monte_carlo_replicates) else as.integer(reps_override)

spacing <- as.numeric(G$spacing_m)
nights <- as.integer(G$nights)
checks <- as.integer(G$checks_per_night)
true_sigma <- as.numeric(G$true_sigma_m)
g0 <- as.numeric(G$g0_per_check)
density <- as.numeric(G$density_animals_per_ha)
pop_buffer <- as.numeric(G$population_buffer_m)
fit_buffer <- as.numeric(G$fit_mask_buffer_m)
rho_cal <- as.numeric(G$same_trap_persistence_rho)
material_threshold <- as.numeric(lock$materiality_threshold)

tr <- make.grid(nx=7,ny=7,spacing=spacing,detector="multi",origin=c(0,0))
mk <- make.mask(tr,buffer=fit_buffer,spacing=5)
xy <- as.data.frame(tr)[,c("x","y"),drop=FALSE]

trap_index <- function(x) {
  z <- as.character(x)
  out <- match(z,rownames(tr))
  bad <- is.na(out)
  if (any(bad)) {
    suppressWarnings(out[bad] <- as.integer(z[bad]))
  }
  if (any(is.na(out)) || any(out<1) || any(out>nrow(tr))) stop("unmapped detector")
  out
}

capture_frame <- function(ch) {
  if (sum(ch)==0) return(data.frame())
  d <- as.data.frame(ch,fmt="trapID")
  names(d)[1:4] <- c("Session","ID","Occasion","TrapID")
  d$Occasion <- as.integer(d$Occasion)
  d$TrapNum <- trap_index(d$TrapID)
  d$Night <- ((d$Occasion-1L) %/% checks)+1L
  d
}

rebuild_ch <- function(d) {
  if (!nrow(d)) stop("cannot rebuild empty history")
  cap <- data.frame(
    Session=1,
    ID=as.character(d$ID),
    Occasion=as.integer(d$Occasion),
    TrapID=rownames(tr)[as.integer(d$TrapNum)],
    stringsAsFactors=FALSE
  )
  make.capthist(
    captures=cap,
    traps=tr,
    fmt="trapID",
    noccasions=nights*checks,
    bysession=TRUE
  )
}

apply_same_trap_persistence <- function(ch,rho,seed) {
  if (rho<=0) return(ch)
  d <- capture_frame(ch)
  if (!nrow(d)) return(ch)
  set.seed(seed)
  key <- paste(d$ID,d$Night,sep="::")
  groups <- split(seq_len(nrow(d)),key)
  for (ii in groups) {
    if (length(ii)<2) next
    if (runif(1) < rho) {
      anchor <- sample(d$TrapNum[ii],1)
      d$TrapNum[ii] <- anchor
    }
  }
  rebuild_ch(d)
}

geometry_summary <- function(ch) {
  d <- capture_frame(ch)
  if (!nrow(d)) return(list(
    all_captured_nights=0L,repeat_nights=0L,conflict_nights=0L,
    conflict_diameters=numeric()
  ))
  key <- paste(d$ID,d$Night,sep="::")
  groups <- split(seq_len(nrow(d)),key)
  repeat_n <- 0L; conflict_n <- 0L; diam <- c()
  for (ii in groups) {
    if (length(ii)<2) next
    repeat_n <- repeat_n+1L
    nums <- d$TrapNum[ii]
    if (length(unique(nums))>1) {
      conflict_n <- conflict_n+1L
      coords <- xy[nums,,drop=FALSE]
      diam <- c(diam,max(as.matrix(dist(coords))))
    }
  }
  list(
    all_captured_nights=length(groups),
    repeat_nights=repeat_n,
    conflict_nights=conflict_n,
    conflict_diameters=diam
  )
}

fit_sigma <- function(ch) {
  tryCatch({
    fit <- secr.fit(
      ch,
      mask=mk,
      CL=TRUE,
      detectfn="HN",
      model=list(g0~1,sigma~1),
      trace=FALSE,
      ncores=1
    )
    p <- predict(fit)
    if (!("sigma" %in% rownames(p))) stop("sigma row absent")
    list(ok=TRUE,sigma=as.numeric(p["sigma","estimate"]),logLik=as.numeric(logLik(fit)))
  },error=function(e) list(ok=FALSE,sigma=NA_real_,logLik=NA_real_,error=conditionMessage(e)))
}

reduce_nightly <- function(ch,select) {
  reduce(
    ch,
    by=checks,
    outputdetector="multi",
    select=select,
    dropunused=FALSE
  )
}

simulate_base <- function(seed) {
  sim.capthist(
    tr,
    popn=list(D=density,buffer=pop_buffer),
    detectfn="HN",
    detectpar=list(g0=g0,sigma=true_sigma),
    noccasions=nights*checks,
    seed=seed
  )
}

one_scenario <- function(base_ch,scenario,rho,replicate,seed) {
  check_ch <- apply_same_trap_persistence(base_ch,rho,seed+7919L)
  geo <- geometry_summary(check_ch)
  first_ch <- reduce_nightly(check_ch,"first")
  last_ch <- reduce_nightly(check_ch,"last")
  f_check <- fit_sigma(check_ch)
  f_first <- fit_sigma(first_ch)
  f_last <- fit_sigma(last_ch)
  ok <- isTRUE(f_check$ok) && isTRUE(f_first$ok) && isTRUE(f_last$ok)
  first_vs_check <- if(ok) f_first$sigma/f_check$sigma-1 else NA_real_
  last_vs_check <- if(ok) f_last$sigma/f_check$sigma-1 else NA_real_
  data.frame(
    scenario=scenario,
    rho=rho,
    replicate=replicate,
    seed=seed,
    all_captured_nights=geo$all_captured_nights,
    repeat_nights=geo$repeat_nights,
    conflict_nights=geo$conflict_nights,
    repeat_fraction=if(geo$all_captured_nights) geo$repeat_nights/geo$all_captured_nights else NA_real_,
    conflict_fraction=if(geo$repeat_nights) geo$conflict_nights/geo$repeat_nights else NA_real_,
    conflict_diameter_median=if(length(geo$conflict_diameters)) median(geo$conflict_diameters) else NA_real_,
    all_fits_ok=ok,
    sigma_check=f_check$sigma,
    sigma_first=f_first$sigma,
    sigma_last=f_last$sigma,
    check_relerr_true=f_check$sigma/true_sigma-1,
    first_relerr_true=f_first$sigma/true_sigma-1,
    last_relerr_true=f_last$sigma/true_sigma-1,
    first_vs_check=first_vs_check,
    last_vs_check=last_vs_check,
    rule_neutral_signed=if(ok) 0.5*(first_vs_check+last_vs_check) else NA_real_,
    mean_abs_rule_sensitivity=if(ok) 0.5*(abs(first_vs_check)+abs(last_vs_check)) else NA_real_,
    max_abs_rule_sensitivity=if(ok) max(abs(first_vs_check),abs(last_vs_check)) else NA_real_,
    either_ge_10pct=if(ok) max(abs(first_vs_check),abs(last_vs_check))>=material_threshold else NA,
    last_vs_first=if(ok) f_last$sigma/f_first$sigma-1 else NA_real_,
    stringsAsFactors=FALSE
  )
}

rows <- list(); diameters <- list(exchangeable_static_scr=c(),san_jacinto_calibrated=c())
k <- 0L
for (r in seq_len(reps)) {
  seed <- seed0 + r*10007L
  base <- simulate_base(seed)
  for (sc in c("exchangeable_static_scr","san_jacinto_calibrated")) {
    rho <- if(sc=="exchangeable_static_scr") 0 else rho_cal
    k <- k+1L
    check_ch <- apply_same_trap_persistence(base,rho,seed+7919L)
    geo <- geometry_summary(check_ch)
    diameters[[sc]] <- c(diameters[[sc]],geo$conflict_diameters)
    # reuse transformed history by running equivalent inline fit path
    first_ch <- reduce_nightly(check_ch,"first")
    last_ch <- reduce_nightly(check_ch,"last")
    f_check <- fit_sigma(check_ch); f_first <- fit_sigma(first_ch); f_last <- fit_sigma(last_ch)
    ok <- isTRUE(f_check$ok) && isTRUE(f_first$ok) && isTRUE(f_last$ok)
    a <- if(ok) f_first$sigma/f_check$sigma-1 else NA_real_
    b <- if(ok) f_last$sigma/f_check$sigma-1 else NA_real_
    rows[[k]] <- data.frame(
      scenario=sc,rho=rho,replicate=r,seed=seed,
      all_captured_nights=geo$all_captured_nights,
      repeat_nights=geo$repeat_nights,
      conflict_nights=geo$conflict_nights,
      repeat_fraction=if(geo$all_captured_nights) geo$repeat_nights/geo$all_captured_nights else NA_real_,
      conflict_fraction=if(geo$repeat_nights) geo$conflict_nights/geo$repeat_nights else NA_real_,
      conflict_diameter_median=if(length(geo$conflict_diameters)) median(geo$conflict_diameters) else NA_real_,
      all_fits_ok=ok,
      sigma_check=f_check$sigma,sigma_first=f_first$sigma,sigma_last=f_last$sigma,
      check_relerr_true=f_check$sigma/true_sigma-1,
      first_relerr_true=f_first$sigma/true_sigma-1,
      last_relerr_true=f_last$sigma/true_sigma-1,
      first_vs_check=a,last_vs_check=b,
      rule_neutral_signed=if(ok) 0.5*(a+b) else NA_real_,
      mean_abs_rule_sensitivity=if(ok) 0.5*(abs(a)+abs(b)) else NA_real_,
      max_abs_rule_sensitivity=if(ok) max(abs(a),abs(b)) else NA_real_,
      either_ge_10pct=if(ok) max(abs(a),abs(b))>=material_threshold else NA,
      last_vs_first=if(ok) f_last$sigma/f_first$sigma-1 else NA_real_,
      stringsAsFactors=FALSE
    )
  }
  if (r %% 10 == 0) message("completed replicate ",r,"/",reps)
}
res <- do.call(rbind,rows)

safe_mean <- function(x) mean(x[is.finite(x)])
safe_sd <- function(x) sd(x[is.finite(x)])
q <- function(x,p) as.numeric(quantile(x[is.finite(x)],p,names=FALSE,type=7))
summaries <- list()
for(sc in unique(res$scenario)) {
  z <- res[res$scenario==sc,,drop=FALSE]
  ok <- z[z$all_fits_ok,,drop=FALSE]
  all_n <- sum(z$all_captured_nights)
  repeat_n <- sum(z$repeat_nights)
  conflict_n <- sum(z$conflict_nights)
  primary <- ok$mean_abs_rule_sensitivity
  summaries[[sc]] <- list(
    rho=unique(z$rho)[1],
    replicates=nrow(z),
    all_three_fit_fraction=mean(z$all_fits_ok),
    pooled_geometry=list(
      all_captured_nights=all_n,
      repeat_nights=repeat_n,
      repeat_observation_fraction=repeat_n/all_n,
      conflict_nights=conflict_n,
      cross_trap_conflict_fraction=conflict_n/repeat_n,
      conflict_diameter_median_m=median(diameters[[sc]])
    ),
    sigma=list(
      mean_check_relerr_true=safe_mean(ok$check_relerr_true),
      mean_first_relerr_true=safe_mean(ok$first_relerr_true),
      mean_last_relerr_true=safe_mean(ok$last_relerr_true),
      mean_first_vs_check=safe_mean(ok$first_vs_check),
      mean_last_vs_check=safe_mean(ok$last_vs_check),
      mean_rule_neutral_signed=safe_mean(ok$rule_neutral_signed),
      mean_abs_rule_sensitivity=safe_mean(primary),
      mc_se_mean_abs_rule_sensitivity=safe_sd(primary)/sqrt(length(primary)),
      primary_distribution_q025=q(primary,.025),
      primary_distribution_median=q(primary,.5),
      primary_distribution_q975=q(primary,.975),
      mean_max_abs_rule_sensitivity=safe_mean(ok$max_abs_rule_sensitivity),
      fraction_replicates_either_rule_ge_10pct=mean(ok$either_ge_10pct),
      mean_last_vs_first=safe_mean(ok$last_vs_first)
    ),
    materiality=list(
      threshold=material_threshold,
      primary_mean_abs_rule_sensitivity_exceeds_threshold=safe_mean(primary)>=material_threshold
    )
  )
}

out <- list(
  schema="neon.scr_temporal_collapse.final.v1",
  lock=lock,
  seed=seed0,
  actual_replicates_per_scenario=reps,
  summary=summaries,
  guardrails=list(
    empirical_sigma_effect_opened=FALSE,
    empirical_two_species_stop_relaxed=FALSE,
    generator_parameters_changed_after_lock=FALSE
  )
)
dir.create(dirname(out_json),recursive=TRUE,showWarnings=FALSE)
write_json(out,out_json,pretty=TRUE,auto_unbox=TRUE,digits=10)
write.csv(res,out_csv,row.names=FALSE)
print(toJSON(list(summary=summaries,guardrails=out$guardrails),pretty=TRUE,auto_unbox=TRUE,digits=6))
