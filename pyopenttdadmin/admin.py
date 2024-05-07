import socket
import time

from .enums import *
from .packet import *

class Admin:
    def __init__(self, ip: str = "127.0.0.1", port: int = 3977, name: str = "pyAdminServer", password: str | None = None):
        self.socket = socket.socket()
        self.socket.connect((ip, port))
        self.admin_name = name
        self.admin_password = password
        self._buffer = b""
    
    def __enter__(self):
        if self.admin_password == None:
            raise ValueError("Admin password not set.")
        self.login(self.admin_name, self.admin_password)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.socket.close()
        
    
    def login(self, name: str, password: str, version = 0):
        self._send(PacketType.ADMIN_JOIN, password, name, str(version))
    
    def _send(self, packet: PacketType, *args: str):
        if not args:
            return
        buffer: bytes = ("\x00".join(args)).encode('utf-8') + b"\x00"
        length = (len(buffer) + 3).to_bytes(2, 'little')
        print(buffer, length, packet.value.to_bytes(1, 'little'))
        self.socket.send(length + packet.value.to_bytes(1, 'little') + buffer)
    
    def recv(self) -> list[Packet]:
        self._buffer += self.socket.recv(1024)
        packets = []
        while True:
            packet_len = int.from_bytes(self._buffer[0:2], 'little')
            if len(self._buffer) < packet_len:
                return packets
            
            packets.append(create_packet(self._buffer[2], self._buffer[2: packet_len]))
            self._buffer = self._buffer[packet_len:]
            if not self._buffer:
                return packets
        
    def _rcon(self, command: str):
        self._send(PacketType.ADMIN_RCON, command)
    
    def _chat(self, message: str, action: Actions = Actions.CHAT, desttype: ChatDestTypes = ChatDestTypes.BROADCAST, id: int = 0):
        buffer = (
            action.value.to_bytes(1, 'little') + 
            desttype.value.to_bytes(1, 'little') + 
            id.to_bytes(4, 'little')
        )
        self._send(PacketType.ADMIN_CHAT, buffer.decode('utf-8') + message)
    
    def _subscribe(self, type: AdminUpdateType, frequency: AdminUpdateFrequency = AdminUpdateFrequency.AUTOMATIC):
        buffer = (
            type.value.to_bytes(2, 'little') + 
            frequency.value.to_bytes(2, 'little')
        )
        self._send(PacketType.FREQUENCY, buffer.decode('utf-8'))
    
    def send_rcon(
        self,
        command: str
    ) -> None:
        self._rcon(command)
    
    def send_global(
        self,
        message: str
    ) -> None:
        self._chat(message)

    def send_company(
        self,
        message: str,
        id: int
    ) -> None:
        self._chat(message, desttype=ChatDestTypes.TEAM, id=id)
    
    def send_private(
        self,
        message: str,
        id: int
    ) -> None:
        self._chat(message, desttype=ChatDestTypes.CLIENT, id=id)

    def send_subscribe(
        self,
        type: AdminUpdateType,
        frequency: AdminUpdateFrequency = AdminUpdateFrequency.AUTOMATIC
    ) -> None:
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
    
    def on_packet(self, packet: Packet):
        pass
        