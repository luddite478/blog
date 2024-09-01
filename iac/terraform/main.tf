terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
    tailscale = {
      source  = "tailscale/tailscale"
      version = "~> 0.16.2"
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
    APPLICATION_ENV_VARIABLES_BASE64 = filebase64("${path.module}/../../blog/.server.env"),
    HAPROXY_ENV_VARIABLES_BASE64 = filebase64("${path.module}/../../haproxy/.haproxy.env"),
    MINIO_ENV_VARIABLES_BASE64 = filebase64("${path.module}/../../minio/.minio.env"),
    MONGODB_ENV_VARIABLES_BASE64 = filebase64("${path.module}/../../mongodb/.mongo.env"),
    HOST_ROOT_PASSWORD = local.env_vars["HOST_ROOT_PASSWORD"],
    TAILSCALE_AUTH_KEY = local.env_vars["TAILSCALE_AUTH_KEY"]
  })
}

output "ip" {
  value = digitalocean_droplet.blog.ipv4_address
}