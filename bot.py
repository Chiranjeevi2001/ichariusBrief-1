import discord

from discord.ext import commands
import requests
from dotenv import load_dotenv
import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO

load_dotenv()

TOKEN = os.getenv('TOKEN')
GEMINI_API_KEY = os.getenv('API_KEY')

class InclusiveBrief(commands.Bot):
    
    def __init__(self):
        # define intents
        intents = discord.Intents.default()
        intents.messages = True # allow to read messages
        intents.message_content = True  # allow to read message content
        
        super().__init__(intents=intents, command_prefix='!')   # initialize the bot with the prefix '!'
        
        genai.configure(api_key=GEMINI_API_KEY)  # configure the generative AI API
        self.text_model = genai.GenerativeModel('gemini-1.5-pro-latest')  # create a text model
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')  # create a vision model
        
    async def on_ready(self):   # called when the bot is ready
        print(f'{self.user} has connected to Discord!')
        
        
    async def on_message(self, message: discord.Message) -> None:   # called when a message is sent in a channel the bot has access to
        if message.author == self.user: # ignore messages from the bot itself
            return
        
        command = message.content.lower()
        
        # help, website analyse, website getinfo, vision:analyse_img
        
        if command.startswith('!analyse'):
            await self.get_website_info(message=message, text=command.split(" ")[ 1 : ])

        elif command.startswith('!vision'):
            await self.get_img_info(message=message)
            
    async def get_img_info(self, message: discord.Message) -> None:
        if message.attachments:
            img_url = message.attachments[0]
   
            async with message.channel.typing():
                image_bits = self.download_img(img_url=img_url) # download the image
                
                image = Image.open(BytesIO(image_bits)) # open the image
                response = self.vision_model.generate_content(image)
                text = response.text
                prompt = f"""The following text is the response from a Gemini Vision model analyzing an image:

                {text}

                Please reformat this response into a clear and concise summary with the following structure:

                **Image:**

                * Briefly describe the main subject(s) in the image.

                **Details:**

                * Describe any interesting details or objects in the image.

                **Additional Notes:**

                * Include any relevant information not covered in the previous sections.
                """
                
                response = self.text_model.generate_content(prompt)
                text = response.text
                print(text)
                await message.channel.send(text)

        print(img_url)
    
    @staticmethod
    def download_img(img_url: str) -> None:
        
            response = requests.get(url=img_url)    # send a GET request to the image URL
            
            if(response.status_code == 200):
                
                return response.content   # return the image content
            else:
                print("Error")      # print an error message if the request fails
                    
    async def get_website_info(self, message: discord.Message, text) -> None:
        prompt = f"""Analyze the website: {text}

        **Here's what I'm looking for:**
        
        * **Purpose:** What is the main function or service offered by the website? Is it an e-commerce store, a news website, a portfolio, a blog, etc.?
        * **Content:** Briefly describe the type of content found on the website (e.g., articles, products, services, images, videos).
        * **Target Audience:** Who is the website aimed at? (e.g., businesses, general consumers, a specific niche)
        
        **Pay close attention to the website's metadata, including the title tag, meta description, and keywords.** This information can provide valuable clues about the website's purpose and target audience.
        
        **Keep the response concise and informative.**"""
        
        async with message.channel.typing():
            print("Hello")
            response = self.text_model.generate_content(prompt)
            text = response.text
            print(text)
            await message.channel.send(text)
        
def start_bot():
    inclusivebrief = InclusiveBrief()
    
    inclusivebrief.run(token=TOKEN)
    
    
if __name__ == '__main__':
    start_bot()
        
        