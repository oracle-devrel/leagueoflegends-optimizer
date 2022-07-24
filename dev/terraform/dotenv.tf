resource "local_file" "dotenv" {
  content = templatefile("${path.module}/dotenv.tftpl",
    {
      db_password            = random_password.autonomous_database_admin_password.result
      connection_string      = oci_database_autonomous_database.adb.connection_strings[0].profiles[0].value
      riotgames_api_key      = var.riotgames_api_key
      instant_client_lib_dir = var.instant_client_lib_dir
    }
  )
  filename = "${path.module}/generated/.env"
}
