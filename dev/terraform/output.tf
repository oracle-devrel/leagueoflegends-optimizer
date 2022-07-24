output "compute" {
    value = "ssh opc@${oci_core_instance.compute[0].public_ip}"
}

output "autonomous_database_admin_password" {
  value = random_password.autonomous_database_admin_password.result
  sensitive = true
}