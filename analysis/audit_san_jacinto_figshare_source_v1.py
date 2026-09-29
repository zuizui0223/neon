from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.request
from pathlib import Path

import openpyxl

API_URL="https://api.figshare.com/v2/articles/18295520"
USER_AGENT="san-jacinto-crossscale-source-audit/1.0"


def get_json(url: str) -> dict:
    req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def download(url: str, path: Path) -> bytes:
    req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT})
    with urllib.request.urlopen(req,timeout=180) as response:
        raw=response.read()
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(raw)
    return raw


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+","_",str(value).strip().lower()).strip("_")


TOKENS={
    "identity":{
        "id","individual_id","individualid","animal_id","animalid","tag","tag_id",
        "tagid","ear_tag","eartag","mouse_id","mouseid","unique_id","uniqueid",
    },
    "sex":{"sex","gender"},
    "species":{
        "species","species_code","speciescode","sp","taxon","scientific_name",
        "scientificname","species_name","speciesname",
    },
    "grid":{"grid","grid_id","gridid","plot","plot_id","plotid"},
    "trap":{
        "trap","trap_id","trapid","trap_location","traplocation","station",
        "station_id","stationid","stake","stake_id","stakeid","location",
        "trap_number","trapnumber","flag","flag_id","flagid",
    },
    "date":{
        "date","capture_date","capturedate","sample_date","sampledate","year",
        "month","day",
    },
    "night":{"night","night_id","nightid","trap_night","capture_night","check","trap_check"},
    "time":{"time","capture_time","capturetime","check_time","checktime"},
}


def classify(columns: list[str]) -> dict[str,list[str]]:
    out={key:[] for key in TOKENS}
    for col in columns:
        n=norm(col)
        for key,names in TOKENS.items():
            if n in names:
                out[key].append(col)
    return out


def audit_csv(path: Path) -> list[dict]:
    raw=path.read_bytes()
    text=raw.decode("utf-8-sig",errors="replace")
    try:
        delim=csv.Sniffer().sniff(text[:65536],delimiters=",\t;|").delimiter
    except csv.Error:
        delim=","
    reader=csv.reader(text.splitlines(),delimiter=delim)
    try:
        header=[str(x).strip() for x in next(reader)]
    except StopIteration:
        return []
    rows=sum(1 for row in reader if row)
    return [{
        "table_type":"csv",
        "sheet_or_table":path.name,
        "columns":header,
        "row_count":rows,
        "structural_columns":classify(header),
    }]


def audit_xlsx(path: Path) -> list[dict]:
    wb=openpyxl.load_workbook(path,read_only=True,data_only=True)
    out=[]
    for ws in wb.worksheets:
        all_rows=list(ws.iter_rows(values_only=True))
        if not all_rows:
            continue
        first=all_rows[0]
        header=["" if x is None else str(x).strip() for x in first]
        data_rows=sum(
            1 for row in all_rows[1:]
            if any(x not in (None,"") for x in row)
        )
        preview=[
            ["" if x is None else str(x) for x in row]
            for row in all_rows[:30]
            if any(x not in (None,"") for x in row)
        ]
        out.append({
            "table_type":"xlsx",
            "sheet_or_table":ws.title,
            "columns":header,
            "row_count":data_rows,
            "structural_columns":classify(header),
            "metadata_preview_rows":preview,
        })
    return out


def adequate(structural: dict[str,list[str]]) -> bool:
    temporal=bool(structural["night"] or structural["date"] or structural["time"])
    return all([
        bool(structural["identity"]),
        bool(structural["sex"]),
        bool(structural["species"]),
        bool(structural["grid"]),
        bool(structural["trap"]),
        temporal,
    ])


def audit(article_id: int, output_dir: Path) -> dict:
    article=get_json(f"https://api.figshare.com/v2/articles/{article_id}")
    files=article.get("files") or []
    file_records=[]
    table_records=[]

    for row in files:
        name=str(row.get("name","")).strip()
        url=str(row.get("download_url","")).strip()
        if not name or not url:
            continue
        suffix=Path(name).suffix.lower()
        record={
            "id":row.get("id"),
            "name":name,
            "size":row.get("size"),
            "supplied_md5":row.get("supplied_md5") or row.get("computed_md5"),
            "download_url":url,
            "tabular_candidate":suffix in {".csv",".tsv",".txt",".xlsx",".xls"},
        }
        if record["tabular_candidate"]:
            path=output_dir/name
            raw=download(url,path)
            record["downloaded_bytes"]=len(raw)
            record["sha256"]=hashlib.sha256(raw).hexdigest()
            if suffix in {".csv",".tsv",".txt"}:
                tables=audit_csv(path)
            elif suffix==".xlsx":
                tables=audit_xlsx(path)
            else:
                tables=[]
            for table in tables:
                table["source_file"]=name
                table["structurally_adequate_capture_table"]=adequate(table["structural_columns"])
            table_records.extend(tables)
        file_records.append(record)

    adequate_tables=[
        {
            "source_file":row["source_file"],
            "sheet_or_table":row["sheet_or_table"],
        }
        for row in table_records
        if row["structurally_adequate_capture_table"]
    ]

    return {
        "schema":"neon.san_jacinto_crossscale.source_schema_audit.v1",
        "figshare_article_id":article_id,
        "doi":article.get("doi"),
        "title":article.get("title"),
        "version":article.get("version"),
        "license":article.get("license"),
        "files":file_records,
        "tables":table_records,
        "adequate_capture_tables":adequate_tables,
        "source_adequacy_for_estimability_design":bool(adequate_tables),
        "species_specific_counts_inspected":False,
        "sex_specific_counts_inspected":False,
        "movement_distances_computed":False,
        "packing_effects_computed":False,
        "ecological_effect_models_fit":0,
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--article-id",type=int,default=18295520)
    parser.add_argument("--cache-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    out=audit(args.article_id,args.cache_dir)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
