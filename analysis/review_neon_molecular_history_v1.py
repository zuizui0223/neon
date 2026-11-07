#!/usr/bin/env python3
"""Review official historical taxonomic rationales; no spatial response joins.

Only RELEASE-2026 is examined. Field/previous taxon labels remain previous
labels. DNA-related revision text is provider provenance, not independent
sequence validation or a representative error-rate estimate.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from analysis.audit_neon_identification_evidence_v1 import (
    MOLECULAR,NEGATIVE,extract_history_inventory,select_history_files)

OUT=Path(__file__).resolve().parents[1]/'build/neon_molecular_history_review_v1.json'
FIELDS=('identificationRemarks','identificationReferences','remarks')
REVISION=re.compile(r'\b(?:updat\w*|revis\w*|correct\w*|reidentif\w*|chang\w*)\b',re.I)
# Bounded vocabulary allows scientific reason review, not raw remarks export.
SAFE=set('a an the this that and or with without no not on of to from in based upon using because for is was were has have had been be by at as after before taxon taxonomic taxonomy species identification identified identifications identity updated update updates revision revised change changed corrected correct correction corrections due dna genetic genetically genetics molecular barcode barcodes barcoding bold coi co1 cox1 sequencing sequence sequences analysis analyses results result evidence confirmed confirmation consistent inconsistent morphology morphological field original previous current new unknown uncertain sample samples match matches matching top majority bin reassigned reidentified reassignment supported supports quality high low reliable reliability'.split())


def reason_template(text: str) -> str:
    tokens=[]
    for word in re.findall(r"[A-Za-z]+|\d+",text):
        token=word.lower() if word.lower() in SAFE else '[redacted]'
        if token=='[redacted]' and tokens and tokens[-1]==token: continue
        tokens.append(token)
        if len(tokens)>=42: break
    return ' '.join(tokens)


def review_records(records: list[dict]) -> dict:
    unique={hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':')).encode()).hexdigest():row for row in records}
    counts=Counter(); ids=set(); sites=set(); previous_taxa=Counter(); templates=Counter(); by_field=Counter()
    for row in unique.values():
        counts['unique_rows']+=1
        text=' | '.join(str(row.get(k) or '') for k in FIELDS)
        hid=str(row.get('identificationHistoryID') or '').strip()
        if not hid: counts['rows_without_historyID']+=1
        if not MOLECULAR.search(text):continue
        counts['molecular_mention_rows']+=1
        if hid: ids.add(hid)
        site=str(row.get('siteID') or '').strip()
        if site:sites.add(site)
        old=str(row.get('scientificName') or '').strip()
        counts['old_Peromyscus_molecular_rows']+=old.startswith('Peromyscus ')
        if old.startswith('Peromyscus '):
            tid=str(row.get('taxonID') or '').strip()
            if re.fullmatch(r'PE[A-Z]{2,10}',tid):previous_taxa[tid]+=1
        counts['molecular_rows_with_closed_history_interval']+=bool(str(row.get('endDate') or '').strip())
        negative=bool(NEGATIVE.search(text))
        counts['negative_or_pending_rows']+=negative
        counts['molecular_and_revision_language_rows']+=bool(REVISION.search(text)) and not negative
        for field in FIELDS:
            value=str(row.get(field) or '')
            if MOLECULAR.search(value):
                by_field[field]+=1
                templates[reason_template(value)]+=1
    return {
        'input_rows':len(records),'unique_rows':counts['unique_rows'],
        'molecular_mention_rows':counts['molecular_mention_rows'],
        'molecular_and_revision_language_rows':counts['molecular_and_revision_language_rows'],
        'negative_or_pending_rows':counts['negative_or_pending_rows'],
        'unique_molecular_historyIDs':len(ids),'molecular_history_sites':len(sites),
        'old_Peromyscus_molecular_rows':counts['old_Peromyscus_molecular_rows'],
        'previous_Peromyscus_taxonID_counts_NOT_current_species':dict(previous_taxa),
        'molecular_rows_with_closed_history_interval':counts['molecular_rows_with_closed_history_interval'],
        'rows_without_historyID':counts['rows_without_historyID'],
        'molecular_mention_by_rationale_field':dict(by_field),
        'redacted_vocabulary_only_reason_patterns':[{'pattern':p,'count':n} for p,n in templates.most_common(8)],
        'DNA_species_calls_independently_confirmed':False,'history_taxon_treated_as_current':False,
        'raw_identifiers_person_names_free_text_exported':False,
        'no_W_B_or_F_C_effect_fitted':True,
    }


def run()->dict:
    from analysis.run_multiscale_density_estimability_release2026_v3 import (
        _request_json,_site_codes,_download_many,QUERY_URL,TOKEN_ENV)
    token=os.environ.get(TOKEN_ENV,'').strip()
    if not token:raise RuntimeError('Existing NEON token required')
    product='DP1.10072.001'
    sites=_site_codes(_request_json(f'https://data.neonscience.org/api/v0/products/{product}'))
    payload=_request_json(QUERY_URL,token=token,body={
        'productCode':product,'siteCodes':sites,'startDateMonth':'2013-06',
        'endDateMonth':'2026-09','release':'RELEASE-2026','package':'expanded',
        'includeProvisional':False})
    files,overview=extract_history_inventory(payload)
    if any(f['release']!='RELEASE-2026' for f in files):raise RuntimeError('Unrequested release')
    files=select_history_files(files); representative={}
    for f in files:representative.setdefault((f['table'],f['md5'],f['size']),f)
    metas=list(representative.values()); sources=_download_many(metas,token,max_workers=4)
    rows_by_table={table:[] for table in ('mam_identificationHistory','mam_voucherIdentificationHistory')}
    for meta,raw in zip(metas,sources):
        reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
        if not set(FIELDS).issubset(reader.fieldnames or []):raise RuntimeError('History rationale schema drift')
        rows_by_table[meta['table']].extend(dict(r) for r in reader)
    tables={t:review_records(rows) for t,rows in rows_by_table.items()}
    if tables['mam_identificationHistory']['unique_rows']!=1928:raise RuntimeError('Main history row count drift')
    if tables['mam_identificationHistory']['molecular_mention_rows']!=1533:raise RuntimeError('Molecular mention count drift')
    return {'schema':'neon.provider_molecular_revision_provenance.v1',
        'status':'PROVIDER_HISTORY_REASON_REVIEW_NOT_INDEPENDENT_DNA_VALIDATION',
        'accessed_utc':datetime.now(timezone.utc).isoformat(),'release':'RELEASE-2026',
        'source_manifest_entries':len(files),'distinct_history_payloads_downloaded':len(metas),
        'tables':tables,'source_MD5s':[{'table':f['table'],'md5':f['md5'],'size':f['size']} for f in metas],
        'no_current_species_assignment_performed':True,'no_capture_response_files_downloaded':True,
        'no_W_B_or_F_C_effect_fitted':True,
        'next':'Link documented revision rationales to same-version current records by identificationHistoryID before using provider-corrected species. History taxonID is a previous label, not the molecular call.'}


if __name__=='__main__':
    try:report=run()
    except Exception as exc:
        report={'schema':'neon.provider_molecular_revision_provenance.v1','status':'SOURCE_REVIEW_ERROR',
            'error_type':type(exc).__name__,'no_W_B_or_F_C_effect_fitted':True}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='source_MD5s'},indent=2,sort_keys=True))
    raise SystemExit(3 if report['status']=='SOURCE_REVIEW_ERROR' else 0)
