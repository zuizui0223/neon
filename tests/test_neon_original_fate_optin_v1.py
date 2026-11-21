"""Verify opt-in mammal fate capture uses original source column with zero drift.

Pure synthetic data; old trap rows must be byte-equivalent when fate
is not requested. Unknown fate is missing, NEVER assumed released.
"""
import csv
import io
import unittest
from analysis.run_multiscale_density_estimability_release2026_v3 import _read_trap_rows
from analysis.run_neon_two_genus_source_v1 import original_sources_for_two_genus

def csv_bytes(include_fate=True):
    fields=["nightuid","plotID","trapCoordinate","trapStatus","tagID","taxonID","scientificName","taxonRank"]
    if include_fate:fields+=["fate"]
    buf=io.StringIO()
    writer=csv.DictWriter(buf,fieldnames=fields)
    writer.writeheader()
    rows=[{"nightuid":"N1","plotID":"P","trapCoordinate":"A1","trapStatus":"5 - capture",
           "tagID":"TEMP00001","taxonID":"TX","scientificName":"Faux genus","taxonRank":"genus",
           "fate":"Released"},
          {"nightuid":"N2","plotID":"P","trapCoordinate":"B1","trapStatus":"5 - capture",
           "tagID":"TEMP00002","taxonID":"TX","scientificName":"Faux genus","taxonRank":"genus",
           "fate":"Dead"}]
    writer.writerows([{key:row.get(key,"") for key in fields} for row in rows])
    return buf.getvalue().encode()

class OptInOriginalFateTests(unittest.TestCase):
    def test_original_default_source_record_has_no_added_fate_or_column_key(self):
        raw=csv_bytes()
        base=_read_trap_rows(raw,{"N1","N2"})
        self.assertEqual(len(base),2)
        self.assertNotIn("fate",base[0])
        self.assertNotIn("_fate_column_present",base[0])
        opted=_read_trap_rows(raw,{"N1","N2"},include_fate=True)
        self.assertEqual(len(opted),len(base))
        for orig,plus in zip(base,opted):
            self.assertEqual(orig,{key:value for key,value in plus.items()
                                   if key not in ("fate","_fate_column_present")})
            self.assertTrue(plus["_fate_column_present"])
        self.assertEqual([x["fate"] for x in opted],["Released","Dead"])

    def test_missing_fate_column_is_explicitly_missing_not_released(self):
        raw=csv_bytes(include_fate=False)
        opted=_read_trap_rows(raw,{"N1"},include_fate=True)
        self.assertEqual(len(opted),1)
        self.assertEqual(opted[0]["fate"],"")
        self.assertFalse(opted[0]["_fate_column_present"])

    def test_original_night_subsetting_identical_with_fate_optin(self):
        raw=csv_bytes()
        original=_read_trap_rows(raw,{"N2"})
        expanded=_read_trap_rows(raw,{"N2"},include_fate=True)
        self.assertEqual(len(original),1)
        self.assertEqual(expanded[0]["nightuid"],"N2")
        self.assertEqual(expanded[0]["fate"],"Dead")
        self.assertEqual(original[0]["tagID"],expanded[0]["tagID"])

    def test_public_source_load_refuses_including_private_fate_without_private_return(self):
        with self.assertRaisesRegex(ValueError,"Fate must remain private"):
            original_sources_for_two_genus(include_capture_fate=True)

if __name__=="__main__":
    unittest.main()
