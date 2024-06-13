from pythonosc.udp_client import SimpleUDPClient

def setup_client(ip="127.0.0.1", port=8000):
    client = SimpleUDPClient(ip, port)
    return client

def send_message(client, address, message):
    client.send_message(address, message)
    print(f"OSC message sent with content: {message}")
