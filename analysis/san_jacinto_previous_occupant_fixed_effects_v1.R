suppressPackageStartupMessages({
  library(fixest)
  library(jsonlite)
})

args <- commandArgs(trailingOnly=TRUE)
input_csv <- args[[1]]
out_json <- args[[2]]

SPECIES <- c("CHFA","PEMA","DKR","PEER","LAPM","SKR")
SMALL <- c("CHFA","PEMA","PEER","LAPM")
BINS <- c("EARLY","MIDDLE","LATE")
FLAGS <- unlist(lapply(LETTERS[1:7],function(x)paste0(x,1:7)))

clean <- function(x) trimws(ifelse(is.na(x),"",as.character(x)))
up <- function(x) toupper(clean(x))

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
raw$grid <- clean(raw$grid)
raw$flag <- up(raw$flag)
raw$species <- up(raw$species)
raw$time_bin <- up(raw$time_bin)
raw$.id <- identity_key(raw)

# Only use grid-nights for which all three check labels are observed at least once.
# This avoids imputing whether a missing time bin reflects zero captures or no check.
unit_key <- paste(raw$grid,clean(raw$date),sep="||")
binsets <- split(raw$time_bin,unit_key)
complete_keys <- names(binsets)[vapply(binsets,function(x)all(BINS %in% unique(x)),logical(1))]
d <- raw[unit_key %in% complete_keys & raw$flag %in% FLAGS,,drop=FALSE]
d$.unit <- paste(d$grid,clean(d$date),sep="||")

# Collapse each trap x check to a species state.
cell_key <- paste(d$.unit,d$flag,d$time_bin,sep="||")
cells <- split(seq_len(nrow(d)),cell_key)
cell_state <- list()
ambiguous_cells <- 0L
nonmain_cells <- 0L
for(k in names(cells)){
  ii <- cells[[k]]
  z <- d[ii,,drop=FALSE]
  spp <- unique(z$species[nzchar(z$species)])
  state <- NULL
  if(length(spp)==1L && spp %in% SPECIES) state <- spp
  else if(length(spp)==1L && !(spp %in% SPECIES)) {
    state <- "NONMAIN"; nonmain_cells <- nonmain_cells+1L
  } else {
    state <- "AMBIG"; ambiguous_cells <- ambiguous_cells+1L
  }
  cell_state[[k]] <- list(state=state,ids=unique(z$.id[nzchar(z$.id)]))
}

get_cell <- function(unit,flag,bin){
  k <- paste(unit,flag,bin,sep="||")
  if(is.null(cell_state[[k]])) return(list(state="EMPTY",ids=character()))
  cell_state[[k]]
}

rows <- list()
ri <- 0L
unit_meta <- unique(d[,c(".unit","grid","date")])
for(uix in seq_len(nrow(unit_meta))){
  unit <- unit_meta$.unit[uix]
  grid <- clean(unit_meta$grid[uix])
  date <- clean(unit_meta$date[uix])
  for(flag in FLAGS){
    for(pair in list(c("EARLY","MIDDLE"),c("MIDDLE","LATE"))){
      a <- get_cell(unit,flag,pair[1]); b <- get_cell(unit,flag,pair[2])
      if(a$state %in% c("AMBIG","NONMAIN") || b$state %in% c("AMBIG","NONMAIN")) next
      ri <- ri+1L
      same_ind <- length(intersect(a$ids,b$ids))>0
      rows[[ri]] <- data.frame(
        grid=grid,date=date,flag=flag,
        trap_id=paste(grid,flag,sep=":"),
        transition=paste(pair,collapse="->"),
        stratum=paste(grid,date,paste(pair,collapse="->"),sep=":"),
        grid_date=paste(grid,date,sep=":"),
        from_state=a$state,to_state=b$state,
        same_individual=same_ind,
        stringsAsFactors=FALSE
      )
    }
  }
}
tr <- do.call(rbind,rows)
tr$from_state <- factor(tr$from_state,levels=c("EMPTY",SPECIES))
tr$to_state <- factor(tr$to_state,levels=c("EMPTY",SPECIES))

fit_target <- function(target,exclude_same_ind=FALSE) {
  z <- tr
  if(exclude_same_ind) {
    z <- z[!(z$from_state==target & z$to_state==target & z$same_individual),,drop=FALSE]
  }
  z$y <- as.integer(z$to_state==target)
  fit <- feglm(
    y ~ i(from_state, ref="EMPTY") | trap_id + stratum,
    data=z,
    family=binomial("logit"),
    warn=FALSE,notes=FALSE
  )
  sm <- summary(fit,cluster=~grid_date)
  cf <- coef(sm)
  se <- se(sm)
  pv <- pvalue(sm)
  out <- list()
  for(nm in names(cf)){
    if(!grepl("^from_state::",nm)) next
    from <- sub("^from_state::","",nm)
    beta <- unname(cf[nm]); s <- unname(se[nm]); p <- unname(pv[nm])
    out[[from]] <- list(
      log_odds=beta,
      SE=s,
      odds_ratio=exp(beta),
      lcl95=exp(beta-1.96*s),
      ucl95=exp(beta+1.96*s),
      p=p
    )
  }
  list(
    target=target,
    exclude_same_individual_recurrence=exclude_same_ind,
    n=nrow(z),
    positive=sum(z$y),
    fixed_effects="trap_id + grid_date_transition",
    cluster="grid_date",
    contrasts_vs_previous_empty=out
  )
}

target_models <- list()
for(sp in SPECIES){
  target_models[[sp]] <- fit_target(sp,FALSE)
}
target_models_no_self <- list()
for(sp in SPECIES){
  target_models_no_self[[sp]] <- fit_target(sp,TRUE)
}

# Pooled small-species outcome asks whether recent kangaroo-rat occupancy suppresses
# any non-kangaroo-rat capture at the next check.
tr$from_group <- ifelse(
  tr$from_state=="EMPTY","EMPTY",
  ifelse(tr$from_state %in% c("DKR","SKR"),"KANGAROO","SMALL")
)
tr$from_group <- factor(tr$from_group,levels=c("EMPTY","SMALL","KANGAROO"))
tr$next_small <- as.integer(tr$to_state %in% SMALL)
pool_fit <- feglm(
  next_small ~ i(from_group, ref="EMPTY") | trap_id + stratum,
  data=tr,family=binomial("logit"),warn=FALSE,notes=FALSE
)
pool_sm <- summary(pool_fit,cluster=~grid_date)
pool <- list()
for(nm in names(coef(pool_sm))){
  if(!grepl("^from_group::",nm)) next
  from <- sub("^from_group::","",nm)
  beta <- unname(coef(pool_sm)[nm]); s <- unname(se(pool_sm)[nm])
  pool[[from]] <- list(
    log_odds=beta,SE=s,odds_ratio=exp(beta),
    lcl95=exp(beta-1.96*s),ucl95=exp(beta+1.96*s),
    p=unname(pvalue(pool_sm)[nm])
  )
}

# Guild-level directional alignment with body size.
# This is post-result exploratory: ask whether the effect of the heavier species
# as previous occupant on the lighter target is lower than the reverse direction.
weight_values <- suppressWarnings(as.numeric(raw$weight_g))
weight_species <- up(raw$species)
species_mass <- lapply(SPECIES,function(sp){
  z <- weight_values[weight_species==sp & is.finite(weight_values) & weight_values>0 & weight_values<300]
  list(n=length(z),median_g=median(z),mean_g=mean(z))
})
names(species_mass) <- SPECIES

direction_dyads <- list()
di <- 0L
for(i in seq_len(length(SPECIES)-1L)){
  for(j in (i+1L):length(SPECIES)){
    a <- SPECIES[i]; b <- SPECIES[j]
    heavy <- if(species_mass[[a]]$median_g >= species_mass[[b]]$median_g) a else b
    light <- if(heavy==a) b else a
    hl <- target_models[[light]]$contrasts_vs_previous_empty[[heavy]]
    lh <- target_models[[heavy]]$contrasts_vs_previous_empty[[light]]
    if(is.null(hl) || is.null(lh)) next
    di <- di+1L
    direction_dyads[[di]] <- list(
      heavy=heavy,light=light,
      heavy_median_g=species_mass[[heavy]]$median_g,
      light_median_g=species_mass[[light]]$median_g,
      mass_ratio=species_mass[[heavy]]$median_g/species_mass[[light]]$median_g,
      heavy_to_light_or=hl$odds_ratio,
      light_to_heavy_or=lh$odds_ratio,
      log_direction_ratio=log(hl$odds_ratio/lh$odds_ratio),
      heavy_to_light_lower=(hl$odds_ratio < lh$odds_ratio)
    )
  }
}

permute_vec <- function(v){
  if(length(v)==1L) return(list(v))
  out <- list()
  oi <- 0L
  for(i in seq_along(v)){
    rest <- v[-i]
    for(p in permute_vec(rest)){
      oi <- oi+1L
      out[[oi]] <- c(v[i],p)
    }
  }
  out
}
obs_concordant <- sum(vapply(direction_dyads,function(x)isTRUE(x$heavy_to_light_lower),logical(1)))
mass_vals <- vapply(species_mass,function(x)x$median_g,numeric(1))
perm_counts <- integer()
perms <- permute_vec(mass_vals)
for(pi in seq_along(perms)){
  mm <- setNames(perms[[pi]],SPECIES)
  cc <- 0L
  for(i in seq_len(length(SPECIES)-1L)){
    for(j in (i+1L):length(SPECIES)){
      a <- SPECIES[i]; b <- SPECIES[j]
      heavy <- if(mm[a]>=mm[b]) a else b
      light <- if(heavy==a) b else a
      hl <- target_models[[light]]$contrasts_vs_previous_empty[[heavy]]
      lh <- target_models[[heavy]]$contrasts_vs_previous_empty[[light]]
      if(!is.null(hl) && !is.null(lh) && hl$odds_ratio < lh$odds_ratio) cc <- cc+1L
    }
  }
  perm_counts <- c(perm_counts,cc)
}
body_size_direction_alignment <- list(
  status="post_result_exploratory_guild_level_pattern",
  species_mass=species_mass,
  dyads=direction_dyads,
  concordant_heavy_to_light_lower=obs_concordant,
  n_dyads=length(direction_dyads),
  mass_rank_permutations=length(perm_counts),
  exact_upper_tail_fraction=mean(perm_counts>=obs_concordant),
  interpretation="Across pairwise fixed-effect coefficients, the heavier-to-lighter previous-occupant direction is usually lower than the reverse direction. This is exploratory concordance with a body-size dominance hierarchy, not a causal test of interference competition."
)

# Descriptive transition matrix.
states <- c("EMPTY",SPECIES)
tab <- table(factor(tr$from_state,levels=states),factor(tr$to_state,levels=states))
mat <- lapply(seq_along(states),function(i)as.list(as.integer(tab[i,])))
names(mat) <- states
for(i in seq_along(states)) names(mat[[i]]) <- states

# Compact focal contrasts: previous kangaroo-rat -> next smaller species.
focal <- list()
for(target in SMALL){
  z <- target_models[[target]]$contrasts_vs_previous_empty
  focal[[target]] <- list(
    after_DKR=z$DKR,
    after_SKR=z$SKR
  )
}

out <- list(
  schema="neon.san_jacinto_previous_occupant_fixed_effects.v1",
  status="post_result_ecological_transition_analysis",
  source_sha256_expected="ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301",
  support=list(
    complete_grid_nights=length(complete_keys),
    transition_rows=nrow(tr),
    ambiguous_species_cells=ambiguous_cells,
    nonmain_species_cells=nonmain_cells,
    previous_occupied=sum(tr$from_state!="EMPTY"),
    previous_empty=sum(tr$from_state=="EMPTY")
  ),
  design=list(
    state_space=c("EMPTY",SPECIES),
    transitions=c("EARLY->MIDDLE","MIDDLE->LATE"),
    primary_model="next target-species capture ~ previous trap state | trap_id + grid_date_transition",
    uncertainty="cluster-robust SE by grid_date",
    reason_for_fixed_effects="trap_id absorbs persistent trap/microhabitat propensity; grid_date_transition absorbs check-specific community activity"
  ),
  pooled_small_species_after_previous_group=list(
    target="next capture belongs to CHFA, PEMA, PEER or LAPM",
    contrasts_vs_previous_empty=pool
  ),
  focal_previous_kangaroo_rat_contrasts=focal,
  body_size_direction_alignment=body_size_direction_alignment,
  target_models=target_models,
  target_models_excluding_same_individual_recurrence=target_models_no_self,
  transition_matrix=mat,
  claim_boundary=list(
    causal_scent_effect_identified=FALSE,
    interference_competition_identified=FALSE,
    complete_sampling_schedule_reconstructed=FALSE,
    interpretation="Fixed effects remove persistent trap differences and grid-date-transition-wide activity, but previous occupancy remains observational. Cross-species effects are evidence of short-term conditional association, not proof of scent-mediated avoidance or interference competition."
  ),
  package_versions=list(
    R=as.character(getRversion()),
    fixest=as.character(packageVersion("fixest")),
    jsonlite=as.character(packageVersion("jsonlite"))
  )
)

dir.create(dirname(out_json),recursive=TRUE,showWarnings=FALSE)
write_json(out,out_json,pretty=TRUE,auto_unbox=TRUE,na="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,na="null"),"\n")
