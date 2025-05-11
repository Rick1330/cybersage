# Production EU West Environment
variable "environment" {
  default = "prod"
}

# Configure AWS Provider
provider "aws" {
  region = "eu-west-1"
}
