"""Offline, checksum-gated entry point for the frozen V25 estimand.

No network requests, no alternate download attempts, no changed fit or support
thresholds. Original Dryad v3 source bytes required. Use the separately
provided original ZIP or a directory containing the two CSVs.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,pathlib,zipfile
from analysis.run_neon_joyce_early_late_v25 import analyze,FILES
MANIFEST={
    FILES[0]:(13364,"0a9fe6484953b591bb03fca3d0a20cfbf2fff553cbed28f4c12dfeb4a8be15c2"),
    FILES[1]:(12754,"a1b34061fb5703fe32b31bff15e0b165dcde28943c5e036a8f86d736c3cee183"),
}
MAX_ZIP_BYTES=25_000_000
MAX_MEMBERS=100
def parse_verified(blob,name,expected):
    n,digest=expected
    if len(blob)!=n or hashlib.sha256(blob).hexdigest()!=digest:
        raise ValueError("V3 size or SHA256 mismatch: "+name)
    reader=csv.DictReader(io.StringIO(blob.decode("utf-8-sig"),newline=""))
    h=reader.fieldnames
    if not h or len(set(h))!=len(h):
        raise ValueError("CSV header invalid: "+name)
    rows=list(reader)
    if any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError("CSV width invalid: "+name)
    return rows
def load_input(path,receipt):
    path=pathlib.Path(path)
    raw={}
    if path.is_dir():
        for name,(n,digest) in MANIFEST.items():
            with (path/name).open("rb") as f:blob=f.read(n+1)
            raw[name]=parse_verified(blob,name,(n,digest))
            receipt[name]={"bytes":len(blob),"sha256":digest,"rows":len(raw[name]),"status":"VERIFIED_V3"}
    elif path.is_file():
        if path.stat().st_size>MAX_ZIP_BYTES:raise ValueError("ZIP size exceeds bound")
        with zipfile.ZipFile(path) as z:
            members=z.infolist()
            if len(members)>MAX_MEMBERS:raise ValueError("ZIP roster exceeds bound")
            for name,(n,digest) in MANIFEST.items():
                matches=[m for m in members if not m.is_dir() and pathlib.PurePosixPath(m.filename).name==name]
                if len(matches)!=1:raise ValueError("ZIP member absent or duplicated: "+name)
                m=matches[0]
                if m.file_size!=n:raise ValueError("ZIP member size mismatch: "+name)
                # Read only selected members; never extract paths to disk.
                with z.open(m) as f:blob=f.read(n+1)
                raw[name]=parse_verified(blob,name,(n,digest))
                receipt[name]={"bytes":len(blob),"sha256":digest,"rows":len(raw[name]),"status":"VERIFIED_V3"}
    else:raise ValueError("Input ZIP or directory not found")
    return raw
def run(path):
    out={"status":"STOP_LOCAL_INPUT_OR_SUPPORT","doi":"10.5061/dryad.05qfttfb9","paper":"10.1111/btp.13381","required_version":3,
         "frozen_estimator_commit":"1fc333fb059ee840c2e2a9b3e3266e5d20263692","outcome_opened":False,"files":{},
         "boundary":"No network. Same quadrats, not tracked seed individuals. No causal, seasonality, resource-adjusted, or geographic-generalization claim. Real-data schema and support must pass independently of synthetic tests."}
    try:
        raw=load_input(path,out["files"])
        out["outcome_opened"]=True
        analyze(raw,out)
    except (OSError,ValueError,KeyError,UnicodeError,zipfile.BadZipFile) as e:
        out["reason"]=type(e).__name__+": "+str(e)[:300]
    return out
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",required=True,type=pathlib.Path)
    p.add_argument("--out",type=pathlib.Path,default=pathlib.Path("build/neon_joyce_local_v25.json"))
    a=p.parse_args()
    out=run(a.input)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0 if out["status"]=="DESCRIPTIVE_PREDICTION_COMPLETE" else 2
if __name__=="__main__":raise SystemExit(main())
