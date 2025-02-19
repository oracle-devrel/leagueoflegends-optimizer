terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 4.0"
    }
  }
}

provider "oci" {
  tenancy_ocid = var.tenancy_ocid
  region       = var.region
}

provider "oci" {
  alias        = "home_region"
  tenancy_ocid = var.tenancy_ocid
  region       = lookup(data.oci_identity_regions.home_region.regions[0], "name")
}


variable "region" {
  type = string
}

variable "tenancy_ocid" {
  type = string
}

variable "compartment_ocid" {
  type = string
}

variable "ssh_public_key" {
  type = string
}

variable "config_file_profile" {
  type = string
}

variable "riotgames_api_key" {
  type = string
}

variable "desired_number_cpus" {
  type    = string
  default = 4
}

variable "create_iam_policy" {
  type    = bool
  default = true
}

variable "instant_client_lib_dir" {
  type    = string
  default = "/usr/lib/oracle/21/client64/lib"
}
