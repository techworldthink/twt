echo "Starting TWT Electronics Deployment on Ubuntu..."

# 1. Update and Install Dependencies
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# 2. Install Docker
if ! [ -x "$(command -v docker)" ]; then
    echo "Installing Docker..."
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

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
