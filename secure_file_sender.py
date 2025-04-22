import sys
import time
from pyp2p.net import Net
import argparse
import signal
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver

node = None

class BaseNode(Net):
    def __init__(self, port, net_type="direct", node_type="passive", ultrapeer_ip=None, ultrapeer_port=None):
        super().__init__(
            net_type=net_type,
            node_type=node_type,
            passive_bind="0.0.0.0",
            passive_port=port,
        )
        self.ultrapeer_ip = ultrapeer_ip
        self.ultrapeer_port = ultrapeer_port
        self.connected_peers = {}  # Dictionary to store peer information

    def start_node(self):
        self.start()
        if self.ultrapeer_ip and self.ultrapeer_port:
            self.bootstrap(self.ultrapeer_ip, self.ultrapeer_port)
        else:
            self.bootstrap()

    def on_message(self, message):
        print(f"{self.__class__.__name__} received message: {message}")
        # Add custom logic for handling messages here

    def on_connect(self, peer):
        print(f"Connected with peer_id: {peer['peer_id']}")
        self.connected_peers[peer['peer_id']] = peer  # Store peer information

    def send_message(self, peer_id, message):
        if peer_id in self.connected_peers:
            self.send(message, peer_id)
            print(f"Message sent to peer {peer_id}: {message}")
        else:
            print(f"Peer with peer_id {peer_id} not found")


class RendezvousProtocol(LineReceiver):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        ip_addr = self.transport.getPeer().host
        print(f"Node connected: {ip_addr}")
        self.factory.nodes[ip_addr] = {
            "time": time.time(),
            "connection": self
        }

    def connectionLost(self, reason):
        ip_addr = self.transport.getPeer().host
        if ip_addr in self.factory.nodes:
            del self.factory.nodes[ip_addr]
            print(f"Node disconnected: {ip_addr}")

    def lineReceived(self, line):
        print(f"Received: {line}")
        # Handle messages from nodes (e.g., BOOTSTRAP, CANDIDATE, etc.)
        if line.startswith("BOOTSTRAP"):
            self.handle_bootstrap()

    def handle_bootstrap(self):
        # Send a list of connected nodes to the requester
        nodes = list(self.factory.nodes.keys())
        response = "NODES " + " ".join(nodes)
        self.sendLine(response.encode("utf-8"))


class RendezvousFactory(Factory):
    def __init__(self):
        self.nodes = {}  # Dictionary to store connected nodes

    def buildProtocol(self, addr):
        return RendezvousProtocol(self)


class Ultrapeer(BaseNode):
    def __init__(self, port):
        super().__init__(port, net_type="direct", node_type="passive")
        self.rendezvous_factory = RendezvousFactory()

    def start_node(self):
        print("Starting Ultrapeer as a rendezvous server...")
        reactor.listenTCP(self.passive_port, self.rendezvous_factory, interface="0.0.0.0")
        reactor.run()


class Leaf(BaseNode):
    def __init__(self, port, ultrapeer_ip, ultrapeer_port):
        super().__init__(port, net_type="direct", node_type="passive", ultrapeer_ip=ultrapeer_ip, ultrapeer_port=ultrapeer_port)
        self.ultrapeer_peer_id = None  # Store ultrapeer's peer_id

    def on_connect(self, peer):
        super().on_connect(peer)
        if "peer_id" in peer:
            self.ultrapeer_peer_id = peer["peer_id"]  # Save ultrapeer's peer_id

    def send_message_to_ultrapeer(self, message):
        if self.ultrapeer_peer_id:
            self.send_message(self.ultrapeer_peer_id, message)
        else:
            print("Not connected to any ultrapeer")


def signal_handler(sig, frame):
    print("\nExiting gracefully...")
    global node
    if node is not None:
        node.stop()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, help="Which mode to run as, ultrapeer or leaf")
    parser.add_argument("--ultrapeer", type=str, help="Which ultrapeer to connect to and their port, optional for ultrapeers")
    args = parser.parse_args()
    
    if args.mode == "ultrapeer":
        print("Running as ultrapeer")
        node = Ultrapeer(port=8000)
        node.start_node()
    elif args.mode == "leaf":
        print("Running as leaf node")
        if not args.ultrapeer:
            parser.error("Ultrapeer IP and port must be specified for leaf mode")
        ultrapeer_ip, ultrapeer_port = args.ultrapeer.split(":")
        node = Leaf(port=8000, ultrapeer_ip=ultrapeer_ip, ultrapeer_port=int(ultrapeer_port))
        node.start_node()
        time.sleep(100)
        node.send_message_to_ultrapeer("MESSAGE")
    else:
        parser.error("Invalid mode")
        
    try:
        while True:
            pass
    except KeyboardInterrupt:
        signal_handler(None, None)