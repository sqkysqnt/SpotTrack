from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server

def print_handler(unused_addr, args, volume):
    print(f"[{args[0]}] ~ {volume}")

dispatcher = Dispatcher()
dispatcher.map("/filter", print_handler, "Volume")

server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 8000), dispatcher)
print("Serving on {}".format(server.server_address))
server.serve_forever()
