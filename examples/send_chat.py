from pyopenttdadmin import Admin


# Set the IP address and port number for connection
ip_address = "127.0.0.1"
port_number = 3977


# Instantiate the Admin class and establish connection to the server
admin = Admin(ip = ip_address, port = port_number)
admin.login(name = "pyOpenTTDAdmin", password = "toor")

# Send a global message to all players
admin.send_global(message="Hello! I am a Python-powered OpenTTD bot!")

# Send a private message to player with ID 1
admin.send_private(message="This is a private message sent to ID 1", id=1)


