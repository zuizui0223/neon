from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "dist" / "oikos_main_text_anonymous.docx"

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
FORBIDDEN = ("zhang", "ruiqi", "rachel", "zuizui0223", "rachelzhang")


def main() -> None:
    if not DOCX.is_file():
        raise SystemExit(f"missing: {DOCX}")

    with zipfile.ZipFile(DOCX) as zf:
        doc_xml = zf.read("word/document.xml")
        core_xml = zf.read("docProps/core.xml")
        footer_names = [n for n in zf.namelist() if n.startswith("word/footer") and n.endswith(".xml")]
        footer_xml = b"".join(zf.read(n) for n in footer_names)

    blob = (doc_xml + core_xml + footer_xml).decode("utf-8", errors="ignore").lower()
    hits = [x for x in FORBIDDEN if x in blob]
    if hits:
        raise SystemExit(f"identifying token(s) in DOCX: {hits}")

    root = ET.fromstring(doc_xml)
    sects = root.findall(".//w:sectPr", NS)
    if not sects:
        raise SystemExit("missing section properties")
    ln = sects[-1].find("w:lnNumType", NS)
    if ln is None:
        raise SystemExit("continuous line numbering not configured")
    if ln.attrib.get(f"{{{NS['w']}}}restart") != "continuous":
        raise SystemExit("line numbering is not continuous")

    if b"PAGE" not in footer_xml:
        raise SystemExit("page-number field missing")

    # Double spacing is represented by w:spacing w:line=480 or lineRule=auto
    # in paragraph/style XML. Require multiple explicit double-spacing paragraphs.
    doubles = re.findall(rb'<w:spacing[^>]*(?:w:line="480"|w:line="480\.0")', doc_xml)
    if len(doubles) < 10:
        raise SystemExit(f"too few double-spaced paragraphs detected: {len(doubles)}")

    # Page break must occur before the Introduction heading.
    intro = doc_xml.find(b"1. Introduction")
    page_break = doc_xml.find(b'w:type="page"')
    if intro < 0 or page_break < 0 or page_break > intro:
        raise SystemExit("Introduction is not forced to page 2")

    print(f"DOCX structural checks passed: {DOCX.stat().st_size} bytes")


if __name__ == "__main__":
    main()
