"""Private storage contract failures, checksum capabilities and version pinning."""
import hashlib
import io
from types import SimpleNamespace
from urllib.parse import parse_qs,urlsplit
import boto3
import botocore.session
from botocore.exceptions import ClientError
import pytest
from otgd import storage
from otgd.config import settings
from otgd.errors import Problem

class S3:
    def __init__(self,content=b'private',version='accepted-v1'):
        self.content=content;self.version=version;self.requests=[];self.streams=[];self.conflict=False;self.media='application/pdf'
    def head_object(self,**request):
        self.requests.append(('head',request));return {'VersionId':self.version,'ContentType':self.media}
    def get_object(self,**request):
        self.requests.append(('get',request));stream=io.BytesIO(self.content);self.streams.append(stream)
        return {'ContentLength':len(self.content),'Body':stream,'ContentType':self.media}
    def put_object(self,**request):
        self.requests.append(('put',request))
        if self.conflict:raise ClientError({'Error':{'Code':'PreconditionFailed'},'ResponseMetadata':{'HTTPStatusCode':412}},'PutObject')
        return {'VersionId':self.version}

@pytest.mark.parametrize('version',[None,'null'])
def test_unversioned_read_is_never_accepted(monkeypatch,version):
    client=S3();monkeypatch.setattr(storage,'client',lambda *_:client)
    with pytest.raises(Problem) as missing:storage.versioned_read('private','owned',version,8)
    assert missing.value.code=='VERSIONING_REQUIRED' and not client.requests

def test_bounded_read_closes_body_and_pins_the_authorized_version(monkeypatch):
    client=S3();monkeypatch.setattr(storage,'client',lambda *_:client)
    assert storage.versioned_read('private','owned','accepted-v1',7)==b'private'
    assert client.requests[-1][1]['VersionId']=='accepted-v1' and client.streams[-1].closed
    with pytest.raises(Problem):storage.versioned_read('private','owned','accepted-v1',6)
    assert client.streams[-1].closed
    original=client.get_object
    def lying_length(**request):result=original(**request);result['ContentLength']=1;return result
    client.get_object=lying_length
    with pytest.raises(Problem):storage.versioned_read('private','owned','accepted-v1',6)
    assert client.streams[-1].closed

def test_conditional_publication_reconciles_same_version_but_rejects_changed_content(monkeypatch):
    client=S3();monkeypatch.setattr(storage,'client',lambda *_:client)
    assert storage.put_versioned('private','owned',b'private',conditional=True)=='accepted-v1'
    put=client.requests[0][1]
    assert put['IfNoneMatch']=='*' and put['ContentLength']==7 and put['ServerSideEncryption']=='AES256'
    client.conflict=True
    assert storage.put_versioned('private','owned',b'private',conditional=True)=='accepted-v1'
    assert client.requests[-1][1]['VersionId']=='accepted-v1'
    with pytest.raises(Problem) as changed:storage.put_versioned('private','owned',b'changed',conditional=True)
    assert changed.value.code=='IMMUTABLE_OBJECT_CONFLICT'
    client.conflict=False;client.version=None
    with pytest.raises(Problem) as missing:storage.put_versioned('private','owned',b'private')
    assert missing.value.code=='VERSIONING_REQUIRED'

def test_actual_sdk_upload_signature_binds_size_checksum_conditional_and_encryption(monkeypatch):
    session=botocore.session.Session(session_vars={'profile':(None,None,None,None)})
    sdk=boto3.Session(botocore_session=session).client('s3',region_name='us-east-2',endpoint_url='http://localhost:4566',
        aws_access_key_id='fictional-unit-key',aws_secret_access_key='fictional-unit-secret',config=storage.Config(signature_version='s3v4'))
    monkeypatch.setattr(storage,'client',lambda *_,**__:sdk)
    artifact=SimpleNamespace(id='ticket',bucket='private',key='quarantine/owned',size=7,media_type='video/mp4',sha256=hashlib.sha256(b'private').hexdigest())
    ticket=storage.upload_ticket(artifact);signed=parse_qs(urlsplit(ticket['upload_url']).query)
    assert ticket['method']=='PUT' and ticket['expires_in_seconds']==300
    assert {'content-length','content-type','if-none-match','x-amz-checksum-sha256'}<=set(signed['X-Amz-SignedHeaders'][0].split(';'))
    assert ticket['required_headers']['If-None-Match']=='*' and ticket['required_headers']['Content-Length']=='7'

@pytest.mark.parametrize('content,media,valid',[(b'%PDF-1.7 fixture','application/pdf',True),(b'not PDF','application/pdf',False),(b'1234ftyp1234','video/mp4',True),(b'not mp4','video/mp4',False)])
def test_artifact_media_signature_is_checked_on_pinned_bytes(monkeypatch,content,media,valid):
    client=S3(content);client.media=media;monkeypatch.setattr(storage,'client',lambda *_:client)
    artifact=SimpleNamespace(bucket='private',key='owned',size=len(content),sha256=hashlib.sha256(content).hexdigest(),media_type=media)
    if valid:
        assert storage.verify_artifact(artifact)=='accepted-v1'
        assert client.requests[-1][1]['VersionId']=='accepted-v1'
    else:
        with pytest.raises(Problem) as bad:storage.verify_artifact(artifact)
        assert bad.value.code=='MEDIA_MISMATCH'

def test_object_cleanup_includes_markers_and_never_reports_partial_error_success(monkeypatch):
    class Cleanup:
        def get_paginator(self,name):assert name=='list_object_versions';return self
        def paginate(self,**request):return [{'Versions':[{'Key':'owned/v','VersionId':'1'},{'Key':'foreign','VersionId':'2'}],'DeleteMarkers':[{'Key':'owned/m','VersionId':'3'}]}]
        def delete_objects(self,**request):self.deleted=request['Delete']['Objects'];return {'Errors':[{'Code':'AccessDenied'}]} if self.failed else {}
    client=Cleanup();client.failed=False;monkeypatch.setattr(storage,'client',lambda *_:client)
    assert storage.delete_versions('private','owned/')==2
    assert client.deleted==[{'Key':'owned/v','VersionId':'1'},{'Key':'owned/m','VersionId':'3'}]
    client.failed=True
    with pytest.raises(Problem) as failed:storage.delete_versions('private','owned/')
    assert failed.value.code=='OBJECT_CLEANUP_INCOMPLETE'
