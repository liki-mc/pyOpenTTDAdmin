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
Example code for an echo bot can be found here:
```python
import os

from pyopenttdadmin import Admin, Actions, ChatDestTypes, AdminUpdateType, openttdpacket

PASSWORD = os.getenv('OPENTTD_ADMIN_PASSWORD')
if PASSWORD is None:
    raise ValueError('OPENTTD_ADMIN_PASSWORD environment variable is not set')


class App(Admin):
    def on_packet(self, packet):
        if isinstance(packet, openttdpacket.ChatPacket):
            print("ChatPacket")
            if packet.action == Actions.CHAT:
                if packet.desttype == ChatDestTypes.BROADCAST:
                    self.send_global(packet.message)

with App(password = PASSWORD) as admin:
    admin.send_subscribe(AdminUpdateType.CHAT)
    admin.run()
```

## Contributing

Contributions to pyOpenTTDAdmin are welcome! If you find any issues or have ideas for improvements, feel free to open an issue or submit a pull request on GitHub.
