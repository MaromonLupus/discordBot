from aiohttp import web
import yt_dlp


async def search_song(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'default_search': 'auto',
        'extract_flat': 'in_playlist'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            if info and 'entries' in info and len(info['entries']) > 0:
                video_info = info['entries'][0]
                return video_info['webpage_url']
            else:
                return "No results found."
        except Exception as e:
            return f"Error occurred: {str(e)}"


# Function to process a YouTube URL (video, playlist, or YouTube Music)
async def process_youtube_url(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'extract_flat': 'in_playlist'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:  # If it's a playlist
                # Extract information about each entry in the playlist
                entries_info = [entry['webpage_url'] for entry in info['entries']]
                return entries_info
            else:  # It's a single video
                return [info['webpage_url']]
        except Exception as e:
            return [f"Error occurred: {str(e)}"]


async def handle_search(request):
    data = await request.post()
    query = data['query']

    # Check if the query is a YouTube URL
    if "youtube.com" in query or "youtu.be" in query or "music.youtube.com" in query:
        result = await process_youtube_url(query)
    else:  # If it's not a URL, perform a search
        result = await search_song(query)

    # Return the song data or playlist
    return web.Response(text=str(result))

app = web.Application()
app.add_routes([web.post('/search', handle_search)])

web.run_app(app, port=12345)
