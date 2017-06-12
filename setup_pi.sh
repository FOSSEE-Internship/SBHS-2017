#!/bin/bash

cd /home/pi

echo "Initializing Raspberry Pi setup..."
sudo apt-get update > setup_pi.log

# Install git
echo "Installing git..."
sudo apt-get install -y git >> setup_pi.log
echo "Done."

# Clone the repository from Github
echo "Cloning SBHS repository from Github..."
git clone https://github.com/coderick14/sbhs-pi.git

# Install virtualenv
echo "Installing virtualenv..."
sudo apt-get install -y virtualenv >> setup_pi.log
echo "Done."

# Create virtualenv
echo "Creating virtualenv..."
virtualenv venv >> setup_pi.log
echo "Done."

# Activate virtualenv
echo "Activating virtualenv..."
source venv/bin/activate
echo "Done."

cd sbhs-pi/
mkdir -p log
touch log/django_error.log report.json
cp pi_server/credentials.py.example pi_server/credentials.py

# Database credentials
echo "Setting up database credentials..."

read -p "Enter database host : " dbhost
read -p "Enter database user : " dbuser
read -s -p "Enter database password : " dbpass
echo ''
read -p "Enter database name : " dbname
read -p "Enter database port : " dbport

sed -i "/DB_HOST/c\DB_HOST = '$dbhost'" pi_server/credentials.py
sed -i "/DB_USER/c\DB_USER = '$dbuser'" pi_server/credentials.py
sed -i "/DB_PASS/c\DB_PASS = '$dbpass'" pi_server/credentials.py
sed -i "/DB_NAME/c\DB_NAME = '$dbname'" pi_server/credentials.py
sed -i "/DB_PORT/c\DB_PORT = '$dbport'" pi_server/credentials.py

echo "Done."

# Install dependencies for MySQL
echo "Installing dependencies for MySQL..."
sudo apt-get install -y libmysqlclient-dev python-dev >> setup_pi.log
echo "Done."

# Install requirements through pip
echo "Installing requirements through pip..."
pip install -r requirements.txt >> setup_pi.log
echo "Done."

# Run cron script
echo "Scanning and initializing machines..."
bash cron_job.sh >> setup_pi.log
echo "Done."