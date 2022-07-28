resource "oci_identity_policy" "datascience_vcn_policy" {
  compartment_id = var.tenancy_ocid
  description    = "Allow Data Science service to access VCN"
  name           = "ds_access_vcn-${random_string.deploy_id.result}"
  statements     = ["allow service datascience to use virtual-network-family in compartment id ${var.compartment_ocid}"]
}

# resource "oci_identity_dynamic_group" "data_science_dynamic_group" {
#   compartment_id = var.tenancy_ocid
#   name           = "data_science_dynamic_group"
#   description    = "Data Science Dynamic Group"
#   matching_rule  = "ALL { resource.type = 'datasciencenotebooksession' }"
# }
