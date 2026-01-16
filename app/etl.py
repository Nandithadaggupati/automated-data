import os
import boto3
import pandas as pd
from io import StringIO

# Environment variables (NO hard-coding)
BUCKET_NAME = os.getenv("BUCKET_NAME", "etl-demo-bucket")
RAW_KEY = os.getenv("RAW_KEY", "raw/raw_data.csv")
PROCESSED_KEY = os.getenv("PROCESSED_KEY", "processed/processed_data.csv")
LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT", "http://localhost:4566")

def main():
    s3 = boto3.client(
        "s3",
        endpoint_url=LOCALSTACK_ENDPOINT,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1"
    )

    # Read raw data
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=RAW_KEY)
    df = pd.read_csv(obj["Body"])

    # Simple transformation (example)
    df.columns = [c.upper() for c in df.columns]

    # Write processed data
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=PROCESSED_KEY,
        Body=csv_buffer.getvalue()
    )

    print(f"Written processed file to s3://{BUCKET_NAME}/{PROCESSED_KEY}")

if __name__ == "__main__":
    main()
