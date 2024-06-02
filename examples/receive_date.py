from pyopenttdadmin import Admin, AdminUpdateType, AdminUpdateFrequency, openttdpacket

# Set the IP address and port number for connection
ip_address = "127.0.0.1"
port_number = 3977

# Instantiate the Admin class and establish connection to the server
admin = Admin(ip = ip_address, port = port_number)
admin.login(name = "pyOpenTTDAdmin", password = "toor")

# Subscribe to receive date updates and set the frequency for updates
admin.subscribe(AdminUpdateType.DATE, AdminUpdateFrequency.DAILY)
# Admins can choose different frequencies:
# admin.send_subscribe(AdminUpdateType.DATE, AdminUpdateFrequency.WEEKLY)
# admin.send_subscribe(AdminUpdateType.DATE, AdminUpdateFrequency.ANUALLY)
# admin.send_subscribe(AdminUpdateType.DATE, AdminUpdateFrequency.MONTHLY)

# Print date packets
@admin.add_handler(openttdpacket.DatePacket)
def date_packet(admin: Admin, packet: openttdpacket.DatePacket):
    print(packet)

# Keep the connection open and print incoming date packets
admin.run()
