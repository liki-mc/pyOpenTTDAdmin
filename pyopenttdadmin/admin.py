from __future__ import annotations

import socket
import warnings

from typing import Callable, Type

from .enums import *
from .packet import *
from .auth import Auth

class Admin:
    """This class is used to interact with an OpenTTD server using the admin port.

    - ip (str): The IP address of the server.
    - port (int): The port of the server.
    - auth (Auth): The authentication instance
    """
    def __init__(self, ip: str = "127.0.0.1", port: int = 3977, auth: Auth | None = None):
        self.socket: socket.socket | None = socket.socket()
        self.socket.connect((ip, port))
        self.socket.settimeout(0.5) # used to periodically check for keyboard interrupts
        self._buffer = b""
        self.handlers: dict[Type[Packet], list[Callable]] = {}
        
        self.auth: None | Auth = auth if auth is not None else Auth(_ignore_data = True)
    
    @property
    def authenticated(self) -> bool:
        return self.auth.authenticated

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.socket.close()
        self.auth.clear()

    def login(
        self, 
        name: str | None = None,
        password: str | None = None, 
        version: str | int = "15.0"
    ):
        """Depricated
        Log in to the server.

        Setting arguments to this function is depricated, please use the Auth api:
        ```
        auth  = Auth(name, version, password = password, private_key = private_key)
        admin = Admin(..., auth = auth)
        ```
        Login will happen on the first call to the server.
        """
        if not self.auth._auth_data:
            warnings.warn(DeprecationWarning("The admin.login() function is depcricated. \nInitialise the admin using ```auth  = Auth(name, version, password = password, private_key = private_key)\nadmin = Admin(..., auth = auth)```"))
        
            self.auth._set_login_data(name, version, password)
        self._auth()
        
    def _auth(self):
        if self.authenticated:
            return
        
        packet, is_authenticated = self.auth()
        while not is_authenticated:
            if packet is not None:
                self.__send(packet)
            packet, = self._recv_num(1)
            packet, is_authenticated = self.auth(packet)
        

    def __send(self, packet: Packet):
        data = packet.to_bytes()
        packet_type = packet.packet_type.value.to_bytes(1, 'little')
        data = self.auth.write(packet_type + data)
        
        length = (len(data) + 2).to_bytes(2, 'little')

        self.socket.send(length + data)
    
    def _send(self, packet: Packet):
        if not self.authenticated:
            self._auth()
        
        self.__send(packet)

    def _recv(self, size: int):
        """Help function to periodically check for keyboard interrupts.

        Returns socket.recv(size)
        """
        try:
            return self.socket.recv(size)
        except socket.timeout:
            return b""

    def _recv_num(self, num: int) -> list[Packet]:
        """Receive given number of packets from the server.
        
        - num (int): the number of packets to get
        
        Returns:
        - list[Packet]: A list of packets received from the server.
        """
        packets: list[Packet] = []
        while len(packets) != num:
            self._buffer += self._recv(1024)
            packet_len = int.from_bytes(self._buffer[0:2], 'little')
            while (len(self._buffer) >= packet_len):
            
                data = self.auth.read(self._buffer[2: packet_len])
                self._buffer = self._buffer[packet_len:]
            
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
        if not self.authenticated:
            self._auth()
        
        self._buffer += self._recv(1024)
        packets: list[Packet] = []
        if len(self._buffer) < 2:
            return packets

        while True:
            packet_len = int.from_bytes(self._buffer[0:2], 'little')
            if len(self._buffer) < packet_len:
                return packets
            
            data = self.auth.read(self._buffer[2: packet_len])
            self._buffer = self._buffer[packet_len:]
            
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
        try:
            while True:
                packets = self.recv()
                for packet in packets:
                    self.on_packet(packet)
                    
                    if isinstance(packet, ShutdownPacket):
                        return
        finally:
            self.auth.clear()

    def handle_packet(self, packet: Packet):
        """Handle a packet received from the server.

        - packet (Packet): The packet to handle.
        """
        for handler in self.handlers.get(type(packet), []):
            handler(self, packet)

    def add_handler(self, *packet_types: Type[Packet]):
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
