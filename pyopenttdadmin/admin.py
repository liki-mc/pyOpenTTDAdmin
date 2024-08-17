import socket
import time

from typing import Callable

from .enums import *
from .packet import *

class Admin:
    """This class is used to interact with an OpenTTD server using the admin port.

    - ip (str): The IP address of the server.
    - port (int): The port of the server.
    - name (str): The name of the admin.
    - password (str): The password of the admin.
    """
    def __init__(self, ip: str = "127.0.0.1", port: int = 3977):
        self.socket = socket.socket()
        self.socket.connect((ip, port))
        self.socket.settimeout(0.5) # used to periodically check for keyboard interrupts
        self._buffer = b""
        self.handlers: dict[PacketType, list[Callable]] = {}

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.socket.close()
    
    def login(self, name: str, password: str, version: int = 0):
        """Log in to the server.

        - name (str): The name of the admin.
        - password (str): The password of the admin.
        - version (int): The version of the admin. Default is 0.
        """
        packet = AdminJoinPacket(password, name, str(version))
        self._send(packet)
    
    def _send(self, packet: Packet):
        data = packet.to_bytes()
        packet_type = packet.packet_type.value.to_bytes(1, 'little')
        length = (len(data) + 3).to_bytes(2, 'little')

        self.socket.send(length + packet_type + data)
    
    def _recv(self, size: int):
        """Help function to periodically check for keyboard interrupts.

        Returns socket.recv(size)
        """
        try:
            return self.socket.recv(size)
        except socket.timeout:
            return b""
    
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
            
            packets.append(Packet.create_packet(self._buffer[2: packet_len]))
            self._buffer = self._buffer[packet_len:]
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
        
        If a shutdownpacket is recieved, the method will return.
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
