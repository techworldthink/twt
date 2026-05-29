echo "Starting TWT Electronics Deployment on RedHat-based system..."

# 1. Install Docker
if ! [ -x "$(command -v docker)" ]; then
    echo "Installing Docker..."
    sudo dnf install -y yum-utils
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    sudo systemctl enable --now docker
fi

# 2. Add current user to docker group
sudo usermod -aG docker $USER

# 3. Create Environment File
if [ ! -f .env ]; then
    echo "Creating default .env file..."
    cat <<EOF > .env
DEBUG=0
SECRET_KEY=$(openssl rand -hex 32)
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
DATABASE_URL=postgres://twt_user:twt_password@db:5432/twt_db
POSTGRES_DB=twt_db
POSTGRES_USER=twt_user
POSTGRES_PASSWORD=twt_password
EOF
fi

# 4. Starting the Application
echo "Starting containers..."
sudo docker compose -f deploy/docker-compose.yml up -d --build

echo "Deployment Successful!"
echo "Access your application at http://localhost"
