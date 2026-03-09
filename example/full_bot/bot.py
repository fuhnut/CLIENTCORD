import os
import sys

# load cc_init before Client
import cc_init 
from clientcord.client import Client

client = Client()

if __name__ == "__main__":
    client.run()
