"""Synthetic raster tests. The dedicated pilot workflow installs rasterio."""
import hashlib
import unittest
try:
    import numpy as np
    from rasterio.io import MemoryFile
    from rasterio.transform import from_origin
except ImportError:
    raise unittest.SkipTest('rasterio is installed and tested in the dedicated E5 CHM workflow')
from analysis.neon_e5_chm_pilot_v1 import (
    latest_month_before_cutoff, tile_lower_left, chm_manifest,
    inspect_reference_pixel, verify_raster_bytes,
)


def raster_bytes(nodata=-9999.,value=7.,crs='EPSG:32610'):
    a=np.full((1000,1000),value,dtype='float32')
    with MemoryFile() as mem:
        with mem.open(driver='GTiff',height=1000,width=1000,count=1,
                      dtype='float32',crs=crs,transform=from_origin(500000,5001000,1,1),
                      nodata=nodata,compress='deflate') as dst:
            dst.write(a,1)
        return mem.read()

class PilotTests(unittest.TestCase):
    def test_no_silent_later_year_or_nearest_year(self):
        self.assertEqual(latest_month_before_cutoff(['2024-07','2025-09','2026-02']), '2025-09')
        self.assertIsNone(latest_month_before_cutoff(['2026-01']))
        with self.assertRaises(ValueError):latest_month_before_cutoff(['bad'])
    def test_only_explicit_chm_tile_filename(self):
        self.assertEqual(tile_lower_left('NEON_D16_WREF_DP3_500000_5000000_CHM.tif'),(500000,5000000))
        self.assertIsNone(tile_lower_left('NEON_D16_WREF_DP3_500000_5000000_DTM.tif'))
    def test_manifest_requires_exact_release_and_nonprovisional_package(self):
        f={'name':'NEON_D16_WREF_DP3_500000_5000000_CHM.tif','url':'https://data.neonscience.org/file.tif','size':100,'md5':'a'*32}
        p={'data':{'releases':[{'release':'RELEASE-2026','packages':[{'siteCode':'WREF','month':'2025-09','packageType':'basic','files':[f]}]}]}}
        out=chm_manifest(p,'WREF',2025)
        self.assertEqual(len(out),1)
        self.assertEqual(out[0]['tile_easting'],500000)
        p['data']['releases'][0]['release']='PROVISIONAL'
        with self.assertRaises(ValueError):chm_manifest(p,'WREF',2025)
    def test_byte_checksum_checked_before_raster_read(self):
        b=b'foo';m={'size':3,'md5':hashlib.md5(b).hexdigest()}
        verify_raster_bytes(b,m)
        with self.assertRaises(ValueError):verify_raster_bytes(b,{'size':3,'md5':'0'*32})
    def test_real_geotiff_coordinate_sample_valid_without_station_inference(self):
        out=inspect_reference_pixel(raster_bytes(),500500.5,5000500.5,32610,2.)
        self.assertEqual(out['status'],'VALID_REFERENCE_PIXEL')
        self.assertEqual(out['height_m'],7.)
        self.assertEqual(out['uncertainty_window_valid_fraction'],1.)
        self.assertFalse(out['historical_station_environment_verified'])
        self.assertNotIn('500500',str(out))
    def test_zero_height_is_valid_not_nodata(self):
        r=inspect_reference_pixel(raster_bytes(value=0.),500500.5,5000500.5,32610,0.2)
        self.assertEqual(r['status'],'VALID_REFERENCE_PIXEL')
        self.assertEqual(r['height_m'],0.)
        self.assertFalse(r['zero_means_bare_ground'])
    def test_nodata_not_replaced_by_zero(self):
        r=inspect_reference_pixel(raster_bytes(value=-9999.),500500.5,5000500.5,32610,1.)
        self.assertEqual(r['status'],'REFERENCE_PIXEL_NODATA')
        self.assertIsNone(r['height_m'])
    def test_wrong_crs_or_outside_extent_stops(self):
        r=inspect_reference_pixel(raster_bytes(),500500.5,5000500.5,32611,1.)
        self.assertEqual(r['status'],'CRS_MISMATCH')
        r=inspect_reference_pixel(raster_bytes(),501500.,5000500.,32610,1.)
        self.assertEqual(r['status'],'OUTSIDE_RASTER')
    def test_missing_uncertainty_is_never_assumed_zero(self):
        r=inspect_reference_pixel(raster_bytes(),500500.,5000500.,32610,None)
        self.assertEqual(r['status'],'VALID_REFERENCE_PIXEL')
        self.assertIsNone(r['uncertainty_window_valid_fraction'])
        self.assertFalse(r['coordinate_uncertainty_known'])

if __name__=='__main__':unittest.main()
