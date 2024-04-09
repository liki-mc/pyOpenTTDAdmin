from .enums import *

# reference: https://github.com/OpenTTD/OpenTTD/blob/master/src/network/network_admin.cpp

class Packet:
    def __init__(self, data: bytes):
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

class ErrorPacket(Packet):
    def __init__(self, data: bytes):
        self.error = NetWorkErrorCodes(data[1])
    
    def __repr__(self) -> str:
        return f"ErrorPacket({self.error})"
        
class AdminJoinPacket(Packet):
    def __init__(self, data: bytes):
        pass

class ProtocolPacket(Packet):
    def __init__(self, data: bytes):
        self.version = data[1]
        self.subscriptions: dict[AdminUpdateType, AdminUpdateFrequency | None] = {}
        for i in range(2, len(data) - 1, 5):
            b = bool(data[i])
            if not b:
                continue
            
            update_type = AdminUpdateType(int.from_bytes(data[i + 1: i + 3], 'little'))
            try:
                frequency_type = AdminUpdateFrequency(int.from_bytes(data[i + 3: i + 5], 'little'))
            except ValueError:
                frequency_type = None
            
            self.subscriptions[update_type] = frequency_type
    
    def __repr__(self) -> str:
        subs = "\n    ".join([f"{k}: {v}" for k, v in self.subscriptions.items()])
        return f"ProtocolPacket({self.version}, subs = (\n{subs}\n))"

class WelcomePacket(Packet):
    def __init__(self, data: bytes):
        server_name, _, data = data[1:].partition(b'\x00')
        version, _, data = data.partition(b'\x00')
        self.dedicated = bool(data[0])
        map_name, _, data = data[1:].partition(b'\x00')
        
        self.server_name = server_name.decode('utf-8')
        self.version = version.decode('utf-8')
        self.map_name = map_name.decode('utf-8')
        
        self.seed = int.from_bytes(data[:4], 'little')
        self.landscape = data[4]
        self.startdate = int.from_bytes(data[5:9], 'little')
        self.mapheight = int.from_bytes(data[9:11], 'little')
        self.mapwidth = int.from_bytes(data[11: 13], 'little')
        
    def __repr__(self) -> str:
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

class NewGamePacket(Packet):
    def __init__(self, data: bytes):
        pass
    
    def __repr__(self) -> str:
        return f"NewGamePacket()"

class ShutdownPacket(Packet):
    def __init__(self, data: bytes):
        pass
    
    def __repr__(self) -> str:
        return f"ShutdownPacket()"

class DatePacket(Packet):
    def __init__(self, data: bytes):
        self.date = int.from_bytes(data[1:5], 'little')
    
    def __repr__(self) -> str:
        return f"DatePacket({self.date})"

class ClientJoinPacket(Packet):
    def __init__(self, data: bytes):
        self.id = int.from_bytes(data[1:5], 'little')
    
    def __repr__(self) -> str:
        return f"ClientJoinPacket({self.id})"

class ClientInfoPacket(Packet):
    def __init__(self, data: bytes):
        self.id = int.from_bytes(data[1:5], 'little')
        ip, _, data = data[5:].partition(b'\x00')
        name, _, data = data.partition(b'\x00')
        
        self.ip = ip.decode('utf-8')
        self.name = name.decode('utf-8')
        
        self.lang = data[0]
        self.joined = int.from_bytes(data[1:5], 'little')
        self.company_id = data[5]
    
    def __repr__(self) -> str:
        return f"ClientInfoPacket({self.id}, {self.ip}, {self.name}, {self.lang}, {self.joined}, {self.company_id})"
    
class ClientUpdatePacket(Packet):
    def __init__(self, data: bytes):
        self.id = int.from_bytes(data[1:5], 'little')
        name, _, data = data[5:].partition(b'\x00')
        self.company_id = data[0]
        
        self.name = name.decode('utf-8')
    
    def __repr__(self) -> str:
        return f"ClientUpdatePacket({self.id}, {self.name}, {self.company_id})"

class ClientQuitPacket(Packet):
    def __init__(self, data: bytes):
        self.id = int.from_bytes(data[1:5], 'little')
    
    def __repr__(self) -> str:
        return f"ClientQuitPacket({self.id})"

class ClientErrorPacket(Packet):
    def __init__(self, data: bytes):
        self.id = int.from_bytes(data[1:5], 'little')
        self.error = NetWorkErrorCodes(data[5])
    
    def __repr__(self) -> str:
        return f"ClientErrorPacket({self.id}, {self.error})"

class CompanyNewPacket(Packet):
    def __init__(self, data: bytes):
        self.id = data[1]
    
    def __repr__(self) -> str:
        return f"CompanyNewPacket({self.id})"

class CompanyInfoPacket(Packet):
    def __init__(self, data: bytes):
        self.id = data[1]
        name, _, data = data[2:].partition(b'\x00')
        manager_name, _, data = data.partition(b'\x00')
        
        self.name = name.decode('utf-8')
        self.manager_name = manager_name.decode('utf-8')
        
        self.color = data[0]
        self.passworded = bool(data[1])
        self.year = int.from_bytes(data[2:6], 'little')
        self.is_ai = bool(data[6])
        self.quarters_to_bankruptcy = data[7]
    
    def __repr__(self) -> str:
        return f"CompanyInfoPacket({self.id}, {self.name}, {self.manager_name}, {self.color}, {self.passworded}, {self.year}, {self.is_ai}, {self.quarters_to_bankruptcy})"

class CompanyUpdatePacket(Packet):
    def __init__(self, data: bytes):
        self.id = data[1]
        name, _, data = data[2:].partition(b'\x00')
        manager_name, _, data = data.partition(b'\x00')
        
        self.name = name.decode('utf-8')
        self.manager_name = manager_name.decode('utf-8')
        
        self.color = data[0]
        self.passworded = bool(data[1])
        self.quarters_to_bankruptcy = data[7]
    
    def __repr__(self) -> str:
        return f"CompanyUpdatePacket({self.id}, {self.name}, {self.manager_name}, {self.color}, {self.passworded}, {self.quarters_to_bankruptcy})"

class CompanyRemovePacket(Packet):
    def __init__(self, data: bytes):
        self.id = data[1]
        self.admin_remove_reason = data[2]
    
    def __repr__(self) -> str:
        return f"CompanyRemovePacket({self.id}, {self.admin_remove_reason})"

class CompanyEconomyPacket(Packet):
    def __init__(self, data: bytes):
        self.id = data[1]
        self.money = int.from_bytes(data[2:10], 'little')
        self.current_loan = int.from_bytes(data[10:18], 'little')
        self.delivered_cargo = int.from_bytes(data[18:20], 'little')
        data = data[20:]
        self.quarterly_info = []
        
        for i in range(2):
            company_value = int.from_bytes(data[:8], 'little')
            company_performance_history = int.from_bytes(data[8:10], 'little')
            delivered_cargo = int.from_bytes(data[10:12], 'little')
            self.quarterly_info.append((company_value, company_performance_history, delivered_cargo))
            data = data[12:]
    
    def __repr__(self) -> str:
        return f"CompanyEconomyPacket({self.id}, {self.money}, {self.current_loan}, {self.delivered_cargo})"

class CompanyStatsPacket(Packet):
    def __init__(self, data: bytes):
        self.id = data[1]
        self.num_vehicles: dict[NetworkVehicleType, int] = {}
        for i in range(NetworkVehicleType.NETWORK_VEH_END.value):
            self.num_vehicles[NetworkVehicleType(i)] = int.from_bytes(data[2 + i * 2: 4 + i * 2], 'little')
        
    def __repr__(self) -> str:
        vehicles = "\n    ".join([f"{k}: {v}" for k, v in self.num_vehicles.items()])
        return f"CompanyStatsPacket({self.id}, {vehicles})"

class ChatPacket(Packet):
    def __init__(self, data: bytes):
        self.money = None
        self.action = Actions(data[1])
        self.desttype = ChatDestTypes(data[2])
        self.id = int.from_bytes(data[3: 7], 'little')
        self.message = data[7: -9].decode('utf-8') # -9 is 8 for money + 1 to indicate end of string
        self.money = int.from_bytes(data[-8:], 'little')
    
    def __repr__(self) -> str:
        return f"ChatPacket{self.action.value, self.desttype.value, self.id, self.message, self.money}"

class RconEndPacket(Packet):
    def __init__(self, data: bytes):
        command, *_ = data[1:].partition(b'\x00')
        
        self.command = command.decode('utf-8')
    
    def __repr__(self) -> str:
        return f"RconEndPacket({self.command})"
   
class RconPacket(Packet):
    def __init__(self, data: bytes):
        self.color = int.from_bytes(data[1:3], 'little')
        response, *_ = data[3:].partition(b'\x00')
        
        self.response = response.decode('utf-8')
    
    def __repr__(self) -> str:
        return f"RconPacket({self.color}, {self.response})"

class ConsolePacket(Packet):
    def __init__(self, data: bytes):
        origin, _, data = data[1:].partition(b'\x00')
        message, *_ = data.partition(b'\x00')
        
        self.origin = origin.decode('utf-8')
        self.message = message.decode('utf-8')

    def __repr__(self) -> str:
        return f"ConsolePacket({self.origin}, {self.message})"

class GameScriptPacket(Packet):
    def __init__(self, data: bytes):
        self.json = data[1:].decode('utf-8')
    
    def __repr__(self) -> str:
        return f"GameScriptPacket({self.json})"

class CmdNamesPacket(Packet):
    def __init__(self, data: bytes):
        self.names = []
        while b'\x00' in data:
            name, _, data = data.partition(b'\x00')
            self.names.append(name.decode('utf-8'))
        
        if data[:-1]:
            self.names.append(data[:-1].decode('utf-8'))
    
    def __repr__(self) -> str:
        return f"CmdNamesPacket({self.names})"

class CmdLoggingPacket(Packet):
    def __init__(self, data: bytes):
        self.client_id = int.from_bytes(data[1:5], 'little')
        self.company_id = data[5]
        self.cmd = int.from_bytes(data[6:8], 'little')
        buffer_length = int.from_bytes(data[8:10], 'little')
        self.data = data[10: 10 + buffer_length]
        self.frame = int.from_bytes(data[10 + buffer_length: 14 + buffer_length], 'little')
    
    def __repr__(self) -> str:
        return f"CmdLoggingPacket({self.client_id}, {self.company_id}, {self.cmd}, {self.data}, {self.frame})"

packet_dict = {
    PacketType.SERVER_ERROR.value: ErrorPacket,
    PacketType.ADMIN_JOIN.value: AdminJoinPacket,
    PacketType.SERVER_PROTOCOL.value: ProtocolPacket,
    PacketType.SERVER_WELCOME.value: WelcomePacket,
    PacketType.SERVER_NEWGAME.value: NewGamePacket,
    PacketType.SERVER_SHUTDOWN.value: ShutdownPacket,
    PacketType.SERVER_DATE.value: DatePacket,
    PacketType.SERVER_CLIENT_JOIN.value: ClientJoinPacket,
    PacketType.SERVER_CLIENT_INFO.value: ClientInfoPacket,
    PacketType.SERVER_CLIENT_UPDATE.value: ClientUpdatePacket,
    PacketType.SERVER_CLIENT_QUIT.value: ClientQuitPacket,
    PacketType.SERVER_CLIENT_ERROR.value: ClientErrorPacket,
    PacketType.SERVER_COMPANY_NEW.value: CompanyNewPacket,
    PacketType.SERVER_COMPANY_INFO.value: CompanyInfoPacket,
    PacketType.SERVER_COMPANY_UPDATE.value: CompanyUpdatePacket,
    PacketType.SERVER_COMPANY_REMOVE.value: CompanyRemovePacket,
    PacketType.SERVER_COMPANY_ECONOMY.value: CompanyEconomyPacket,
    PacketType.SERVER_COMPANY_STATS.value: CompanyStatsPacket,
    PacketType.SERVER_CHAT.value: ChatPacket,
    PacketType.SERVER_RCON_END.value: RconEndPacket,
    PacketType.SERVER_RCON.value: RconPacket,
    PacketType.SERVER_CONSOLE.value: ConsolePacket,
    PacketType.SERVER_GAMESCRIPT.value: GameScriptPacket,
    PacketType.SERVER_CMD_NAMES.value: CmdNamesPacket,
    PacketType.SERVER_CMD_LOGGING.value: CmdLoggingPacket
}

def create_packet(type: int, data: bytes):
    return packet_dict[type](data)