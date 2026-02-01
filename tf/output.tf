output "elastic_ip" {
  value = aws_eip.talos.public_ip
}
