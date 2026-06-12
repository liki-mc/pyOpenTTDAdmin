
from .pymonocypher import *
import os
from typing import Literal, overload
from .packet import *
import warnings

try:
    import secrets
    randombytes = secrets.token_bytes
except ImportError:
    import os
    randombytes = os.urandom # type: ignore

KNOWN_PROTOCOL_VERSIONS = [3]

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
    @overload
    def __init__(self, name: str, version: str, *, password: str) -> None: ...
    """Encrypted traffic, password authentication"""
    @overload
    def __init__(self, name: str, version: str, *, password: str, secure: bool = False) -> None: ...
    """Unencrypted traffic, password authentication"""
    @overload
    def __init__(self, name: str, version: str, *, secret_key: str) -> None: ...
    """Encrypted traffic, secret_key authentication"""
    @overload
    def __init__(self, name: str, version: str, *, password: str, secret_key: str) -> None: ...
    """Encrypted traffic, secret_key or password authentication. OpenTTD tries multiple methods if one fails."""
    
    def __init__(
        self, 
        name: str | None = None, 
        version: str | None = None, 
        *, 
        password: str | None = None, 
        secret_key: str | None = None, 
        secure: bool = True,
        _ignore_data: bool = False
    ):
        if not _ignore_data:
            self._set_login_data(name, version, password = password, secret_key = secret_key, secure = secure)
        else:
            self._auth_data = {}
        self._authenticated: bool = False
    
    @property
    def authenticated(self) -> bool:
        return self._authenticated
    
    def _set_login_data(self, name: str, version: str, password: str | None = None, secret_key: str | None = None, secure: bool = False):
        # Data checks
        if not secure:
            if password is None:
                raise AuthenticationError("Expected password on insecure login.")
            if secret_key is not None:
                # This technically does not matter, login is possible but it makes no sense
                raise AuthenticationError("Expected secret key to be 'None' on insecure login.")
        
        self._auth_data = {
            "data": {
                "password": password,
                "secret_key": secret_key if secret_key is None else bytes.fromhex(secret_key),
                "name": name,
                "version": version,
            },
            "secure": secure,
        }
    
    # Idea is that the admin creates the auth at init, and then has a while loop where it calls auth (self.auth()) followed by getting a package (self.recv_num(1))
    def __call__(self, packet: Packet | None = None) -> tuple[Packet | None, bool]:
        """
        This will start the auth exchange, depending on the settings
        this will use secure auth, or insecure authentication.
        
        The class keeps a state internally to indicate where
        in the auth handshake we are, this function return
        - packet: packet to send to the server
        - is welcome packet: if this is True, authentication was finished and successfull
        
        This function can have 3 results:
        - An error
            - AuthenticationError, something went wrong in the authentication, either the password was incorrect or the key was not recognised.
            - UnknownAuthenticationError, something went wrong, but it is likely the libraries fault and not the users fault
        - (packet | None, False):
            - False means that the auth expects further communication, the auth handshake has not yet finished. Call again with a new packet.
        - (packet | None, True):
            - True means that the auth was succesful. Now the user can send any packet they like.
        """
        match packet:
            case None:
                return self._start_auth(), False
            case WelcomePacket():
                self._authenticated = True
                return (packet, True)
            case ServerAuthenticationRequestPacket(authentication_type = NetworkAuthenticationMethod.X25519_PAKE):
                return self._auth_PAKE(packet), False
            case ServerAuthenticationRequestPacket(authentication_type = NetworkAuthenticationMethod.X25519_AuthorisedKey):
                return self._auth_key(packet), False
            case ServerEnableEncryptionPacket():
                return self._enable_encryption(packet), False
            case ProtocolPacket():
                if packet.version not in KNOWN_PROTOCOL_VERSIONS:
                    warnings.warn(RuntimeWarning(f"[OTTDA1000] Protocol version mismatch. The PyOpenTTDAdmin library was not tested against protocol version {packet.version}. Some features might not work."))
                return (None, False)
            
            case _:
                warnings.warn("[0TTDA1001] Unexpected packet in auth flow")
                # Retry getting packet up to 5 times:
                self._auth_data["auth_counter"] = self._auth_data.get("auth_counter", -1) + 1
                if self._auth_data["auth_counter"] >= 5:
                    raise AuthenticationError("Authentication flow keeps getting unexpected packets.")
                return (None, False)
    
    def _start_auth(self) -> Packet:
        """
        Start the authentication flow
        
        On insecure:
        
        	AdminJoinPacket() ->
        								-> WelcomePacket()
        
        On secure:
        
        	AdminJoinSecurePacket() ->
        								-> ServerAuthenticationRequestPacket(authentication_type)
        	AdminAuthenticationResponsePacket(authentication_type_data) ->
        	(on fail and more types)	...
        								-> ServerAuthenticationRequestPacket(authentication_type2)
        	AdminAuthenticationResponsePacket(authentication_type2_data) ->
        								...
        	(on succes)
        								-> ServerEnableEncryptionPacket()
        								-> WelcomePacket()
        """
        data = self._auth_data["data"]
        packet: AdminJoinPacket | AdminJoinSecurePacket
        if self._auth_data["secure"]:
            method_mask = 0x0
        
            # Password key exchange
            if data["password"] is not None:
                method_mask |= 1 << NetworkAuthenticationMethod.X25519_PAKE.value
        
            # Known public key
            if data["secret_key"] is not None:
                method_mask |= 1 << NetworkAuthenticationMethod.X25519_AuthorisedKey.value
            else:
                data["secret_key"] = randombytes(32)
        
            data["public_key"] = get_public_key(data["secret_key"])
        
            packet = AdminJoinSecurePacket(data["name"], data["version"], method_mask)
        else:
            packet = AdminJoinPacket(data["password"], data["name"], data["version"])
            
        
        return packet
    
    
    def _auth_PAKE(self, packet: ServerAuthenticationRequestPacket) -> AdminAuthenticationResponsePacket:
        """
        Generate Admin Response for PAKE handshake
        
        Returns:
        - AdminAuthenticationResponsePacket
        """
        password = self._auth_data["data"]["password"]
        secret_key = self._auth_data["data"]["secret_key"]
        public_key = self._auth_data["data"]["public_key"]
        
        shared_key = shared_keys(secret_key, packet.server_public_key)
        client_to_server_key, server_to_client_key = derive_keys(
            shared_key, 
            side = "client", 
            our_public = public_key, 
            peer_public = packet.server_public_key, 
            extra_payload = password.encode('utf-8')
        )
        self._auth_data["keys"] = {
            "client_to_server_key": client_to_server_key, 
            "server_to_client_key": server_to_client_key,
        }
        
        plaintext = os.urandom(8)
        mac, ciphertext = CryptoAeadCtx.lock(
            plaintext, 
            client_to_server_key, 
            packet.server_nonce, 
            public_key
        )
        
        return AdminAuthenticationResponsePacket(public_key, mac, ciphertext)
    
    def _auth_key(self, packet: ServerAuthenticationRequestPacket) -> AdminAuthenticationResponsePacket:
        """
        Generate Admin Response for authorised key handshake
        
        Returns:
        - AdminAuthenticationResponsePacket
        """
        secret_key = self._auth_data["data"]["secret_key"]
        public_key = self._auth_data["data"]["public_key"]
        
        shared_key = shared_keys(secret_key, packet.server_public_key)
        client_to_server_key, server_to_client_key = derive_keys(
            shared_key, 
            side = "client", 
            our_public = public_key, 
            peer_public = packet.server_public_key,
        )
        self._auth_data["keys"] = {
            "client_to_server_key": client_to_server_key, 
            "server_to_client_key": server_to_client_key,
        }
        
        plaintext = os.urandom(8)
        mac, ciphertext = CryptoAeadCtx.lock(
            plaintext, 
            client_to_server_key, 
            packet.server_nonce, 
            public_key
        )
        
        return AdminAuthenticationResponsePacket(public_key, mac, ciphertext)
    
    
    def _enable_encryption(self, packet: ServerEnableEncryptionPacket) -> None:
        self._auth_data = {
            "receive_handler": CryptoAeadCtx(self._auth_data["keys"]["server_to_client_key"], packet.encryption_nonce),
            "send_handler": CryptoAeadCtx(self._auth_data["keys"]["client_to_server_key"], packet.encryption_nonce),
        }
        
        # update read/write handlers
        self.read = self._auth_data["receive_handler"].read
        self.write = self._auth_data["send_handler"].write
        
        return None
    
    def read(self, data: bytes) -> bytes:
        return data
    
    def write(self, data: bytes) -> bytes:
        return data
    
    def clear(self):
        """
        Python does not really allow to wipe information, overwriting strings and bytes will not overwrite the physical location in memory.
        The cpp extension does allow this, so we wipe those keys.
        """
        if self._auth_data.get("receive_handler"):
            self._auth_data["receive_handler"].wipe()
        if self._auth_data.get("send_handler"):
            self._auth_data["send_handler"].wipe()

























