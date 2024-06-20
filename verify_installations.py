import importlib
import subprocess

def verify_python_package(package_name):
    try:
        importlib.import_module(package_name)
        print(f"{package_name} (Python package) is installed correctly!")
    except ImportError:
        print(f"{package_name} (Python package) is NOT installed.")

def verify_system_package(package_name):
    try:
        result = subprocess.run(['dpkg', '-s', package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f"{package_name} (system package) is installed correctly!")
        else:
            print(f"{package_name} (system package) is NOT installed.")
    except Exception as e:
        print(f"Error checking {package_name} (system package): {e}")

def main():
    python_packages = [
        'fastapi',
        'uvicorn',
        'paho.mqtt.client',
        'pythonosc',
        'logging'
    ]

    system_packages = [
        'rabbitmq-server',
        'ola',
        'python3-opencv'
    ]
    
    print("Verifying Python packages...")
    for package in python_packages:
        verify_python_package(package)

    print("\nVerifying system packages...")
    for package in system_packages:
        verify_system_package(package)

if __name__ == "__main__":
    main()
