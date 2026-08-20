
# IMPORTS


# ConnectedEv runs when WhatsApp connects.
# event keeps the application running.
from neonize.events import ConnectedEv, event


# Import the ONE shared WhatsApp client.
from .session import client


# Import listener so its MessageEv handler
# gets registered BEFORE we connect to WhatsApp.
from . import listener



# CONNECTION EVENT


@client.event(ConnectedEv)
def on_connected(client, connected_event):

    print("WhatsApp connected successfully!")



# START WHATSAPP


def start_whatsapp():

    print("Starting WhatsApp...")

    # Connect our shared client.
    client.connect()

    # Keep application running.
    event.wait()



# PYTHON MAIN GUARD


if __name__ == "__main__":
    start_whatsapp()