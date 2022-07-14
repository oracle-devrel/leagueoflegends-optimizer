resource "oci_identity_policy" "datascience_vcn_policy" {
  compartment_id = "ocid1.compartment.oc1..aaaaaaaaqeolpprws7vszzgzndaukypaxvfbfigeieahoufpq75wyxvmba3q"
  description    = "Allow Data Science service to access VCN"
  name           = "ds_access_vcn"
  statements     = ["allow service datascience to use virtual-network-family in compartment id ${var.compartment_ocid}"]
}
