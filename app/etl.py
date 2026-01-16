import os
import boto3
import pandas as pd
from io import StringIO

BUCKET_NAME = os.getenv("BUCKET_NAME", "etl-demo-bucket")
RAW_KEY = os.getenv("RAW_KEY", "raw/raw_data.csv")
PROCESSED_KEY = os.getenv("PROCESSED_KEY", "processed/processed_data.csv")

LOCALSTACK_HOST = os.getenv("LOCALSTACK_HOST", "localhost")
LOCALSTACK_PORT = os.getenv("LOCALSTACK_PORT", "4566")
LOCALSTACK_ENDPOINT = f"http://{LOCALSTACK_HOST}:{LOCALSTACK_PORT}"

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


def main():
    s3 = boto3.client(
        "s3",
        endpoint_url=LOCALSTACK_ENDPOINT,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    obj = s3.get_object(Bucket=BUCKET_NAME, Key=RAW_KEY)
    df = pd.read_csv(obj["Body"])

    df.columns = [c.upper() for c in df.columns]

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=PROCESSED_KEY,
        Body=csv_buffer.getvalue(),
    )

    print(f"Written processed file to s3://{BUCKET_NAME}/{PROCESSED_KEY}")


if __name__ == "__main__":
    main()
