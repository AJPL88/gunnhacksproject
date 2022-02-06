import discord
import os
import math
import traceback
import asyncio
import requests
import time
import sqlite3
from youtube_dl import YoutubeDL
from discord.ext import commands

class hackBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("hax."))
    async def on_ready(self):
        print(f"Logged in as {self.user}")

client = hackBot()
squelch = sqlite3.connect("inventories.db")
curse = squelch.cursor()

@client.command()
async def inv(ctx: commands.Context):
    pass

@client.command()
async def connectvoice(ctx: commands.Context):
    if ctx.author.voice.channel == None:
        await ctx.send(f"<@{ctx.author.id}> You are not currently connected to a voice channel!")
        return
    vc = ctx.author.voice.channel
    await vc.connect()
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)
    

@client.command()
async def ping(ctx: commands.Context):
    await ctx.send(f"{round(client.latency*1000,2)}ms")

if __name__ == '__main__':
    client.run(os.getenv('token'))
