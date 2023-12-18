import json
from disnake.ext import commands
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor

from config import OPEN_API_KEY

class OpenAICommands(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.messages = [{"role": "system", "content": "You are a helpful assistant designed to output JSON."}]

    async def generate_image_with_dalle(self, prompt):
        client = OpenAI(api_key=OPEN_API_KEY)
        try:
            response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    n=1,
            )
            image_url = response.data[0].url
            return image_url
        except Exception as e:
            print(f"Error generating image with DALL-E: {e}")
            return None
        
    async def generate_answer_with_chat(self, prompt):
        client = OpenAI(api_key=OPEN_API_KEY)
        self.messages.append({"role": "user", "content": prompt})
        try:
            response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            response_format={ "type": "json_object" },
            messages=self.messages
            )
            parsed_json = json.loads(response.choices[0].message.content)

            # Extract the first value
            first_value = next(iter(parsed_json.values()), "No value found.")
            return first_value
        except Exception as e:
            print(f"Error generating image with DALL-E: {e}")
            return None
    
    @commands.slash_command(
        name="generate_image",
        description="Generate an image using DALL-E with a given prompt"
    )
    async def generate_image(self, inter, prompt: str):
        await inter.response.defer()
        image_url = await self.generate_image_with_dalle(prompt)
        if image_url:
            await inter.followup.send(f"Here's your generated image: {image_url}")
        else:
            await inter.followup.send("Sorry, I couldn't generate an image right now.")
    
    @commands.slash_command(
        name="generate_answer",
        description="Generate an answer using chat-GPT"
    )
    async def generate_answer(self, inter, prompt: str):
        await inter.response.defer()
        answer = await self.generate_answer_with_chat(prompt)
        if answer:
            await inter.followup.send(f"{prompt}\n{answer}")
        else:
            await inter.followup.send("Sorry, I couldn't generate an ansswer right now.")

def setup(bot):
    bot.add_cog(OpenAICommands(bot))
