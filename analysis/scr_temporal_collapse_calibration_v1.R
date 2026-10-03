#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(secr)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
arg_value <- function(flag, default = NULL) {
  i <- match(flag, args)
  if (is.na(i)) return(default)
  if (i == length(args)) stop(paste("missing value for", flag))
  args[[i + 1]]
}
out_json <- arg_value("--output-json", "results/scr_temporal_collapse_calibration_v1.json")
reps <- as.integer(arg_value("--replicates", "50"))
seed0 <- as.integer(arg_value("--seed", "20261003"))

spacing <- 6.25
nights <- 3L
checks <- 3L
density <- 30
pop_buffer <- 100
empirical_fraction <- 426 / 592
empirical_fraction_band <- c(0.69, 0.73)
empirical_changed_median_band <- c(12.5, 14.0)

tr <- make.grid(nx=7, ny=7, spacing=spacing, detector="multi", origin=c(0,0))
xy <- as.data.frame(tr)[,c("x","y"),drop=FALSE]

trap_index <- function(x) {
  z <- as.character(x)
  out <- match(z, rownames(tr))
  bad <- is.na(out)
  if (any(bad)) suppressWarnings(out[bad] <- as.integer(z[bad]))
  if (any(is.na(out))) stop("unmapped detector")
  out
}

night_distances <- function(ch) {
  if (sum(ch) == 0) return(numeric())
  d <- as.data.frame(ch, fmt="trapID")
  if (!nrow(d)) return(numeric())
  names(d)[1:4] <- c("Session","ID","Occasion","TrapID")
  d$Occasion <- as.integer(d$Occasion)
  d$TrapNum <- trap_index(d$TrapID)
  d$Night <- ((d$Occasion - 1L) %/% checks) + 1L
  key <- paste(d$ID,d$Night,sep="::")
  groups <- split(seq_len(nrow(d)),key)
  ans <- c()
  for (ii in groups) {
    if (length(ii)<2) next
    z <- d[ii,,drop=FALSE]
    z <- z[order(z$Occasion),,drop=FALSE]
    a <- xy[z$TrapNum[[1]],]
    b <- xy[z$TrapNum[[nrow(z)]],]
    ans <- c(ans, sqrt((a$x-b$x)^2 + (a$y-b$y)^2))
  }
  ans
}

sigma_values <- spacing * c(0.5,0.75,1,1.25,1.5,2,2.5,3)
g0_values <- c(0.05,0.10,0.15,0.25,0.35)
rows <- list(); k <- 0L
for (sig in sigma_values) {
  for (g0 in g0_values) {
    all_dist <- c()
    detected <- c()
    for (r in seq_len(reps)) {
      k <- k + 1L
      ch <- sim.capthist(
        tr,
        popn=list(D=density,buffer=pop_buffer),
        detectfn="HN",
        detectpar=list(g0=g0,sigma=sig),
        noccasions=nights*checks,
        seed=seed0 + k*1009L
      )
      all_dist <- c(all_dist, night_distances(ch))
      if (sum(ch) == 0) {
        detected <- c(detected, 0)
      } else {
        dd <- as.data.frame(ch,fmt="trapID")
        detected <- c(detected, length(unique(dd[,2])))
      }
    }
    repeat_n <- length(all_dist)
    material <- sum(all_dist >= spacing - 1e-12)
    changed <- all_dist[all_dist > 1e-12]
    frac <- if (repeat_n) material/repeat_n else NA_real_
    changed_median <- if (length(changed)) median(changed) else NA_real_
    rows[[length(rows)+1L]] <- data.frame(
      sigma_m=sig,
      sigma_over_spacing=sig/spacing,
      g0=g0,
      replicates=reps,
      repeat_nights=repeat_n,
      material_shift_count=material,
      material_shift_fraction=frac,
      changed_nights=length(changed),
      changed_median_m=changed_median,
      mean_detected_animals=mean(detected),
      fraction_distance_from_empirical=abs(frac-empirical_fraction),
      changed_median_distance_from_band_mid=abs(changed_median-mean(empirical_changed_median_band)),
      stringsAsFactors=FALSE
    )
  }
}
res <- do.call(rbind,rows)
res$within_empirical_fraction_band <- (
  res$material_shift_fraction >= empirical_fraction_band[1] &
  res$material_shift_fraction <= empirical_fraction_band[2]
)
res$within_empirical_changed_median_band <- (
  res$changed_median_m >= empirical_changed_median_band[1] &
  res$changed_median_m <= empirical_changed_median_band[2]
)
res$matches_both_empirical_summaries <- (
  res$within_empirical_fraction_band &
  res$within_empirical_changed_median_band
)

ord <- order(
  !res$matches_both_empirical_summaries,
  res$fraction_distance_from_empirical,
  res$changed_median_distance_from_band_mid
)
res <- res[ord,,drop=FALSE]

out <- list(
  schema="neon.scr_temporal_collapse.calibration.v1",
  purpose="effect-blind calibration of simulated repeated-check conflict geometry to held-out positional summaries; no empirical SCR sigma is fitted",
  protocol=list(
    grid="7x7",
    spacing_m=spacing,
    nights=nights,
    checks_per_night=checks,
    detector="multi",
    detectfn="HN",
    density_animals_per_ha=density,
    population_buffer_m=pop_buffer
  ),
  empirical_targets=list(
    material_shift_fraction_combined=empirical_fraction,
    material_shift_fraction_species_band=empirical_fraction_band,
    changed_night_median_distance_m_band=empirical_changed_median_band
  ),
  cells=res,
  best_cells=head(res,10),
  guardrails=list(
    empirical_sigma_effect_opened=FALSE,
    empirical_scr_stop_gate_relaxed=FALSE
  )
)

dir.create(dirname(out_json),recursive=TRUE,showWarnings=FALSE)
write_json(out,out_json,pretty=TRUE,auto_unbox=TRUE,digits=10)
print(head(res,15),row.names=FALSE)
