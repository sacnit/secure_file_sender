import sys
from pyp2p.net import Net
import argparse
import signal

node = None

def signal_handler(sig, frame):
    print("\nExiting gracefully...")
    global node
    if node is not None:
        node.stop()
    sys.exit(0)

def create_ultrapeer(port, ultrapeer="0.0.0.0"):
    try:
        ultrapeer = Net(
            net_type="direct",
            node_type="ultrapeer",
            passive_bind="0.0.0.0",
            passive_port=port
        )
        ultrapeer.start()
        if ultrapeer == "0.0.0.0":
            ultrapeer.bootstrap()
        else:
            ultrapeer.bootstrap(ultrapeer, port)
        return ultrapeer
    except KeyboardInterrupt:
        print("\nInterrupted during ultrapeer creation.")
        sys.exit(0)

def create_leaf(port, ultrapeer_ip, ultrapeer_port):
    try:
        leaf = Net(
            net_type="direct",
            node_type="peer",
            passive_bind="0.0.0.0",
            passive_port=port,
        )
        leaf.start()
        leaf.bootstrap(ultrapeer_ip, ultrapeer_port)
        return leaf
    except KeyboardInterrupt:
        print("\nInterrupted during leaf creation.")
        sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, help="Which mode to run as, ultrapeer or leaf")
    parser.add_argument("--ultrapeer", type=str, help="Which ultrapeer to connect to, optional for ultrapeers")
    args = parser.parse_args()
    
    if args.mode == "ultrapeer":
        print("Running as ultrapeer")
        node = create_ultrapeer(port=8000)
    elif args.mode == "leaf":
        print("Running as leaf node")
        node = create_leaf(port=8000, ultrapeer_ip="127.0.0.1", ultrapeer_port=8000)
    else:
        parser.error("Invalid mode")
        
    try:
        while True:
            pass
    except KeyboardInterrupt:
        signal_handler(None, None)