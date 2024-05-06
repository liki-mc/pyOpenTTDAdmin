from src.main import Admin
from src.enums import AdminUpdateType, AdminUpdateFrequency
from src.packet import DatePacket

# Set the IP address and port number for connection
ip_address = "127.0.0.1"
port_number = 3977

# Instantiate the Admin class and establish connection to the server
with Admin(ip=ip_address, port=port_number, name="pyOpenTTDAdmin", password="toor") as admin:

    # Subscribe to receive date updates and set the frequency for updates
    admin.send_subscribe(AdminUpdateType.DATE, AdminUpdateFrequency.DAILY)
    # Admins can choose different frequencies:
    # admin.send_subscribe(AdminUpdateType.DATE, AdminUpdateFrequency.WEEKLY)
    # admin.send_subscribe(AdminUpdateType.DATE, AdminUpdateFrequency.ANUALLY)
    # admin.send_subscribe(AdminUpdateType.DATE, AdminUpdateFrequency.MONTHLY)

    # Keep the connection open and print incoming date packets
    while True:
        # Receive packets from the server
        packets = admin.recv()
        for packet in packets:
            if isinstance(packet, DatePacket):
                # Print date packet details
                print(packet)
