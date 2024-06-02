import asyncio
from aiopyopenttdadmin import Admin, AdminUpdateType, openttdpacket

# Set the IP address and port number for connection
ip_address = "127.0.0.1"
port_number = 3977

async def main():
    # Instantiate the Admin class and establish connection to the server
    admin = Admin(ip = ip_address, port = port_number)
    await admin.login("pyOpenTTDAdmin", "toor")

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