variable "db_password" {
  type    = string
  default = "Password123!"
}

variable "open_cidr" {
  type    = string
  default = "0.0.0.0/0"
}

variable "environment" {
  default = "prod"
}

variable "api_key" {
  default = "sk-prod-super-secret"
}

variable "instance_type" {
  default = "p5.48xlarge"
}