"""Effect-blind comparison of future complete events to all frozen identities."""
import unittest
from analysis.audit_future_neon_release_disjointness_v1 import compare_identifiers

COMPLETE = "setting complete, processing complete"


def bout(site,plot,event,prefix):
    return [{"siteID":site,"plotID":plot,"eventID":event,
             "nightuid":f"{prefix}{k}","gridCompletion":COMPLETE,
             "collectDate":f"2026-07-{k+1:02d}"} for k in range(3)]


class DisjointnessTests(unittest.TestCase):
    def test_valid_release_disjointness(self):
        frozen = bout("ABBY","P1","old-event","A")
        future = bout("ABBY","P1","future-event","B")
        result = compare_identifiers(frozen,future)
        self.assertEqual(result["status"],"IDENTIFIER_DISJOINTNESS_PASS")
        self.assertEqual(result["candidate_complete_events"],1)
        self.assertEqual(result["overlapping_event_count"],0)
        self.assertEqual(result["overlapping_nightuid_count"],0)
        self.assertFalse(result["future_W_B_opened"])

    def test_shared_event_fails_even_when_nights_differ(self):
        frozen=bout("HARV","P2","event-same","A")
        future=bout("HARV","P2","event-same","B")
        result=compare_identifiers(frozen,future)
        self.assertEqual(result["status"],"STOP_OVERLAPPING_FROZEN_RELEASE_IDENTIFIERS")
        self.assertEqual(result["overlapping_event_count"],1)
        self.assertEqual(result["overlapping_nightuid_count"],0)

    def test_shared_night_fails_even_when_events_differ(self):
        frozen=bout("HARV","P2","old","A")
        future=bout("HARV","P2","new","A")
        result=compare_identifiers(frozen,future)
        self.assertEqual(result["overlapping_event_count"],0)
        self.assertEqual(result["overlapping_nightuid_count"],3)
        self.assertEqual(result["status"],"STOP_OVERLAPPING_FROZEN_RELEASE_IDENTIFIERS")

    def test_incomplete_future_is_not_candidate(self):
        frozen=bout("HARV","P2","old","A")
        future=bout("HARV","P2","new","B")[:2]
        with self.assertRaisesRegex(RuntimeError,"empty source"):
            compare_identifiers(frozen,future)

    def test_frozen_conflicting_night_uid_stops(self):
        frozen=bout("ABBY","P1","a","A")
        frozen.append({**frozen[0],"eventID":"b"})
        with self.assertRaisesRegex(RuntimeError,"conflicting night"):
            compare_identifiers(frozen,bout("ABBY","P1","future","B"))

if __name__ == "__main__":
    unittest.main()
