import unittest
try:
    import rasterio
except ImportError:
    raise unittest.SkipTest('rasterio is installed and tested in the dedicated E5 CHM workflow')
from analysis import neon_chm_monthly_source_v2 as m

class MonthlyTests(unittest.TestCase):
    def payload(self,checksum=None):
        return {'data':{'release':'RELEASE-2026','productCode':'DP3.30015.001','siteCode':'TEST','month':'2024-07','files':[{'name':'NEON_D01_TEST_DP3_500000_5000000_CHM.tif','url':'https://example.org/file','size':3,'md5':None,'crc32':checksum}]}}
    def test_crc32c_known_vector_and_base64(self):
        self.assertEqual(m._crc32c(b'123456789'),0xe3069283)
        self.assertEqual(m._crc_integer('4waSgw=='),0xe3069283)
    def test_provider_unpadded_hex_crc32c_known_byte_vector(self):
        # CRC32C(b'319') = 0x0011fd1e: the NEON AOP metadata may omit
        # leading zero digits from its hexadecimal checksum string.
        self.assertEqual(m._crc32c(b'319'), 0x0011fd1e)
        self.assertEqual(m._crc_integer('11fd1e'), 0x0011fd1e)
        self.assertEqual(m._crc_integer('0x11fd1e'), 0x0011fd1e)
        self.assertEqual(m._crc_integer('0123456'), 0x0123456)
        self.assertEqual(m._crc_integer('1234567'), 0x1234567)
        p=self.payload()
        p['data']['files'][0]['crc32c']='11fd1e'
        p['data']['files'][0]['crc32']=None
        r=m.monthly_chm_manifest(p,'TEST','2024-07')
        self.assertEqual(r[0]['checksum_kind'],'crc32c')
        m.verify_raster_bytes(b'319',r[0])
        with self.assertRaisesRegex(ValueError,'checksum mismatch'):
            m.verify_raster_bytes(b'318',r[0])

    def test_malformed_crc_does_not_avoid_integrity_gate(self):
        for bad in ('zzzzzz','123456789','0x','-1','',None):
            p=self.payload()
            p['data']['files'][0]['crc32c']=bad
            p['data']['files'][0]['crc32']=None
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    m.monthly_chm_manifest(p,'TEST','2024-07')

    def test_monthly_parser_supported(self):
        r=m.monthly_chm_manifest(self.payload('8c736521'),'TEST','2024-07')
        self.assertEqual(r[0]['checksum_kind'],'crc32')
        m.verify_raster_bytes(b'foo',r[0])
    def test_crc_bytes_and_missing_digest(self):
        r=m.monthly_chm_manifest(self.payload('8c736521'),'TEST','2024-07')
        with self.assertRaises(ValueError):m.verify_raster_bytes(b'bar',r[0])
        with self.assertRaises(ValueError):m.monthly_chm_manifest(self.payload(),'TEST','2024-07')
    def test_provisional_or_other_month_rejected(self):
        p=self.payload('8c736521');p['data']['release']='PROVISIONAL'
        with self.assertRaises(ValueError):m.monthly_chm_manifest(p,'TEST','2024-07')
        with self.assertRaises(ValueError):m.monthly_chm_manifest(self.payload('8c736521'),'TEST','2024-08')

if __name__=='__main__':unittest.main()
