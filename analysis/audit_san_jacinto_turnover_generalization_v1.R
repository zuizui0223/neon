#!/usr/bin/env Rscript

suppressPackageStartupMessages({library(EcoSimR); library(jsonlite)})

args <- commandArgs(trailingOnly=TRUE)
arg_value <- function(flag,default=NULL){i<-match(flag,args);if(is.na(i))return(default);if(i==length(args))stop(paste("missing",flag));args[[i+1]]}
OUT<-arg_value("--output","results/san_jacinto_turnover_generalization_v1.json")
CACHE<-arg_value("--cache","/tmp/year_round_trap_data.csv")
SUPPORT<-arg_value("--support","results/san_jacinto_turnover_generalization_support_v1.json")
NREPS<-as.integer(arg_value("--nreps","10000")); BURN<-as.integer(arg_value("--burn","500")); BASE_SEED<-as.integer(arg_value("--seed","2026100508"))

URL<-"https://ndownloader.figshare.com/files/33058799"
SHA256<-"ec70b40fdcc66a3f9c07a3fda64b5eda06d251a899b9bc99cc5c5dff8c4ab301"
FOCAL<-c("CHFA","DKR","LAPM","PEER","PEMA","SKR")
FLAGS<-unlist(lapply(LETTERS[1:7],function(r)paste0(r,1:7)))

clean<-function(x)trimws(as.character(x))
parse_time<-function(x){
 x<-clean(x); if(!grepl("^[0-9]{1,2}:[0-9]{2}$",x))return(NA_real_)
 z<-strsplit(x,":",fixed=TRUE)[[1]];h<-as.integer(z[1]);m<-as.integer(z[2]);if(is.na(h)||is.na(m)||m>=60)return(NA_real_)
 if(h>=7&&h<=11)h<-h+12 else if(h==12)h<-24 else if(h>=0&&h<=6)h<-h+24 else return(NA_real_);h+m/60
}
parse_date<-function(x){for(fmt in c("%m/%d/%Y","%m/%d/%y","%Y-%m-%d","%m-%d-%Y","%m-%d-%y")){d<-as.Date(clean(x),format=fmt);if(!is.na(d))return(d)};as.Date(NA)}
season_from_month<-function(m){if(m%in%c(8,9,10))"fall" else if(m%in%c(11,12,1))"winter" else if(m%in%c(2,3,4))"spring" else if(m%in%c(5,6,7))"summer" else stop("bad month")}
sha256sum<-function(path){sub(" .*","",system2("sha256sum",path,stdout=TRUE)[1])}
download_source<-function(){dir.create(dirname(CACHE),recursive=TRUE,showWarnings=FALSE);download.file(URL,CACHE,mode="wb",quiet=TRUE);if(!identical(sha256sum(CACHE),SHA256))stop("checksum mismatch");read.csv(CACHE,stringsAsFactors=FALSE,check.names=FALSE)}

nightly_first_rows<-function(raw){
 rows<-list();k<-0L
 for(i in seq_len(nrow(raw))){
  sp<-toupper(clean(raw$species[i]));grid<-clean(raw$grid[i]);uid<-clean(raw$unique_ID[i]);ds<-clean(raw$date[i]);flag<-toupper(clean(raw$flag[i]));tt<-parse_time(raw$time[i]);dd<-parse_date(ds)
  if(!(sp%in%FOCAL)||!nzchar(grid)||!nzchar(uid)||!(flag%in%FLAGS)||!is.finite(tt)||is.na(dd))next
  k<-k+1L;rows[[k]]<-data.frame(row_index=i,species=sp,grid=grid,uid=uid,date=ds,date_obj=dd,season=season_from_month(as.integer(format(dd,"%m"))),flag=flag,time=tt,stringsAsFactors=FALSE)
 }
 x<-do.call(rbind,rows);key<-paste(x$species,x$grid,x$uid,x$date,sep="|");spl<-split(seq_len(nrow(x)),key)
 idx<-vapply(spl,function(ii){z<-x[ii,,drop=FALSE];ii[order(z$time,z$row_index)[1]]},integer(1));y<-x[idx,,drop=FALSE];rownames(y)<-NULL;y
}
split_dates<-function(z){d<-sort(unique(z$date_obj));h<-floor(length(d)/2);if(length(d)%%2==0)list(e=d[seq_len(h)],l=d[(h+1):length(d)],m=as.Date(NA)) else list(e=d[seq_len(h)],l=d[(h+2):length(d)],m=d[h+1])}
build_matrix<-function(z,species,dates){zz<-z[z$species%in%species&z$date_obj%in%dates,,drop=FALSE];m<-matrix(0L,nrow=length(species),ncol=length(FLAGS),dimnames=list(species,FLAGS));if(nrow(zz))for(i in seq_len(nrow(zz)))m[zz$species[i],zz$flag[i]]<-1L;m}
matched_overlap<-function(E,L)sum((E>0)&(L>0))

prepare_unit<-function(nf,id){
 p<-strsplit(id,"|",fixed=TRUE)[[1]];z<-nf[nf$grid==p[1]&nf$season==p[2],,drop=FALSE];sp<-split_dates(z)
 e0<-z[z$date_obj%in%sp$e,,drop=FALSE];l0<-z[z$date_obj%in%sp$l,,drop=FALSE]
 bridge<-intersect(unique(paste(e0$species,e0$uid,sep="|")),unique(paste(l0$species,l0$uid,sep="|")))
 e<-e0[!(paste(e0$species,e0$uid,sep="|")%in%bridge),,drop=FALSE];l<-l0[!(paste(l0$species,l0$uid,sep="|")%in%bridge),,drop=FALSE]
 elig<-FOCAL[vapply(FOCAL,function(s)length(unique(e$uid[e$species==s]))>=1&&length(unique(l$uid[l$species==s]))>=1,logical(1))]
 if(length(elig)<3)stop(paste("support mismatch",id))
 E<-build_matrix(e,elig,sp$e);L<-build_matrix(l,elig,sp$l);cols<-colSums(L)>0;E<-E[,cols,drop=FALSE];L<-L[,cols,drop=FALSE]
 list(id=id,grid=p[1],season=p[2],species=elig,bridge_n=length(bridge),E=E,L=L)
}
run_null<-function(u,seed){
 obs<-matched_overlap(u$E,u$L);set.seed(seed);m<-u$L;for(i in seq_len(BURN))m<-EcoSimR::sim9_single(m)
 sim<-numeric(NREPS);for(i in seq_len(NREPS)){m<-EcoSimR::sim9_single(m);sim[i]<-matched_overlap(u$E,m)}
 mu<-mean(sim);sdv<-sd(sim);z<-if(is.finite(sdv)&&sdv>0)(obs-mu)/sdv else NA_real_;p<-(1+sum(sim>=obs))/(NREPS+1)
 list(obs=obs,mu=mu,sd=sdv,z=z,p=p,sim=sim)
}
signflip_grid<-function(gridmeans){
 vals<-as.numeric(gridmeans);obs<-mean(vals);G<-length(vals);stats<-numeric(2^G)
 for(k in 0:(2^G-1)){bits<-as.integer(intToBits(k))[seq_len(G)];sgn<-ifelse(bits==1,1,-1);stats[k+1]<-mean(vals*sgn)}
 list(observed=obs,p=sum(stats>=obs-1e-15)/length(stats),patterns=length(stats),positive=sum(vals>0),negative=sum(vals<0))
}

if("--self-test"%in%args){stopifnot(matched_overlap(matrix(c(1,0,0,1),2),matrix(c(1,0,1,0),2))==1);cat("self-test ok\n");quit(status=0)}

support<-fromJSON(SUPPORT,simplifyVector=FALSE)
eligible_ids<-vapply(Filter(function(u)as.integer(u$eligible_species_count)>=3,support$units),function(u)u$id,character(1))
if(length(eligible_ids)!=18)stop(paste("expected 18 supported units, got",length(eligible_ids)))
raw<-download_source();nf<-nightly_first_rows(raw);units<-lapply(eligible_ids,function(id)prepare_unit(nf,id));names(units)<-eligible_ids

res<-list();nulls<-list()
for(i in seq_along(units)){
 u<-units[[i]];rr<-run_null(u,BASE_SEED+i);nulls[[u$id]]<-rr$sim
 res[[i]]<-list(id=u$id,grid=u$grid,season=u$season,species=u$species,species_count=length(u$species),bridge_individuals_removed=u$bridge_n,
                 observed_overlap=rr$obs,null_mean=rr$mu,null_sd=rr$sd,z=if(is.finite(rr$z))rr$z else NULL,p_upper=rr$p,seed=BASE_SEED+i)
}
info<-which(vapply(res,function(x)!is.null(x$z)&&is.finite(x$z),logical(1)));ninfo<-length(info);npos<-sum(vapply(res,function(x)!is.null(x$z)&&is.finite(x$z)&&x$z>0,logical(1)))
ids<-vapply(res[info],function(x)x$id,character(1));mus<-setNames(vapply(res[info],function(x)x$null_mean,numeric(1)),ids);sds<-setNames(vapply(res[info],function(x)x$null_sd,numeric(1)),ids)
if(ninfo){
 Tobs<-mean(vapply(res[info],function(x)x$z,numeric(1)));Tnull<-numeric(NREPS)
 for(b in seq_len(NREPS))Tnull[b]<-mean(vapply(ids,function(id)(nulls[[id]][b]-mus[[id]])/sds[[id]],numeric(1)))
 pglobal<-(1+sum(Tnull>=Tobs))/(NREPS+1)
}else{Tobs<-pglobal<-NA_real_}

gridvals<-tapply(vapply(res,function(x)if(is.null(x$z))NA_real_ else as.numeric(x$z),numeric(1)),vapply(res,function(x)x$grid,character(1)),function(v)mean(v[is.finite(v)]))
gridvals<-gridvals[is.finite(gridvals)];gf<-signflip_grid(gridvals)
unit_pass<-ninfo>=12&&npos>=12&&is.finite(Tobs)&&Tobs>0&&is.finite(pglobal)&&pglobal<0.05
grid_pass<-length(gridvals)==6&&gf$positive>=5&&gf$p<0.05

result<-list(
 schema="neon.san_jacinto_turnover_generalization.v1",status="stage8_post_result_generalization_complete",
 frozen_design="docs/SAN_JACINTO_TRANSITION_NICHE_EXPLORATION_V1.md",
 design=list(source_units=22,eligible_units=eligible_ids,turnover_rule="identical to Stage7",n_replicates=NREPS,burn_in=BURN,seed_base=BASE_SEED),
 primary=list(informative_units=ninfo,positive_z_units=npos,global_mean_z=if(is.finite(Tobs))Tobs else NULL,global_p_upper=if(is.finite(pglobal))pglobal else NULL,
              unit_level_robustness_pass=unit_pass,
              grid_means=as.list(gridvals),grid_positive=gf$positive,grid_negative=gf$negative,grid_exact_signflip_p_upper=gf$p,grid_sign_patterns=gf$patterns,
              grid_level_robustness_pass=grid_pass,
              decision=if(unit_pass&&grid_pass)"broader_turnover_generalization_supported" else "broader_turnover_generalization_not_supported"),
 units=res,
 claim_boundary=list(confirmatory=FALSE,can_rescue_stage7=FALSE,habitat_mechanism_identified=FALSE,competition_causally_identified=FALSE,species_pair_decomposition_opened=FALSE)
)
dir.create(dirname(OUT),recursive=TRUE,showWarnings=FALSE);writeLines(toJSON(result,pretty=TRUE,auto_unbox=TRUE,digits=10,na="null"),OUT);cat(toJSON(result$primary,pretty=TRUE,auto_unbox=TRUE,digits=10,na="null"),"\n")
