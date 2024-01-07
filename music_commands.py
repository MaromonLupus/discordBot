import os
import asyncio
from collections import deque
import aiohttp

import disnake
from pytube import Playlist
from UI_view import PaginationView

from config import DOWNLOAD_DIRECTORY_MUSIC, SONG_PLAYLIST_NUMBER
import random

song_queues = {}

def get_song_queue(guild_id):
    """
    Retrieves or creates a song queue for the specified guild.
    """
    if guild_id not in song_queues:
        song_queues[guild_id] = deque()
    return song_queues[guild_id]

async def play_next_song(inter):
    """
    Plays the next song in the guild's queue, if available.
    """
    guild_id = inter.guild.id
    song_queue = get_song_queue(guild_id)

    if song_queue and inter.guild.voice_client:
        song_to_play = song_queue.popleft()
        inter.guild.voice_client.play(
            disnake.FFmpegPCMAudio(song_to_play), 
            after=lambda e: after_song_play(e, inter)
        )
        await inter.send(f"Now playing: {os.path.basename(song_to_play)}")

async def ensure_voice_client(inter):
    """
    Ensures that the bot is connected to a voice channel.
    """
    if inter.guild.voice_client is None:
        if inter.author.voice:
            await inter.author.voice.channel.connect()
            return True
        else:
            await inter.send("You are not connected to a voice channel.")
            return False
    return True
async def add_random_songs_to_queue(inter, num_songs):
    """
    Adds a specified number of random songs from the DOWNLOAD_DIRECTORY_MUSIC 
    to the guild's song queue and starts playing if not already playing.
    """
    songs = [os.path.join(DOWNLOAD_DIRECTORY_MUSIC, f) for f in os.listdir(DOWNLOAD_DIRECTORY_MUSIC)
             if os.path.isfile(os.path.join(DOWNLOAD_DIRECTORY_MUSIC, f)) and f.endswith('.mp3')]

    if len(songs) < num_songs:
        await inter.send(f"Not enough songs in the download directory. Found {len(songs)} songs.")
        return
    
    random_songs = random.sample(songs, num_songs)

    song_queue = get_song_queue(inter.guild.id)
    song_queue.extend(random_songs)

    if not inter.guild.voice_client.is_playing():
        await play_next_song(inter)
        
def after_song_play(error, inter):
    """
    Callback function after a song is played.
    """
    if error:
        print(f"An error occurred: {error}")
    asyncio.run_coroutine_threadsafe(play_next_song(inter), inter.bot.loop)

def get_expected_filename(ydl, info):
    """
    Generates the expected filename for a downloaded song.
    """
    filename = ydl.prepare_filename(info)
    base, _ = os.path.splitext(filename)
    return base + '.mp3'

async def give_song(inter, search_query):
    """
    Sends a request to the worker service to download the song.
    """
    worker_url = 'http://localhost:12345/search' 
    payload = {'query': search_query, 'download_directory': DOWNLOAD_DIRECTORY_MUSIC}

    async with aiohttp.ClientSession() as session:
        async with session.post(worker_url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                song_path = data['path']
                song_queue = get_song_queue(inter.guild.id)
                song_queue.append(song_path)

                if not inter.guild.voice_client.is_playing():
                    await play_next_song(inter)
            else:
                error_message = await response.text()
                await inter.send(f"Error downloading song: {error_message}")
def setup(bot):
    """
    Sets up the bot commands.
    """
    @bot.slash_command(description="Play a song or playlist from yt")
    async def play(inter, *, search_query):
        await inter.response.defer()

        if not await ensure_voice_client(inter):
            return

        if not inter.author.voice:
            await inter.send("You need to join a voice channel first.")
            return

        if not os.path.exists(DOWNLOAD_DIRECTORY_MUSIC):
            os.makedirs(DOWNLOAD_DIRECTORY_MUSIC)

        if 'playlist' in search_query or 'list=' in search_query:
            playlist_urls = Playlist(search_query)
            for url in playlist_urls:
                await give_song(inter, url)
        else:
            await give_song(inter, search_query)

        await inter.edit_original_response(content="Songs are going to be added")

    @bot.slash_command(description="Skip this song")
    async def skip(inter):
        if not await ensure_voice_client(inter):
            return

        if inter.guild.voice_client.is_playing():
            inter.guild.voice_client.stop()
            await inter.send("Skipped the current song.")
        else:
            await inter.send("No song is currently playing.")
    @bot.slash_command(description="Shuffles the current playlist for the guild.")
    async def shuffle(inter):
        guild_id = inter.guild.id
        song_queue = get_song_queue(guild_id)

        if len(song_queue) > 1:
            random.shuffle(song_queue)
            await inter.send("Playlist shuffled.")
        else:
            await inter.send("Not enough songs in the queue to shuffle.")
    @bot.slash_command(description="Kick bot from VC")
    async def leave(inter):
        guild_id = inter.guild.id
        song_queue = get_song_queue(guild_id)
        song_queue.clear()

        if inter.guild.voice_client:
            await inter.guild.voice_client.disconnect()
            await inter.send("Disconnected and cleared the queue.")
        else:
            await inter.send("The bot is not connected to a voice channel.")
    @bot.slash_command(description="Pauses the currently playing song.")
    async def pause(inter):
        if inter.guild.voice_client and inter.guild.voice_client.is_playing():
            inter.guild.voice_client.pause()
            await inter.send("Paused the current song.")
        else:
            await inter.send("No song is currently playing.")

    @bot.slash_command(description="Resumes the paused song.")
    async def resume(inter):
        if inter.guild.voice_client and inter.guild.voice_client.is_paused():
            inter.guild.voice_client.resume()
            await inter.send("Resumed the song.")
        else:
            await inter.send("No song is currently paused or playing.")


    @bot.slash_command(description="Play a specified number of random songs from the download directory")
    async def randomplay(inter, number_of_songs: int = 1):
        await inter.response.defer()

        if not await ensure_voice_client(inter):
            return

        if not inter.author.voice:
            await inter.send("You need to join a voice channel first.")
            return

        if number_of_songs < 1:
            await inter.send("Please enter a positive number of songs.")
            return

        await add_random_songs_to_queue(inter, number_of_songs)
        await inter.edit_original_response(content=f"{number_of_songs} random song(s) from the library are now queued to play")

    @bot.slash_command(description="Lists all the songs in the current queue with pagination.")
    async def list_songs(inter):
        guild_id = inter.guild.id
        song_queue = get_song_queue(guild_id)

        if song_queue:
            page_size = SONG_PLAYLIST_NUMBER
            view = PaginationView(list(song_queue), page_size)
            await inter.response.send_message("Use the buttons to navigate through the song list.", view=view)
            await view.update_message(inter)
        else:
            await inter.response.send_message("The song queue is currently empty.")



