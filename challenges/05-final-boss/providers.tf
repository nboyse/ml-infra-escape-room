terraform {
  required_version = ">= 0.11"
}

provider "aws" {
  region = "us-east-1"

  access_key = "AKIAFAKEACCESSKEY"
  secret_key = "super-secret-key"

  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  skip_region_validation      = true

  insecure = true
}