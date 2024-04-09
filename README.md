# pyOpenTTDAdmin
Python library to communicate with OpenTTD Admin port

## Usage
Example code for an echo bot can be found here:
```python
import os

from src.main import Admin
from src.packet import ChatPacket
from src.enums import Actions, ChatDestTypes, AdminUpdateType

PASSWORD = os.getenv('OPENTTD_ADMIN_PASSWORD')
if PASSWORD is None:
    raise ValueError('OPENTTD_ADMIN_PASSWORD environment variable is not set')


class App(Admin):
    def on_packet(self, packet):
        if isinstance(packet, ChatPacket):
            print("ChatPacket")
            if packet.action == Actions.CHAT:
                if packet.desttype == ChatDestTypes.BROADCAST:
                    self.send_global(packet.message)

with App(password = PASSWORD) as admin:
    admin.send_subscribe(AdminUpdateType.CHAT)
    admin.run()
```

I am very sorry I got lazy and didn't write a proper package, nor a proper README.md  
Please make an issue if you want me to continue this project.
