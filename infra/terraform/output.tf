output "elastic_ip" {
  value = aws_eip.control_plane.public_ip
}

output "ssh_user" {
  value = "ubuntu"
}
