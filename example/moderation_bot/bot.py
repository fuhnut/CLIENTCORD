from clientcord import Client

client = Client(
    token="YOUR_BOT_TOKEN_HERE",
    commands="/commands"
)

if __name__ == "__main__":
    client.run()
