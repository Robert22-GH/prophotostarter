import os, hashlib
import boto3
from botocore.client import Config

_s3 = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION","us-east-1"),
    config=Config(s3={"addressing_style":"virtual"})
)
_BUCKET = os.getenv("S3_BUCKET")

def upload_bytes(fileobj, key, content_type):
    fileobj.seek(0); data = fileobj.read()
    sha = hashlib.sha256(data).hexdigest()
    fileobj.seek(0)
    _s3.upload_fileobj(fileobj, _BUCKET, key, ExtraArgs={"ContentType": content_type, "ACL":"private"})
    return sha

def presign_get(key, seconds=300):
    return _s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": _BUCKET, "Key": key},
        ExpiresIn=seconds
    )
