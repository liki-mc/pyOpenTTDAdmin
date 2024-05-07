from pyopenttdadmin import Admin, AdminUpdateType, openttdpacket

# Set the IP address and port number for connection
ip_address = "127.0.0.1"
port_number = 3977


# Instantiate the Admin class and establish connection to the server
with Admin(ip=ip_address, port=port_number, name="pyOpenTTDAdmin", password="toor") as admin:

    # Subscribe to receive chat updates
    admin.send_subscribe(AdminUpdateType.CHAT)

    # Keep the connection open and print incoming chat messages
    while True:
        # Receive packets from the server
        packets = admin.recv()
        for packet in packets:
            if isinstance(packet, openttdpacket.ChatPacket):
                # Print chat message details
                print(f'ID: {packet.id} Message: {packet.message}')
