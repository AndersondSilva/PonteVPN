terraform {
  required_providers {
    vultr = {
      source = "vultr/vultr"
      version = "2.11.0"
    }
    hcloud = {
      source = "hetznercloud/hcloud"
      version = "1.35.0"
    }
  }
}

variable "vultr_api_key" {
  type = string
  sensitive = true
}

variable "hcloud_token" {
  type = string
  sensitive = true
}

variable "agent_secret" {
  type = string
  sensitive = true
}

provider "vultr" {
  api_key = var.vultr_api_key
  rate_limit = 100
  retry_limit = 3
}

provider "hcloud" {
  token = var.hcloud_token
}

# 1. Servidor no Brasil (Vultr - São Paulo)
resource "vultr_instance" "vpn_br" {
  plan = "vc2-1c-1gb"
  region = "sgp" # São Paulo
  os_id = 1743 # Ubuntu 22.04 x64
  label = "pontevpn-br-core"
  hostname = "vpn-br.pontevpn.com"
  enable_ipv6 = true
  
  user_data = <<-EOF
              #!/bin/bash
              curl -s https://raw.githubusercontent.com/seu-repo/pontevpn/main/infrastructure/setup-vpn-server.sh | bash -s ${var.agent_secret}
              EOF
}

# 2. Servidor na Europa (Hetzner - Alemanha)
resource "hcloud_server" "vpn_eu" {
  name = "pontevpn-eu-core"
  image = "ubuntu-22.04"
  server_type = "cx11"
  location = "nbg1" # Nuremberg
  
  user_data = <<-EOF
              #!/bin/bash
              curl -s https://raw.githubusercontent.com/seu-repo/pontevpn/main/infrastructure/setup-vpn-server.sh | bash -s ${var.agent_secret}
              EOF
}

output "vpn_br_ip" {
  value = vultr_instance.vpn_br.main_ip
}

output "vpn_eu_ip" {
  value = hcloud_server.vpn_eu.ipv4_address
}
