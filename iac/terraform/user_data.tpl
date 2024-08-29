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


echo "Extracting application env..."
echo "${APPLICATION_ENV_VARIABLES_BASE64}" | base64 --decode > /home/luddite478/blog/blog/.server.env

echo "Extracting minio env..."
echo "${MINIO_ENV_VARIABLES_BASE64}" | base64 --decode > /home/luddite478/blog/minio/.minio.env

echo "Extracting haproxy env..."
echo "${HAPROXY_ENV_VARIABLES_BASE64}" | base64 --decode > /home/luddite478/blog/haproxy/.haproxy.env

echo "Extracting mongodb env..."
echo "${MONGODB_ENV_VARIABLES_BASE64}" | base64 --decode > /home/luddite478/blog/mongodb/.mongo.env
# extract fullchain value
HAPROXY_FULLCHAIN_BASE64=$(grep 'HAPROXY_FULLCHAIN_BASE64' /home/luddite478/blog/haproxy/.haproxy.env | cut -d'=' -f2)
# save fullchain value to file
echo "$HAPROXY_FULLCHAIN_BASE64" | base64 --decode > "/home/luddite478/blog/haproxy/fullchain.pem"
# update fullchain path in haproxy env
echo "" >> /home/luddite478/blog/haproxy/.haproxy.env
echo "HAPROXY_FULLCHAIN_PATH=/haproxy/fullchain.pem" >> /home/luddite478/blog/haproxy/.haproxy.env


echo "Starting application..."
sudo -u luddite478 -i -- sh -c 'cd /home/luddite478/blog && docker-compose up -d --build'
