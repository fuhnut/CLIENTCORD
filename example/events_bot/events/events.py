from clientcord.declare import event
from cc_init import client

@event("READY")
async def on_ready(payload):
    print("bot connected!")
    await client.sync_commands()

@event("MESSAGE_CREATE")
async def on_message(payload):
    if payload.get("content") == "ping":
        await client.http.send_message(payload["channel_id"], "pong!")
