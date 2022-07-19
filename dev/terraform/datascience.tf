resource "oci_datascience_project" "lol_project" {
  compartment_id = var.compartment_ocid

  description  = "League of Legends Project"
  display_name = "LoL Project"

  depends_on = [
    oci_core_subnet.privatesubnet
  ]
}

# FIXME bad hack: fail to create notebook session with subnet
resource "time_sleep" "wait_a_bit" {
  create_duration = "60s"
}

resource "oci_datascience_notebook_session" "lol_notebook_session" {
  compartment_id = var.compartment_ocid
  project_id     = oci_datascience_project.lol_project.id

  display_name = "League of Legends Notebook Session"

  notebook_session_config_details {
    shape = data.oci_datascience_notebook_session_shapes.ds_shapes.notebook_session_shapes[0].name

    subnet_id = oci_core_subnet.privatesubnet.id
  }

  depends_on = [
    time_sleep.wait_a_bit
  ]

}

data "oci_datascience_notebook_session_shapes" "ds_shapes" {
  compartment_id = var.compartment_ocid
  filter {
    name   = "core_count"
    values = [1]
  }
}

output "ds_notebook_session_shape" {
  value = data.oci_datascience_notebook_session_shapes.ds_shapes.notebook_session_shapes[0].name
}

output "ds_notebook_session" {
  value = oci_datascience_notebook_session.lol_notebook_session.notebook_session_url
}
