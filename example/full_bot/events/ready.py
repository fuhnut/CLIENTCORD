from clientcord.declare import event
from clientcord.client import Client
from clientcord.logger import info

@event("READY")
async def on_ready(payload: dict, client: Client):
    user = payload.get("user", {})
    info(f"Logged in as {user.get('username')}#{user.get('discriminator')} ({user.get('id')})")
    info("Syncing Application Commands...")
    await client.sync_commands()
    info("Clientcord test complete! Bot is fully operational.")
