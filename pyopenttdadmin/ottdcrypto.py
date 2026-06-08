
from .pymonocypher import *
import os
from typing import Literal

def derive_keys(
    shared_secret: bytes, 
    side: Literal["server", "client"], 
    our_public: bytes, 
    peer_public: bytes, 
    extra_payload: bytes = b''
) -> tuple[bytes, bytes]:
    blake2b_updates = [shared_secret]
    if side == "server":
        blake2b_updates.append(our_public)
        blake2b_updates.append(peer_public)
    elif side == "client":
        blake2b_updates.append(peer_public)
        blake2b_updates.append(our_public)
    else:
        raise ValueError(f"Expected side to be 'server' or 'client', got {side}")
        
    if extra_payload:
        blake2b_updates.append(extra_payload)
    out = blake2b(64, blake2b_updates)
    # (client_to_server, server_to_client)
    return out[:32], out[32:64]


class Auth:
    def __init__(self, secret_key: bytes, password: str | None = None):
        self.secret_key = secret_key
        self.public_key = get_public_key(self.secret_key)
        self.password = password
        self.client_to_server_key: None | bytes = None
        self.server_to_client_key: None | bytes = None
        
    
    def PAKE(self, peer_public_key: bytes, nonce: bytes) -> tuple[bytes, bytes, bytes]:
        """
        Get Admin Response information for PAKE handshake
        
        Returns:
        - our_public_key
        - mac
        - cyphertext
        """
        if self.password is None:
            raise ValueError("Cannot use PAKE without password")
        
        shared_key = shared_keys(self.secret_key, peer_public_key)
        self.client_to_server_key, self.server_to_client_key = derive_keys(
            shared_key, 
            side = "client", 
            our_public = self.public_key, 
            peer_public = peer_public_key, 
            extra_payload = self.password.encode('utf-8')
        )
        
        plaintext = os.urandom(8)
        mac, ciphertext = CryptoAeadCtx.lock(
        	plaintext, 
        	self.client_to_server_key, 
        	nonce, 
        	self.public_key
        )
        
        return self.public_key, mac, ciphertext
    
    def get_receive_handler(self, nonce: bytes) -> CryptoAeadCtx:
        if self.server_to_client_key is None:
            raise ValueError("server_to_client_key not yet set. Please make an issue on github")
        return CryptoAeadCtx(self.server_to_client_key, nonce)
    
    def get_send_handler(self, nonce: bytes) -> CryptoAeadCtx:
        if self.client_to_server_key is None:
            raise ValueError("server_to_client_key not yet set. Please make an issue on github")
        return CryptoAeadCtx(self.client_to_server_key, nonce)

























