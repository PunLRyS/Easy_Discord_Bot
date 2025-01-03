import discord
from discord.ext import commands
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

from src import bot_events, bot_commands, bot_voice, bot_games

# bot_events.setup(bot)
bot_commands.setup(bot)
bot_voice.setup(bot)
bot_games.setup(bot)

bot.run(os.getenv("DISCORD_TOKEN"))