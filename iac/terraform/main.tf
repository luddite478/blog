locals {
  env_vars = {
    for tuple in regexall("(.*?)=(.*)", file("../.env")) :
    tuple[0] => replace(replace(tuple[1], "/\"/", ""), "/\\r$/", "")
  }
}

terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

resource "digitalocean_floating_ip" "blog_ip" {
  droplet_id = digitalocean_droplet.blog.id
  region = digitalocean_droplet.blog.region
}

output "floating_ip" {
  value = digitalocean_floating_ip.blog_ip.ip_address
}

provider "digitalocean" {
  token = local.env_vars["DIGITALOCEAN_TOKEN"]
}

resource "digitalocean_ssh_key" "key1" {
  name       = "deployment_key"
  public_key = file(local.env_vars["SSH_PUBLIC_KEY_PATH"])
}

provider "random" {}

resource "random_id" "server_suffix" {
  byte_length = 4 
}

resource "digitalocean_droplet" "blog" {
  image  = "ubuntu-20-04-x64"
  name   = "blog-${random_id.server_suffix.hex}"
  region = "ams3"
  size   = "s-1vcpu-1gb"
  ssh_keys = [
    digitalocean_ssh_key.key1.id,
  ]

  connection {
    type        = "ssh"
    user        = local.env_vars["SSH_USER"]
    private_key = file(local.env_vars["SSH_PRIVATE_KEY_PATH"])
    host        = self.ipv4_address
  }

  user_data = templatefile("${path.module}/user_data.tpl", {
    env_content = file("${path.module}/../../.env")
  })
}

output "ip" {
  value = digitalocean_droplet.blog.ipv4_address
}