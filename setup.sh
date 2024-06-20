#!/bin/bash

# Function to exit script on error
exit_on_error() {
    echo "Error: $1"
    exit 1
}

# Update and upgrade the system
sudo apt-get update || exit_on_error "Failed to update package list."
sudo apt-get upgrade -y || exit_on_error "Failed to upgrade packages."

# Install Python and pip
sudo apt-get install -y python3 python3-pip || exit_on_error "Failed to install Python and pip."

# Install virtual environment package
sudo apt-get install -y python3-venv || exit_on_error "Failed to install python3-venv."

# Create a virtual environment (run as the user, not root)
python3 -m venv env || exit_on_error "Failed to create virtual environment."
source env/bin/activate || exit_on_error "Failed to activate virtual environment."

# Install required Python packages from requirements.txt
pip install -r requirements.txt || exit_on_error "Failed to install Python packages."

# Install system packages
sudo apt-get install -y \
    rabbitmq-server \
    ola \
    python3-opencv \
    hostapd \
    dnsmasq || exit_on_error "Failed to install system packages."

# Enable and start RabbitMQ server
sudo systemctl enable rabbitmq-server || exit_on_error "Failed to enable RabbitMQ server."
sudo systemctl start rabbitmq-server || exit_on_error "Failed to start RabbitMQ server."

# Enable and start hostapd and dnsmasq services
sudo systemctl unmask hostapd
sudo systemctl enable hostapd || echo "Failed to enable hostapd."
sudo systemctl enable dnsmasq || echo "Failed to enable dnsmasq."

# Install and configure Samba for home directory access
#sudo apt-get install -y samba samba-common-bin || exit_on_error "Failed to install Samba."

# Backup existing smb.conf
#sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.bak || exit_on_error "Failed to backup smb.conf."

# Add configuration for home directory sharing
#echo -e "\n[homes]\n   comment = Home Directories\n   browseable = yes\n   read only = no\n   create mask = 0700\n   directory mask = 0700\n   valid users = %S" | sudo tee -a /etc/samba/smb.conf || exit_on_error "Failed to configure Samba."

# Set Samba password for the current user
#sudo smbpasswd -a $USER || exit_on_error "Failed to set Samba password."

# Restart Samba service
#sudo systemctl restart smbd || exit_on_error "Failed to restart Samba service."

# Ensure necessary directories exist
mkdir -p logs
mkdir -p templates
mkdir -p static/css
mkdir -p static/js

# Print completion message
echo "Setup complete. Please ensure the required configurations are correct."

# Run the verification script
python3 verify_installations.py
