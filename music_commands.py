import os
import asyncio
from collections import deque
import aiohttp

import disnake
from pytube import Playlist

from config import DOWNLOAD_DIRECTORY
import random

# Global dictionary to hold song queues for different guilds
song_queues = {}

def get_song_queue(guild_id):
    """
    Retrieves or creates a song queue for the specified guild.
    """
    if guild_id not in song_queues:
        song_queues[guild_id] = deque()
    return song_queues[guild_id]

async def play_next_song(ctx):
    """
    Plays the next song in the guild's queue, if available.
    """
    guild_id = ctx.guild.id
    song_queue = get_song_queue(guild_id)

    if song_queue and ctx.voice_client:
        song_to_play = song_queue.popleft()
        ctx.voice_client.play(
            disnake.FFmpegPCMAudio(song_to_play), 
            after=lambda e: after_song_play(e, ctx)
        )
        await ctx.send(f"Now playing: {os.path.basename(song_to_play)}")

async def ensure_voice_client(ctx):
    """
    Ensures that the bot is connected to a voice channel.
    """
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
            return True
        else:
            await ctx.send("You are not connected to a voice channel.")
            return False
    return True

def after_song_play(error, ctx):
    """
    Callback function after a song is played.
    """
    if error:
        print(f"An error occurred: {error}")
    asyncio.run_coroutine_threadsafe(play_next_song(ctx), ctx.bot.loop)

def get_expected_filename(ydl, info):
    """
    Generates the expected filename for a downloaded song.
    """
    filename = ydl.prepare_filename(info)
    base, _ = os.path.splitext(filename)
    return base + '.mp3'

async def give_song(ctx, search_query):
    """
    Sends a request to the worker service to download the song.
    """
    worker_url = 'http://localhost:12345/search' 
    payload = {'query': search_query, 'download_directory': DOWNLOAD_DIRECTORY}

    async with aiohttp.ClientSession() as session:
        async with session.post(worker_url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                song_path = data['path']
                song_queue = get_song_queue(ctx.guild.id)
                song_queue.append(song_path)

                if not ctx.voice_client.is_playing():
                    await play_next_song(ctx)
            else:
                error_message = await response.text()
                await ctx.send(f"Error downloading song: {error_message}")
def setup(bot):
    """
    Sets up the bot commands.
    """
    @bot.command()
    async def play(ctx, *, search_query):
        if not await ensure_voice_client(ctx):
            return

        if not ctx.author.voice:
            await ctx.send("You need to join a voice channel first.")
            return

        if not os.path.exists(DOWNLOAD_DIRECTORY):
            os.makedirs(DOWNLOAD_DIRECTORY)

        if 'playlist' in search_query or 'list=' in search_query:
            playlist_urls = Playlist(search_query)
            for url in playlist_urls:
                await give_song(ctx, url)
        else:
            await give_song(ctx, search_query)

    @bot.command()
    async def skip(ctx):
        if not await ensure_voice_client(ctx):
            return

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Skipped the current song.")
        else:
            await ctx.send("No song is currently playing.")
    @bot.command()
    async def shuffle(ctx):
        """
        Shuffles the current playlist for the guild.
        """
        guild_id = ctx.guild.id
        song_queue = get_song_queue(guild_id)

        if len(song_queue) > 1:
            random.shuffle(song_queue)  # Shuffle the queue
            await ctx.send("Playlist shuffled.")
        else:
            await ctx.send("Not enough songs in the queue to shuffle.")
        @bot.command()
        async def leave(ctx):
            guild_id = ctx.guild.id
            song_queue = get_song_queue(guild_id)
            song_queue.clear()

            if ctx.voice_client:
                await ctx.voice_client.disconnect()
                await ctx.send("Disconnected and cleared the queue.")
            else:
                await ctx.send("The bot is not connected to a voice channel.")
