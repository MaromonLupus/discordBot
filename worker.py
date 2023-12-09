from aiohttp import web
import os
import yt_dlp

async def download_song(download_directory, search_query):
    """
    Downloads a song based on the given search query.
    
    Parameters:
    - download_directory: The directory where the song will be downloaded.
    - search_query: The query or URL for the song to be downloaded.

    Returns:
    - The path of the downloaded song file.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(download_directory, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=False)
        video_info = info['entries'][0] if 'entries' in info else info

        filename = ydl.prepare_filename(video_info)
        base, _ = os.path.splitext(filename)
        expected_filename = base + '.mp3'

        if not os.path.exists(expected_filename):
            ydl.download([video_info['webpage_url']])

        return expected_filename

async def search_song(request):
    """
    Web handler to process song search requests.
    """
    try:
        data = await request.json()
        search_query = data.get('query')
        download_directory = data.get('download_directory', 'downloads')

        if not search_query:
            return web.Response(text="Search query is required", status=400)

        song_path = await download_song(download_directory, search_query)
        return web.json_response({'path': song_path})
    except Exception as e:
        return web.Response(text=str(e), status=500)

# Set up the web application
app = web.Application()
app.add_routes([web.post('/search', search_song)])

# Run the web server
if __name__ == "__main__":
    web.run_app(app, port=12345)
