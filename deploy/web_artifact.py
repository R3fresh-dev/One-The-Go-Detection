"""Exact-source, independently signed Expo web artifacts; no actions on import."""
from __future__ import annotations
from pathlib import Path, PurePosixPath
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:]=[entry for entry in sys.path if Path(entry).resolve()!=ROOT/'deploy']
sys.path.insert(0,str(ROOT/'services'/'api'))
sys.path.insert(0,str(ROOT))

import base64
import hashlib
import io
import json
import os
import re
import subprocess
import tarfile
import tempfile
import zipfile
from urllib.parse import urlsplit

from botocore.exceptions import ClientError
import httpx

from deploy.provenance import Gate, bounded_file, sha256, verify_signed_record

MAX_FILES = 256
MAX_BYTES = 128 * 1024 * 1024
MAX_FILE_BYTES = 16 * 1024 * 1024
CONTENT_TYPES = {'.html':'text/html; charset=utf-8','.js':'application/javascript; charset=utf-8',
    '.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml',
    '.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.ico':'image/x-icon','.woff2':'font/woff2','.ttf':'font/ttf'}


def file_record(name, data):
    path = PurePosixPath(name)
    if (not name or len(name)>256 or path.is_absolute() or '\\' in name or
        any(p in ('','..','.') for p in name.split('/')) or any(ord(c)<32 for c in name)):
        raise Gate('Unsafe web artifact path')
    suffix = path.suffix.lower()
    if suffix not in CONTENT_TYPES or suffix=='.map':
        raise Gate('Only reviewed public web asset types are publishable')
    if len(data)>MAX_FILE_BYTES:
        raise Gate('Web asset exceeds the bounded artifact size')
    return {'path':name,'size':len(data),'sha256':hashlib.sha256(data).hexdigest(),'content_type':CONTENT_TYPES[suffix]}


def package(directory, archive):
    files=[];total=0
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():raise Gate('Web artifact must not contain symlinks')
        if not path.is_file():continue
        data=bounded_file(path,MAX_FILE_BYTES);record=file_record(path.relative_to(directory).as_posix(),data)
        files.append((record,data));total+=len(data)
        if len(files)>MAX_FILES or total>MAX_BYTES:raise Gate('Web artifact exceeds supported limits')
    if not files or 'index.html' not in {r['path'] for r,_ in files}:raise Gate('Web build has no index.html')
    manifest={'schema_version':'1.0.0','digest_algorithm':'RFC8785-SHA256','files':[r for r,_ in files]}
    if len(json.dumps(manifest).encode())>48_000:raise Gate('Web file manifest exceeds signed evidence bounds')
    if archive.exists():raise Gate('Web archive is immutable; choose a new output')
    archive.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as output:
        for record,data in files:
            info=zipfile.ZipInfo(record['path'],date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16;output.writestr(info,data)
    return manifest


def contents(archive, manifest, *, snapshot=None):
    snapshot=bounded_file(archive,MAX_BYTES) if snapshot is None else snapshot
    if len(snapshot)>MAX_BYTES:raise Gate('Web archive exceeds supported limits')
    records=manifest.get('files') if isinstance(manifest,dict) else None
    if (not isinstance(records,list) or not 0<len(records)<=MAX_FILES or
        manifest.get('schema_version')!='1.0.0' or manifest.get('digest_algorithm')!='RFC8785-SHA256'):
        raise Gate('Invalid signed web file manifest')
    with zipfile.ZipFile(io.BytesIO(snapshot)) as source:
        entries=source.infolist()
        names=[entry.filename for entry in entries]
        if len(names)!=len(set(names)) or set(names)!={r.get('path') for r in records} or len(names)!=len(records):
            raise Gate('Web archive entries differ from the signed manifest')
        if sum(entry.file_size for entry in entries)>MAX_BYTES or any(entry.file_size>MAX_FILE_BYTES or entry.flag_bits&1 or entry.is_dir() for entry in entries):
            raise Gate('Web archive entries exceed supported limits')
        result={}
        for record in records:
            data=source.read(record['path'])
            if file_record(record['path'],data)!=record:raise Gate('Web archive bytes differ from signed evidence')
            result[record['path']]=data
        if 'index.html' not in result:raise Gate('Web artifact has no application entry point')
        return result


def build_environment(runtime):
    """Public bundle tools receive public configuration, never deploy credentials."""
    prefixes=('EXPO_PUBLIC_','APP_','EAS_','AWS_','GH_','GITHUB_','OTGD_','OPENAI_','ANTHROPIC_','APPETIZE_','AZURE_','GOOGLE_','GCLOUD_','SSH_')
    sensitive=re.compile(r'(^|_)(TOKEN|SECRET|PASSWORD|PRIVATE_KEY|API_KEY|CREDENTIALS)(_|$)',re.IGNORECASE)
    env={key:value for key,value in os.environ.items() if not key.startswith(prefixes) and key!='NODE_OPTIONS' and not sensitive.search(key)}
    env.update(APP_ENV=runtime['environment'],EXPO_PUBLIC_APP_ENV=runtime['environment'],EXPO_PUBLIC_API_URL=runtime['api_url'],
        EXPO_PUBLIC_OAUTH_ISSUER=runtime['issuer'],EXPO_PUBLIC_OAUTH_CLIENT_ID=runtime['client_id'],
        EXPO_PUBLIC_HOSTED_PREVIEW='false',EXPO_NO_TELEMETRY='1',CI='1')
    return env


def build(platform,args,c,out,service_release,archive,record_path):
    platform.require_clean_source(c['releaseId'])
    platform.require_trusted_signer(args.signing_key,args.trusted_public_key)
    runtime={'environment':c['environment'],'api_url':out['ApiOrigin'],'issuer':out['Issuer'],
        'client_id':out['ClientId'],'web_origin':out['WebOrigin'],'callback_uri':out['WebCallbackUri']}
    if (runtime['api_url']!='https://'+c['domain'] or not runtime['issuer'].startswith('https://cognito-idp.'+c['region']+'.amazonaws.com/') or
        runtime['callback_uri']!=runtime['web_origin']+'/' or not runtime['web_origin'].startswith('https://') or not runtime['client_id']):
        raise Gate('Actual infrastructure outputs do not provide the pinned web identity')
    with tempfile.TemporaryDirectory(prefix='otgd-web-build-') as temporary:
        root=Path(temporary);context=root/'source';context.mkdir();source=root/'source.tar'
        platform.run(['git','archive','--format=tar','--output',str(source),c['releaseId']])
        with tarfile.open(source) as packed:packed.extractall(context,filter='data')
        mobile=context/'apps/mobile'
        env=build_environment(runtime)
        subprocess.run(['npm','ci'],cwd=mobile,env=env,check=True)
        # Metro's transform cache is not environment-keyed. Every admitted
        # source revision must rebuild its pinned public runtime, including
        # revisions whose package script predates the --clear safeguard.
        subprocess.run(['npm','run','export:web','--','--clear'],cwd=mobile,env=env,check=True)
        manifest=package(mobile/'dist',archive)
        lock_sha=hashlib.sha256((mobile/'package-lock.json').read_bytes()).hexdigest()
    platform.require_clean_source(c['releaseId'])
    platform.require_release(args,c)
    payload={'schema_version':'1.0.0','purpose':'web-release','environment':c['environment'],'account':c['account'],'region':c['region'],
        'release_id':c['releaseId'],'image_digest':c['imageDigest'],'service_release_sha256':hashlib.sha256(bounded_file(args.release,65_536)).hexdigest(),
        'gate_provenance_sha256':service_release['gate_provenance_sha256'],'runtime':runtime,'runtime_sha256':sha256(runtime),
        'package_lock_sha256':lock_sha,'archive_sha256':hashlib.sha256(bounded_file(archive,MAX_BYTES)).hexdigest(),
        'manifest':manifest,'manifest_sha256':sha256(manifest),'release_prefix':'releases/'+c['releaseId'],'inference_available':False}
    if c['environment']=='prod':payload['qa_web_release_sha256']=hashlib.sha256(bounded_file(args.source_web_release,65_536)).hexdigest()
    platform.sign_release(payload,record_path,args.signing_key)
    return payload


def verify(record_path,archive,public_key,c,service_path,service_release,out=None,qa_web_release_sha256=None):
    snapshot=bounded_file(archive,MAX_BYTES)
    payload=verify_signed_record(record_path,public_key)
    expected={'schema_version':'1.0.0','purpose':'web-release','environment':c['environment'],'account':c['account'],'region':c['region'],
        'release_id':c['releaseId'],'image_digest':c['imageDigest'],'service_release_sha256':hashlib.sha256(bounded_file(service_path,65_536)).hexdigest(),
        'gate_provenance_sha256':service_release['gate_provenance_sha256'],'release_prefix':'releases/'+c['releaseId'],'inference_available':False}
    if any(payload.get(k)!=v for k,v in expected.items()):raise Gate('Web release differs from its signed service/environment/source')
    if c['environment']=='prod' and (not re.fullmatch(r'[0-9a-f]{64}',qa_web_release_sha256 or '') or payload.get('qa_web_release_sha256')!=qa_web_release_sha256):
        raise Gate('Production web release lacks the independently approved QA web binding')
    if (payload.get('archive_sha256')!=hashlib.sha256(snapshot).hexdigest() or payload.get('manifest_sha256')!=sha256(payload.get('manifest')) or
        payload.get('runtime_sha256')!=sha256(payload.get('runtime')) or not re.fullmatch(r'[0-9a-f]{64}',payload.get('package_lock_sha256',''))):
        raise Gate('Web release artifact/runtime digest does not match')
    runtime=payload['runtime']
    if runtime.get('environment')!=c['environment'] or runtime.get('api_url')!='https://'+c['domain'] or runtime.get('callback_uri')!=runtime.get('web_origin','')+'/':
        raise Gate('Web runtime configuration differs from the environment')
    if out and runtime!={'environment':c['environment'],'api_url':out['ApiOrigin'],'issuer':out['Issuer'],'client_id':out['ClientId'],'web_origin':out['WebOrigin'],'callback_uri':out['WebCallbackUri']}:
        raise Gate('Web artifact does not match the actual deployed service identity')
    return payload,contents(archive,payload['manifest'],snapshot=snapshot)


def put_immutable(s3,bucket,key,data,content_type):
    digest=hashlib.sha256(data).digest()
    try:
        s3.put_object(Bucket=bucket,Key=key,Body=data,ContentType=content_type,CacheControl='no-store',
            ChecksumSHA256=base64.b64encode(digest).decode(),ServerSideEncryption='AES256',IfNoneMatch='*')
    except ClientError as error:
        if error.response.get('Error',{}).get('Code') not in ('PreconditionFailed','412'):raise
    response=s3.get_object(Bucket=bucket,Key=key)
    body=response['Body']
    try:actual=body.read(len(data)+1)
    finally:body.close()
    if hashlib.sha256(actual).digest()!=digest or len(actual)!=len(data):raise Gate('Published web bytes conflict with this immutable release')


def verify_distribution(aws,out,release_prefix,region):
    """Bind delivery and DNS admission to the actual enabled private origin."""
    cf=aws.client('cloudfront')
    distribution=cf.get_distribution(Id=out['WebDistributionId'])['Distribution']
    config=distribution['DistributionConfig']
    behavior=config.get('DefaultCacheBehavior',{})
    origins=config.get('Origins',{}).get('Items',[])
    selected=[origin for origin in origins if origin.get('Id')==behavior.get('TargetOriginId')]
    suffix='amazonaws.com.cn' if region.startswith('cn-') else 'amazonaws.com'
    if (distribution.get('Status')!='Deployed' or config.get('Enabled') is not True
        or len(origins)!=1 or config.get('CacheBehaviors',{}).get('Quantity',0)!=0
        or config.get('CacheBehaviors',{}).get('Items') or config.get('OriginGroups',{}).get('Quantity',0)!=0
        or config.get('OriginGroups',{}).get('Items')
        or distribution.get('DomainName')!=out['WebDistributionDomain']
        or behavior.get('ViewerProtocolPolicy')!='redirect-to-https' or len(selected)!=1
        or selected[0].get('DomainName')!=out['WebBucket']+'.s3.'+region+'.'+suffix
        or selected[0].get('OriginPath')!='/'+release_prefix
        or not isinstance(selected[0].get('S3OriginConfig'),dict)
        or selected[0].get('CustomOriginConfig') is not None
        or not isinstance(selected[0].get('OriginAccessControlId'),str) or not selected[0]['OriginAccessControlId']):
        raise Gate('Actual enabled CloudFront private origin differs from the admitted web target')
    control=cf.get_origin_access_control(Id=selected[0]['OriginAccessControlId'])['OriginAccessControl']
    authority=control.get('OriginAccessControlConfig',{})
    if (control.get('Id')!=selected[0]['OriginAccessControlId']
        or authority.get('OriginAccessControlOriginType')!='s3'
        or authority.get('SigningBehavior')!='always' or authority.get('SigningProtocol')!='sigv4'):
        raise Gate('Actual CloudFront origin must always use S3 SigV4 access control')
    return distribution


def publish(aws,out,payload,files):
    if out['WebReleasePrefix']!=payload['release_prefix'] or out['ReleaseId']!=payload['release_id'] or out['ImageDigest']!=payload['image_digest']:
        raise Gate('Web target does not match the admitted release')
    verify_distribution(aws,out,payload['release_prefix'],payload['region'])
    cf=aws.client('cloudfront')
    s3=aws.client('s3')
    # The entry point is the publication barrier and is written last.
    for name in sorted(files,key=lambda name:(name=='index.html',name)):
        put_immutable(s3,out['WebBucket'],payload['release_prefix']+'/'+name,files[name],file_record(name,files[name])['content_type'])
    invalidation=cf.create_invalidation(DistributionId=out['WebDistributionId'],InvalidationBatch={'Paths':{'Quantity':1,'Items':['/*']},'CallerReference':'otgd-'+payload['manifest_sha256']})['Invalidation']['Id']
    cf.get_waiter('invalidation_completed').wait(DistributionId=out['WebDistributionId'],Id=invalidation,WaiterConfig={'Delay':20,'MaxAttempts':45})
    return {'distribution_id':out['WebDistributionId'],'invalidation_id':invalidation,'manifest_sha256':payload['manifest_sha256']}


def verify_security_headers(headers,out):
    origins=[]
    for name in ('ApiOrigin','IdentityOrigin','Issuer'):
        value=urlsplit(out[name])
        if value.scheme!='https' or not value.hostname or value.username or value.password or value.query or value.fragment:
            raise Gate('Browser network policy requires actual HTTPS deployment origins')
        origins.append('https://'+value.netloc)
    if 'ArtifactUploadOrigin' in out:
        # Serverless presigned PUTs use a regional path-style dualstack URL.
        # Keep the trailing slash: without it CSP could admit a neighboring
        # bucket prefix. Never treat an arbitrary output URL as authority.
        bucket=out.get('ArtifactBucket')
        if (not isinstance(bucket,str) or
            not re.fullmatch(r'otgd-serverless-development-[0-9]{12}-us-east-2-artifacts',bucket)):
            raise Gate('Browser upload policy requires the exact serverless artifact bucket')
        upload='https://s3.dualstack.us-east-2.amazonaws.com/'+bucket+'/'
        if out['ArtifactUploadOrigin']!=upload:
            raise Gate('Browser upload policy must bind the exact Ohio artifact bucket path')
        origins.append(upload)
    expected={
        'default-src':{"'self'"}, 'script-src':{"'self'"},
        'style-src':{"'self'","'unsafe-inline'"}, 'img-src':{"'self'",'data:'},
        'font-src':{"'self'"}, 'connect-src':{"'self'",*origins},
        'object-src':{"'none'"}, 'base-uri':{"'self'"}, 'frame-ancestors':{"'none'"},
    }
    raw=headers.get('content-security-policy','')
    actual={}
    if len(raw)>8192:raise Gate('Published browser policy exceeds its bounded size')
    for item in raw.split(';'):
        fields=item.split()
        if not fields:continue
        name=fields[0].lower()
        if name in actual or len(fields[1:])!=len(set(fields[1:])):
            raise Gate('Published browser policy contains ambiguous directives')
        actual[name]=set(fields[1:])
    transport={}
    for item in headers.get('strict-transport-security','').split(';'):
        parts=item.strip().lower().split('=',1)
        if not parts[0] or parts[0] in transport:
            raise Gate('Published HSTS policy is missing or ambiguous')
        transport[parts[0]]=parts[1] if len(parts)>1 else ''
    age=transport.get('max-age','')
    if (actual!=expected or headers.get('referrer-policy','').lower()!='no-referrer'
        or headers.get('x-content-type-options','').lower()!='nosniff'
        or headers.get('x-frame-options','').upper()!='DENY'
        or not age.isdigit() or int(age)<31536000 or transport.get('includesubdomains')!=''
        or set(transport)-{'max-age','includesubdomains','preload'}):
        raise Gate('Published web security response headers failed exact policy verification')


def verify_access(out,payload,files,*,timeout=15):
    # This public transport probe is not a signed-in customer acceptance test.
    with httpx.Client(timeout=timeout,follow_redirects=False) as client:
        paths=['index.html',next((name for name in files if name.endswith('.js')),'index.html')]
        for path in paths:
            headers=verify_public_bytes(client,out['WebOrigin']+'/'+path,files[path])
            if path=='index.html':verify_security_headers(headers,out)
        headers=verify_public_bytes(client,out['WebOrigin']+'/history',files['index.html'])
        verify_security_headers(headers,out)
        with client.stream('GET',out['WebOrigin']+'/otgd-missing-release-asset.js') as missing:
            if missing.status_code not in (403,404):raise Gate('Missing web asset was hidden by SPA fallback')
        with client.stream('GET',out['ApiOrigin']+'/health/ready') as ready:
            if ready.status_code!=200:raise Gate('API readiness failed after rollout')
    return {'web_https':'passed','spa_navigation':'passed','missing_asset':'passed','api_ready':'passed','authenticated_customer_acceptance':'not_executed'}


def verify_public_bytes(client,url,expected):
    # Request an uncompressed body, then refuse unsolicited encoding before
    # reading: a malicious compressed response cannot inflate outside the bound.
    with client.stream('GET',url,headers={'Accept-Encoding':'identity'}) as response:
        if response.status_code!=200 or response.headers.get('content-encoding','identity').lower()!='identity':
            raise Gate('Published web HTTPS response failed verification')
        total=0;observed=hashlib.sha256()
        for part in response.iter_bytes(chunk_size=min(65536,len(expected)+1)):
            total+=len(part)
            if total>len(expected):raise Gate('Published web response exceeded its exact admitted size')
            observed.update(part)
        if total!=len(expected) or observed.digest()!=hashlib.sha256(expected).digest():
            raise Gate('Published web HTTPS bytes failed verification')
        return response.headers
