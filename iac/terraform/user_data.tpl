#!/bin/bash
set -e
echo "Permitting root login..."
sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

echo "Watching for package locks release..."
while lsof /var/lib/dpkg/lock-frontend; do sleep 10; done
while lsof /var/lib/apt/lists/lock; do sleep 10; done
while lsof /var/cache/apt/archives/lock; do sleep 10; done

echo "Install packages..."
sudo apt-get update
sudo apt-get install -y git docker docker-compose

echo "Setting up users repo..."
sudo adduser --disabled-password --gecos "" luddite478
sudo mkdir -p /home/luddite478/.ssh
sudo cp /root/.ssh/authorized_keys /home/luddite478/.ssh/
sudo chown -R luddite478:luddite478 /home/luddite478/.ssh
sudo chmod 700 /home/luddite478/.ssh
sudo chmod 600 /home/luddite478/.ssh/authorized_keys
sudo usermod -aG docker luddite478
echo "root:${HOST_ROOT_PASSWORD}" | sudo chpasswd

echo "Cloning repo..."
sudo mkdir -p /home/luddite478/blog
sudo chown luddite478:luddite478 /home/luddite478/blog
git clone https://github.com/luddite478/blog /home/luddite478/blog
sudo chown -R luddite478:luddite478 /home/luddite478/blog

gh workflow run deploy-secrets.yml && \
sleep 5 && \
gh run watch $(gh run list --workflow=deploy-secrets.yml --json databaseId --limit 1 | jq .[0].'databaseId')

# extract fullchain value
HAPROXY_FULLCHAIN_BASE64=$(grep 'HAPROXY_FULLCHAIN_BASE64' /home/luddite478/blog/haproxy/.haproxy.env | cut -d'=' -f2)
# save fullchain value to file
echo "$HAPROXY_FULLCHAIN_BASE64" | base64 --decode > "/home/luddite478/blog/haproxy/fullchain.pem"

echo "Setup tailscale..."
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list
sudo apt-get update
sudo apt-get install tailscale
sudo tailscale up --authkey ${TAILSCALE_AUTH_KEY}

echo "Starting application..."
sudo -u luddite478 -i -- sh -c 'cd /home/luddite478/blog && docker-compose up -d --build'


