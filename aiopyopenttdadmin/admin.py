from pyopenttdadmin.enums import *
from pyopenttdadmin.packet import *

from typing import Callable, Coroutine

import asyncio

class Admin:
    """This class is used to interact with an OpenTTD server using the admin port.

    - ip (str): The IP address of the server.
    - port (int): The port of the server.
    """
    def __init__(self, ip: str = "127.0.0.1", port: int = 3977):
        self.ip = ip
        self.port = port
        self._buffer = b""
        self._packets = []

        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

        self.handlers: dict[PacketType, list[Callable[[Admin, Packet], Coroutine]]] = {}
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        if self._writer is not None:
            if not self._writer.is_closing():
                self._writer.close()
            
            await self._writer.wait_closed()
    
    async def connect(self):
        self._reader, self._writer = await asyncio.open_connection(self.ip, self.port)
    
    async def login(self, name: str, password: str, version: int = 0):
        """Log in to the server.

        - name (str): The name of the admin.
        - password (str): The password of the admin.
        - version (int): The version of the admin. Default is 0.
        """
        if self._writer is None:
            await self.connect()
        
        packet = AdminJoinPacket(password, name, str(version))
        await self._send(packet)
    
    async def _send(self, packet: Packet):
        if self._writer is None:
            raise ValueError("Not connected to server.")
        
        data = packet.to_bytes()
        packet_type = packet.packet_type.value.to_bytes(1, 'little')
        length = (len(data) + 3).to_bytes(2, 'little')

        self._writer.write(length + packet_type + data)
        await self._writer.drain()
    
    async def recv(self) -> list[Packet]:
        """Receive packets from the server.
        
        Returns:
        - list[Packet]: A list of packets received from the server.
        """
        if self._reader is None:
            raise ValueError("Not connected to server.")
        
        self._buffer += await self._reader.read(1024)

        # buffer can be empty
        if not self._buffer:
            return []
        
        packets = self._packets
        self._packets = []

        fetched = 1
        while True:
            if len(self._buffer) < 2:
                return packets
            
            packet_len = int.from_bytes(self._buffer[0:2], 'little')
            if len(self._buffer) < packet_len:
                if fetched > 5:
                    # only keep fetching 5 times on incomplete data
                    return packets

                # more data is available
                self._buffer += await self._reader.read(1024)
                fetched += 1
                continue
            
            packets.append(Packet.create_packet(self._buffer[2: packet_len]))
            self._buffer = self._buffer[packet_len:]

            # no data available
            if not self._buffer:
                return packets
        
    async def _rcon(self, command: str):
        packet = AdminRconPacket(command)
        await self._send(packet)
    
    async def _chat(self, message: str, action: Actions = Actions.CHAT, desttype: ChatDestTypes = ChatDestTypes.BROADCAST, id: int = 0):
        packet = AdminChatPacket(message, action, desttype, id)
        await self._send(packet)
    
    async def _subscribe(self, type: AdminUpdateType, frequency: AdminUpdateFrequency = AdminUpdateFrequency.AUTOMATIC):
        packet = AdminSubscribePacket(type, frequency)
        await self._send(packet)
    
    async def send_rcon(
        self,
        command: str
    ) -> None:
        """Send an RCON command to the server.
        
        - command (str): The RCON command to send.
        """
        await self._rcon(command)
    
    async def send_global(
        self,
        message: str
    ) -> None:
        """Send a global chat message to the server.
        
        - message (str): The message to send.
        """
        await self._chat(message)

    async def send_company(
        self,
        message: str,
        id: int
    ) -> None:
        """Send a chat message to a company.

        - message (str): The message to send.
        - id (int): The company ID.
        """
        await self._chat(message, desttype=ChatDestTypes.TEAM, id=id)
    
    async def send_private(
        self,
        message: str,
        id: int
    ) -> None:
        """Send a private chat message to a client.

        - message (str): The message to send.
        - id (int): The client ID.
        """
        await self._chat(message, desttype=ChatDestTypes.CLIENT, id=id)

    async def subscribe(
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
        
        await self._subscribe(type, frequency)
    
    async def run(self):
        """This method will keep polling the server for packets, it calls on_packet for each packet received.
        
        If a shutdownpacket is recieved, the method will return.
        """
        while True:
            packets = await self.recv()

            for packet in packets:
                await self.on_packet(packet)
                
                if isinstance(packet, ShutdownPacket):
                    return
    
    async def handle_packet(self, packet: Packet):
        """Handle a packet received from the server.

        - packet (Packet): The packet to handle.
        """
        tasks = set()
        for handler in self.handlers.get(type(packet), []):
            tasks.add(handler(self, packet))
        
        await asyncio.gather(*tasks)
    
    def add_handler(self, *packets: type[Packet]):
        """Decorator to add a handler for a specific packet type.

        - packets (Packet): The packet classes to handle.
        """
        def decorator(func: Callable[[Admin, Packet], Coroutine]):
            if not asyncio.iscoroutinefunction(func):
                raise ValueError("Handler must be a coroutine.")

            for packet_type in packets:
                if packet_type not in self.handlers:
                    self.handlers[packet_type] = []
                self.handlers[packet_type].append(func)
            
            return func
        
        return decorator
    
    async def on_packet(self, packet: Packet):
        """This method is called for each packet received from the server.
        
        - packet (Packet): Packet received from the server.
        """
        await self.handle_packet(packet)