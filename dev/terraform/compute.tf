variable "instance_name" {
  default = "lol"
}

data "oci_core_shapes" "core_shapes" {
  compartment_id      = var.tenancy_ocid
  availability_domain = data.oci_identity_availability_domain.ad.name
}

locals {
  shape_names = [
    for each in data.oci_core_shapes.core_shapes.shapes :
    each.name if each.ocpus <= var.instance_ocpus && each.memory_in_gbs <= var.instance_shape_config_memory_in_gbs && each.is_flexible == true
  ]
}

output "compute_available_shapes" {
  value = local.shape_names
}

variable "instance_shape" {
  default = "VM.Standard.E4.Flex"
}

variable "instance_ocpus" {
  default = 1
}

variable "instance_shape_config_memory_in_gbs" {
  default = 16
}

data "oci_core_images" "images" {
  compartment_id           = var.compartment_ocid
  shape                    = var.instance_shape
  operating_system         = "Oracle Linux"
  operating_system_version = "8"
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

data "oci_identity_availability_domain" "ad" {
  compartment_id = var.tenancy_ocid
  ad_number      = 1
}

resource "oci_core_instance" "compute" {
  count               = 1
  availability_domain = data.oci_identity_availability_domain.ad.name
  compartment_id      = var.compartment_ocid
  display_name        = "${var.instance_name}-${random_string.deploy_id.result}_${count.index}"
  shape               = var.instance_shape

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
  }

  shape_config {
    ocpus         = var.instance_ocpus
    memory_in_gbs = var.instance_shape_config_memory_in_gbs
  }

  create_vnic_details {
    subnet_id                 = oci_core_subnet.publicsubnet.id
    display_name              = var.instance_name
    assign_public_ip          = true
    assign_private_dns_record = true
    hostname_label            = "${var.instance_name}${count.index}"
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.images.images[0].id
  }

  timeouts {
    create = "60m"
  }
}
