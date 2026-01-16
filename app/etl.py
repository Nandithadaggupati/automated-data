import os
import io
import boto3
import pandas as pd

BUCKET_NAME = os.getenv("BUCKET_NAME")
RAW_KEY = os.getenv("RAW_KEY", "raw/raw_data.csv")
PROCESSED_KEY = os.getenv("PROCESSED_KEY", "processed/processed_data.csv")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
ENDPOINT_URL = os.getenv("ENDPOINT_URL", "http://localstack:4566")

def main():
    session = boto3.session.Session()
    s3 = session.client(
        service_name="s3",
        region_name=AWS_REGION,
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )

    obj = s3.get_object(Bucket=BUCKET_NAME, Key=RAW_KEY)
    raw_bytes = obj["Body"].read()
    df = pd.read_csv(io.BytesIO(raw_bytes))

    df = df[df["value"] > 10]
    df["value_x2"] = df["value"] * 2

    out_buf = io.StringIO()
    df.to_csv(out_buf, index=False)
    out_bytes = out_buf.getvalue().encode("utf-8")

    s3.put_object(
      Bucket=BUCKET_NAME,
      Key=PROCESSED_KEY,
      Body=out_bytes,
      ContentType="text/csv",
    )

    print(f"Written processed file to s3://{BUCKET_NAME}/{PROCESSED_KEY}")

if __name__ == "__main__":
    main()
