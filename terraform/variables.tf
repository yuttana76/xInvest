variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "ap-southeast-1"
}

variable "project" {
  description = "Name prefix used for tagging and resource naming"
  type        = string
  default     = "xinvest"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "root_volume_size" {
  description = "Root EBS volume size in GB"
  type        = number
  default     = 50
}

variable "allowed_ssh_cidr" {
  description = "CIDR allowed to SSH into the instance, e.g. 1.2.3.4/32 — never leave this as 0.0.0.0/0"
  type        = string
}

variable "public_key_path" {
  description = "Path to the local SSH public key file to install on the instance"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "ecr_keep_image_count" {
  description = "Number of tagged images to retain per ECR repo before lifecycle policy expires the rest"
  type        = number
  default     = 10
}
