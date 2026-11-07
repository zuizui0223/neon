"""Synthetic tests of pre-effect worst-case observed-identity warning removal."""
import unittest
from analysis.audit_mosa_warning_removal_support_v1 import (
    conservative_warning_exclusion_support,
)

FIELDS = ["NUMBER","DATE","GRID","SPECIES","X","Y","WEIGHT",
          "TOE","SX","SEXCON","FLAGS"]


def row(t, d, *, x="3", y="B", sx="M", sp="MN"):
    return dict(NUMBER="1", DATE=d, GRID="MOSA", SPECIES=sp,
                X=x, Y=y, WEIGHT="20", TOE=t, SX=sx,
                SEXCON="AN", FLAGS="")


def data(tags, dates=("13/07/2000", "14/07/2000")):
    return [row(t,d) for t in tags for d in dates]


def month(s="2000-07", m=5, n=12):
    return dict(year_month=s, year=int(s[:4]), month=int(s[-2:]), m=m, MNA=n)


def check(rows, tags, strict, **kw):
    return conservative_warning_exclusion_support(
        rows, FIELDS, set(tags), set(), strict, **kw
    )


class WarningRemovalTests(unittest.TestCase):
    def test_multi_station_key_reduces_five_to_four(self):
        rec=data("abcde")
        rec.append(row("a","13/07/2000",x="4"))
        a=check(rec,"abcde",[month()])
        self.assertEqual(a["station_warning_codes"],1)
        self.assertEqual(a["original_repeat_supported_code_month_pairs"],5)
        self.assertEqual(a["warning_affected_original_repeat_code_month_pairs"],1)
        self.assertEqual(a["months_newly_below_m5"],1)
        self.assertEqual(a["months_m_ge5_after_worst_case_code_removal"],0)
        self.assertEqual(a["status"],"STOP_WARNING_REMOVAL_INSUFFICIENT_SUPPORT")
        self.assertFalse(a["ecological_effects_opened"])

    def test_six_to_five_remains_supported(self):
        rec=data("abcdef")
        rec.append(row("a","13/07/2000",x="4"))
        a=check(rec,"abcdef",[month(m=6)],min_months=1,min_varying_years=0)
        self.assertEqual(a["months_m_ge5_after_worst_case_code_removal"],1)
        self.assertEqual(a["months_newly_below_m5"],0)
        self.assertEqual(a["months_by_m_reduction"],{1:1})

    def test_same_station_repeat_logging_is_not_warning(self):
        rec=data("abcde")
        rec.append(row("a","13/07/2000"))
        a=check(rec,"abcde",[month()])
        self.assertEqual(a["union_warning_codes"],0)
        self.assertEqual(a["months_newly_below_m5"],0)

    def test_cross_sex_even_outside_frozen_month_warns(self):
        rec=data("abcde")
        rec.append(row("a","13/08/2000",sx="F"))
        a=check(rec,"abcde",[month()])
        self.assertEqual(a["sex_warning_codes"],1)
        self.assertEqual(a["months_newly_below_m5"],1)
        self.assertEqual(a["warning_affected_original_months"],1)

    def test_unknown_SX_not_a_warning(self):
        rec=data("abcde")
        rec.append(row("a","13/08/2000",sx="NA"))
        a=check(rec,"abcde",[month()])
        self.assertEqual(a["sex_warning_codes"],0)

    def test_species_warning_not_a_relabel(self):
        rec=data("abcde")
        rec.append(row("a","13/08/2000",sp="TA"))
        a=check(rec,"abcde",[month()])
        self.assertEqual(a["species_warning_codes"],1)
        self.assertEqual(a["warning_affected_original_months"],1)

    def test_whitespace_exclusion_remains_excluded(self):
        rec=data("abcdef")
        rec.append(row("a","13/07/2000",x="4"))
        a=conservative_warning_exclusion_support(
            rec,FIELDS,set("abcdef"),{"a"},[month(m=5)])
        self.assertEqual(a["union_warning_codes"],0)
        self.assertEqual(a["original_repeat_supported_code_month_pairs"],5)

    def test_original_frozen_m_is_guarded(self):
        with self.assertRaisesRegex(ValueError,"Frozen within-month m"):
            check(data("abcde"),"abcde",[month(m=6)])

    def test_original_year_MNA_variation_preserved(self):
        rows = data("abcde")+data("abcde",("13/08/2000","14/08/2000"))
        a = check(rows,"abcde",[month(),month("2000-08",m=5,n=18)],
                  min_months=2,min_varying_years=1)
        self.assertEqual(a["years_with_ge2_distinct_FROZEN_MNA_levels_after_removal"],1)
        self.assertEqual(a["retained_months_in_FROZEN_MNA_varying_years"],2)
        self.assertEqual(a["status"],"OBSERVATION_SUPPORT_STRESS_PASS_ECOLOGY_STILL_HOLD")

    def test_row_order_invariant(self):
        rows=data("abcdef")+[row("a","13/07/2000",x="4")]
        a=check(rows,"abcdef",[month(m=6)],min_months=1,min_varying_years=0)
        b=check(list(reversed(rows)),"abcdef",[month(m=6)],min_months=1,min_varying_years=0)
        self.assertEqual(a,b)

    def test_no_labels_or_calendar_dates_in_output(self):
        code="PRIVATE_TOE_12345"
        tags={code,"b","c","d","e"}
        rows=data(tags)
        a=check(rows,tags,[month()])
        self.assertNotIn(code,str(a))
        self.assertNotIn("2000-07",str(a))
        self.assertTrue(a["original_TOE_values_dates_and_station_positions_exported"] is False)

if __name__=="__main__":
    unittest.main()
