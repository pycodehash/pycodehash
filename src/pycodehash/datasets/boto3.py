"""Helper functions for interacting with S3 on DAP."""

from __future__ import annotations

import os
from copy import deepcopy
from typing import Any

import boto3


def _from_env_var(*args, default: dict[str, Any] | None = None):
    for name in args:
        if name in os.environ:
            return os.environ[name]
    return default


class S3ClientFactory:
    def __init__(self, credentials: dict[str, Any] | None = None):
        self.creds = deepcopy(credentials)

    def new(self, clean: bool = False, credentials: dict[str, Any] | None = None) -> boto3.client.S3:
        creds = deepcopy(credentials) if credentials else self.creds
        if creds is None or clean:
            # revert to default AWS environment variables, for endpoint, region, session, access.
            self.creds = {
                "endpoint_url": _from_env_var("AWS_S3_ENDPOINT_URL", "AWS_S3_ENDPOINT"),
                "region_name": _from_env_var("AWS_DEFAULT_REGION", "AWS_S3_REGION"),
                "aws_access_key_id": _from_env_var("AWS_ACCESS_KEY_ID"),
                "aws_secret_access_key": _from_env_var("AWS_SECRET_ACCESS_KEY"),
                "aws_session_token": _from_env_var("AWS_SESSION_TOKEN"),
            }
            creds = self.creds
        return boto3.client("s3", **creds)

    def __call__(self, clean: bool = False, credentials: dict[str, Any] | None = None) -> boto3.Session.client:
        return self.new(clean=clean, credentials=credentials)


_s3_client = S3ClientFactory()


def new_s3_client(clean: bool = False, credentials: dict[str, Any] | None = None) -> boto3.client.S3:
    """Get new connection to S3."""
    return _s3_client(clean=clean, credentials=credentials)
