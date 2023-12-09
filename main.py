import discord
from discord.ext import commands
import requests
from config import BOT_TOKEN # Import the configuration settings

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Enable the message content intent


bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name='play')
async def play(ctx, *, query: str):
    # Send the query to the worker bot
    response = requests.post("http://localhost:12345/search", data={"query": query})
    song_data = response.text  # This will be the response from the worker bot

    # Respond in Discord
    await ctx.send(f"Got song URL: {song_data}")

bot.run(BOT_TOKEN)
