import discord
import os
import math
import traceback
import asyncio
import requests
import time
from youtube_dl import YoutubeDL
from discord.ext import commands

class hackBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("hax."))
    async def on_ready(self):
        print(f"Logged in as {self.user}")

client = hackBot()

@client.command
async def inv(ctx: commands.Context):
    pass

@client.command
async def connectvoice(ctx: commands.Context):
    pass

@client.command
async def ping(ctx: commands.Context):
    await ctx.send(f"{round(client.latency*1000,2)}ms")

if __name__ == '__main__':
    client.run(os.getenv('token'))
