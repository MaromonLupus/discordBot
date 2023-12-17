
# Project Title: Your Discord Music Bot

## Description

This Discord bot is designed to enhance your server's music experience. It allows users to play music from YouTube, manage playlists, and control playback within a voice channel. Features include playing songs, handling playlists, shuffling, skipping tracks, and more, all with simple commands.

## Getting Started

### Prerequisites

- Python 3.8+
- A Discord bot token (obtainable from the [Discord Developer Portal](https://discord.com/developers/applications))

### Installation

1. **Clone the repository**:
   ```sh
   git clone https://github.com/MaromonLupus/discordBot.git
   cd your-discord-bot
   ```

2. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up the Discord bot token and path**:
   In the `config.py` file in your project add your bot token and if want edit the path for the downloaded files:
   ```env
   BOT_TOKEN = 'your_bot_token'
   DOWNLOAD_DIRECTORY = 'your_path'
   ```
   Replace `your_bot_token` with the token you obtained from the Discord Developer Portal.

### Usage

Run the bot with:

```sh
python discord_bot.py
python worker.py
```

Your bot should now be online in your Discord server. Use commands like `/play`, `/skip`, `/shuffle`, etc., to interact with the bot.

## Commands

- `/play [song/url]`: Plays the specified song or adds it to the queue.
- `/skip`: Skips the current song.
- `/shuffle`: Shuffles the current playlist.
- and many more that I'm too lazy to add

## License

This project is licensed under the [MIT License](LICENSE.md).
