"""Source-only E5/CHM pilot. No station reconstruction or ecology regression."""
from __future__ import annotations
import hashlib
import math
import re
import numpy as np
from rasterio.io import MemoryFile
from rasterio.windows import Window

PRODUCT='DP3.30015.001'
RELEASE='RELEASE-2026'
CUTOFF_YEAR=2025


def latest_month_before_cutoff(months):
    valid=[]
    for month in months:
        if not isinstance(month,str) or not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])',month):
            raise ValueError('invalid source acquisition month')
        if 2015<=int(month[:4])<=CUTOFF_YEAR:valid.append(month)
    return max(valid) if valid else None


def tile_lower_left(name):
    m=re.search(r'_(\d{5,6})_(\d{6,7})_CHM\.tif$',str(name),re.I)
    return (int(m[1]),int(m[2])) if m else None


def chm_manifest(payload,site,year):
    blocks=[b for b in payload.get('data',{}).get('releases',[]) if b.get('release')==RELEASE]
    if len(blocks)!=1:raise ValueError('exact released CHM block absent')
    found={}
    for p in blocks[0].get('packages',[]):
        if p.get('siteCode')!=site or p.get('packageType')!='basic':continue
        month=p.get('month','')
        if not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])',month) or int(month[:4])!=year:
            raise ValueError('source CHM acquisition year mismatch')
        for r in p.get('files',[]):
            xy=tile_lower_left(r.get('name'))
            if xy is None:continue
            if not re.fullmatch('[0-9a-fA-F]{32}',str(r.get('md5',''))):raise ValueError('CHM missing MD5')
            size=r.get('size');url=r.get('url','')
            if isinstance(size,bool) or not isinstance(size,int) or size<=0 or not url.startswith('https://'):
                raise ValueError('invalid source CHM byte metadata')
            row={'name':r['name'],'url':url,'size':size,'md5':r['md5'].lower(),
                 'site':site,'month':month,'tile_easting':xy[0],'tile_northing':xy[1]}
            key=(month,row['name'])
            if key in found and found[key]!=row:raise ValueError('conflicting repeated CHM tile')
            found[key]=row
    return [found[k] for k in sorted(found)]


def verify_raster_bytes(raw,meta):
    if len(raw)!=meta['size'] or hashlib.md5(raw).hexdigest()!=meta['md5'].lower():
        raise ValueError('CHM bytes fail official size/MD5')


def inspect_reference_pixel(raw,x,y,epsg,uncertainty_m):
    if not all(math.isfinite(float(v)) for v in (x,y)):
        raise ValueError('nonfinite projected E5 coordinate')
    if uncertainty_m is not None and (not math.isfinite(uncertainty_m) or uncertainty_m<0):
        raise ValueError('invalid coordinate uncertainty')
    base={'height_m':None,'coordinate_uncertainty_known':uncertainty_m is not None,
          'uncertainty_window_valid_fraction':None,'uncertainty_window_height_range_m':None,
          'zero_means_bare_ground':False,'historical_station_environment_verified':False,
          'site_coordinates_or_sample_identifiers_exported':False}
    with MemoryFile(raw) as mem,mem.open() as ds:
        if ds.crs is None or ds.crs.to_epsg()!=epsg:return {**base,'status':'CRS_MISMATCH'}
        if ds.count!=1 or any(abs(abs(r)-1)>1e-6 for r in ds.res):
            return {**base,'status':'NOT_SINGLE_BAND_ONE_METRE_CHM'}
        if abs(ds.transform.b)>1e-8 or abs(ds.transform.d)>1e-8:
            return {**base,'status':'UNSUPPORTED_ROTATED_RASTER'}
        row,col=ds.index(x,y)
        if not(0<=row<ds.height and 0<=col<ds.width):return {**base,'status':'OUTSIDE_RASTER'}
        a=ds.read(1,window=Window(col,row,1,1),masked=True)
        if np.ma.is_masked(a[0,0]) or not math.isfinite(float(a[0,0])):
            return {**base,'status':'REFERENCE_PIXEL_NODATA'}
        h=float(a[0,0]);out={**base,'status':'VALID_REFERENCE_PIXEL','height_m':h,
                           'negative_height_flag':h<0,'raster_resolution_m':list(ds.res)}
        if uncertainty_m is not None and uncertainty_m<=50:
            # Square neighbourhood, not a calibrated confidence region.
            n=max(1,math.ceil(uncertainty_m+math.sqrt(.5)))
            left=max(0,col-n);top=max(0,row-n)
            right=min(ds.width,col+n+1);bottom=min(ds.height,row+n+1)
            w=ds.read(1,window=Window(left,top,right-left,bottom-top),masked=True)
            mask=np.ma.getmaskarray(w)|~np.isfinite(w.data)
            valid=w.data[~mask]
            out['uncertainty_window_valid_fraction']=float(valid.size/w.size)
            out['uncertainty_window_height_range_m']=[float(valid.min()),float(valid.max())] if valid.size else None
            out['uncertainty_window_clipped_at_tile_boundary']=(left!=col-n or top!=row-n or right!=col+n+1 or bottom!=row+n+1)
        return out
