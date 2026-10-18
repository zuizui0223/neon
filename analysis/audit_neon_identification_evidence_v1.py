#!/usr/bin/env python3
"""Read NEON identification histories, not new spatial ecological outcomes.

RELEASE-2026 and any returned provisional block are kept separate. Historical
identifications are not current determinations. Molecular mentions are only
source-evidence candidates, not independently validated species or animals.
No sample/tag/person names, free-text remarks or sequences are exported.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

TARGETS = {'mam_identificationHistory', 'mam_voucherIdentificationHistory'}
TABLE_RE = re.compile(r'\.(mam_[A-Za-z0-9_]+)\.(\d{4}-\d{2})\.(basic|expanded)\.')
MOLECULAR = re.compile(r'\b(?:DNA|COI|CO1|COX1|BOLD|genetic(?:s|ally)?|molecular|sequenc\w*|barcod\w*|PacBio|GenBank)\b', re.I)
NEGATIVE = re.compile(r'\b(?:no|not|without|pending|await\w*|unconfirmed|unavailable)\b.{0,70}\b(?:DNA|COI|genetic|molecular|sequenc\w*|barcod\w*|confirm\w*)\b|\b(?:DNA|sequenc\w*|barcod\w*)\b.{0,40}\b(?:failed|pending|unavailable)\b', re.I)
RATIONALE_NAMES = {'identificationmethod','identificationremarks','identificationreferences', 'remarks','reason','rationale','taxonomynotes','identificationnotes','identificationreason','updatejustification','updatejustificationremarks','taxonidentificationmethod'}
METHOD_NAMES = {'identificationmethod','taxonidentificationmethod'}
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/neon_identification_evidence_v1.json'


def extract_history_inventory(payload: dict) -> tuple[list[dict], dict]:
    data = payload.get('data')
    if not isinstance(data, dict) or not isinstance(data.get('releases'), list):
        raise ValueError('Unexpected NEON query release structure')
    files = {}; counts = Counter(); blocks = []
    for block in data['releases']:
        release = str(block.get('release') or '')
        if not release:
            raise ValueError('Unlabelled release block')
        blocks.append(release)
        for pkg in block.get('packages', []):
            for item in pkg.get('files', []):
                name = str(item.get('name') or '')
                match = TABLE_RE.search(name)
                if not name.endswith('.csv') or not match:
                    continue
                table = match.group(1); counts[table] += 1
                if table not in TARGETS:
                    continue
                digest = str(item.get('md5') or '').lower(); size = item.get('size')
                if not re.fullmatch('[0-9a-f]{32}', digest):
                    raise ValueError('Invalid history source MD5')
                if isinstance(size, bool) or not isinstance(size, int) or size < 0:
                    raise ValueError('Invalid history source size')
                url = str(item.get('url') or '')
                if not url.startswith('https://'):
                    raise ValueError('Invalid history source URL')
                entry = {'release': release, 'site': str(pkg.get('siteCode') or ''),
                         'month': str(pkg.get('month') or ''), 'table': table,
                         'package': str(pkg.get('packageType') or ''),
                         'name': name, 'md5': digest, 'size': size, 'url': url}
                key = (release, entry['site'], entry['month'], name)
                if key in files and files[key] != entry:
                    raise ValueError('History manifest conflict')
                files[key] = entry
    return [files[k] for k in sorted(files)], {
        'returned_release_blocks': blocks, 'all_csv_tables': dict(sorted(counts.items())),
        'other_data_top_level_keys': sorted(k for k in data if k != 'releases'),
        'only_history_files_selected': True,
    }


def summarize_history_csv(raw: bytes, *, seen: set[str] | None = None) -> dict:
    reader = csv.reader(io.StringIO(raw.decode('utf-8-sig')))
    header = next(reader, [])
    if not header or len(set(header)) != len(header) or any(not h.strip() for h in header):
        raise ValueError('Empty or duplicate history header')
    field_index = {h: i for i, h in enumerate(header)}
    reasons = [h for h in header if h.casefold() in RATIONALE_NAMES]
    methods = [h for h in header if h.casefold() in METHOD_NAMES]
    counts = Counter(); categories = Counter()
    seen = set() if seen is None else seen
    for row in reader:
        if not row: continue
        if len(row) != len(header): raise ValueError('Ragged history row')
        counts['raw_rows'] += 1
        fingerprint = hashlib.sha256(json.dumps(dict(zip(header,row)), sort_keys=True, separators=(',',':')).encode()).hexdigest()
        if fingerprint in seen:
            counts['duplicate_rows'] += 1; continue
        seen.add(fingerprint); counts['rows'] += 1
        text = ' | '.join(row[field_index[h]] for h in reasons)
        method = ' | '.join(row[field_index[h]] for h in methods)
        mention = bool(MOLECULAR.search(text)); negative = bool(NEGATIVE.search(text))
        explicit = bool(MOLECULAR.search(method)) and not bool(NEGATIVE.search(method))
        counts['any_molecular_mention_rows'] += mention
        counts['explicit_molecular_method_rows'] += explicit
        counts['negative_or_pending_evidence_rows'] += mention and negative
        category = 'molecular_method_candidate' if explicit else 'morphology' if re.search(r'morpholog',method,re.I) else 'other_method' if method.strip() else 'method_missing'
        categories[category] += 1
    return {
        'columns': header, 'rationale_columns': reasons, 'rationale_columns_present': bool(reasons),
        'rows': counts['rows'], 'raw_rows': counts['raw_rows'], 'duplicate_rows': counts['duplicate_rows'],
        'any_molecular_mention_rows': counts['any_molecular_mention_rows'],
        'explicit_molecular_method_rows': counts['explicit_molecular_method_rows'],
        'negative_or_pending_evidence_rows': counts['negative_or_pending_evidence_rows'],
        'method_categories': dict(categories),
        'evidence_status': 'MOLECULAR_MENTION_CANDIDATES' if counts['any_molecular_mention_rows'] else 'NO_MOLECULAR_MENTION_IN_INSPECTED_FIELDS' if reasons else 'NO_RATIONALE_COLUMNS',
        'molecular_species_identity_proven': False, 'historical_taxon_is_current_taxon': False,
        'raw_identifiers_names_and_remarks_exported': False,
    }


def run() -> dict:
    # Existing release-aware, size/MD5-validating transport only. Importing
    # here keeps the pure unit tests runnable without network or credentials.
    from analysis.run_multiscale_density_estimability_release2026_v3 import (
        _request_json, _site_codes, _download_many, QUERY_URL, TOKEN_ENV)
    token = os.environ.get(TOKEN_ENV, '').strip()
    if not token: raise RuntimeError('Existing NEON token required')
    product = 'DP1.10072.001'; release = 'RELEASE-2026'
    sites = _site_codes(_request_json(f'https://data.neonscience.org/api/v0/products/{product}'))
    selected = {}; inventories = []
    # Inspect both documented packages, never infer missing history from
    # a parser that only accepts pertrapnight/perplotnight tables.
    for package in ('basic', 'expanded'):
        payload = _request_json(QUERY_URL, token=token, body={
            'productCode': product, 'siteCodes': sites, 'startDateMonth':'2013-06',
            'endDateMonth':'2026-09','release':release,'package':package,
            'includeProvisional':True})
        files, overview = extract_history_inventory(payload)
        inventories.append({'requested_package': package, **overview})
        for f in files:
            key = (f['release'], f['site'], f['month'], f['table'], f['md5'])
            selected.setdefault(key, f)
    files = [selected[k] for k in sorted(selected)]
    manifest = [{k:v for k,v in f.items() if k != 'url'} for f in files]
    raw_files = _download_many(files, token, max_workers=4)
    groups = {}; seen_by_group = defaultdict(set)
    for meta, raw in zip(files, raw_files):
        key = meta['release'] + '/' + meta['table']
        summary = summarize_history_csv(raw, seen=seen_by_group[key])
        g = groups.setdefault(key, {'release':meta['release'], 'table':meta['table'],
            'files':0,'sites':set(),'schemas':set(),'rationale_columns':set(),
            'raw_rows':0,'unique_rows':0,'duplicate_rows':0,'any_molecular_mention_rows':0,
            'explicit_molecular_method_rows':0,'negative_or_pending_evidence_rows':0,
            'method_categories':Counter()})
        g['files'] += 1; g['sites'].add(meta['site']); g['schemas'].add(tuple(summary['columns']))
        g['rationale_columns'].update(summary['rationale_columns'])
        for name in ('raw_rows','duplicate_rows','any_molecular_mention_rows','explicit_molecular_method_rows','negative_or_pending_evidence_rows'):
            g[name] += summary[name]
        g['unique_rows'] += summary['rows']; g['method_categories'].update(summary['method_categories'])
    for g in groups.values():
        g['site_count'] = len(g.pop('sites')); g['schemas'] = [list(s) for s in sorted(g['schemas'])]
        g['rationale_columns'] = sorted(g['rationale_columns']); g['method_categories'] = dict(g['method_categories'])
    return {'schema':'neon.identification_history_molecular_source_evidence.v1',
        'status':'HISTORY_EVIDENCE_SCANNED_NOT_SPECIES_VALIDATED' if files else 'NO_HISTORY_TABLES_IN_RETURNED_INVENTORIES',
        'accessed_utc':datetime.now(timezone.utc).isoformat(),'requested_release':release,
        'requested_include_provisional':True,'requested_collection_window':['2013-06','2026-09'],
        'inventory_overviews':inventories,'downloaded_history_files':len(files),
        'manifest':manifest,'manifest_sha256':hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest(),
        'groups':groups,'explicit_molecular_species_calls_verified':0,
        'claims':{'no_spatial_response_files_downloaded':True,'no_W_B_or_F_C_effect_fitted':True,
            'not_a_species_error_rate':True,'history_rows_are_past_determinations_not_current_species':True,
            'molecular_mentions_require_manual_evidence_review':True,'different_releases_never_pooled':True,
            'original_eight_genus_guard':'FAILED_5_OF_8_UNCHANGED','MOSA_effects':'SEALED'}}


def main() -> int:
    try: result = run()
    except Exception as exc:
        result = {'schema':'neon.identification_history_molecular_source_evidence.v1',
            'status':'SOURCE_AUDIT_ERROR','error_type':type(exc).__name__,
            'diagnostic': str(exc)[:220] if isinstance(exc,(ValueError,RuntimeError)) and 'http' not in str(exc).lower() else 'Source retrieval or schema failed; URLs and identifiers suppressed',
            'no_W_B_or_F_C_effect_fitted':True}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='manifest'},indent=2,sort_keys=True))
    return 3 if result['status']=='SOURCE_AUDIT_ERROR' else 0


if __name__=='__main__': raise SystemExit(main())
