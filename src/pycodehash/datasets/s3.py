import os
import boto3


def s3path_to_bucket_key(s3_file_path: str):
    split = [s for s in s3_file_path.split('/') if not s.startswith('s3') and len(s) > 0]
    bucket = split[0]
    key = '/'.join(split[1:])
    return bucket, key


def hash_file(s3_file_path: str = None, bucket: str = None, key: str = None,
              endpoint_url: str = os.env['AWS_S3_ENDPOINT_URL']):
    """ Get MD5 hash string of file on s3

    :param str: s3 file path
    :return: MD5 hash
    """
    if s3_file_path is not None:
        bucket, key = s3path_to_bucket_key(s3_file_path=s3_file_path)
    assert None not in [bucket, key]

    s3 = boto3.client('s3', endpoint_url=endpoint_url)

    # The head_object() method in s3 client object will fetch the metadata (headers) of a given object
    # stored in the s3 bucket. Not the object itself.
    obj = s3.head_object(Bucket=bucket, Key=key)
    etag = obj['ETag'].strip('"')
    return etag
