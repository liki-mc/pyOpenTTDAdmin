from .enums import *

from typing_extensions import Self

# reference: https://github.com/OpenTTD/OpenTTD/blob/master/src/network/core/tcp_admin.h

class Packet:
    packet_type = PacketType.INVALID_ADMIN_PACKET
    def __init__(self, data: bytes):
        self.data = data
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.data})"
    
    def to_bytes(self) -> bytes:
        raise NotImplementedError()

    @staticmethod
    def create_packet(data: bytes):
        type = PacketType(data[0])
        return packet_dict[type].from_bytes(data)
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        raise NotImplementedError()

class ErrorPacket(Packet):
    packet_type = PacketType.SERVER_ERROR
    def __init__(self, error: NetWorkErrorCodes):
        self.error = error
    
    def __repr__(self) -> str:
        return f"ErrorPacket({self.error})"
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        error = NetWorkErrorCodes(data[1])
        return ErrorPacket(error)
        
class AdminJoinPacket(Packet):
    packet_type = PacketType.ADMIN_JOIN
    def __init__(self, password: str, string: str, version: str):
        self.password = password
        self.string = string
        self.version = version

    def __repr__(self) -> str:
        return f"AdminJoinPacket()"
    
    def to_bytes(self) -> bytes:
        return f"{self.password}\x00{self.string}\x00{self.version}\x00".encode('utf-8')
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        password, _, data = data[1:].partition(b'\x00')
        string, _, data = data.partition(b'\x00')
        version, _, data = data.partition(b'\x00')
        
        return AdminJoinPacket(password.decode('utf-8'), string.decode('utf-8'), version.decode('utf-8'))

class ProtocolPacket(Packet):
    packet_type = PacketType.SERVER_PROTOCOL
    def __init__(self, version: int, subscriptions: dict[AdminUpdateType, AdminUpdateFrequency | None]):
        self.version = version
        self.subscriptions = subscriptions
    
    def __repr__(self) -> str:
        return f"ProtocolPacket({self.version}, {self.subscriptions})"
    
    def print(self) -> str:
        subs = "\n    ".join([f"{k}: {v}" for k, v in self.subscriptions.items()])
        return f"ProtocolPacket({self.version}, subs = (\n{subs}\n))"
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        version = data[1]
        subscriptions: dict[AdminUpdateType, AdminUpdateFrequency | None] = {}
        for i in range(2, len(data) - 1, 5):
            b = bool(data[i])
            if not b:
                continue
            
            update_type = AdminUpdateType(int.from_bytes(data[i + 1: i + 3], 'little'))
            try:
                frequency_type = AdminUpdateFrequency(int.from_bytes(data[i + 3: i + 5], 'little'))
            except ValueError:
                frequency_type = None
            
            subscriptions[update_type] = frequency_type
        
        return ProtocolPacket(version, subscriptions)

class WelcomePacket(Packet):
    packet_type = PacketType.SERVER_WELCOME
    def __init__(self, server_name: str, version: str, dedicated: bool, map_name: str, seed: int, landscape: int, startdate: int, mapheight: int, mapwidth: int):
        self.server_name = server_name
        self.version = version
        self.dedicated = dedicated
        self.map_name = map_name
        self.seed = seed
        self.landscape = landscape
        self.startdate = startdate
        self.mapheight = mapheight
        self.mapwidth = mapwidth
        
    def __repr__(self) -> str:
        return f"WelcomePacket({self.server_name}, {self.version}, {self.dedicated}, {self.map_name}, {self.seed}, {self.landscape}, {self.startdate}, {self.mapheight}, {self.mapwidth})"
    
    def print(self) -> str:
        return f"""WelcomePacket(
    {self.server_name},
    {self.version},
    {self.dedicated},
    {self.map_name},
    {self.seed},
    {self.landscape},
    {self.startdate},
    {self.mapheight},
    {self.mapwidth}
)"""
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        server_name, _, data = data[1:].partition(b'\x00')
        version, _, data = data.partition(b'\x00')
        dedicated = bool(data[0])
        map_name, _, data = data[1:].partition(b'\x00')
        
        server_name = server_name.decode('utf-8')
        version = version.decode('utf-8')
        map_name = map_name.decode('utf-8')
        
        seed = int.from_bytes(data[:4], 'little')
        landscape = Landscape(data[4])
        startdate = int.from_bytes(data[5:9], 'little')
        mapheight = int.from_bytes(data[9:11], 'little')
        mapwidth = int.from_bytes(data[11: 13], 'little')

        return WelcomePacket(server_name, version, dedicated, map_name, seed, landscape, startdate, mapheight, mapwidth)

class NewGamePacket(Packet):
    packet_type = PacketType.SERVER_NEWGAME
    def __init__(self, data: bytes):
        pass
    
    def __repr__(self) -> str:
        return f"NewGamePacket()"

    @staticmethod
    def from_bytes(data: bytes) -> Self:
        return NewGamePacket(data)

class ShutdownPacket(Packet):
    packet_type = PacketType.SERVER_SHUTDOWN
    def __init__(self, data: bytes):
        pass
    
    def __repr__(self) -> str:
        return f"ShutdownPacket()"

    @staticmethod
    def from_bytes(data: bytes) -> Self:
        return ShutdownPacket(data)

class DatePacket(Packet):
    packet_type = PacketType.SERVER_DATE
    def __init__(self, date: int):
        self.date = date
    
    def __repr__(self) -> str:
        return f"DatePacket({self.date})"
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        date = int.from_bytes(data[1:5], 'little')
        return DatePacket(date)

class ClientJoinPacket(Packet):
    packet_type = PacketType.SERVER_CLIENT_JOIN
    def __init__(self, id: int):
        self.id = id
    
    def __repr__(self) -> str:
        return f"ClientJoinPacket({self.id})"

    @staticmethod
    def from_bytes(data: bytes) -> Self:
        id = int.from_bytes(data[1:5], 'little')
        return ClientJoinPacket(id)

class ClientInfoPacket(Packet):
    packet_type = PacketType.SERVER_CLIENT_INFO
    def __init__(self, id: int, ip: str, name: str, lang: int, joined: int, company_id: int):
        self.id = id
        self.ip = ip
        self.name = name
        self.lang = lang
        self.joined = joined
        self.company_id = company_id
    
    def __repr__(self) -> str:
        return f"ClientInfoPacket({self.id}, {self.ip}, {self.name}, {self.lang}, {self.joined}, {self.company_id})"
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        id = int.from_bytes(data[1:5], 'little')
        ip, _, data = data[5:].partition(b'\x00')
        name, _, data = data.partition(b'\x00')
        
        lang = data[0]
        joined = int.from_bytes(data[1:5], 'little')
        company_id = data[5]
        
        return ClientInfoPacket(id, ip.decode("utf-8"), name.decode("utf-8"), lang, joined, company_id)
    
class ClientUpdatePacket(Packet):
    packet_type = PacketType.SERVER_CLIENT_UPDATE
    def __init__(self, id: int, name: str, company_id: int):
        self.id = id
        self.name = name
        self.company_id = company_id
    
    def __repr__(self) -> str:
        return f"ClientUpdatePacket({self.id}, {self.name}, {self.company_id})"
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        id = int.from_bytes(data[1:5], 'little')
        name, _, data = data[5:].partition(b'\x00')
        company_id = data[0]
        
        return ClientUpdatePacket(id, name.decode('utf-8'), company_id)

class ClientQuitPacket(Packet):
    packet_type = PacketType.SERVER_CLIENT_QUIT
    def __init__(self, id: int):
        self.id = id
    
    def __repr__(self) -> str:
        return f"ClientQuitPacket({self.id})"

    @staticmethod
    def from_bytes(data: bytes) -> Self:
        id = int.from_bytes(data[1:5], 'little')
        return ClientQuitPacket(id)

class ClientErrorPacket(Packet):
    packet_type = PacketType.SERVER_CLIENT_ERROR
    def __init__(self, id: int, error: NetWorkErrorCodes):
        self.id = id
        self.error = error
    
    def __repr__(self) -> str:
        return f"ClientErrorPacket({self.id}, {self.error})"
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        id = int.from_bytes(data[1:5], 'little')
        error = NetWorkErrorCodes(data[5])
        return ClientErrorPacket(id, error)

class CompanyNewPacket(Packet):
    packet_type = PacketType.SERVER_COMPANY_NEW
    def __init__(self, id: int):
        self.id = id
    
    def __repr__(self) -> str:
        return f"CompanyNewPacket({self.id})"
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        id = data[1]
        return CompanyNewPacket(id)

class CompanyInfoPacket(Packet):
    packet_type = PacketType.SERVER_COMPANY_INFO
    def __init__(self, id: int, name: str, manager_name: str, color: Color, passworded: bool, year: int, is_ai: bool, quarters_to_bankruptcy: int):
        self.id = id
        self.name = name
        self.manager_name = manager_name
        self.color = color
        self.passworded = passworded
        self.year = year
        self.is_ai = is_ai
        self.quarters_to_bankruptcy = quarters_to_bankruptcy
    
    def __repr__(self) -> str:
        return f"CompanyInfoPacket({self.id}, {self.name}, {self.manager_name}, {self.color}, {self.passworded}, {self.year}, {self.is_ai}, {self.quarters_to_bankruptcy})"

    @staticmethod
    def from_bytes(data: bytes) -> Self:
        id = data[1]
        name, _, data = data[2:].partition(b'\x00')
        manager_name, _, data = data.partition(b'\x00')
        
        color = Color(data[0])
        passworded = bool(data[1])
        year = int.from_bytes(data[2:6], 'little')
        is_ai = bool(data[6])
        quarters_to_bankruptcy = data[7]
        
        return CompanyInfoPacket(id, name.decode('utf-8'), manager_name.decode('utf-8'), color, passworded, year, is_ai, quarters_to_bankruptcy)

class CompanyUpdatePacket(Packet):
    packet_type = PacketType.SERVER_COMPANY_UPDATE
    def __init__(self, id: int, name: str, manager_name: str, color: Color, passworded: bool, quarters_to_bankruptcy: int):
        self.id = id
        self.name = name
        self.manager_name = manager_name
        self.color = color
        self.passworded = passworded
        self.quarters_to_bankruptcy = quarters_to_bankruptcy
    
    def __repr__(self) -> str:
        return f"CompanyUpdatePacket({self.id}, {self.name}, {self.manager_name}, {self.color}, {self.passworded}, {self.quarters_to_bankruptcy})"

    @staticmethod
    def from_bytes(data: bytes) -> Self:
        print(data)
        id = data[1]
        name, _, data = data[2:].partition(b'\x00')
        manager_name, _, data = data.partition(b'\x00')
        
        name = name.decode('utf-8')
        manager_name = manager_name.decode('utf-8')
        
        print(data)
        color = Color(data[0])
        passworded = bool(data[1])
        quarters_to_bankruptcy = data[2]

        return CompanyUpdatePacket(id, name, manager_name, color, passworded, quarters_to_bankruptcy)


class CompanyRemovePacket(Packet):
    packet_type = PacketType.SERVER_COMPANY_REMOVE
    def __init__(self, id: int, admin_remove_reason: AdminCompanyRemoveReason):
        self.id = id
        self.admin_remove_reason = admin_remove_reason
    
    def __repr__(self) -> str:
        return f"CompanyRemovePacket({self.id}, {self.admin_remove_reason})"
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        id = data[1]
        admin_remove_reason = AdminCompanyRemoveReason(data[2])
        return CompanyRemovePacket(id, admin_remove_reason)

class CompanyEconomyPacket(Packet):
    packet_type = PacketType.SERVER_COMPANY_ECONOMY
    def __init__(self, id: int, money: int, current_loan: int, delivered_cargo: int, quarterly_info: list[tuple[int, int, int]]):
        self.id = id
        self.money = money
        self.current_loan = current_loan
        self.delivered_cargo = delivered_cargo
        self.quarterly_info = quarterly_info
    
    def __repr__(self) -> str:
        return f"CompanyEconomyPacket({self.id}, {self.money}, {self.current_loan}, {self.delivered_cargo})"
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        id = data[1]
        money = int.from_bytes(data[2:10], 'little')
        current_loan = int.from_bytes(data[10:18], 'little')
        delivered_cargo = int.from_bytes(data[18:20], 'little')
        data = data[20:]
        quarterly_info = []
        
        for i in range(2):
            company_value = int.from_bytes(data[:8], 'little')
            company_performance_history = int.from_bytes(data[8:10], 'little')
            delivered_cargo = int.from_bytes(data[10:12], 'little')
            quarterly_info.append((company_value, company_performance_history, delivered_cargo))
            data = data[12:]
        
        return CompanyEconomyPacket(id, money, current_loan, delivered_cargo, quarterly_info)

class CompanyStatsPacket(Packet):
    packet_type = PacketType.SERVER_COMPANY_STATS
    def __init__(self, id: int, num_vehicles: dict[NetworkVehicleType, int]):
        self.id = id
        self.num_vehicles = num_vehicles
        
    def __repr__(self) -> str:
        vehicles = "\n    ".join([f"{k}: {v}" for k, v in self.num_vehicles.items()])
        return f"CompanyStatsPacket({self.id}, {vehicles})"

    @staticmethod
    def from_bytes(data: bytes) -> Self:
        id = data[1]
        num_vehicles: dict[NetworkVehicleType, int] = {}
        for i in range(NetworkVehicleType.NETWORK_VEH_END.value):
            num_vehicles[NetworkVehicleType(i)] = int.from_bytes(data[2 + i * 2: 4 + i * 2], 'little')
        
        return CompanyStatsPacket(id, num_vehicles)

class ChatPacket(Packet):
    packet_type = PacketType.SERVER_CHAT
    def __init__(self, action: Actions, desttype: ChatDestTypes, id: int, message: str, money: int):
        self.action = action
        self.desttype = desttype
        self.id = id
        self.message = message
        self.money = money
    
    def __repr__(self) -> str:
        return f"ChatPacket{self.action.value, self.desttype.value, self.id, self.message, self.money}"
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        money = None
        action = Actions(data[1])
        desttype = ChatDestTypes(data[2])
        id = int.from_bytes(data[3: 7], 'little')
        message = data[7: -9].decode('utf-8') # -9 is 8 for money + 1 to indicate end of string
        money = int.from_bytes(data[-8:], 'little')

        return ChatPacket(action, desttype, id, message, money)

class RconEndPacket(Packet):
    packet_type = PacketType.SERVER_RCON_END
    def __init__(self, command: str):
        self.command = command
    
    def __repr__(self) -> str:
        return f"RconEndPacket({self.command})"

    @staticmethod
    def from_bytes(data: bytes) -> Self:
        command, *_ = data[1:].partition(b'\x00')
        return RconEndPacket(command)
   
class RconPacket(Packet):
    packet_type = PacketType.SERVER_RCON
    def __init__(self, color: bytes, response: str):
        self.color = color
        self.response = response
    
    def __repr__(self) -> str:
        return f"RconPacket({self.color}, {self.response})"
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        color = data[1:3] # Color(int.from_bytes(data[1:3], 'little')) - this uses colors up to 256
        response, *_ = data[3:].partition(b'\x00')
        return RconPacket(color, response.decode('utf-8'))

class ConsolePacket(Packet):
    packet_type = PacketType.SERVER_CONSOLE
    def __init__(self, origin: str, message: str):
        self.origin = origin
        self.message = message

    def __repr__(self) -> str:
        return f"ConsolePacket({self.origin}, {self.message})"
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        origin, _, data = data[1:].partition(b'\x00')
        message, *_ = data.partition(b'\x00')
        
        return ConsolePacket(origin.decode('utf-8'), message.decode('utf-8'))

class GameScriptPacket(Packet):
    packet_type = PacketType.SERVER_GAMESCRIPT
    def __init__(self, json: str):
        self.json = json
    
    def __repr__(self) -> str:
        return f"GameScriptPacket({self.json})"
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        json = data[1:].decode('utf-8')
        return GameScriptPacket(json)

class CmdNamesPacket(Packet):
    packet_type = PacketType.SERVER_CMD_NAMES
    def __init__(self, names: list[str]):
        self.names = names
    
    def __repr__(self) -> str:
        return f"CmdNamesPacket({self.names})"
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        names = []
        while b'\x00' in data:
            name, _, data = data.partition(b'\x00')
            names.append(name.decode('utf-8'))
        
        if data[:-1]:
            names.append(data[:-1].decode('utf-8'))

        return CmdNamesPacket(names)

class CmdLoggingPacket(Packet):
    packet_type = PacketType.SERVER_CMD_LOGGING
    def __init__(self, client_id: int, company_id: int, cmd: int, data: bytes, frame: int):
        self.client_id = client_id
        self.company_id = company_id
        self.cmd = cmd
        self.data = data
        self.frame = frame
    
    def __repr__(self) -> str:
        return f"CmdLoggingPacket({self.client_id}, {self.company_id}, {self.cmd}, {self.data}, {self.frame})"
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        client_id = int.from_bytes(data[1:5], 'little')
        company_id = data[5]
        cmd = int.from_bytes(data[6:8], 'little')
        buffer_length = int.from_bytes(data[8:10], 'little')
        data = data[10: 10 + buffer_length]
        frame = int.from_bytes(data[10 + buffer_length: 14 + buffer_length], 'little')

        return CmdLoggingPacket(client_id, company_id, cmd, data, frame)

class AdminRconPacket(Packet):
    packet_type = PacketType.ADMIN_RCON
    def __init__(self, command: str):
        self.command = command
    
    def __repr__(self) -> str:
        return f"AdminRconPacket({self.command})"
    
    def to_bytes(self) -> bytes:
        return f"{self.command}\x00".encode('utf-8')
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        command, *_ = data[1:].partition(b'\x00')
        return AdminRconPacket(command.decode('utf-8'))

class AdminChatPacket(Packet):
    packet_type = PacketType.ADMIN_CHAT
    def __init__(self, message: str, action: Actions = Actions.CHAT, desttype: ChatDestTypes = ChatDestTypes.BROADCAST, id: int = 0):
        self.message = message
        self.action = action
        self.desttype = desttype
        self.id = id
    
    def __repr__(self) -> str:
        return f"AdminChatPacket({self.message}, {self.action}, {self.desttype}, {self.id})"
    
    def to_bytes(self) -> bytes:
        buffer = (
            self.action.value.to_bytes(1, 'little') + 
            self.desttype.value.to_bytes(1, 'little') + 
            self.id.to_bytes(4, 'little')
        )
        return buffer + f"{self.message}\x00".encode('utf-8')
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        action = Actions(data[1])
        desttype = ChatDestTypes(data[2])
        id = int.from_bytes(data[3:7], 'little')
        message, *_ = data[7:].partition(b'\x00')
        return AdminChatPacket(message.decode('utf-8'), action, desttype, id)

class AdminSubscribePacket(Packet):
    packet_type = PacketType.FREQUENCY
    def __init__(self, type: AdminUpdateType, frequency: AdminUpdateFrequency):
        self.type = type
        self.frequency = frequency

    def __repr__(self) -> str:
        return f"AdminFrequencyPacket({self.type}, {self.frequency})"
    
    def to_bytes(self) -> bytes:
        return self.type.value.to_bytes(2, 'little') + self.frequency.value.to_bytes(2, 'little') + b"\x00"
    
    @staticmethod
    def from_bytes(data: bytes) -> Self:
        type = AdminUpdateType(int.from_bytes(data[1:3], 'little'))
        frequency = AdminUpdateFrequency(int.from_bytes(data[3:5], 'little'))
        return AdminSubscribePacket(type, frequency)


packet_dict: dict[PacketType, Packet] = {
    PacketType.SERVER_ERROR: ErrorPacket,
    PacketType.ADMIN_JOIN: AdminJoinPacket,
    PacketType.SERVER_PROTOCOL: ProtocolPacket,
    PacketType.SERVER_WELCOME: WelcomePacket,
    PacketType.SERVER_NEWGAME: NewGamePacket,
    PacketType.SERVER_SHUTDOWN: ShutdownPacket,
    PacketType.SERVER_DATE: DatePacket,
    PacketType.SERVER_CLIENT_JOIN: ClientJoinPacket,
    PacketType.SERVER_CLIENT_INFO: ClientInfoPacket,
    PacketType.SERVER_CLIENT_UPDATE: ClientUpdatePacket,
    PacketType.SERVER_CLIENT_QUIT: ClientQuitPacket,
    PacketType.SERVER_CLIENT_ERROR: ClientErrorPacket,
    PacketType.SERVER_COMPANY_NEW: CompanyNewPacket,
    PacketType.SERVER_COMPANY_INFO: CompanyInfoPacket,
    PacketType.SERVER_COMPANY_UPDATE: CompanyUpdatePacket,
    PacketType.SERVER_COMPANY_REMOVE: CompanyRemovePacket,
    PacketType.SERVER_COMPANY_ECONOMY: CompanyEconomyPacket,
    PacketType.SERVER_COMPANY_STATS: CompanyStatsPacket,
    PacketType.SERVER_CHAT: ChatPacket,
    PacketType.SERVER_RCON_END: RconEndPacket,
    PacketType.SERVER_RCON: RconPacket,
    PacketType.SERVER_CONSOLE: ConsolePacket,
    PacketType.SERVER_GAMESCRIPT: GameScriptPacket,
    PacketType.SERVER_CMD_NAMES: CmdNamesPacket,
    PacketType.SERVER_CMD_LOGGING: CmdLoggingPacket,
    PacketType.ADMIN_RCON: AdminRconPacket,
    PacketType.ADMIN_CHAT: AdminChatPacket,
    PacketType.FREQUENCY: AdminSubscribePacket
}
