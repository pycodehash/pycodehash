from __future__ import annotations

import os
from typing import Any

import boto3

from pycodehash.datasets.approximate_hasher import ApproximateHasher


def s3path_to_bucket_key(s3_file_path: str):
    split = [
        s for s in s3_file_path.split("/") if not s.startswith("s3") and len(s) > 0
    ]
    bucket = split[0]
    key = "/".join(split[1:])
    return bucket, key


class S3Hash(ApproximateHasher):
    def collect_metadata(
        self,
        s3_file_path: str | None = None,
        bucket: str | None = None,
        key: str | None = None,
        s3_client: Any = None,
        endpoint_url: str = os.env["AWS_S3_ENDPOINT_URL"],
    ) -> dict[str, Any]:
        """Get metadata of s3 file (specifically the MD5 hash of the file on s3)

        Args:
            s3_file_path:  path to the file on s3
            bucket: name of the bucket
            key: bucket key
            s3_client: boto3 s3 client
            endpoint_url: endpoint URL in case s3 client is not provided

        Returns:
            metadata dictionary
        """
        if s3_file_path is not None:
            bucket, key = s3path_to_bucket_key(s3_file_path=s3_file_path)
        assert None not in [bucket, key]

        if s3_client is None:
            s3_client = boto3.client("s3", endpoint_url=endpoint_url)

        # The list_objects_v2() method in s3 client object will fetch the metadata (headers) of a given object
        # stored in the s3 bucket. (Not the object itself.) If key is a directory it will retrieve all object in the
        # directory in alphabetic order. Per object: Etag (md5 hash), size, last modification data, and storage class.
        files = s3_client.list_objects_v2(Bucket=bucket, Prefix=key)
        for file in files:
            # clean up the ETag hash, remove unnecessary quotes.
            file["ETag"] = file["ETag"].strip('"')

        dict_to_hash = {}
        for idx, file in enumerate(files):
            keys = list(file.keys())
            for key in keys:
                dict_to_hash[f"__file{idx}__{key}"] = file[key]

        return dict_to_hash
