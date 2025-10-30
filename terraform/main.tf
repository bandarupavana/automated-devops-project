# --- Provider and Variables ---

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Your specific project ID is now the default
variable "project_id" {
  description = "The ID of the Google Cloud Project"
  type        = string
  default     = "genial-core-476715-n3"
}
variable "region" {
  description = "The region for the resources"
  type        = string
  default     = "us-central1"
}
variable "zone" {
  description = "The zone for the VM instance"
  type        = string
  default     = "us-central1-a"
}

# --- VM Network and Firewall Rules ---

resource "google_compute_network" "vpc_network" {
  name                    = "vm-network-tf"
  auto_create_subnetworks = true
}

resource "google_compute_firewall" "allow_ssh" {
  name    = "allow-ssh-for-vm"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  source_ranges = ["0.0.0.0/0"]
}

# --- Compute Engine VM Instance with Cloud SDK Installation ---

resource "google_compute_instance" "cloud_sdk_vm_instance" {
  name         = "cloud-sdk-vm-provisioned"
  machine_type = "e2-medium"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size  = 20
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.name
    access_config {
    }
  }

  service_account {
    # This is a common pattern for the default Compute Engine SA. You should verify this in the GCP Console.
    email  = "${var.project_id}-compute@developer.gserviceaccount.com"
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  # Startup script to install Google Cloud SDK
  metadata_startup_script = <<-EOF
    #!/bin/bash
    set -e
    
    # Install dependencies for Cloud SDK
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates gnupg
    
    # Add the Google Cloud SDK distribution URI and key
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
    
    # Update and install the Cloud SDK
    sudo apt-get update && sudo apt-get install -y google-cloud-cli
    
    echo "Google Cloud SDK successfully installed on VM."
    EOF
}

# --- Output ---

output "vm_external_ip" {
  description = "The external IP address of the provisioned VM"
  value       = google_compute_instance.cloud_sdk_vm_instance.network_interface[0].access_config[0].nat_ip
}