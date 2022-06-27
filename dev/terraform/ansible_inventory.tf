resource "local_file" "ansible_inventory" {
  content = templatefile("${path.module}/inventory.tftpl",
    {
     public_ip = oci_core_instance.compute[0].public_ip
    }
  )
  filename = "${path.module}/generated/app.ini"
}