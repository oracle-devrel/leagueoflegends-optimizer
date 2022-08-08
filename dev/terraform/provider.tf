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

variable "instant_client_lib_dir" {
  type    = string
  default = "/usr/lib/oracle/21/client64/lib"
}
