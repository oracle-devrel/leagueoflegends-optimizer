resource "local_file" "dotenv" {
  content = templatefile("${path.module}/dotenv.tftpl",
    {
     db_password = random_password.autonomous_database_admin_password.result
     connection_string = oci_database_autonomous_database.adb.connection_strings[0].profiles[0].value
     riotgames_api_key = var.riotgames_api_key
    }
  )
  filename = "${path.module}/generated/.env"
}