from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse

import boto3

from pycodehash.datasets.approximate_hasher import ApproximateHasher


def s3path_to_bucket_key(s3_file_path: str) -> tuple[str, str]:
    result = urlparse(s3_file_path)

    bucket = result.netloc
    key = result.path.lstrip("/")
    if result.query:
        key += "?" + result.query

    return bucket, key


class S3Hash(ApproximateHasher):
    def __init__(self, s3_client: Any = None, endpoint_url: str = os.environ.get("AWS_S3_ENDPOINT_URL", "")):
        """Initialization of S3Hash

        Args:
            s3_client: boto3 s3 client
            endpoint_url: endpoint URL in case s3 client is not provided
        """
        super().__init__()

        if s3_client is None:
            s3_client = boto3.client("s3", endpoint_url=endpoint_url)

        self.s3_client = s3_client

    def collect_metadata(
        self, s3_file_path: str | None = None, bucket: str | None = None, key: str | None = None
    ) -> dict[str, Any]:
        """Get metadata of s3 file (specifically the MD5 hash of the file on s3)
        [Documentation of `list_objects_v2`](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/list_objects_v2.html)

        Args:
            s3_file_path: path to the file on s3
            bucket: name of the bucket
            key: bucket key

        Returns:
            metadata dictionary

        """
        if s3_file_path is not None:
            bucket, key = s3path_to_bucket_key(s3_file_path=s3_file_path)
        assert None not in {bucket, key}

        # The list_objects_v2() method in s3 client object will fetch the metadata (headers) of a given object
        # stored in the s3 bucket. (Not the object itself.) If key is a directory, it will retrieve all objects in the
        # directory in alphabetic order. Per object: ETag (md5 hash), size, last modification data, and storage class.
        response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=key)
        files = response["Contents"]

        for file in files:
            # clean up the ETag hash, remove unnecessary quotes.
            file["ETag"] = file["ETag"].strip('"')

        return {f"__file{idx}__ETag": file["ETag"] for idx, file in enumerate(sorted(files, key=lambda x: x["Key"]))}
