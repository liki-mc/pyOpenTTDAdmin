from __future__ import annotations

import socket

from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .pymonocypher import CryptoAeadCtx

from .enums import *
from .packet import *
from .ottdcrypto import Auth

try:
    import secrets
    randombytes = secrets.token_bytes
except ImportError:
    import os
    randombytes = os.urandom

class Admin:
    """This class is used to interact with an OpenTTD server using the admin port.

    - ip (str): The IP address of the server.
    - port (int): The port of the server.
    - name (str): The name of the admin.
    - password (str): The password of the admin.
    """
    def __init__(self, ip: str = "127.0.0.1", port: int = 3977, secure: bool = True):
        self.socket = socket.socket()
        self.socket.connect((ip, port))
        self.socket.settimeout(0.5) # used to periodically check for keyboard interrupts
        self._buffer = b""
        self.handlers: dict[PacketType, list[Callable]] = {}
        self.receive_crypto_handler: None | CryptoAeadCtx = None
        self.send_crypto_handler: None | CryptoAeadCtx = None
        self.auth: None | Auth = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.socket.close()

    def login(
        self, 
        name: str,
        password: str | None = None, 
        version: str | int = "15.0",
        private_key: bytes | None = None,  
        secure: bool = True
    ):
        """Log in to the server.

        - name (str): The name of the admin.
        - password (str): The password of the admin.
        - version (int): The version of the admin. Default is 0.
        - private_key (str): private key of the admin, can only be used with secure login
        - secure (bool): whether or not to make a secure connection
        """
        if not secure:
            packet = AdminJoinPacket(password, name, str(version))
            self._send(packet)
        else:
            login_methods = 0x0000
            if private_key is None:
                private_key = randombytes(32)
            else:
                login_methods |= (1 << NetworkAuthenticationMethod.X25519_AuthorisedKey.value)
            
            if password is not None:
                login_methods |= (1 << NetworkAuthenticationMethod.X25519_PAKE.value)
            
            if not login_methods:
                raise ValueError(f"Unable to login, either set a password or provide a private key")
            
            self.auth = Auth(private_key, password)
            packet = AdminJoinSecurePacket(
                name = name,
                version = str(version),
                method_mask = login_methods
            )
            
            self._send(packet)
            
            packet, = self.recv_num(1)
            if not isinstance(packet, ServerAuthenticationRequestPacket):
                raise RuntimeError(f"Expected a ServerAuthenticationRequestPacket, instead got {type(packet)}, please make an issue on github")
            public_key, mac, ciphertext = self.auth.PAKE(
                packet.server_public_key,
                packet.server_nonce
            )
            packet = AdminAuthenticationResponsePacket(
                public_key = public_key,
                mac = mac,
                message = ciphertext
            )
            self._send(packet)
            
            packet, = self.recv_num(1)
            if not isinstance(packet, ServerEnableEncryptionPacket):
                raise RuntimeError(f"Expected a ServerEnableEncryptionPacket, instead got {type(packet)}, please make an issue on github")
            
            self.receive_crypto_handler = self.auth.get_receive_handler(packet.encryption_nonce)
            self.send_crypto_handler = self.auth.get_send_handler(packet.encryption_nonce)
            del self.auth
            self.auth = None
        return
        

    def _send(self, packet: Packet):
        data = packet.to_bytes()
        packet_type = packet.packet_type.value.to_bytes(1, 'little')
        data = packet_type + data
        if self.send_crypto_handler is not None:
            mac, ciphertext = self.send_crypto_handler.write(data)
            data = mac + ciphertext
        
        length = (len(data) + 2).to_bytes(2, 'little')

        self.socket.send(length + data)

    def _recv(self, size: int):
        """Help function to periodically check for keyboard interrupts.

        Returns socket.recv(size)
        """
        try:
            return self.socket.recv(size)
        except socket.timeout:
            return b""

    def recv_num(self, num: int) -> list[Packet]:
        """Receive given number of packets from the server.
        
        - num (int): the number of packets to get
        
        Returns:
        - list[Packet]: A list of packets received from the server.
        """
        packets = []
        while len(packets) != num:
            self._buffer += self._recv(1024)
            packet_len = int.from_bytes(self._buffer[0:2], 'little')
            
            while (len(self._buffer) >= packet_len):
            
                data = self._buffer[2: packet_len]
                self._buffer = self._buffer[packet_len:]
                if self.receive_crypto_handler is not None:
                    data = self.receive_crypto_handler.read(data[:16], data[16:])
            
                packet = Packet.create_packet(data)
                packets.append(packet)
                
                if len(packets) == num:
                    return packets
                
                packet_len = int.from_bytes(self._buffer[0:2], 'little')
        
        return packets
            

    def recv(self) -> list[Packet]:
        """Receive packets from the server.
        
        Returns:
        - list[Packet]: A list of packets received from the server.
        """
        self._buffer += self._recv(1024)
        packets = []
        if len(self._buffer) < 2:
            return packets

        while True:
            packet_len = int.from_bytes(self._buffer[0:2], 'little')
            if len(self._buffer) < packet_len:
                return packets
            
            data = self._buffer[2: packet_len]
            self._buffer = self._buffer[packet_len:]
            if self.receive_crypto_handler is not None:
                data = self.receive_crypto_handler.read(data[:16], data[16:])
            
            packets.append(Packet.create_packet(data))
            if not self._buffer:
                return packets
        
    def _rcon(self, command: str):
        packet = AdminRconPacket(command)
        self._send(packet)

    def _chat(self, message: str, action: Actions = Actions.CHAT, desttype: ChatDestTypes = ChatDestTypes.BROADCAST, id: int = 0):
        packet = AdminChatPacket(message, action, desttype, id)
        self._send(packet)

    def _subscribe(self, type: AdminUpdateType, frequency: AdminUpdateFrequency = AdminUpdateFrequency.AUTOMATIC):
        packet = AdminSubscribePacket(type, frequency)
        self._send(packet)

    def send_rcon(
        self,
        command: str
    ) -> None:
        """Send an RCON command to the server.
        
        - command (str): The RCON command to send.
        """
        self._rcon(command)

    def send_global(
        self,
        message: str
    ) -> None:
        """Send a global chat message to the server.
        
        - message (str): The message to send.
        """
        self._chat(message)

    def send_company(
        self,
        message: str,
        id: int
    ) -> None:
        """Send a chat message to a company.

        - message (str): The message to send.
        - id (int): The company ID.
        """
        self._chat(message, action = Actions.CHAT_COMPANY, desttype = ChatDestTypes.TEAM, id = id)

    def send_private(
        self,
        message: str,
        id: int
    ) -> None:
        """Send a private chat message to a client.

        - message (str): The message to send.
        - id (int): The client ID.
        """
        self._chat(message, action = Actions.CHAT_CLIENT, desttype = ChatDestTypes.CLIENT, id = id)

    def subscribe(
        self,
        type: AdminUpdateType,
        frequency: AdminUpdateFrequency = AdminUpdateFrequency.AUTOMATIC
    ) -> None:
        """Subscribe to an update type.

        - type (AdminUpdateType): The type of update to subscribe to.
        - frequency (AdminUpdateFrequency): The frequency of the update. Default is AdminUpdateFrequency.AUTOMATIC.
        """
        if frequency not in AdminUpdateTypeFrequencyMatrix[type]:
            raise ValueError(f"Invalid frequency ({frequency}) for {type}")
        self._subscribe(type, frequency)

    def run(self):
        """This method will keep polling the server for packets, it calls on_packet for each packet received.
        
        If a ShutdownPacket is recieved, the method will return.
        """
        while True:
            packets = self.recv()
            for packet in packets:
                self.on_packet(packet)
                
                if isinstance(packet, ShutdownPacket):
                    return

    def handle_packet(self, packet: Packet):
        """Handle a packet received from the server.

        - packet (Packet): The packet to handle.
        """
        for handler in self.handlers.get(type(packet), []):
            handler(self, packet)

    def add_handler(self, *packet_types: type[Packet]):
        """Decorator to add a handler for a specific packet type.

        - packets (Packet): The packet classes to handle.
        """
        def decorator(func: Callable[[Admin, Packet], None]):
            for packet_type in packet_types:
                if packet_type not in self.handlers:
                    self.handlers[packet_type] = []
                self.handlers[packet_type].append(func)
            return func
        
        return decorator

    def on_packet(self, packet: Packet):
        """This method is called for each packet received from the server.
        
        - packet (Packet): Packet received from the server.
        """
        self.handle_packet(packet)
