# Terraform (AWS EC2 + Talos)
## Overview

The tf/ folder contains Terraform code that provisions minimal AWS infrastructure to run a single Talos Linux EC2 instance.

This setup contains:
- One VPC
- One public subnet
- One EC2 instance
- One Elastic IP
- One security group that allows everything


## Infrastructure Managed Here
### VPC

CIDR: 10.0.0.0/16
DNS enabled
Internet Gateway attached

### Subnet

Single public subnet (10.0.0.0/24)
Single AZ
Auto-assign public IPs

### Security Group

Allows all inbound traffic
Allows all outbound traffic
No port restrictions
No protocol restrictions

[!WARNING]
This security group is fully open. This is intentional as once the Talos master is configured properly, nobody without the credentials can connect to it.

### EC2 Instance

AMI: Talos Linux (official Sidero Labs image, auto-discovered)
Instance type: t3.small
Public EC2
Elastic IP attached

### Elastic IP

An Elastic IP is allocated and attached to the instance to provide:
- Stable public endpoint
- IP persistence across reboots

[!NOTE]
Elastic IPs incur cost if allocated and not attached.

Directory Structure
tf/
├── main.tf        # Resources (VPC, subnet, EC2, EIP, SG)
├── variables.tf  # Region, AZ, instance type
├── outputs.tf    # Public IP / Elastic IP outputs
└── versions.tf   # Provider + Terraform version constraints

## Usage
### Prerequisites

- Terraform installed
- AWS CLI installed
- AWS credentials configured via:
```bash
aws configure
```


Terraform automatically uses credentials from:

- ~/.aws/credentials
- environment variables


### Deploy

From repo root:
```bash
cd tf
terraform init
terraform apply
```

Approve when prompted.

### Outputs

After apply, Terraform will print:

- EC2 instance ID
- Elastic IP address

Use the Elastic IP as the stable endpoint.

### Destroy
```bash
terraform destroy
```

This removes all AWS resources created by this folder.