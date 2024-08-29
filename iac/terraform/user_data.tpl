#!/bin/bash
set -e
# Harden SSH security
sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Wait for dpkg lock to be released
while lsof /var/lib/dpkg/lock-frontend; do sleep 10; done
while lsof /var/lib/apt/lists/lock; do sleep 10; done
while lsof /var/cache/apt/archives/lock; do sleep 10; done

# Update and install necessary packages
sudo apt-get update
sudo apt-get install -y git docker docker-compose

# Setup users
sudo adduser --disabled-password --gecos "" luddite478
sudo mkdir -p /home/luddite478/.ssh
sudo cp /root/.ssh/authorized_keys /home/luddite478/.ssh/
sudo chown -R luddite478:luddite478 /home/luddite478/.ssh
sudo chmod 700 /home/luddite478/.ssh
sudo chmod 600 /home/luddite478/.ssh/authorized_keys
sudo usermod -aG docker luddite478
echo "root:${HOST_ROOT_PASSWORD}" | sudo chpasswd


# Ensure the blog directory exists
sudo mkdir -p /home/luddite478/blog
sudo chown luddite478:luddite478 /home/luddite478/blog

# Clone the repository
git clone https://github.com/luddite478/blog /home/luddite478/blog
sudo chown -R luddite478:luddite478 /home/luddite478/blog

# Extract application env
echo "${APPLICATION_ENV_VARIABLES_BASE64}" | base64 --decode > /home/luddite478/blog/.env
echo "${HAPROXY_ENV_VARIABLES_BASE64}" | base64 --decode > /home/luddite478/blog/haproxy/.haproxy.env
HAPROXY_FULLCHAIN_BASE64=$(grep 'HAPROXY_FULLCHAIN_BASE64' /home/luddite478/blog/haproxy/.haproxy.env | cut -d'=' -f2)

echo "$HAPROXY_FULLCHAIN_BASE64" | base64 --decode > "/home/luddite478/blog/haproxy/fullchain.pem"
echo "HAPROXY_FULLCHAIN_PATH=/haproxy/fullchain.pem" >> /home/luddite478/blog/haproxy/.haproxy.env
# Start the application using docker-compose
sudo -u luddite478 -i -- sh -c 'cd /home/luddite478/blog && docker-compose up -d --build'