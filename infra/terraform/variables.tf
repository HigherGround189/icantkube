variable "region" {
  type    = string
  default = "us-east-1"
}

variable "az" {
  type    = string
  default = "us-east-1a"
}

variable "instance_type" {
  type    = string
  default = "m7i-flex.large"
}

variable "key_name" {
  type        = string
  default     = null
  description = "Existing AWS EC2 Key Pair name used for SSH access to the Ubuntu instance."
}
