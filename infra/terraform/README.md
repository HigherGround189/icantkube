# Terraform (AWS EC2 + Ubuntu + k3s)

## Overview
This folder provisions AWS infrastructure for a single Ubuntu EC2 node used as the k3s control-plane host.

Infrastructure includes:
- One VPC
- One public subnet
- One Internet Gateway and route table
- One security group (currently wide open)
- One Ubuntu EC2 instance
- One Elastic IP attached to the instance
- One additional EBS data volume

## Files
- `main.tf`: VPC, subnet, security group, EC2 instance, EIP, and EBS resources
- `variables.tf`: region, AZ, instance type, and optional SSH key pair name
- `output.tf`: Elastic IP and SSH username output
- `versions.tf`: Terraform and provider version constraints

## Prerequisites
- Terraform
- AWS credentials configured (for example with `aws configure`)
- Existing AWS EC2 key pair name set through `TF_VAR_key_name` (recommended for SSH access)

## Usage
From repo root:

```bash
cd infra/terraform
terraform init
terraform apply
```

Useful outputs:
- `elastic_ip`: public IP for SSH and kubeconfig endpoint
- `ssh_user`: default SSH username (`ubuntu`)

Destroy:

```bash
terraform destroy
```

## Notes
- The security group currently allows all inbound and outbound traffic.
- k3s installation and Kubernetes bootstrap are handled by `infra/deploy-cloud.sh`, not Terraform directly.
