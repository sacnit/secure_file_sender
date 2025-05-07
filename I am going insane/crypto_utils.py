# crypto_utils.py
# Handles RSA key generation, certificate generation, and port derivation.

import hashlib
import ssl
import tempfile
import os
from datetime import datetime, timedelta

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from config import LEAF_P2P_PORT_RANGE_START, LEAF_P2P_PORT_RANGE_END, RSA_KEY_SIZE

def generate_rsa_key_pair():
    """Generates a new RSA private/public key pair."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=RSA_KEY_SIZE,
    )
    public_key = private_key.public_key()
    return private_key, public_key

def serialize_key(key, is_private=True, password=None):
    """Serializes a private or public key to PEM format."""
    if is_private:
        encryption_algorithm = serialization.BestAvailableEncryption(password) if password else serialization.NoEncryption()
        pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )
    else:
        pem = key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    return pem.decode('utf-8')

def deserialize_public_key(pem_data):
    """Deserializes a PEM-encoded public key."""
    return serialization.load_pem_public_key(pem_data.encode('utf-8'))

def deserialize_private_key(pem_data, password=None):
    """Deserializes a PEM-encoded private key."""
    return serialization.load_pem_private_key(pem_data.encode('utf-8'), password=password)

def generate_self_signed_cert(hostname, private_key, public_key):
    """
    Generates a self-signed X.509 certificate.
    Returns PEM-encoded certificate and key.
    """
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, hostname),
    ]))
    builder = builder.issuer_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, hostname),  # Self-signed
    ]))
    builder = builder.not_valid_before(datetime.utcnow())
    builder = builder.not_valid_after(datetime.utcnow() + timedelta(days=30)) # Short-lived cert
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.public_key(public_key)
    builder = builder.add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True, # CA=True for self-signed simplicity
    )
    # Sign the certificate with the private key.
    certificate = builder.sign(
        private_key=private_key, algorithm=hashes.SHA256(),
    )

    cert_pem = certificate.public_bytes(serialization.Encoding.PEM).decode('utf-8')
    # The key is already available, just ensure it's in PEM format for consistency if needed elsewhere
    # key_pem = serialize_key(private_key, is_private=True) 

    return cert_pem #, key_pem (private key is managed by the caller)


def derive_port_from_public_key(public_key_pem):
    """
    Derives a port number from a public key PEM string.
    Ensures the port is within the defined dynamic/private range.
    """
    hasher = hashlib.sha256()
    hasher.update(public_key_pem.encode('utf-8'))
    # Use the first 2 bytes of the hash for port derivation
    # This gives a range of 0-65535 from the hash bytes
    hash_int = int.from_bytes(hasher.digest()[:2], byteorder='big')

    port_range_size = LEAF_P2P_PORT_RANGE_END - LEAF_P2P_PORT_RANGE_START + 1
    derived_port = (hash_int % port_range_size) + LEAF_P2P_PORT_RANGE_START
    return derived_port

def create_ssl_context(is_server, cert_pem=None, key_pem=None):
    """
    Creates an SSL context for client or server.
    For servers, cert_pem and key_pem (private key for the cert) are required.
    Generated certs/keys are written to temp files for loading.
    """
    protocol = ssl.PROTOCOL_TLS_SERVER if is_server else ssl.PROTOCOL_TLS_CLIENT
    context = ssl.SSLContext(protocol)

    if is_server:
        if not cert_pem or not key_pem:
            raise ValueError("Certificate and private key PEM strings are required for server SSL context.")
        
        # Write cert and key to temporary files to load them
        # These files will be deleted automatically when closed
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".pem") as cert_file, \
             tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".key") as key_file:
            
            cert_file.write(cert_pem)
            cert_filepath = cert_file.name
            
            key_file.write(key_pem) # key_pem is the private key for the certificate
            key_filepath = key_file.name

        try:
            context.load_cert_chain(certfile=cert_filepath, keyfile=key_filepath)
        finally:
            # Clean up temporary files
            os.unlink(cert_filepath)
            os.unlink(key_filepath)
    else:
        # Client context for connecting to peers with self-signed certificates
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # Do not verify CA for self-signed certs
    
    return context

if __name__ == '__main__':
    # Test functions
    priv_key, pub_key = generate_rsa_key_pair()
    pub_key_pem = serialize_key(pub_key, is_private=False)
    priv_key_pem = serialize_key(priv_key)
    print("Public Key PEM:\n", pub_key_pem)
    print("Private Key PEM:\n", priv_key_pem)

    deserialized_pub_key = deserialize_public_key(pub_key_pem)
    # Test if deserialized key is the same (not straightforward to compare directly without serializing again)
    assert serialize_key(deserialized_pub_key, is_private=False) == pub_key_pem
    print("Public key deserialized successfully.")

    derived_port = derive_port_from_public_key(pub_key_pem)
    print(f"Derived Port from Public Key: {derived_port}")
    assert LEAF_P2P_PORT_RANGE_START <= derived_port <= LEAF_P2P_PORT_RANGE_END

    # Test cert generation
    cert_pem_data = generate_self_signed_cert("localhost", priv_key, pub_key)
    print("\nGenerated Certificate PEM:\n", cert_pem_data)
    
    # Test SSL context creation (basic check)
    server_ctx = create_ssl_context(is_server=True, cert_pem=cert_pem_data, key_pem=priv_key_pem)
    print("Server SSL context created.")
    client_ctx = create_ssl_context(is_server=False)
    print("Client SSL context created.")
