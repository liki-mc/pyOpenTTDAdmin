from pyopenttdadmin import Admin, AdminUpdateType, openttdpacket as p, Auth

# Set the IP address and port number for connection
ip_address = "127.0.0.1"
port_number = 3977

# Setup authentification
auth = Auth(
    name = "pyOpenTTDAdmin", # This name shows up in the logs
    version = "15.0",
    password = "toor" # assuming the password is 'toor'
)

# Instantiate the Admin class and establish connection to the server
admin = Admin(ip = ip_address, port = port_number, auth = auth)

# Subscribe to receive chat updates
admin.subscribe(AdminUpdateType.CHAT)

# Print chat packets
@admin.add_handler(p.ChatPacket)
def chat_packet(admin: Admin, packet: p.ChatPacket):
    print(f'ID: {packet.id} Message: {packet.message}')

# Echo chat
@admin.add_handler(p.ChatPacket)
def echo_chat(admin: Admin, packet: p.ChatPacket):
    admin.send_global(packet.message)

# Run admin
admin.run()
