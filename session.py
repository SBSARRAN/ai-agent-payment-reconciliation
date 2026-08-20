# Import Neonize client
from neonize.client import NewClient


# Create ONE shared WhatsApp client.
#
# Every other file will import this exact same object.
client = NewClient("payment-reconciliation")