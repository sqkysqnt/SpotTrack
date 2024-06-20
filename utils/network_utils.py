import os
import subprocess
import socket
from utils.logging_utils import logger

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    except Exception as e:
        ip_address = "127.0.0.1"
    finally:
        s.close()
    return ip_address

def ensure_dhcpcd():
    try:
        result = subprocess.run(['systemctl', 'is-active', '--quiet', 'dhcpcd'])
        if result.returncode != 0:
            logger.info("dhcpcd service is not running. Attempting to start it...")
            result = subprocess.run(['sudo', 'systemctl', 'start', 'dhcpcd'])
            if result.returncode != 0:
                logger.info("dhcpcd service is not installed. Attempting to install it...")
                subprocess.run(['sudo', 'apt-get', 'update'], check=True)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'dhcpcd5'], check=True)
                subprocess.run(['sudo', 'systemctl', 'enable', 'dhcpcd'], check=True)
                subprocess.run(['sudo', 'systemctl', 'start', 'dhcpcd'], check=True)
                logger.info("dhcpcd service installed and started successfully.")
            else:
                logger.info("dhcpcd service started successfully.")
        else:
            logger.info("dhcpcd service is already running.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to ensure dhcpcd service is running: {e}")

def backup_network_config():
    try:
        os.makedirs("backup", exist_ok=True)
        logger.info("Backing up current network configuration...")
        
        files_to_backup = ['/etc/dhcpcd.conf', '/etc/hostapd/hostapd.conf']
        for file in files_to_backup:
            if os.path.exists(file):
                backup_file = os.path.join("backup", os.path.basename(file) + ".backup")
                subprocess.run(['sudo', 'cp', file, backup_file], check=True)
            else:
                logger.warning(f"File {file} does not exist, skipping backup.")

        logger.info("Network configuration backup completed.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to backup network configuration: {e}")

def configure_wireless_router():
    try:
        ensure_dhcpcd()
        backup_network_config()

        dhcpcd_conf_path = '/etc/dhcpcd.conf'
        hostapd_conf_path = '/etc/hostapd/hostapd.conf'

        with open(dhcpcd_conf_path, 'a') as dhcpcd_conf:
            dhcpcd_conf.write("interface wlan0\n")
            dhcpcd_conf.write("    static ip_address=192.168.4.1/24\n")
            dhcpcd_conf.write("    nohook wpa_supplicant\n")

        with open(hostapd_conf_path, 'w') as hostapd_conf:
            hostapd_conf.write("interface=wlan0\n")
            hostapd_conf.write("driver=nl80211\n")
            hostapd_conf.write("ssid=StageTrackingSetup\n")
            hostapd_conf.write("hw_mode=g\n")
            hostapd_conf.write("channel=7\n")
            hostapd_conf.write("macaddr_acl=0\n")
            hostapd_conf.write("auth_algs=1\n")
            hostapd_conf.write("ignore_broadcast_ssid=0\n")
            hostapd_conf.write("wpa=2\n")
            hostapd_conf.write("wpa_passphrase=stagetracking\n")
            hostapd_conf.write("wpa_key_mgmt=WPA-PSK\n")
            hostapd_conf.write("wpa_pairwise=TKIP\n")
            hostapd_conf.write("rsn_pairwise=CCMP\n")

        subprocess.run(['sudo', 'systemctl', 'enable', 'hostapd'], check=True)
        subprocess.run(['sudo', 'systemctl', 'start', 'hostapd'], check=True)
        subprocess.run(['sudo', 'systemctl', 'restart', 'dhcpcd'], check=True)
        logger.info("Wireless router configured with SSID 'StageTrackingSetup'.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to configure wireless router: {e}")
