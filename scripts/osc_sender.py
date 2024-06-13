from pythonosc.udp_client import SimpleUDPClient

ip = "127.0.0.1"
port = 8000

client = SimpleUDPClient(ip, port)
client.send_message("/filter", 1.0)
print("OSC message sent")
