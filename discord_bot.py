import disnake
from disnake.ext import commands, tasks

from config import BOT_TOKEN
import music_commands
import open_ai_commands

intents = disnake.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@tasks.loop(minutes=800)
async def check_inactivity():
    """
    Periodically checks for inactivity in voice channels and disconnects if appropriate.
    """
    for vc in bot.voice_clients:
        if not vc.is_playing() and not vc.is_paused():
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

music_commands.setup(bot)
open_ai_commands.setup(bot)

check_inactivity.start()

bot.run(BOT_TOKEN)
