"""Synthetic-only integrity tests for running original published PNAS C++ configs."""
import unittest
from analysis.reproduce_ranc_2021_published_memory_models_v1 import (
    corrected_paths_only,git_blob,MODELS
)
import hashlib

def fake_original(model_type="3"):
    return ("parameter;value\n"
            "output_directory_path;/Path/to/outputs/\n"
            "time_series_path;/Path/to/time.txt\n"
            "initialization_data_path;/Path/to/init.txt\n"
            f"model_type;{model_type}\n"
            "fs_light_i_beta;-0.4\n"
            "fs_light_r_beta;-0.2\n"
            "fs_light_abs_r_beta;0\n"
            "fs_min_daily_temp_beta;-0.1\n"
            "fs_res_pres_beta;-4\n"
            "fs_res_pres_within_beta;-0.08\n"
            "fs_res_access_beta;1.2\n"
            "fs_res_access_within_beta;0.9\n"
            "manipulated_fs_pref;0.4\n"
            "ref_decay_rate;0.008\n"
            "att_decay_rate;0.048\n")

def paths():
    return {"output_directory_path":"/tmp/model/",
            "time_series_path":"/tmp/original/data.txt",
            "initialization_data_path":"/tmp/original/init.txt"}

class OriginalPNASFittedModelPositiveControlTests(unittest.TestCase):
    def test_only_local_paths_change_and_all_original_numeric_values_survive(self):
        orig=fake_original("3")
        patched=corrected_paths_only(orig,paths(),"3")
        self.assertIn("output_directory_path;/tmp/model/\n",patched)
        self.assertIn("ref_decay_rate;0.008\n",patched)
        self.assertIn("att_decay_rate;0.048\n",patched)
        self.assertIn("model_type;3\n",patched)
        for val in ("-0.4","1.2","0.048"):
            self.assertIn(";"+val+"\n",patched)
        self.assertNotEqual(orig,patched)

    def test_exact_author_terminal_blank_lines_preserved(self):
        original=fake_original("3")+"\n"
        patched=corrected_paths_only(original,paths(),"3")
        self.assertTrue(patched.endswith("att_decay_rate;0.048\n\n"))
        self.assertEqual(len(patched.splitlines(keepends=True)),
                         len(original.splitlines(keepends=True)))

    def test_model_type_not_relabelled_memory_as_perception(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            corrected_paths_only(fake_original("1"),paths(),"3")

    def test_extra_source_param_refused(self):
        inp=fake_original("3").replace(
            "att_decay_rate;0.048\n",
            "att_decay_rate;0.048\nextra_adjusted_param;1\n"
        )
        with self.assertRaisesRegex(ValueError,"CONFIG_PARAMS_CHANGED"):
            corrected_paths_only(inp,paths(),"3")

    def test_malformed_or_duplicate_source_config_refused(self):
        text=fake_original("3").replace("parameter;value\n","something;else\n")
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            corrected_paths_only(text,paths(),"3")
        text=fake_original("3").replace(
            "ref_decay_rate;0.008\n","ref_decay_rate;0.008\nref_decay_rate;0.1\n"
        )
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            corrected_paths_only(text,paths(),"3")

    def test_source_only_paths_and_safe_no_semicolon_or_newline(self):
        p=paths()
        p["time_series_path"]="/tmp/foo\nmodel_type;0"
        with self.assertRaisesRegex(ValueError,"INVALID_NEW_LOCAL_PATH"):
            corrected_paths_only(fake_original(),p,"3")

    def test_source_git_blob_hash_is_verifiable(self):
        b=b"abc\n"
        expected=hashlib.sha1(b"blob 4\x00abc\n").hexdigest()
        self.assertEqual(git_blob(b),expected)

    def test_exact_original_three_published_model_types_and_checksums_pinned(self):
        self.assertEqual({k:v[2] for k,v in MODELS.items()},
                         {"omniscience":"0","perception":"1","memory":"3"})
        self.assertTrue(all(len(v[1])==40 for v in MODELS.values()))

if __name__=="__main__":
    unittest.main()
