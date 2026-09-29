from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

USER_AGENT="sevilleta-dataone-replica-probe/1.0"
CN="https://cn.dataone.org/cn/v2"
PID=(
    "https://pasta.lternet.edu/package/data/eml/"
    "knb-lter-sev/8/297976/d70c7027949ca1d8ae053eb10300dc0e"
)


def request(url: str, *, method: str="GET", timeout: int=120) -> tuple[int,dict[str,str],bytes]:
    req=urllib.request.Request(
        url,
        method=method,
        headers={
            "User-Agent":USER_AGENT,
            "Accept":"*/*",
        },
    )
    try:
        with urllib.request.urlopen(req,timeout=timeout) as response:
            return (
                int(response.status),
                {k.lower():v for k,v in response.headers.items()},
                response.read(),
            )
    except urllib.error.HTTPError as error:
        return (
            int(error.code),
            {k.lower():v for k,v in error.headers.items()},
            error.read(),
        )


def solr_lookup(pid: str) -> dict:
    params=urllib.parse.urlencode({
        "q":f'identifier:"{pid}"',
        "wt":"json",
        "rows":"10",
    })
    status,headers,raw=request(f"{CN}/query/solr/?{params}")
    if status!=200:
        raise RuntimeError(f"DataONE Solr query failed: HTTP {status}")
    payload=json.loads(raw.decode("utf-8"))
    return payload


def node_map() -> dict[str,str]:
    status,headers,raw=request(f"{CN}/node/")
    if status!=200:
        raise RuntimeError(f"DataONE node list failed: HTTP {status}")
    root=ET.fromstring(raw)
    out={}
    for node in root.iter():
        if not node.tag.endswith("node"):
            continue
        identifier=None
        base=None
        for child in node:
            tag=child.tag.rsplit("}",1)[-1]
            if tag=="identifier":
                identifier=(child.text or "").strip()
            elif tag=="baseURL":
                base=(child.text or "").strip()
        if identifier and base:
            out[identifier]=base.rstrip("/")
    return out


def candidate_nodes(doc: dict) -> list[str]:
    result=[]
    for key in ("authoritativeMN","replicaMN","datasource","originMemberNode"):
        value=doc.get(key)
        if isinstance(value,str):
            result.append(value)
        elif isinstance(value,list):
            result.extend(str(x) for x in value if x)
    seen=set()
    return [x for x in result if not (x in seen or seen.add(x))]


def object_url(base: str, pid: str) -> str:
    if base.endswith("/mn/v2"):
        return f"{base}/object/{urllib.parse.quote(pid,safe='')}"
    if "/mn/" in base:
        return f"{base}/object/{urllib.parse.quote(pid,safe='')}"
    return f"{base}/mn/v2/object/{urllib.parse.quote(pid,safe='')}"


def probe(pid: str) -> dict:
    lookup=solr_lookup(pid)
    response=lookup.get("response") or {}
    docs=response.get("docs") or []
    nodes=node_map()

    doc_summaries=[]
    all_candidates=[]
    for doc in docs:
        summary={
            key:doc.get(key)
            for key in (
                "identifier","title","formatId","size","checksum",
                "authoritativeMN","replicaMN","datasource","originMemberNode",
                "dateUploaded","dateModified"
            )
            if key in doc
        }
        doc_summaries.append(summary)
        all_candidates.extend(candidate_nodes(doc))

    # The CN resolver is also tested, without credentials and without following
    # a guessed private endpoint.
    resolver=(
        f"{CN}/resolve/{urllib.parse.quote(pid,safe='')}"
    )
    r_status,r_headers,r_raw=request(resolver,method="GET")

    probes=[]
    seen=set()
    for node_id in all_candidates:
        if node_id in seen:
            continue
        seen.add(node_id)
        base=nodes.get(node_id)
        row={
            "node_id":node_id,
            "base_url":base,
            "attempted":False,
            "http_status":None,
            "content_type":None,
            "content_length_header":None,
            "bytes_received":0,
        }
        if base:
            url=object_url(base,pid)
            status,headers,raw=request(url)
            row.update({
                "attempted":True,
                "object_url":url,
                "http_status":status,
                "content_type":headers.get("content-type"),
                "content_length_header":headers.get("content-length"),
                "bytes_received":len(raw),
                "anonymous_success":status==200 and len(raw)>1000,
            })
        probes.append(row)

    return {
        "schema":"neon.sevilleta_dataone_replica_probe.v1",
        "pid":pid,
        "solr_num_found":int(response.get("numFound",0) or 0),
        "documents":doc_summaries,
        "resolver":{
            "url":resolver,
            "http_status":r_status,
            "location":r_headers.get("location"),
            "content_type":r_headers.get("content-type"),
            "bytes_received":len(r_raw),
        },
        "node_probes":probes,
        "anonymous_public_replica_available":any(
            bool(row.get("anonymous_success")) for row in probes
        ),
        "sex_specific_effects_inspected":False,
        "ecological_effect_models_fit":0,
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    out=probe(PID)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
