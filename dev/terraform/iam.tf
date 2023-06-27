resource "oci_identity_policy" "datascience_vcn_policy" {
  provider       = oci.home_region
  count          = var.create_iam_policy ? 1 : 0
  compartment_id = var.tenancy_ocid
  description    = "Allow Data Science service to access VCN"
  name           = "ds_access_vcn-${random_string.deploy_id.result}"
  statements     = ["allow service datascience to use virtual-network-family in compartment id ${var.compartment_ocid}"]
}
