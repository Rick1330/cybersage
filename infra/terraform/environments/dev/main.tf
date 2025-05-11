# Development Environment
variable "environment" {
  default = "dev"
}

# Configure AWS Provider
provider "aws" {
  region = "us-east-1"
}
