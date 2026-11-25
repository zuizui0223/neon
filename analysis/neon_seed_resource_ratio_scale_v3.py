"""Xiao et al. 2013 Table 1, Model A. Published-model reparameterization only.
DOI 10.1111/1365-2745.12113. No raw observations or refitting.
"""
import math,json
ROWS={
 'removal':(-2.030,1.233,0.162,1.180),
 'primary_cache':(-3.466,0.951,1.887,0.917),
 'secondary_cache':(-4.973,1.926,2.425,1.761),
 'survival_at_source':(12.389,4.484,-6.301,3.426),
 'survival_at_cache':(-3.076,1.208,0.713,1.067),
}
def calculate():
 result={}
 for endpoint,(a,sa,b,sb) in ROWS.items():
  scale=a+b
  # Unknown coefficient covariance: largest possible SE by Cauchy-Schwarz.
  se_max=sa+sb
  lim=[scale-1.96*se_max,scale+1.96*se_max]
  result[endpoint]={'beta_log10_crop':a,'beta_log10_consumer':b,'beta_log10_scale_at_fixed_ratio':round(scale,6), 'odds_ratio_joint_doubling':round(math.exp(scale*math.log10(2)),6),'worst_covariance_normal_interval': [round(x,6) for x in lim], 'excludes_zero_for_all_covariances':lim[0]>0 or lim[1]<0}
  assert math.isclose(a*math.log10(2)+b*math.log10(2),scale*math.log10(2))
 assert not any(x['excludes_zero_for_all_covariances'] for x in result.values())
 return result
if __name__=='__main__':
 print(json.dumps({'status':'PUBLISHED_MODEL_REPARAMETERIZATION_NO_NEW_FIT','warning':'Reported spreads match estimate/z and are treated as approximate SE; covariance unavailable; conservative normal envelopes, not cluster-calibrated confidence intervals.','results':calculate()},indent=2))
