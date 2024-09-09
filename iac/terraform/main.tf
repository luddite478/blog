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

resource "digitalocean_droplet" "blog" {
  image  = "ubuntu-20-04-x64"
  name   = "blog"
  region = "ams3"
  size   = "s-1vcpu-1gb"
  ssh_keys = [
    digitalocean_ssh_key.key1.id,
  ]

  user_data = templatefile("${path.module}/user_data.tpl", {
    HOST_ROOT_PASSWORD = local.env_vars["HOST_ROOT_PASSWORD"],
    GITHUB_WORKFLOW_TOKEN = local.env_vars["GITHUB_WORKFLOW_TOKEN"],
    TAILSCALE_AUTH_KEY = local.env_vars["TAILSCALE_AUTH_KEY"],
    TAILSCALE_API_KEY = local.env_vars["TAILSCALE_API_KEY"]
  })
}

resource "digitalocean_volume" "blog_volume" {
  name   = "blog-volume"
  region = "ams3"
  size   = 5
}

resource "digitalocean_volume_attachment" "blog_volume_attachment" {
  droplet_id = digitalocean_droplet.blog.id
  volume_id  = digitalocean_volume.blog_volume.id
}

output "ip" {
  value = digitalocean_droplet.blog.ipv4_address
}