# --- Provider and Variables ---

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = { # Required for the service identity resource
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

provider "google-beta" {
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
  description = "The zone for the resources (often needed for GKE)"
  type        = string
  default     = "us-central1-a"
}

# --- VPC Network and Firewall Rules (Needed for GKE) ---

resource "google_compute_network" "vpc_network" {
  name                    = "gke-network-tf"
  auto_create_subnetworks = true
}

resource "google_compute_firewall" "allow_gke_traffic" {
  name    = "allow-gke-ingress"
  network = google_compute_network.vpc_network.name

  # Allow HTTP/HTTPS to the Load Balancer
  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  # Allow internal communication required for GKE's control plane to reach nodes
  source_ranges = ["10.128.0.0/9"] 
  
  # Apply to GKE nodes (using default GKE tags)
  target_tags   = ["gke-my-gke-cluster-all"] 
}

# --- GKE API Enablement and Cluster Configuration ---

# Ensure the GKE API is recognized
resource "google_project_service_identity" "gke_service_identity" {
  provider = google-beta
  project  = var.project_id
  service  = "container.googleapis.com"
}

# GKE Cluster Definition
resource "google_container_cluster" "primary" {
  name                     = "my-gke-cluster"
  location                 = var.zone 
  initial_node_count       = 1
  remove_default_node_pool = true 
  network                  = google_compute_network.vpc_network.name

  # Enable Workload Identity (Best practice)
  workload_identity_config {
    identity_namespace = "${var.project_id}.svc.id.goog"
  }

  release_channel {
    channel = "REGULAR"
  }

  timeouts {
    create = "30m"
    update = "40m"
  }
}

# GKE Node Pool Definition
resource "google_container_node_pool" "primary_nodes" {
  name       = "primary-node-pool"
  location   = var.zone
  cluster    = google_container_cluster.primary.name
  node_count = 1

  node_config {
    machine_type = "e2-small"
    disk_size_gb = 20
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
    # Use the default compute service account for nodes
    service_account = "${var.project_id}-compute@developer.gserviceaccount.com" 
  }
}

# --- Output the GKE Cluster endpoint ---

output "gke_cluster_endpoint" {
  description = "The IP address of the cluster control plane."
  value       = google_container_cluster.primary.endpoint
}
