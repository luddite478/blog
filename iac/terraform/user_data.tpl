#!/bin/bash
set -e

echo "Permitting root login..."
sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd

echo "Watching for package locks release..."
while lsof /var/lib/dpkg/lock-frontend; do sleep 10; done
while lsof /var/lib/apt/lists/lock; do sleep 10; done
while lsof /var/cache/apt/archives/lock; do sleep 10; done

echo "Install packages..."
apt-get update
apt-get install -y git docker docker-compose jq

echo "Setting up users repo..."
# Define variables
USERNAME="luddite478"
adduser --disabled-password --gecos "" $USERNAME
mkdir -p /home/$USERNAME/.ssh
cp /root/.ssh/authorized_keys /home/$USERNAME/.ssh/
chown -R $USERNAME:$USERNAME /home/$USERNAME/.ssh
chmod 700 /home/$USERNAME/.ssh
chmod 600 /home/$USERNAME/.ssh/authorized_keys
sudo usermod -aG docker $USERNAME
echo "root:${HOST_ROOT_PASSWORD}" | sudo chpasswd

echo "Cloning repository..."
REPO_DIR="/home/$USERNAME/blog"
mkdir -p $REPO_DIR
chown $USERNAME:$USERNAME $REPO_DIR
su - "$USERNAME" -c "git clone https://github.com/luddite478/blog $REPO_DIR"
chown -R $USERNAME:$USERNAME $REPO_DIR

echo "Running GitHub Actions workflow to deploy secrets to this machine..."
apt-key adv --keyserver keyserver.ubuntu.com --recv-key C99B11DEB97541F0
apt-key adv --keyserver keyserver.ubuntu.com --recv-key 23F3D4EA75716059
apt-add-repository https://cli.github.com/packages
apt update
apt install gh
cd $REPO_DIR
export HOME="/root"
git config --global --add safe.directory $REPO_DIR
echo ${GITHUB_WORKFLOW_TOKEN} | gh auth login --with-token 
gh workflow run deploy-secrets.yml -f restart-containers=false && \
sleep 5 && \
gh run watch $(gh run list --workflow=deploy-secrets.yml --json databaseId --limit 1 | jq .[0].'databaseId')

# extract fullchain value from .haproxy.env and decode it
HAPROXY_FULLCHAIN_BASE64=$(awk -F'=' '/HAPROXY_FULLCHAIN_BASE64/ {print substr($0, index($0,$2))}' $REPO_DIR/haproxy/.haproxy.env)
echo "$HAPROXY_FULLCHAIN_BASE64" | base64 --decode > "$REPO_DIR/haproxy/fullchain.pem"

echo "Setup tailscale..."
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list
apt-get update
apt-get install -y tailscale
tailscale up --authkey ${TAILSCALE_AUTH_KEY}

echo "Mounting the volume..."
VOLUME_ID="/dev/disk/by-id/scsi-0DO_Volume_blog-volume"
MOUNT_POINT="/mnt/blog-volume"
# Create a mount point
mkdir -p $MOUNT_POINT
# Mount the volume
mount -o defaults,nofail,discard,noatime $VOLUME_ID $MOUNT_POINT
# Update /etc/fstab to mount the volume on reboot
echo "$VOLUME_ID $MOUNT_POINT xfs defaults,nofail,discard,noatime 0 2" >> /etc/fstab

mkdir $MOUNT_POINT/minio
mkdir $MOUNT_POINT/mongodb

echo "Starting application..."
sudo -u "$USERNAME" -i -- sh -c "cd $REPO_DIR && docker-compose up -d --build"