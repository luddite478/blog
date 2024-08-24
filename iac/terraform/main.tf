locals {
  env_vars = { for tuple in regexall("(.*?)=(.*)", file("../.env")) : tuple[0] => tuple[1] }
}

terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = local.env_vars["DIGITALOCEAN_TOKEN"]
}

resource "digitalocean_ssh_key" "default" {
  name       = "deployment_key"
  public_key = file(local.env_vars["SSH_PUBLIC_KEY_PATH"])
}

resource "digitalocean_droplet" "web" {
  image  = "docker-20-04"
  name   = "web-droplet"
  region = "nyc3"
  size   = "s-1vcpu-1gb"
  ssh_keys = [
    digitalocean_ssh_key.default.id,
  ]

  connection {
    type        = "ssh"
    user        = file(local.env_vars["SSH_USER"])
    private_key = file(local.env_vars["SSH_PRIVATE_KEY_PATH"])
    host        = self.ipv4_address
  }

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y git docker docker-compose",
      "git clone https://your-repository-url.git /app",
      "cd /app && sudo docker-compose up -d"
    ]
  }
}

output "ip" {
  value = digitalocean_droplet.web.ipv4_address
}

variable "do_token" {}
variable "ssh_public_key_path" {}
variable "git_repo_url" {}