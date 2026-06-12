from __future__ import annotations

import asyncio
import warnings

from typing import Callable, Coroutine, Type

from pyopenttdadmin.enums import *
from pyopenttdadmin.packet import *
from pyopenttdadmin.auth import Auth

class Admin:
    """This class is used to interact with an OpenTTD server using the admin port.

    - ip (str): The IP address of the server.
    - port (int): The port of the server.
    - auth (Auth): The authentication instance
    """
    def __init__(self, ip: str = "127.0.0.1", port: int = 3977, auth: Auth = None):
        self.ip = ip
        self.port = port
        self._packets = asyncio.Queue(20)

        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

        self.handlers: dict[PacketType, list[Callable[[Admin, Packet], Coroutine]]] = {}
        self.auth: None | Auth = auth if auth is not None else Auth(_ignore_data = True)
        
        # Temp workaround if people call connect explicitely
        self.login_data = auth is not None
        self.encryption_lock = asyncio.Lock
    
    @property
    def authenticated(self) -> bool:
        return self.auth.authenticated
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        if self._writer is not None:
            if not self._writer.is_closing():
                self._writer.close()
            
            await self._writer.wait_closed()
        
        self.auth.clear()
    
    async def connect(self):
        self._reader, self._writer = await asyncio.open_connection(self.ip, self.port)
        if self.login_data:
            await self._auth()
    
    async def _get_packet(self):
        header = await self._reader.readexactly(2)
        packet_len = int.from_bytes(header, "little")
        payload = await self._reader.readexactly(packet_len - 2)
        data = self.auth.read(payload)
        return Packet.create_packet(data)
    
    async def _poll_packets(self):
        """
        Continuously poll for new packets
        """
        while not self._writer.is_closing():
            await self._packets.put(await self._get_packet())
    
    async def login(
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
            self.login_data = True
        
        if self._writer is None:
            await self.connect()
        else:
            await self._auth()
        
    async def _auth(self):
        if self.authenticated:
            return
        
        packet, is_authenticated = self.auth()
        while not is_authenticated:
            if packet is not None:
                await self._send(packet)
            packet = await self._get_packet()
            packet, is_authenticated = self.auth(packet)
        
        asyncio.create_task(
            self._poll_packets()
        )
    
    async def _send(self, packet: Packet):
        if self._writer is None:
            raise ValueError("Not connected to server.")
        
        data = packet.to_bytes()
        packet_type = packet.packet_type.value.to_bytes(1, 'little')
        data = self.auth.write(packet_type + data)
        length = (len(data) + 2).to_bytes(2, 'little')

        self._writer.write(length + data)
        await self._writer.drain()
        
    async def _recv_num(self, num: int) -> list[Packet]:
        """Receive given number of packets from the server.
        
        - num (int): the number of packets to get
        
        Returns:
        - list[Packet]: A list of packets received from the server.
        """
        return [await self._packets.get() for _ in range(num)]
    
    async def recv(self) -> list[Packet]:
        """Receive packets from the server.
        
        Returns:
        - list[Packet]: A list of packets received from the server.
        """
        out: list[Packet] = []
        try:
            while True:
                out.append(self._packets.get_nowait())
        except asyncio.QueueEmpty:
            if out:
                return out
            
            # nothing available now — await one item
            out.append(await self._packets.get())
            return out
        
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
        await self._chat(message, action = Actions.CHAT_COMPANY, desttype = ChatDestTypes.TEAM, id = id)
    
    async def send_private(
        self,
        message: str,
        id: int
    ) -> None:
        """Send a private chat message to a client.

        - message (str): The message to send.
        - id (int): The client ID.
        """
        await self._chat(message, action = Actions.CHAT_CLIENT, desttype = ChatDestTypes.CLIENT, id = id)

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
        try:
            while True:
                packets = await self.recv()
                for packet in packets:
                    await self.on_packet(packet)
                    
                    if isinstance(packet, ShutdownPacket):
                        return
        finally:
            self.auth.clear()
    
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
