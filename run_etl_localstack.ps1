# run_etl_localstack.ps1
# Automated ETL + LocalStack setup

# Variables
$NETWORK_NAME = "localstack-net"
$LOCALSTACK_NAME = "localstack"
$LOCALSTACK_IMAGE = "localstack/localstack:latest"
$ETL_IMAGE = "etl-image:latest"
$BUCKET_NAME = "etl-demo-bucket"
$RAW_KEY = "raw/raw_data.csv"
$PROCESSED_KEY = "processed/processed_data.csv"
$LOCALSTACK_ENDPOINT = "http://localhost:4566"
$AWS_ACCESS_KEY_ID = "test"
$AWS_SECRET_ACCESS_KEY = "test"
$AWS_DEFAULT_REGION = "us-east-1"

# 1. Create Docker network if missing
try {
    docker network inspect $NETWORK_NAME | Out-Null
    Write-Host "Docker network '$NETWORK_NAME' already exists"
} catch {
    docker network create $NETWORK_NAME
    Write-Host "Docker network '$NETWORK_NAME' created"
}

# 2. Stop/remove old LocalStack container
$old = docker ps -a --format "{{.Names}}" | Select-String $LOCALSTACK_NAME
if ($old) {
    docker stop $LOCALSTACK_NAME
    docker rm $LOCALSTACK_NAME
    Write-Host "Old LocalStack container stopped and removed"
} else {
    Write-Host "No old LocalStack container found"
}

# 3. Start LocalStack container
docker run -d --name $LOCALSTACK_NAME --network $NETWORK_NAME -p 4566:4566 $LOCALSTACK_IMAGE
Write-Host "LocalStack starting..."
Start-Sleep -Seconds 10

# 4. Create S3 bucket
aws --endpoint-url=$LOCALSTACK_ENDPOINT s3 mb s3://$BUCKET_NAME 2>$null
Write-Host "Bucket '$BUCKET_NAME' created"

# 5. Upload raw data if exists
if (Test-Path ".\raw_data.csv") {
    aws --endpoint-url=$LOCALSTACK_ENDPOINT s3 cp .\raw_data.csv s3://$BUCKET_NAME/$RAW_KEY
    Write-Host "Uploaded raw_data.csv to s3://$BUCKET_NAME/$RAW_KEY"
} else {
    Write-Host "Warning: raw_data.csv not found!"
}

# 6. Build ETL Docker image
docker build -t $ETL_IMAGE .\app
Write-Host "ETL Docker image built"

# 7. Run ETL container
docker run --network $NETWORK_NAME `
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID `
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY `
    -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION `
    -e BUCKET_NAME=$BUCKET_NAME `
    -e RAW_KEY=$RAW_KEY `
    -e PROCESSED_KEY=$PROCESSED_KEY `
    -e LOCALSTACK_ENDPOINT=$LOCALSTACK_ENDPOINT `
    $ETL_IMAGE

Write-Host "ETL container executed"

# 8. Verify processed file
Write-Host "Verifying ETL output..."
aws --endpoint-url=$LOCALSTACK_ENDPOINT s3 ls s3://$BUCKET_NAME/$PROCESSED_KEY
