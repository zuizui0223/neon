import unittest
from analysis.audit_future_neon_plot_structure_v1 import (
    event_structure, select_provisional_plot_files,
)


class FuturePlotSupportTests(unittest.TestCase):
    def test_excludes_current_release_and_unmatched_month(self):
        candidate={("ABBY","2026-07")}
        def f(path):
            return {"name":path,"url":"https://file.test/c.csv",
                    "size":123,"md5":"a"*32}
        q={"data":{"releases":[
            {"release":"RELEASE-2026","packages":[{"siteCode":"ABBY","month":"2026-06",
                  "packageType":"basic","files":[f("mam_perplotnight_old.csv")]}]},
            {"release":"PROVISIONAL","packages":[
                {"siteCode":"ABBY","month":"2026-07","packageType":"basic",
                 "files":[f("mam_perplotnight_new.csv"),f("mam_pertrapnight_new.csv")]},
                {"siteCode":"ABBY","month":"2026-06","packageType":"basic",
                 "files":[f("mam_perplotnight_new.csv")]}
            ]}
        ]}}
        out=select_provisional_plot_files(q,candidate)
        self.assertEqual(len(out["files"]),1)
        self.assertEqual(out["files"][0]["name"],"mam_perplotnight_new.csv")
        self.assertEqual(out["files"][0]["release"],"PROVISIONAL")

    def test_count_only_complete_three_night_bouts(self):
        rows=[]
        for site, plot, event, n, completion in (
                ("ABBY","P1","A",3,"setting complete, processing complete"),
                ("ABBY","P1","B",2,"setting complete, processing complete"),
                ("ABBY","P2","C",3,"incomplete"),
                ("SRER","P9","D",3,"setting complete, processing complete")
        ):
            rows += [{"siteID":site,"plotID":plot,"eventID":event,
                      "nightuid":f"{event}{i}","gridCompletion":completion,
                      "collectDate":f"2026-07-{i+1:02d}"}
                      for i in range(n)]
        v=event_structure(rows)
        self.assertEqual(v["exact_three_night_complete_standard_events"],1)
        self.assertEqual(v["exact_three_night_not_complete"],1)
        self.assertEqual(v["eligible_distinct_sites"],1)
        self.assertFalse(v["capture_or_taxon_support_estimated"])


if __name__=="__main__":
    unittest.main()
