# provider "tailscale" {
#   api_key = local.env_vars["TAILSCALE_API_TOKEN"]
# }

# data "tailscale_device" "blog_host_device" {
#   name = "blog"
# }

# resource "tailscale_device_authorization" "blog_authorization" {
#   device_id  = data.tailscale_device.blog_host_device.id
#   authorized = true
# }

# resource "tailscale_device_tags" "sample_tags" {
#   device_id = data.tailscale_device.blog_host_device.id
#   tags      = ["tag:blog"]
# }

# resource "tailscale_dns_preferences" "sample_preferences" {
#   magic_dns = true
# }