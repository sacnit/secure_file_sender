import argparse
import ast
import hashlib
import logging
import sys
import threading
import time
from Crypto.PublicKey import RSA
from OpenSSL import crypto, SSL
import warnings
import os
from twisted.internet import reactor, ssl, threads
from twisted.internet.protocol import Protocol, ClientFactory, Factory
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

# logging stuff, this should be removed in release
global logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(threadName)s) %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=str(os.getpid()),
    filemode="w"
)
logger = logging.getLogger(__name__)

# This has so many variables that can probably be combined or just removed as a whole that I am sad
class State:
    def __init__(self):
        self.connected_to_ultrapeer = False
        self.connected_to_peer = False
        self.connecting_to_peer = False
        self.connector = False
        self.filesend_requesting = False
        self.filesend = False
        self.filerecieve = False
        self.filepath = ""
        self.filename = ""
        self.chunk_size = 65536

# ... take a guess
def hash_string_to_port_range(input_string):
    hashed_string = hashlib.sha256(input_string.encode()).hexdigest()
    hash_int = int(hashed_string, 16)
    mapped_value = 5000 + (hash_int % (9999 - 5000 + 1))
    return mapped_value

# This is just for handling a dictionary in a way that can be searched efficiently (even though it isnt)
class Contacts:
    def __init__(self):
        self.contacts_dict = {}
        self.contacts_counter = 0

    def initialize_contact(self, public_key):
        try:
            _test = self.contacts_dict[public_key]
        except KeyError:
            self.contacts_dict[public_key] = {
                "public_key": public_key,
                "number": -1,
                "ip": None,
                "port": None,
            }

    def finalize_contact(self, details):
        try:
            if self.contacts_dict[details[0]]["public_key"] == details[0] and self.contacts_dict[details[0]]["number"] == -1:
                self.contacts_dict[details[0]] = {
                    "public_key": details[0],
                    "ip": details[1],
                    "port": int(details[2]),
                    "state": "",
                    "number": self.contacts_counter
                }
                self.contacts_counter += 1
        except KeyError:
            logger.warning(f"Attempted to finalize non-existent contact: {details[0]}")
        except IndexError:
            logger.error(f"finalize_contact received incomplete details: {details}")

    def get_contacts(self):
        for contact_info in self.contacts_dict.values():
            print(f"{contact_info['number']}. {contact_info['public_key'][88:108]}{contact_info['state']}")
        return self.contacts_dict

    def get_contact(self, number):
        for public_key, contact_info in self.contacts_dict.items():
            if contact_info.get("number") == int(number):
                return (contact_info.get("public_key"), contact_info.get("ip"), contact_info.get("port"))
        return None
    
    def poll_contacts(self, _ip, _port): # WIP
        pass

# This protocol and factory handle the connection with another peer
class CommunicationProtocol(Protocol):
    def __init__(self):
        self.connection_ready_event = threading.Event()

    def connectionMade(self):
        logger.info("P2P connection established.")
        self.factory.peer_protocol = self
        self.send_line(f"Cześć||{self.factory.public_key}") # Moved to inputloop

    def dataReceived(self, data):
        decoded_data = data.decode('utf-8')
        if decoded_data.startswith("Cześć||") and not program_state.connected_to_peer:
            if decoded_data.replace("Cześć||", "") == (f"{keypair.public_key().export_key()}".encode("'utf-8")).decode('utf-8'):
                print("Peer requesting to connect\nUse command `accept` to accept communication\nUse command `refuse` to refuse communication")
                timeout = 3 * 20
                program_state.connecting_to_peer = True # This way the inputloop can decide if its connecting
                while program_state.connecting_to_peer and timeout > 0: # wait for verdict... poorly
                    time.sleep(0.3) # Just to make it a lil less spammy
                    timeout -= 1
                if timeout < 0:
                    print("Request timed out")
                    program_state.connecting_to_peer = False
                    return
                if program_state.connected_to_peer:
                    self.send_line("Witajcie towarzysze||") # Welcome the comrade
                else:
                    self.connectionRefused()
        elif decoded_data.startswith("Witajcie towarzysze||") and program_state.connecting_to_peer:
            print("Peer connected\nUse command `join` to start communicating")
            program_state.connected_to_peer = True
            program_state.connecting_to_peer = False
        elif decoded_data.startswith("Plik?||") and not program_state.filesend_requesting:
            file_path = decoded_data.removeprefix("Plik?||")
            file_name = os.path.basename(file_path)
            program_state.filename = file_name
            print(f"Peer is attempting to send file {file_path}\nUse command `accept` to accept file\nUse command `refuse` to refuse file")
            program_state.filesend_requesting = True
            timeout = 3 * 20
            while program_state.filesend_requesting and timeout > 0: # wait for verdict... poorly
                time.sleep(0.3) # Just to make it a lil less spammy
                timeout -= 1
            if timeout < 0:
                print("Request timed out")
                program_state.filesend_requesting = False
                return
            if program_state.filerecieve:
                self.send_line("Plik||")
            else:
                self.send_line("nie ma pliku, dzięki||")
        elif decoded_data.startswith("Plik||"):
            print("File send accepted")
            program_state.filesend = True
            program_state.filesend_requesting = False
            if not os.path.exists(program_state.filepath):
                raise FileNotFoundError(f"File not found at: {program_state.filepath}")

            with open(program_state.filepath, 'rb') as f:
                chunk = f.read()  # Read the entire file
                self.transport.write(f"¬||¬{chunk}".encode('utf-8'))
        elif decoded_data.startswith("nie ma pliku, dzięki||") and program_state.filesend_requesting:
            print("File send rejected")
            program_state.filesend = False
            program_state.filesend_requesting = False
        elif decoded_data.startswith("¬||¬") and ( program_state.filerecieve or program_state.filesend ):
            file_data = ast.literal_eval(decoded_data.replace("¬||¬", "")) # This could break horribly
            filepath = program_state.filename
            if not os.path.exists(filepath):
                print(f"File not found. Creating: {filepath}")

            if isinstance(file_data, str):
                with open(filepath, 'ab', encoding='utf-8') as f:
                    f.write(file_data)
                print(f"String data appended to {filepath}")
            elif isinstance(file_data, bytes):
                with open(filepath, 'ab') as f:
                    f.write(file_data)
                print(f"Bytes data appended to {filepath}")
            else:
                raise TypeError("Data must be either str or bytes.")
        else:
            print(f"\r<<< {decoded_data}")
            
    def connectionRefused(self):
        program_state.connected_to_peer = False
        program_state.connecting_to_peer = False
        self.transport.loseConnection()

    def send_line(self, line):
        if self.transport and line:
            self.transport.write(line.encode('utf-8'))
            logger.info(f"P2P Sent: {line}")
        elif not self.transport:
            logger.warning("P2P Cannot send data, transport is not available.")

    def connectionLost(self, reason):
        logger.info(f"P2P connection lost: {reason.getErrorMessage()}")
        if hasattr(self.factory, 'peer_protocol') and self.factory.peer_protocol == self:
            self.factory.peer_protocol = None

class CommunicationClientFactory(ClientFactory):
    protocol = CommunicationProtocol
    peer_protocol = None

    def __init__(self, public_key):
        self.public_key = public_key

    def buildProtocol(self, addr):
        proto = self.protocol()
        proto.factory = self
        self.peer_protocol = proto
        return proto

    def clientConnectionFailed(self, connector, reason):
        logger.error(f"P2P Connection failed: {reason.getErrorMessage()}")

    def clientConnectionLost(self, connector, reason):
        logger.info(f"Resetting P2P connection related flags and variables")
        program_state.connected_to_peer = False
        program_state.connecting_to_peer = False
        if hasattr(self, 'peer_protocol') and self.peer_protocol and self.peer_protocol.transport:
            self.peer_protocol.transport = None
            self.peer_protocol = None

# This protocol and factory handle the connection with the ultrapeer
class LeafProtocol(Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.connection_ready_event = threading.Event()

    def connectionMade(self):
        logger.info("Connection established to ultrapeer.")
        self.factory.client_instance = self
        self.connection_ready_event.set()
        program_state.connected_to_ultrapeer = True
        self.send_line(f"Registration¬|¬{keypair.public_key().export_key()}¬|¬{p2p_port}")

    def dataReceived(self, data):
        decoded_data = data.decode('utf-8')
        if decoded_data.startswith("Response||¬"):
            response = decoded_data.replace("Response||¬", "").split("||¬")
            contacts.finalize_contact(response)
        else:
            print(f"\r<< {decoded_data}")

    def send_line(self, line):
        if self.transport and line:
            self.transport.write(line.encode('utf-8'))
            logger.info(f"Sent: {line}")
        elif not self.transport:
            logger.warning("Cannot send data, transport is not available.")

    def connectionLost(self, reason):
        logger.info(f"Connection lost from ultrapeer: {reason.getErrorMessage()}")
        self.connection_ready_event.clear()
        if self.factory.client_instance == self:
            self.factory.client_instance = None
        self.factory.signal_input_thread_shutdown()

class LeafFactory(ClientFactory):
    protocol = LeafProtocol

    def __init__(self):
        self.client_instance = None
        self._input_thread_shutdown_event = threading.Event()

    def buildProtocol(self, addr):
        return LeafProtocol(self)

    def clientConnectionFailed(self, connector, reason):
        logger.info(f"Connection to ultrapeer failed: {reason.getErrorMessage()}")
        self.signal_input_thread_shutdown()
        if reactor.running:
            reactor.stop()

    def clientConnectionLost(self, connector, reason):
        logger.info(f"Connection to ultrapeer lost: {reason.getErrorMessage()}")
        program_state.connected_to_ultrapeer = False

    def signal_input_thread_shutdown(self):
        self._input_thread_shutdown_event.set()

    def should_input_thread_shutdown(self):
        return self._input_thread_shutdown_event.is_set()

# This loop handles all the input from the user... Poorly
def input_loop(prompt_session, factory):
    global p2p_factory # This is needed to access it i think
    logger.info("Input thread started. Waiting for connection to ultrapeer...")
    connection_entered = False

    while not factory.should_input_thread_shutdown():
        client = factory.client_instance
        if client and client.connection_ready_event.is_set():
            logger.info("Connection to ultrapeer ready. Starting input prompt.")
            break
        time.sleep(0.1)

    if factory.should_input_thread_shutdown():
        logger.info("Input thread shutting down before prompt could start.")
        return

    try:
        while not factory.should_input_thread_shutdown():
            try:
                if not program_state.connected_to_peer or not connection_entered:
                    user_input = prompt_session.prompt(">> ")

                    if user_input is None:
                        logger.info("EOF received from prompt, stopping input.")
                        if reactor.running:
                            reactor.callFromThread(reactor.stop)
                        break

                    # Handling commands from the user to the ultrapeer or itself
                    if user_input.lower() == "identity":
                        logger.info("Identity requested")
                        print(f"Identity:\n{keypair.public_key().export_key()}")
                    elif user_input.lower() == "accept" and program_state.connecting_to_peer:
                        print("Accepting connection\nUse command `join` to start communicating")
                        program_state.connected_to_peer = True
                        program_state.connecting_to_peer = False
                        pass
                    elif user_input.lower() == "refuse" and program_state.connecting_to_peer:
                        print("Refusing connection")
                        program_state.connecting_to_peer = False
                    elif user_input.lower() == "exit" or program_state.connected_to_ultrapeer == False:
                        factory.signal_input_thread_shutdown()
                    elif user_input.lower() == "contacts":
                        contacts.get_contacts()
                    elif user_input.lower() == "help":
                        print("Ultrapeer commands:")
                        print("identity - display identity for querying")
                        print("accept - accept an incoming p2p chat connection")
                        print("refuse - refuse an incoming p2p chat connection")
                        print("exit - exit program")
                        print("contacts - display contacts")
                        print("query [pubkey] - queries and adds the peer specified by pubkey to contacts")
                        print("connect [contact number] - connects to leaf specified in contacts at contact number")
                        print("join - enteres the p2p chat connection")
                    elif user_input.lower() == "join" and program_state.connected_to_peer:
                        connection_entered = True
                    elif user_input.split(" ")[0].lower().startswith("query"):
                        current_client = factory.client_instance
                        if current_client:
                            query = f"Query¬¬|{user_input[6:]}"
                            contacts.initialize_contact(user_input[6:])
                            reactor.callFromThread(current_client.send_line, query)
                        else:
                            logger.warning("No connection to ultrapeer to send query.")
                    elif user_input.lower().startswith("connect"):
                        print("Connecting to peer")
                        parts = user_input.split()
                        program_state.connector = True # Becuase i need to differentiate between connecting instances
                        if len(parts) == 2:
                            contact_number = parts[1]
                            details = contacts.get_contact(contact_number)
                            if details:
                                peer_public_key, peer_ip, peer_port = details
                                p2p_factory = CommunicationClientFactory(peer_public_key)
                                ssl_factory = SSLFactory()
                                reactor.connectSSL(peer_ip, peer_port, p2p_factory, ssl_factory)
                                program_state.connecting_to_peer = True
                                logger.info(f"Attempting P2P connection to {peer_ip}:{peer_port} with key {peer_public_key[:20]}...")
                            else:
                                print(f"Error: Contact with number {contact_number} not found.")
                        else:
                            print("Usage: connect <contact_number>")
                    else:
                        # This doesnt need to be here
                        # current_client = factory.client_instance
                        # if current_client:
                        #     reactor.callFromThread(current_client.send_line, user_input)
                        # else:
                        #     logger.warning("No connection to ultrapeer to send data.")
                        pass
                else:
                    # Handling commands from the user to the other peer or itself
                    user_input = prompt_session.prompt(">>> ")
                    try:
                        if user_input.lower() == "exit":
                            try:
                                reactor.callFromThread(p2p_factory.peer_protocol.connectionRefused)
                            except:
                                reactor.callFromThread(p2p_factory_listen.peer_protocol.connectionRefused)
                        elif user_input.lower() == "help":
                            print("Leaf commands:")
                            print("exit - disconnect from peer")
                            print("send [filepath] - send file at path")
                            print("accept - accept an incoming file")
                            print("refuse - refuse an incoming file")
                        elif user_input.startswith("send") or user_input.startswith("Send"):
                            print("Requesting to send file to peer")
                            program_state.filepath = user_input[len("send ")::] # Not sure why this sometimes just doesnt work
                            file_size = os.path.getsize(program_state.filepath) # Just gunna assume thisll work just fine
                            if file_size > 1024 * 5:
                                print("File greater than limit (5kb)")
                            else:
                                try:
                                    reactor.callFromThread(p2p_factory.peer_protocol.send_line, f"Plik?||{user_input[5::]}")
                                    success = True
                                except:
                                    try:
                                        reactor.callFromThread(p2p_factory_listen.peer_protocol.send_line, f"Plik?||")
                                        success = True
                                    except:
                                        success = False
                                if not success:
                                    raise Exception("Both send attempts failed")
                        elif user_input.lower() == "accept" and program_state.filesend_requesting:
                            print("Accepting file")
                            program_state.filerecieve = True
                            program_state.filesend_requesting = False
                            pass
                        elif user_input.lower() == "refuse" and program_state.filesend_requesting:
                            print("Refusing file")
                            program_state.filesend_requesting = False
                        try:
                            reactor.callFromThread(p2p_factory.peer_protocol.send_line, user_input)
                            success = True
                        except:
                            try:
                                reactor.callFromThread(p2p_factory_listen.peer_protocol.send_line, user_input)
                                success = True
                            except:
                                success = False
                        if not success:
                            raise Exception("Both send attempts failed")
                    except:
                        print("Peer connection failed")
                        program_state.connected_to_peer = False

            except EOFError:
                logger.info("EOFError in prompt, stopping input.")
                if reactor.running:
                    reactor.callFromThread(reactor.stop)
                break
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt in prompt, stopping input and reactor.")
                if reactor.running:
                    reactor.callFromThread(reactor.stop)
                break
            except Exception as e:
                logger.error(f"Unexpected error in input loop: {e}", exc_info=True)
                if reactor.running:
                    reactor.callFromThread(reactor.stop)
                break
    finally:
        logger.info("Input thread finished.")
        factory.signal_input_thread_shutdown()

# Does what it says on the tin, makes ssl stuff in memory. this cant be authenticated as its just a trust-me-bro one
class SSLFactory(ssl.ContextFactory):
    def __init__(self):
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)
        cert = crypto.X509()
        cert.get_subject().CN = "localhost"
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(31536000)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, "sha256")
        self.private_key = key
        self.certificate = cert

    def getContext(self):
        ctx = ssl.SSL.Context(ssl.SSL.TLSv1_2_METHOD)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            ctx.use_privatekey(self.private_key)
            ctx.use_certificate(self.certificate)
            ## Does not work with multiple local hosts && in memory certificates so cannot test
            # ctx.set_verify(
            #     SSL.VERIFY_PEER | SSL.VERIFY_CLIENT_ONCE | SSL.VERIFY_FAIL_IF_NO_PEER_CERT
            # )
        return ctx

def main(ultrapeer, port, certificate):
    # All this jazz needs to be initialised for stuff to work chucklenuts
    global program_state
    global contacts
    global factory
    global p2p_port
    global p2p_factory
    global p2p_factory_listen
    global prompt_session
    global keypair
    
    program_state = State()

    keypair = RSA.generate(2048)

    contacts = Contacts()

    factory = LeafFactory()

    p2p_port = hash_string_to_port_range((f"{keypair.public_key().export_key()}".encode('utf-8')).decode('utf-8'))
    p2p_factory_listen = CommunicationClientFactory(keypair.public_key().export_key())
    if certificate == "":
        ssl_factory = SSLFactory()
    else:
        try:
            ssl_factory = cert_options = ssl.CertificateOptions(
                privateKey=(certificate+"cert.crt").encode('ascii'),
                certificate=(certificate+"key.key").encode('ascii'),
                verify=True # Genuinely it only needs verification if actual keys and certs are being used
            )
            pass
        except:
            print(f"Invalid SSL certificate directory {certificate}\nPlease make sure it contains both `cert.crt` and `key.key` and that they are a valid SSL certificate and key")
            os._exit(1)
    reactor.listenSSL(p2p_port, p2p_factory_listen, ssl_factory)
    logger.info(f"Listening for P2P connections on port {p2p_port} (SSL).")

    reactor.connectSSL(ultrapeer, port, factory, ssl_factory)
    logger.info(f"Connecting to ultrapeer {ultrapeer}:{port} (SSL).")

    prompt_session = PromptSession()

    input_d = threads.deferToThread(input_loop, prompt_session, factory)

    def input_thread_errback(failure):
        logger.error(f"Input thread encountered an error: {failure.getErrorMessage()}")
        failure.printTraceback()
        if reactor.running:
            reactor.callFromThread(reactor.stop)
    input_d.addErrback(input_thread_errback)

    try:
        with patch_stdout():
            reactor.run()
    except KeyboardInterrupt:
        logger.info("Reactor interrupted by KeyboardInterrupt (Ctrl-C in main thread).")
        if reactor.running:
            reactor.stop()
    finally:
        logger.info("Reactor stopped.")
        factory.signal_input_thread_shutdown()

    logger.info("Application exiting.")
    
# Main function handling commandline arguments specifying the ultrapeer to join
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Twisted TUI Client",
        description="A Twisted client with an interactive terminal interface."
    )
    parser.add_argument("-U", "--ultrapeer", dest="ultrapeer", default="127.0.0.1",
                        help="Server host address (default: 127.0.0.1)")
    parser.add_argument("-P", "--port", dest="port", type=int, default=9999,
                        help="Server port number (default: 9999)")
    parser.add_argument("-C", "--certificate", dest="certificate", type=str, default="",
                        help="Directory containing certificate `cert.crt` and key `key.key`")
    args = parser.parse_args()
    
    ultrapeer = args.ultrapeer
    port = args.port
    certificate = args.certificate
    main(ultrapeer, port, certificate)