import boto3
from moto import mock_s3
from pycodehash.datasets.s3 import S3Hash, s3path_to_bucket_key


def test_s3path_to_bucket_key():
    path = "s3://bucket_name/folder1/folder2/file1.json"
    bucket, key = s3path_to_bucket_key(path)
    assert bucket == "bucket_name"
    assert key == "folder1/folder2/file1.json"


@mock_s3
def test_s3_hash():
    bucket_name = "bucket_name"
    key = "folder1/folder2/file1.txt"
    s3_file_path = f"s3://{bucket_name}/{key}"

    client = boto3.client("s3", region_name="us-east-1")
    client.create_bucket(Bucket=bucket_name)
    client.put_object(Bucket=bucket_name, Key=key, Body="hello world")

    s3h = S3Hash(s3_client=client)
    result = s3h.collect_metadata(s3_file_path)
    assert isinstance(result, dict)
    assert len(result) == 1
    assert result["etag"] == "5eb63bbbe01eeed093cb22bb8f5acdc3"

    assert s3h.compute_hash(s3_file_path) == "578825776ff1306b1ee7dfeef1e2cb8277db7b261d15a2229296934f375c90bb"
