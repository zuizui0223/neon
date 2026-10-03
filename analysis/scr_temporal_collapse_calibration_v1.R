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
empirical_endpoint_fraction <- 426 / 592
empirical_conflict_fraction <- 450 / 592
empirical_repeat_fraction <- 592 / 1520
empirical_repeat_fraction_band <- c(107/301, 485/1219)
empirical_diameter_median <- 13.975424859373685
empirical_diameter_band <- c(12.5, 14.0)

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

night_summary <- function(ch) {
  if (sum(ch) == 0) {
    return(list(all_captured_nights=0L, repeat_nights=0L,
                conflict_nights=0L, conflict_diameters=numeric()))
  }
  d <- as.data.frame(ch, fmt="trapID")
  names(d)[1:4] <- c("Session","ID","Occasion","TrapID")
  d$Occasion <- as.integer(d$Occasion)
  d$TrapNum <- trap_index(d$TrapID)
  d$Night <- ((d$Occasion - 1L) %/% checks) + 1L
  key <- paste(d$ID,d$Night,sep="::")
  groups <- split(seq_len(nrow(d)),key)
  repeat_n <- 0L
  conflict_n <- 0L
  diam <- c()
  for (ii in groups) {
    if (length(ii) < 2) next
    repeat_n <- repeat_n + 1L
    z <- d[ii,,drop=FALSE]
    traps_i <- z$TrapNum
    if (length(unique(traps_i)) > 1) {
      conflict_n <- conflict_n + 1L
      coords <- xy[traps_i,,drop=FALSE]
      dm <- as.matrix(dist(coords))
      diam <- c(diam, max(dm))
    }
  }
  list(
    all_captured_nights=length(groups),
    repeat_nights=repeat_n,
    conflict_nights=conflict_n,
    conflict_diameters=diam
  )
}

sigma_values <- spacing * c(0.5,0.75,1,1.25,1.5,2,2.5,3)
g0_values <- c(0.05,0.10,0.15,0.25,0.35)
rows <- list(); k <- 0L
for (sig in sigma_values) {
  for (g0 in g0_values) {
    all_diam <- c()
    all_captured_nights <- 0L
    repeat_nights <- 0L
    conflict_nights <- 0L
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
      ns <- night_summary(ch)
      all_captured_nights <- all_captured_nights + ns$all_captured_nights
      repeat_nights <- repeat_nights + ns$repeat_nights
      conflict_nights <- conflict_nights + ns$conflict_nights
      all_diam <- c(all_diam, ns$conflict_diameters)
      if (sum(ch) == 0) {
        detected <- c(detected, 0)
      } else {
        dd <- as.data.frame(ch,fmt="trapID")
        detected <- c(detected, length(unique(dd[,2])))
      }
    }
    repeat_fraction <- if (all_captured_nights) repeat_nights/all_captured_nights else NA_real_
    conflict_fraction <- if (repeat_nights) conflict_nights/repeat_nights else NA_real_
    diameter_median <- if (length(all_diam)) median(all_diam) else NA_real_
    retention_needed <- if (is.finite(conflict_fraction) && conflict_fraction>0) {
      max(0, min(1, 1 - empirical_conflict_fraction/conflict_fraction))
    } else NA_real_
    rows[[length(rows)+1L]] <- data.frame(
      sigma_m=sig,
      sigma_over_spacing=sig/spacing,
      g0=g0,
      replicates=reps,
      all_captured_nights=all_captured_nights,
      repeat_nights=repeat_nights,
      repeat_observation_fraction=repeat_fraction,
      cross_trap_conflict_count=conflict_nights,
      cross_trap_conflict_fraction=conflict_fraction,
      conflict_diameter_median_m=diameter_median,
      mean_detected_animals=mean(detected),
      repeat_fraction_distance=abs(repeat_fraction-empirical_repeat_fraction),
      diameter_median_distance_m=abs(diameter_median-empirical_diameter_median),
      same_trap_retention_needed=retention_needed,
      stringsAsFactors=FALSE
    )
  }
}
res <- do.call(rbind,rows)
res$within_empirical_repeat_fraction_band <- (
  res$repeat_observation_fraction >= min(empirical_repeat_fraction_band) &
  res$repeat_observation_fraction <= max(empirical_repeat_fraction_band)
)
res$within_empirical_diameter_band <- (
  res$conflict_diameter_median_m >= empirical_diameter_band[1] &
  res$conflict_diameter_median_m <= empirical_diameter_band[2]
)
res$matches_base_scr_targets <- (
  res$within_empirical_repeat_fraction_band &
  res$within_empirical_diameter_band
)

# Rank using only quantities intended to calibrate the base SCR process.
# Conflict frequency is deliberately excluded: it is the mismatch to be
# absorbed by the separately reported same-trap retention parameter.
res$calibration_score <- (
  res$repeat_fraction_distance / 0.05 +
  res$diameter_median_distance_m / spacing
)
ord <- order(
  !res$matches_base_scr_targets,
  res$calibration_score,
  res$repeat_fraction_distance,
  res$diameter_median_distance_m
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
    repeat_observation_fraction_combined=empirical_repeat_fraction,
    repeat_observation_fraction_species_band=sort(empirical_repeat_fraction_band),
    cross_trap_conflict_fraction_combined=empirical_conflict_fraction,
    endpoint_change_fraction_combined=empirical_endpoint_fraction,
    conflict_diameter_median_m=empirical_diameter_median,
    conflict_diameter_median_species_band=empirical_diameter_band
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
