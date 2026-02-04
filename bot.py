import discord

from main import print_task

TOKEN_DISCORD= env...
API_TOKEN = TOKEN_DISCORD


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.name == "tasks":
        # sent text to receipt printer 
        print_task(message.content, "LOW")
        # TODO discord-react to message with green checkmark when done

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(API_TOKEN)
