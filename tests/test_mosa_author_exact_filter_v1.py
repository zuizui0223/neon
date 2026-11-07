"""Replay only the authors' published RMarkdown deletion/date-correction syntax."""
import unittest
from datetime import date

from analysis.audit_mosa_author_exact_filter_v1 import (
    parse_author_filter_commands, replay_author_schedule, source_first_species,
)


class MOSAAuthorExactFilterTests(unittest.TestCase):
    def test_deletions_are_source_date_indices_not_calendar_months(self):
        rmd='''MN=MN[-(which(MN[,2]==xx[3,2])),]
MN=MN[-(which(MN[,2]==xx[4,2])),]
MN[(which(MN[,2]==xx[5,2])),2]=as.Date("1994-03-18")
'''
        cmds=parse_author_filter_commands(rmd, expected_deletions=None)
        self.assertEqual(cmds["removed_original_unique_date_indices"],[3,4])
        self.assertEqual(cmds["corrected_source_date_index"],5)
        self.assertEqual(cmds["corrected_to_date"],"1994-03-18")
        records=[
            {"DATE":"10/03/1994","TOE":"a","SPECIES":"MN"},
            {"DATE":"11/03/1994","TOE":"a","SPECIES":"MN"},
            {"DATE":"12/03/1994","TOE":"b","SPECIES":"MN"},
            {"DATE":"13/03/1994","TOE":"b","SPECIES":"MN"},
            {"DATE":"14/03/1994","TOE":"c","SPECIES":"NA"},
        ]
        replay=replay_author_schedule(
            records,"DATE",cmds,expected_author_days=None)
        self.assertEqual(replay["retained_days"],{
            date(1994,3,10),date(1994,3,11),date(1994,3,18)})
        self.assertEqual(len(replay["retained_rows"]),3)
        self.assertEqual(replay["retained_rows"][-1]["TOE"],"c")

    def test_author_first_retained_species_avoids_later_species_reassignment(self):
        raw=[
            {"TOE":"a","SPECIES":"NA"},
            {"TOE":"a","SPECIES":"MN"},
            {"TOE":"b","SPECIES":"MN"},
            {"TOE":"b","SPECIES":"LR"},
            {"TOE":"NO_CAPTURE","SPECIES":"NA"},
        ]
        labels=source_first_species(raw,"TOE","SPECIES")
        self.assertEqual(labels["a"],"NA")
        self.assertEqual(labels["b"],"MN")
        self.assertNotIn("NO_CAPTURE",labels)

    def test_unknown_author_syntax_does_not_silently_guess(self):
        with self.assertRaisesRegex(ValueError,"no explicit date deletion"):
            parse_author_filter_commands('MN <- subset(MN, DATE>0)',
                                         expected_deletions=None)

    def test_duplicated_deletion_index_is_invalid(self):
        x='''MN=MN[-(which(MN[,2]==xx[3,2])),]
MN=MN[-(which(MN[,2]==xx[3,2])),]
MN[(which(MN[,2]==xx[5,2])),2]=as.Date("1994-03-18")
'''
        with self.assertRaisesRegex(ValueError,"duplicate"):
            parse_author_filter_commands(x,expected_deletions=None)


if __name__=="__main__":
    unittest.main()
