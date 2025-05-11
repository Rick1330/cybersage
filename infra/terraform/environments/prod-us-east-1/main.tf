# Production US East Environment
variable "environment" {
  default = "prod"
}

# Configure AWS Provider
provider "aws" {
  region = "us-east-1"
}
