# pyOpenTTDAdmin

pyOpenTTDAdmin is a Python library designed to facilitate communication with OpenTTD's Admin port. OpenTTD (Open Transport Tycoon Deluxe) is an open-source simulation game where players manage a transport company.

This library enables developers to interact with an OpenTTD server programmatically, allowing them to perform various administrative tasks and receive real-time updates from the game server.

## Features

- **Authentication**: Authenticate with an OpenTTD server using the provided password.
- **Packet Handling**: Receive and parse packets from the server, allowing developers to react to different events and messages.
- **Sending Commands**: Send commands to the OpenTTD server, such as chat messages, remote console commands, and more.
- **Subscription to Updates**: Subscribe to various types of updates from the server, including chat messages, client information, company data, and more.
- **Flexible Usage**: The library provides a flexible framework for building custom applications that interact with OpenTTD servers.


## Usage
The basic usage of pyOpenTTDAdmin involves creating an instance of the `Admin` class, subscribing to updates from the server, and handling the received packets.

Example code for an echo bot can be found here:
```python
from pyopenttdadmin import Admin, AdminUpdateType, openttdpacket

# Set the IP address and port number for connection
ip_address = "127.0.0.1"
port_number = 3977

# Instantiate the Admin class and establish connection to the server
admin = Admin(ip = ip_address, port = port_number)
admin.login("pyOpenTTDAdmin", password = "toor") # assuming the password is "toor"

# Subscribe to receive chat updates
admin.subscribe(AdminUpdateType.CHAT)

# Print chat packets
@admin.add_handler(openttdpacket.ChatPacket)
def chat_packet(admin: Admin, packet: openttdpacket.ChatPacket):
    print(f'ID: {packet.id} Message: {packet.message}')

# Echo chat
@admin.add_handler(openttdpacket.ChatPacket)
def echo_chat(admin: Admin, packet: openttdpacket.ChatPacket):
    admin.send_global(packet.message)

# Run admin
admin.run()
```

pyOpenTTDAdmin also support async/await syntax:
```python
import asyncio
from aiopyopenttdadmin import Admin, AdminUpdateType, openttdpacket

# Set the IP address and port number for connection
ip_address = "127.0.0.1"
port_number = 3977

async def main():
    # Instantiate the Admin class and establish connection to the server
    admin = Admin(ip = ip_address, port = port_number)
    await admin.login("pyOpenTTDAdmin", password = "toor") # assuming the password is "toor"

    # Subscribe to receive chat updates
    await admin.subscribe(AdminUpdateType.CHAT)

    # Print chat packets
    @admin.add_handler(openttdpacket.ChatPacket)
    async def chat_packet(admin: Admin, packet: openttdpacket.ChatPacket):
        print(f'ID: {packet.id} Message: {packet.message}')

    # Echo chat
    @admin.add_handler(openttdpacket.ChatPacket)
    async def echo_chat(admin: Admin, packet: openttdpacket.ChatPacket):
        await admin.send_global(packet.message)

    # Run admin
    print("running")
    await admin.run()


if __name__ == "__main__":
    asyncio.run(main())
```

## Available Subscribe Types and Packet Types

The following are the available subscribe types that can be used with the library:

- DATE: Updates about the date of the game.
- CLIENT_INFO: Updates about the information of clients.
- COMPANY_INFO: Updates about the generic information of companies.
- COMPANY_ECONOMY: Updates about the economy of companies.
- COMPANY_STATS: Updates about the statistics of companies.
- CHAT: The admin would like to have chat messages.
- CONSOLE: The admin would like to have console messages.
- CMD_NAMES: The admin would like a list of all DoCommand names.
- CMD_LOGGING: The admin would like to have DoCommand information.
- GAMESCRIPT: The admin would like to have gamescript messages.

Here you find a list of all the packets that can be received from the server:

- Errorpacket: The server tells the admin an error has occurred.
- AdminJoinPacket: The admin announces and authenticates itself to the server.
- ProtocolPacket: The server tells the admin its protocol version.
- WelcomePacket: The server welcomes the admin to a game.
- NewGamePacket: The server tells the admin its going to start a new game.
- ShutdownPacket: The server tells the admin its shutting down.
- DatePacket: The server tells the admin what the current game date is.
- ClientJoinPacket: The server tells the admin that a client has joined.
- ClientInfoPacket: The server gives the admin information about a client.
- ClientUpdatePacket: The server gives the admin an information update on a client.
- ClientQuitPacket: The server tells the admin that a client quit.
- ClientErrorPacket: The server tells the admin that a client caused an error.
- CompanyNewPacket: The server tells the admin that a new company has started.
- CompanyInfoPacket: The server gives the admin information about a company.
- CompanyUpdatePacket: The server gives the admin an information update on a company.
- CompanyRemovePacket: The server tells the admin that a company has been removed.
- CompanyEconomyPacket: The server gives the admin some economy related company information.
- CompanyStatsPacket: The server gives the admin some statistics about a company.
- ChatPacket: The server received a chat message and relays it.
- RconEndPacket: The server indicates that the remote console command has completed.
- RconPacket: The server's reply to a remote console command.
- ConsolePacket: The server gives the admin the data that got printed to its console.
- GamescriptPacket: The server gives the admin information from the GameScript in JSON.
- CmdNamesPacket: The server sends out the names of the DoCommands to the admins.
- CmdLoggingPacket: The server gives the admin copies of incoming command packets.
- AdminRconPacket: The admin sends a remote console command.
- AdminChatPacket: The admin sends a chat message to be distributed.
- AdminSubscribePacket: The admin tells the server the update frequency of a particular piece of information.

## Contributing

Contributions to pyOpenTTDAdmin are welcome! If you find any issues or have ideas for improvements, feel free to open an issue or submit a pull request on GitHub.
