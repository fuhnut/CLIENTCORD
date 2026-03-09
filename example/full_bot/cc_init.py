import os
import sys

# Ensure clientcord can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from clientcord.intents import Intents

token = "PLACE_HOLDER"
intents = Intents.all()
prefix = "!" # Prefix used for the hybrid and prefix commands
commands = "commands"
events = "events"
components = "components"
