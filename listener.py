
# IMPORTS


# time is used to record when our application started.
# This helps us ignore old/history-sync messages.
import time

# MessageEv runs whenever Neonize sends us a message event.
from neonize.events import MessageEv

# Import the ONE shared WhatsApp client.
from .session import client

# Import our downloader.
from .downloader import download_image



# APPLICATION START TIME


# Save the time when this listener starts.
#
# WhatsApp timestamps from Neonize are in milliseconds.
APP_START_TIME = int(time.time() * 1000)



# PROCESSED MESSAGE IDS


# Sometimes WhatsApp/Neonize may send the same event again.
#
# We store IDs here so the same image is not processed twice.
processed_message_ids = set()



# MESSAGE LISTENER


@client.event(MessageEv)
def on_message(client, message_event):

    # Get the actual message.
    message = message_event.Message

    # Get information about sender/chat/message.
    info = message_event.Info


    
    # IGNORE OLD / HISTORY MESSAGES
    

    # During WhatsApp synchronization,
    # Neonize may provide older messages.
    #
    # We only want messages received after
    # our application started.
    if info.Timestamp < APP_START_TIME:

        return


    
    # IGNORE OUR OWN MESSAGES
    

    # If the connected company WhatsApp itself
    # sent the message, ignore it.
    if info.MessageSource.IsFromMe:

        return


    
    # IGNORE WHATSAPP STATUS
    

    # WhatsApp Status uses:
    #
    # status@broadcast
    #
    # We don't want status images.
    chat_user = info.MessageSource.Chat.User
    chat_server = info.MessageSource.Chat.Server

    if (
        chat_user == "status"
        or chat_server == "broadcast"
    ):

        return


    
    # IGNORE DUPLICATE EVENTS
    

    # Every WhatsApp message has an ID.
    message_id = info.ID


    # If we already processed this message,
    # ignore it.
    if message_id in processed_message_ids:

        return


    
    # ONLY PROCESS IMAGES
    

    # Ignore:
    #
    # text
    # video
    # audio
    # documents
    #
    # Our project currently wants images only.
    if not message.HasField("imageMessage"):

        return


    
    # MARK MESSAGE AS PROCESSED
    

    processed_message_ids.add(
        message_id
    )


    
    # IMAGE RECEIVED
    

    print("\nNEW CUSTOMER IMAGE RECEIVED")


    # Send the image to downloader.py.
    download_image(
        client,
        message_event
    )