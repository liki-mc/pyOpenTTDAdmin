from pyopenttdadmin import Admin, AdminUpdateType, openttdpacket

# Set the IP address and port number for connection
ip_address = "127.0.0.1"
port_number = 3977


# Instantiate the Admin class and establish connection to the server
admin = Admin(ip = ip_address, port = port_number)
admin.login("pyOpenTTDAdmin", "toor")

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