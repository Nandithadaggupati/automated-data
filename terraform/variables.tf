variable "bucket_name" {
  type        = string
  description = "S3 bucket name"
  default     = "etl-demo-bucket"
}

variable "region" {
  type        = string
  description = "AWS region"
  default     = "us-east-1"
}

variable "localstack_s3_endpoint" {
  type        = string
  description = "LocalStack S3 endpoint"
  default     = "http://localstack:4566"
}
