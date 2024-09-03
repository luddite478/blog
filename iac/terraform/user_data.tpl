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
# Define variables
USERNAME="luddite478"
sudo adduser --disabled-password --gecos "" $USERNAME
sudo mkdir -p /home/$USERNAME/.ssh
sudo cp /root/.ssh/authorized_keys /home/$USERNAME/.ssh/
sudo chown -R $USERNAME:$USERNAME /home/$USERNAME/.ssh
sudo chmod 700 /home/$USERNAME/.ssh
sudo chmod 600 /home/$USERNAME/.ssh/authorized_keys
sudo usermod -aG docker $USERNAME
echo "root:${HOST_ROOT_PASSWORD}" | sudo chpasswd

echo "Cloning repo..."
sudo mkdir -p /home/$USERNAME/blog
sudo chown $USERNAME:$USERNAME /home/$USERNAME/blog
git clone https://github.com/luddite478/blog /home/$USERNAME/blog
sudo chown -R $USERNAME:$USERNAME /home/$USERNAME/blog

echo "Running GitHub Actions workflow to deploy secrets..."
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key C99B11DEB97541F0
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key 23F3D4EA75716059
sudo apt-add-repository https://cli.github.com/packages
sudo apt update
sudo apt install gh
echo ${GITHUB_WORKFLOW_TOKEN} | gh auth login --with-token 
gh workflow run deploy-secrets.yml && \
sleep 5 && \
gh run watch $(gh run list --workflow=deploy-secrets.yml --json databaseId --limit 1 | jq .[0].'databaseId')

# extract fullchain value from .haproxy.env and decode it
HAPROXY_FULLCHAIN_BASE64=$(grep 'HAPROXY_FULLCHAIN_BASE64' /home/$USERNAME/blog/haproxy/.haproxy.env | cut -d'=' -f2)
echo "$HAPROXY_FULLCHAIN_BASE64" | base64 --decode > "/home/$USERNAME/blog/haproxy/fullchain.pem"

echo "Setup tailscale..."
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list
sudo apt-get update
sudo apt-get install -y tailscale
sudo tailscale up --authkey ${TAILSCALE_AUTH_KEY}

echo "Starting application..."
sudo -u "$USERNAME" -i -- sh -c "cd /home/$USERNAME/blog && docker-compose up -d --build"