from minio import Minio
from minio.error import S3Error
import os
import json

def init_minio():
    MINIO_INTERNAL_ADDRESS = os.environ.get('MINIO_INTERNAL_ADDRESS')
    MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
    MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
    client = Minio(
        MINIO_INTERNAL_ADDRESS,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    bucket_name = "audio"

    # Create the bucket if it doesn't exist
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' created.")
    else:
        print(f"Bucket '{bucket_name}' already exists.")

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
            }
        ]
    }

    # Convert policy dictionary to JSON string
    policy_json = json.dumps(policy)

    # Set the bucket policy
    client.set_bucket_policy(bucket_name, policy_json)
    print(f"Bucket policy for '{bucket_name}' set to public.")
