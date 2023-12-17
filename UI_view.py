import os
import disnake
from disnake.ui import Button, View

class PreviousButton(Button):
    def __init__(self):
        super().__init__(label="Previous", style=disnake.ButtonStyle.grey)

    async def callback(self, inter):
        if self.view.current_page > 0:
            self.view.current_page -= 1
            formatted_message = await self.view.update_message(inter)
            if inter.response.is_done():
                await inter.edit_original_response(content=formatted_message)
            else:
                await inter.response.edit_message(content=formatted_message)

class NextButton(Button):
    def __init__(self):
        super().__init__(label="Next", style=disnake.ButtonStyle.grey)

    async def callback(self, inter):
        if self.view.current_page < self.view.max_page - 1:
            self.view.current_page += 1
            formatted_message = await self.view.update_message(inter)
            if inter.response.is_done():
                await inter.edit_original_response(content=formatted_message)
            else:
                await inter.response.edit_message(content=formatted_message)

class PaginationView(View):
    def __init__(self, songs, page_size):
        super().__init__(timeout=60)
        self.songs = songs
        self.page_size = page_size
        self.current_page = 0
        self.max_page = len(songs) // page_size + (1 if len(songs) % page_size else 0)

        # Add custom buttons to the view without passing arguments
        self.add_item(PreviousButton())
        self.add_item(NextButton())

    async def update_message(self, inter):
        # Calculate range of songs to display
        start_index = self.current_page * self.page_size
        end_index = start_index + self.page_size
        songs_to_display = self.songs[start_index:end_index]

        # Format the message
        formatted_message = "Songs in queue:\n"


        # Create table header
        table = "┌─────┬────────────────────────────┐\n"
        table += "│ No. │ Song Name                  │\n"
        table += "├─────┼────────────────────────────┤\n"

        # Add each song to the table
        for index, song in enumerate(songs_to_display, start=start_index + 1):
            song_name = os.path.basename(song)
            # Ensure the song name fits in the column width
            song_name = (song_name[:24] + '..') if len(song_name) > 26 else song_name
            table += f"│ {index:<4}│ {song_name:<26} │\n"

        table += "└─────┴────────────────────────────┘"

        formatted_message += (f"```{table}```")  # Use markdown for code block format


        # Check if the interaction has already been responded to
        if inter.response.is_done():
            await inter.edit_original_response(content=formatted_message)
        else:
            await inter.response.edit_message(content=formatted_message)
        
        return formatted_message
