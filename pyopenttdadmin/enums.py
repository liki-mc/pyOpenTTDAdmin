from enum import Enum

class PacketType(Enum):
    """Packet types."""
    ADMIN_JOIN = 0x00             # The admin announces and authenticates itself to the server.
    ADMIN_QUIT = 0x01             # The admin tells the server that it is quitting.
    FREQUENCY = 0x02              # The admin tells the server the update frequency of a particular piece of information.
    ADMIN_POLL = 0x03             # The admin explicitly polls for a piece of information.
    ADMIN_CHAT = 0x04             # The admin sends a chat message to be distributed.
    ADMIN_RCON = 0x05             # The admin sends a remote console command.
    ADMIN_GAMESCRIPT = 0x06       # The admin sends a JSON string for the GameScript.
    ADMIN_PING = 0x07             # The admin sends a ping to the server, expecting a ping-reply (PONG) packet.
    ADMIN_EXTERNAL_CHAT = 0x08    # The admin sends a chat message from external source.

    SERVER_FULL = 0x64            # The server tells the admin it cannot accept the admin.
    SERVER_BANNED = 0x65          # The server tells the admin it is banned.
    SERVER_ERROR = 0x66           # The server tells the admin an error has occurred.
    SERVER_PROTOCOL = 0x67        # The server tells the admin its protocol version.
    SERVER_WELCOME = 0x68         # The server welcomes the admin to a game.
    SERVER_NEWGAME = 0x69         # The server tells the admin its going to start a new game.
    SERVER_SHUTDOWN = 0x6A        # The server tells the admin its shutting down.

    SERVER_DATE = 0x6B            # The server tells the admin what the current game date is.
    SERVER_CLIENT_JOIN = 0x6C     # The server tells the admin that a client has joined.
    SERVER_CLIENT_INFO = 0x6D     # The server gives the admin information about a client.
    SERVER_CLIENT_UPDATE = 0x6E   # The server gives the admin an information update on a client.
    SERVER_CLIENT_QUIT = 0x6F     # The server tells the admin that a client quit.
    SERVER_CLIENT_ERROR = 0x70    # The server tells the admin that a client caused an error.
    SERVER_COMPANY_NEW = 0x71     # The server tells the admin that a new company has started.
    SERVER_COMPANY_INFO = 0x72    # The server gives the admin information about a company.
    SERVER_COMPANY_UPDATE = 0x73  # The server gives the admin an information update on a company.
    SERVER_COMPANY_REMOVE = 0x74  # The server
    SERVER_COMPANY_ECONOMY = 0x75 # The server gives the admin some economy related company information.
    SERVER_COMPANY_STATS = 0x76   # The server gives the admin some statistics about a company.
    SERVER_CHAT = 0x77            # The server received a chat message and relays it.
    SERVER_RCON = 0x78            # The server's reply to a remove console command.
    SERVER_CONSOLE = 0x79         # The server gives the admin the data that got printed to its console.
    SERVER_CMD_NAMES = 0x7A       # The server sends out the names of the DoCommands to the admins.
    SERVER_CMD_LOGGING_OLD = 0x7B # Used to be the type ID of \c SERVER_CMD_LOGGING in \c NETWORK_GAME_ADMIN_VERSION 1.
    SERVER_GAMESCRIPT = 0x7C      # The server gives the admin information from the GameScript in JSON.
    SERVER_RCON_END = 0x7D        # The server indicates that the remote console command has completed.
    SERVER_PONG = 0x7E            # The server replies to a ping request from the admin.
    SERVER_CMD_LOGGING = 0x7F     # The server gives the admin copies of incoming command packets.
    
    INVALID_ADMIN_PACKET = 0xFF   # An invalid marker for admin packets.

class Actions(Enum):
    JOIN = 0x00
    LEAVE = 0x01
    SERVER_MESSAGE = 0x02
    CHAT = 0x03
    CHAT_COMPANY = 0x04
    CHAT_CLIENT = 0x05
    GIVE_MONEY = 0x06
    NAME_CHANGE = 0x07
    COMPANY_SPECTATOR = 0x08
    COMPANY_JOIN = 0x09
    COMPANY_NEW = 0x0A

class AdminCompanyRemoveReason(Enum):
    """Reasons for removing a company - communicated to admins"""
    ADMIN_CRR_MANUAL = 0x00    # The company is manually removed.
    ADMIN_CRR_AUTOCLEAN = 0x01 # The company is removed due to autoclean.
    ADMIN_CRR_BANKRUPT = 0x02  # The company went belly-up.
    
    ADMIN_CRR_END = 0x03       # Sentinel for end.

class AdminStatus(Enum):
    """Status of an admin."""
    INACTIVE = 0x00 # The admin is not connected nor active.
    ACTIVE = 0x01   # The admin is active.
    END = 0x02      # Must ALWAYS be on the end of this list!! (period)

class AdminUpdateFrequency(Enum):
    """Update frequencies an admin can register."""
    POLL = 0x01      # The admin can poll this.
    DAILY = 0x02     # The admin gets information about this on a daily basis.
    WEEKLY = 0x04    # The admin gets information about this on a weekly basis.
    MONTHLY = 0x08   # The admin gets information about this on a monthly basis.
    QUARTERLY = 0x10 # The admin gets information about this on a quarterly basis.
    ANUALLY = 0x20   # The admin gets information about this on a yearly basis.
    AUTOMATIC = 0x40 # The admin gets information about this when it changes.

class AdminUpdateType(Enum):
    """Update types an admin can register a frequency for."""
    DATE = 0x00            # Updates about the date of the game.
    CLIENT_INFO = 0x01     # Updates about the information of clients.
    COMPANY_INFO = 0x02    # Updates about the generic information of companies.
    COMPANY_ECONOMY = 0x03 # Updates about the economy of companies.
    COMPANY_STATS = 0x04   # Updates about the statistics of companies.
    CHAT = 0x05            # The admin would like to have chat messages.
    CONSOLE = 0x06         # The admin would like to have console messages.
    CMD_NAMES = 0x07       # The admin would like a list of all DoCommand names.
    CMD_LOGGING = 0x08     # The admin would like to have DoCommand information.
    GAMESCRIPT = 0x09      # The admin would like to have gamescript messages.
    END = 0x0A             # Must ALWAYS be on the end of this list!! (period)

class ChatDestTypes(Enum):
    BROADCAST = 0x00
    TEAM = 0x01
    CLIENT = 0x02

class Color(Enum):
    DARK_BLUE = 0x00
    PALE_GREEN = 0x01
    PINK = 0x02
    YELLOW = 0x03
    RED = 0x04
    LIGHT_BLUE = 0x05
    GREEN = 0x06
    DARK_GREEN = 0x07
    BLUE = 0x08
    CREAM = 0x09
    MAUVE = 0x0A
    PURPLE = 0x0B
    ORANGE = 0x0C
    BROWN = 0x0D
    GREY = 0x0E
    WHITE = 0x0F

class Landscape(Enum):
    TEMPERATE = 0x00
    SUB_ARCTIC = 0x01
    SUB_TROPICAL = 0x02
    TOYLAND = 0x03

class NetWorkErrorCodes(Enum):
    NETWORK_ERROR_GENERAL = 0x00 # Try to use this one like never

	# Signals from clients 
    NETWORK_ERROR_DESYNC = 0x01
    NETWORK_ERROR_SAVEGAME_FAILED = 0x02
    NETWORK_ERROR_CONNECTION_LOST = 0x03
    NETWORK_ERROR_ILLEGAL_PACKET = 0x04
    
    # Signals from servers
    NETWORK_ERROR_NOT_AUTHORIZED = 0x05
    NETWORK_ERROR_NOT_EXPECTED = 0x06
    NETWORK_ERROR_WRONG_REVISION = 0x07
    NETWORK_ERROR_NAME_IN_USE = 0x08
    NETWORK_ERROR_WRONG_PASSWORD = 0x09
    NETWORK_ERROR_COMPANY_MISMATCH = 0x0A # Happens in CLIENT_COMMAND
    NETWORK_ERROR_KICKED = 0x0B
    NETWORK_ERROR_CHEATER = 0x0C
    NETWORK_ERROR_FULL = 0x0D
    NETWORK_ERROR_TOO_MANY_COMMANDS = 0x0E
    NETWORK_ERROR_TIMEOUT_PASSWORD = 0x0F
    NETWORK_ERROR_TIMEOUT_COMPUTER = 0x10
    NETWORK_ERROR_TIMEOUT_MAP = 0x11
    NETWORK_ERROR_TIMEOUT_JOIN = 0x12
    NETWORK_ERROR_INVALID_CLIENT_NAME = 0x13
    NETWORK_ERROR_NOT_ON_ALLOW_LIST = 0x14
    
    NETWORK_ERROR_END = 0x15

class NetworkVehicleType(Enum):
    NETWORK_VEH_TRAIN = 0
    NETWORK_VEH_LORRY = 1
    NETWORK_VEH_BUS = 2
    NETWORK_VEH_PLANE = 3
    NETWORK_VEH_SHIP = 4

    NETWORK_VEH_END = 5

AdminUpdateTypeFrequencyMatrix: dict[AdminUpdateType, list[AdminUpdateFrequency]] = {
    AdminUpdateType.DATE : [AdminUpdateFrequency.POLL , AdminUpdateFrequency.DAILY , AdminUpdateFrequency.WEEKLY , AdminUpdateFrequency.MONTHLY , AdminUpdateFrequency.QUARTERLY , AdminUpdateFrequency.ANUALLY],
    AdminUpdateType.CLIENT_INFO : [AdminUpdateFrequency.POLL , AdminUpdateFrequency.AUTOMATIC],
    AdminUpdateType.COMPANY_INFO : [AdminUpdateFrequency.POLL , AdminUpdateFrequency.AUTOMATIC],
    AdminUpdateType.COMPANY_ECONOMY : [AdminUpdateFrequency.POLL , AdminUpdateFrequency.WEEKLY , AdminUpdateFrequency.MONTHLY , AdminUpdateFrequency.QUARTERLY , AdminUpdateFrequency.ANUALLY],
    AdminUpdateType.COMPANY_STATS : [AdminUpdateFrequency.POLL , AdminUpdateFrequency.WEEKLY , AdminUpdateFrequency.MONTHLY , AdminUpdateFrequency.QUARTERLY , AdminUpdateFrequency.ANUALLY],
    AdminUpdateType.CHAT : [AdminUpdateFrequency.AUTOMATIC],
    AdminUpdateType.CONSOLE : [AdminUpdateFrequency.AUTOMATIC],
    AdminUpdateType.CMD_NAMES : [AdminUpdateFrequency.POLL],
    AdminUpdateType.CMD_LOGGING : [AdminUpdateFrequency.AUTOMATIC],
    AdminUpdateType.GAMESCRIPT : [AdminUpdateFrequency.AUTOMATIC],
}