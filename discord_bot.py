import disnake
from disnake.ext import commands, tasks

from config import BOT_TOKEN  # Import the configuration settings
import music_commands
import open_ai_commands

# Define intents for the bot
intents = disnake.Intents.default()
intents.message_content = True  # Enable message content intent for prefix commands

# Define the bot instance with command prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents)

@tasks.loop(minutes=800)
async def check_inactivity():
    """
    Periodically checks for inactivity in voice channels and disconnects if appropriate.
    """
    for vc in bot.voice_clients:
        if not vc.is_playing() and not vc.is_paused():
            # Disconnect the bot if it's alone in the voice channel
            if len(vc.channel.members) == 1:
                await vc.disconnect()

@check_inactivity.before_loop
async def before_check_inactivity():
    """
    Prepares the bot before starting the inactivity check loop.
    """
    await bot.wait_until_ready()

@bot.event
async def on_ready():
    """
    Event handler for when the bot is ready.
    """
    print(f'We have logged in as {bot.user}')

# Setup the commands with the bot instance
music_commands.setup(bot)
open_ai_commands.setup(bot)
# Start the inactivity check loop
check_inactivity.start()

# Run the bot with the provided token
bot.run(BOT_TOKEN)
