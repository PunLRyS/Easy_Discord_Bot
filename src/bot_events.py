import discord
from discord.ext import commands

def setup(bot):
    @bot.event
    async def on_ready():
        print('Bot is ready.')