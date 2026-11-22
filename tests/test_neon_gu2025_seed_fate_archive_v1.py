"""Checks the distinction between an unassigned actor and an unknown seed fate."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from analysis.inspect_neon_gu2025_seed_fate_archive_v1 import (
    check_file, describe_rows, main, source_manifest,
)


class ArchiveRowsTests(unittest.TestCase):
    def test_repeated_seed_preserves_both_rows_and_no_identifier_leaks(self):
        result = describe_rows([
            {"Code": "private-a", "Fate": "SHI", "Dispersers": "Apodemus draco"},
            {"Code": "private-a", "Fate": "M", "Dispersers": "Apodemus draco"},
            {"Code": "private-b", "Fate": "EIS", "Dispersers": "Not triggered"},
            {"Code": "private-c", "Fate": "M", "Dispersers": "Not triggered"},
            {"Code": "private-d", "Fate": None, "Dispersers": None},
            {"Code": "private-e", "Fate": "IIS", "Dispersers": "undetermined"},
        ])
        self.assertEqual(result["archive_rows"], 6)
        self.assertEqual(result["distinct_seed_codes"], 5)
        self.assertEqual(result["repeated_code_groups"], 1)
        self.assertEqual(result["nonidentical_repeated_code_groups"], 1)
        self.assertEqual(result["rows_by_disperser_class_and_fate"], {
            "species_assigned": {"SHI": 1, "M": 1},
            "literal_not_triggered": {"EIS": 1, "M": 1},
            "blank": {"blank": 1}, "other": {"IIS": 1},
        })
        self.assertNotIn("private-", json.dumps(result))

    def test_equal_rows_are_counted_separately_from_nonidentical_rows(self):
        row = {"Code": "private-y", "Fate": "EAR", "Dispersers": "Not triggered"}
        result = describe_rows([row, row])
        self.assertEqual(result["archive_rows"], 2)
        self.assertEqual(result["nonidentical_repeated_code_groups"], 0)
        self.assertEqual(result["rows_by_disperser_class_and_fate"]["literal_not_triggered"], {"EAR": 2})

    def test_equal_size_corrupt_file_fails_checksum(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample"
            path.write_bytes(b"abc")
            md5 = "900150983cd24fb0d6963f7d28e17f72"
            self.assertEqual(check_file(path, 3, md5), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
            path.write_bytes(b"abd")
            with self.assertRaises(ValueError):
                check_file(path, 3, md5)

    def test_cli_rejects_source_files_and_aliases_before_reading_workbook(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / "output"
            nested.mkdir()
            for name in ("Raw data.xlsx", "Gu_code.R", "README.txt", "Gu_v2_metadata.json"):
                source = root / name
                source.write_bytes(b"original source")
                symlink = nested / ("sym-" + name)
                symlink.symlink_to(source)
                hardlink = nested / ("hard-" + name)
                hardlink.hardlink_to(source)
                for target in (nested / ".." / name, symlink, hardlink):
                    with self.subTest(target=target):
                        argv = ["inspect", "--source-dir", str(root), "--output", str(target)]
                        with (
                            patch("sys.argv", argv),
                            patch("analysis.inspect_neon_gu2025_seed_fate_archive_v1.inspect",
                                  return_value={"archive_rows": 1}),
                            contextlib.redirect_stderr(io.StringIO()),
                        ):
                            with self.assertRaises(SystemExit) as error:
                                main()
                        self.assertEqual(error.exception.code, 2)
                        self.assertEqual(source.read_bytes(), b"original source")

    def test_wrong_provider_version_rejected_before_local_files_are_used(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Gu_v2_metadata.json").write_text(json.dumps({
                "id": 29815622, "version": 1, "doi": "10.6084/m9.figshare.29815622.v1", "files": []
            }))
            with self.assertRaisesRegex(ValueError, "version"):
                source_manifest(root)


if __name__ == "__main__":
    unittest.main()
