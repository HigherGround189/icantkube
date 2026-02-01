provider "aws" {
  region = var.region
}

resource "aws_vpc" "this" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.this.id
  cidr_block              = "10.0.0.0/24"
  availability_zone       = var.az
  map_public_ip_on_launch = true
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "allow_all" {
  name   = "allow-all"
  vpc_id = aws_vpc.this.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "aws_ami" "talos" {
  most_recent = true
  owners      = ["540036508848"] # Sidero Labs (Talos)

  filter {
    name   = "name"
    values = ["talos-*"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "talos" {
  ami                         = data.aws_ami.talos.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.allow_all.id]
  associate_public_ip_address = true

  tags = {
    Name = "Talos-II"
  }
}

resource "aws_eip" "talos" {
  domain = "vpc"
}

resource "aws_eip_association" "talos" {
  instance_id   = aws_instance.talos.id
  allocation_id = aws_eip.talos.id
}
