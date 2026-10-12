#!/usr/bin/env python3
"""Explicit local-only lifecycle. Never sends credentials in argv or prints .env."""
import argparse
import json
import os
from pathlib import Path
import secrets
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
LOCAL=ROOT/'infra/local'


def prepare(host='localhost',lan=False):
    if not re.fullmatch(r'[A-Za-z0-9.-]+',host): raise ValueError('Supply a hostname or IPv4 address, without scheme/port')
    env=LOCAL/'.env'
    if env.exists():
        print('Existing local environment preserved. Edit only its documented origin fields to change routing.')
    else:
        rows={
            'OTGD_LOCAL_MIGRATION_PASSWORD':secrets.token_hex(24),
            'OTGD_LOCAL_APP_PASSWORD':secrets.token_hex(24),
            'OTGD_TOMBSTONE_KEY':secrets.token_hex(32),
            'LOCALSTACK_AUTH_TOKEN':os.environ.get('LOCALSTACK_AUTH_TOKEN',''),
            'OTGD_LOCAL_API_ORIGIN':f'http://{host}:8000',
            'OTGD_LOCAL_IDENTITY_ORIGIN':f'http://{host}:8081',
            'OTGD_LOCAL_S3_ORIGIN':f'http://{host}:4566',
            'OTGD_LOCAL_OAUTH_REDIRECT_URIS':json.dumps(list(dict.fromkeys(['otgd-local://oauth/callback','http://localhost:8082/',f'http://{host}:8082/'])),separators=(',',':')),
            'OTGD_BIND_ADDRESS':'0.0.0.0' if lan else '127.0.0.1',
            'OTGD_LOCAL_UID':str(os.getuid()),'OTGD_LOCAL_GID':str(os.getgid()),
        }
        if any('\n' in v or '\r' in v for v in rows.values()): raise ValueError('Invalid environment value')
        # O_EXCL and 0600 avoid replacing credentials or exposing them during creation.
        with os.fdopen(os.open(env,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:
            # Compose single quotes preserve literal dollar signs in tokens.
            f.write('\n'.join(k+"='"+v.replace("'","\\'")+"'" for k,v in rows.items())+'\n')
        print('Created protected local settings. Default Apache-2.0 LocalStack 4.14 needs no token; the explicit licensed preset requires an authorized token.')
    key=LOCAL/'secrets/identity-key.pem'
    key.parent.mkdir(mode=0o700,exist_ok=True)
    if not key.exists():
        if not shutil.which('uv'): raise RuntimeError('Install uv, then repeat prepare; existing settings are preserved')
        code="from cryptography.hazmat.primitives.asymmetric import rsa; from cryptography.hazmat.primitives import serialization; import os,sys; k=rsa.generate_private_key(public_exponent=65537,key_size=3072); p=k.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()); f=os.open(sys.argv[1],os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600); os.write(f,p); os.close(f)"
        subprocess.run(['uv','run','--project',str(ROOT/'services/api'),'python','-c',code,str(key)],check=True)
    capture_key=LOCAL/'secrets/capture-signing-key.pem'
    if not capture_key.exists():
        if not shutil.which('uv'):raise RuntimeError('Install uv, then repeat prepare; existing settings are preserved')
        # Fresh capability provisioning is anchored by the additive migration.
        # A replacement file cannot change an existing public-key database anchor.
        code="from cryptography.hazmat.primitives.asymmetric import ec; from cryptography.hazmat.primitives import serialization; import os,sys; k=ec.generate_private_key(ec.SECP256R1()); p=k.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()); f=os.open(sys.argv[1],os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600); os.write(f,p); os.close(f)"
        subprocess.run(['uv','run','--project',str(ROOT/'services/api'),'python','-c',code,str(capture_key)],check=True)
    print('Local signing key is present; no credentials printed. Published ports are loopback unless explicitly prepared for LAN testing.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['prepare','up','down','status','logs','migrate','check','check-app','reset'])
    p.add_argument('--host',default='localhost');p.add_argument('--lan',action='store_true')
    p.add_argument('--confirm-local-data-loss',action='store_true')
    p.add_argument('--confirm-fictional-workspace',action='store_true')
    p.add_argument('--licensed-localstack',action='store_true',help='Select the pinned current licensed image; requires authorized LOCALSTACK_AUTH_TOKEN')
    a=p.parse_args()
    if a.command=='prepare': prepare(a.host,a.lan);return
    if not shutil.which('docker'): raise RuntimeError('Docker is unavailable; local integration is UNEXECUTED')
    if not (LOCAL/'.env').exists(): raise RuntimeError('Run prepare first')
    cmd=['docker','compose','--project-name','otgd-local','--env-file',str(LOCAL/'.env'),'-f',str(LOCAL/'compose.yml')]
    if a.licensed_localstack:cmd+=['-f',str(LOCAL/'compose.localstack-licensed.yml')]
    operations={
        'up':['up','--build','--detach','--wait','--wait-timeout','180'],
        'down':['down'], 'status':['ps'], 'logs':['logs','--tail','100'],
        'migrate':['run','--rm','migrate'],
        'check':['run','--rm','--no-deps','api','uv','run','--no-sync','python','/app/infra/local/smoke.py'],
        'check-app':['run','--rm','--no-deps','api','uv','run','--no-sync','python','/app/infra/local/app_flow.py','--confirm-fictional-workspace'],
    }
    if a.command=='check-app' and not a.confirm_fictional_workspace:raise RuntimeError('The application flow deletes Fictional Account A data; confirm a disposable workspace with --confirm-fictional-workspace')
    if a.command=='reset':
        if not a.confirm_local_data_loss: raise RuntimeError('reset deletes only this local Compose project volumes; repeat with --confirm-local-data-loss after reviewing unsaved local data')
        args=['down','--volumes']
    else: args=operations[a.command]
    subprocess.run(cmd+args,check=True,cwd=ROOT)


if __name__=='__main__':
    try: main()
    except (ValueError,RuntimeError,subprocess.CalledProcessError) as e:
        print(f'Local platform: {e}',file=sys.stderr);sys.exit(1)
