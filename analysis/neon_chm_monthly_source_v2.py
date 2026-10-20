"""Corrected AOP transport, not relaxed habitat inference. No pixel selection by value."""
from __future__ import annotations
import base64
import hashlib
import re
import zlib
from analysis.neon_e5_chm_pilot_v1 import PRODUCT,RELEASE,tile_lower_left


def _crc_integer(value):
    if isinstance(value,int) and not isinstance(value,bool) and 0<=value<=0xffffffff:return value
    if not isinstance(value,str):raise ValueError('unrecognized provider CRC encoding')
    s=value.strip()
    # Official NEON AOP monthly metadata uses variable-width hexadecimal
    # CRC values: the source has 6-, 7- and 8-character CRC32C strings.
    # Missing leading zero hex digits are NOT missing checksum bytes.
    # Digit-only source strings are interpreted as HEX, not decimal.
    if re.fullmatch(r'(?:0[xX])?[0-9a-fA-F]{1,8}',s):return int(s,16)
    try:
        raw=base64.b64decode(s,validate=True)
        if len(raw)==4:return int.from_bytes(raw,'big')
    except Exception:pass
    raise ValueError('unrecognized provider CRC encoding')


def _crc32c(raw):
    table=[]
    for byte in range(256):
        c=byte
        for _ in range(8):c=(c>>1)^0x82f63b78 if c&1 else c>>1
        table.append(c)
    c=0xffffffff
    for byte in raw:c=table[(c^byte)&255]^(c>>8)
    return c^0xffffffff


def monthly_chm_manifest(payload,site,month):
    d=payload.get('data',{})
    if (d.get('release'),d.get('productCode'),d.get('siteCode'),d.get('month')) != (RELEASE,PRODUCT,site,month):
        raise ValueError('exact monthly released CHM identity mismatch')
    records={}
    for r in d.get('files',[]):
        xy=tile_lower_left(r.get('name'))
        if xy is None:continue
        size=r.get('size');url=str(r.get('url') or '')
        if isinstance(size,bool) or not isinstance(size,int) or size<=0 or not url.startswith('https://'):
            raise ValueError('invalid monthly CHM byte metadata')
        checks={}
        if r.get('md5'):
            text=str(r['md5']).lower()
            if not re.fullmatch('[0-9a-f]{32}',text):raise ValueError('invalid provider MD5')
            checks['md5']=text
        for algorithm in ('crc32','crc32c'):
            if r.get(algorithm) is not None and r.get(algorithm)!='':checks[algorithm]=_crc_integer(r[algorithm])
        if not checks:raise ValueError('CHM has no usable provider checksum')
        out={'site':site,'month':month,'name':r['name'],'url':url,'size':size,
             'provider_checksums':checks,'checksum_kind':'+'.join(sorted(checks)),
             'tile_easting':xy[0],'tile_northing':xy[1]}
        if out['name'] in records and records[out['name']]!=out:raise ValueError('ambiguous CHM duplicate')
        records[out['name']]=out
    return [records[k] for k in sorted(records)]


def verify_raster_bytes(raw,meta):
    if len(raw)!=meta['size']:raise ValueError('CHM bytes fail official size')
    checks=meta.get('provider_checksums')
    if not checks:raise ValueError('provider checksum missing')
    for algorithm,expected in checks.items():
        actual=(hashlib.md5(raw).hexdigest() if algorithm=='md5' else
                (zlib.crc32(raw)&0xffffffff) if algorithm=='crc32' else
                _crc32c(raw) if algorithm=='crc32c' else None)
        if actual is None or actual!=expected:raise ValueError('CHM provider checksum mismatch')


def download_monthly_tile(meta,token):
    """Bounded HTTPS download; account token sent only to official NEON API host."""
    import urllib.request
    from urllib.parse import urlparse
    host=urlparse(meta['url']).hostname or ''
    allowed=(host=='data.neonscience.org' or host=='storage.googleapis.com' or
             host.endswith('.storage.googleapis.com') or host.endswith('.s3.amazonaws.com'))
    if not allowed:raise ValueError('unrecognized provider tile host')
    headers={'User-Agent':'NEON-E5-source-only-pilot/2'}
    if host=='data.neonscience.org':headers['X-API-Token']=token
    class SafeRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,req,fp,code,msg,hdrs,newurl):
            new=super().redirect_request(req,fp,code,msg,hdrs,newurl)
            if new is not None and urlparse(newurl).hostname!='data.neonscience.org':new.remove_header('X-api-token')
            if not newurl.startswith('https://'):raise ValueError('non-HTTPS tile redirect')
            return new
    opener=urllib.request.build_opener(SafeRedirect())
    with opener.open(urllib.request.Request(meta['url'],headers=headers),timeout=180) as response:
        raw=response.read(meta['size']+1)
    verify_raster_bytes(raw,meta)
    return raw
