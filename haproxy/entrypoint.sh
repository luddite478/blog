#!/bin/bash
# Replace environment variables in the HAProxy configuration template
envsubst < /usr/local/etc/haproxy/haproxy.cfg.template > /usr/local/etc/haproxy/haproxy.cfg

# Start HAProxy in the foreground
exec haproxy -f /usr/local/etc/haproxy/haproxy.cfg