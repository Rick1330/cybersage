# Staging Environment
variable "environment" {
  default = "staging"
}

# Configure AWS Provider
provider "aws" {
  region = "us-east-1"
}
