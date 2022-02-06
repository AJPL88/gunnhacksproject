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
from characters import Character as Charac
from characters import LanguageC,LanguageJava,LanguagePython

class hackBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("hax."))
    async def on_ready(self):
        print(f"Logged in as {self.user}")

client = hackBot()
squelch = sqlite3.connect("inventories.db")
curse = squelch.cursor()
tar = 445010725862244350
#rows = curse.execute("SELECT gold FROM invs WHERE uid=?", [445010725862244350]).fetchall()
#rows2 = curse.execute("SELECT uid, gold, stuff FROM invs").fetchall()
#print(rows)
#print(rows2)

def fromInvGetChar(uid: int):
    row = curse.execute(f"SELECT stuff FROM invs WHERE uid={uid}").fetchall()
    return row[0]

@client.command()
async def sqlexec(ctx: commands.Context, val: str):
    if ctx.author.id == 445010725862244352:
        try:
            x = curse.execute(val)
            squelch.commit()
        except Exception:
            print(traceback.format_exc())

@client.command()
async def sqlprint(ctx: commands.Context, val: str):
    if ctx.author.id == 445010725862244352:
        try:
            x = curse.execute(val).fetchall()
            print(x)
        except Exception:
            print(traceback.format_exc())

@client.command()
async def connectvoice(ctx: commands.Context):
    if ctx.author.voice.channel == None:
        await ctx.send(f"<@{ctx.author.id}> You are not currently connected to a voice channel!")
        return
    vc = ctx.author.voice.channel
    await vc.connect()
    voice = discord.utils.get(client.voice_clients, guild = ctx.guild)

@client.command()
async def character(ctx: commands.Context, *args):
    print(args)
    if args == ():
        try:
            thing = fromInvGetChar(ctx.author.id)
        except IndexError:
            await ctx.send("You don't have a character yet! Would you like to create one? (Yes/No)")
            try:
                rep = await client.wait_for("message", check = lambda x: x.author.id == ctx.author.id and x.channel.id == ctx.channel.id, timeout = 30.0)
            except asyncio.TimeoutError:
                return
            if rep.content.lower() in ['yes','y']:
                embeda = discord.Embed(title="Character Selection", description = "Languages to choose from: \n_:one:: C_\nHP: 12, DEF: 10, ATK: 7, SPD: 10\n_:two:: Java_\nHP: 10, DEF: 10, ATK: 9, SPD: 10\n_:three:: Python_\nHP: 9, DEF: 10, ATK: 12, SPD: 10", color=0x00FF00)
                ms = await ctx.send("",embed=embeda)
                await asyncio.sleep(1)
                await ms.add_reaction("\u0031\uFE0F\u20E3")
                await asyncio.sleep(0.5)
                await ms.add_reaction("\u0032\uFE0F\u20E3")
                await asyncio.sleep(0.5)
                await ms.add_reaction("\u0033\uFE0F\u20E3")
                try:
                    reac, userr = await client.wait_for("reaction_add", check=lambda r,u: str(r.emoji) in ['\u0031\uFE0F\u20E3','\u0032\uFE0F\u20E3','\u0033\uFE0F\u20E3'] and u.id == ctx.author.id and r.message.id == ms.id, timeout = 30.0)
                except asyncio.TimeoutError:
                    return
                if str(reac.emoji) == '\u0033\uFE0F\u20E3':
                    cur = LanguagePython()
                    curse.execute(f"INSERT INTO invs VALUES ({userr.id}, 0, '{cur.getStorageStr()}')")
                    squelch.commit()
                    await character(ctx)
                    return
                elif str(reac.emoji) == '\u0032\uFE0F\u20E3':
                    cur = LanguageJava()
                    curse.execute(f"INSERT INTO invs VALUES ({userr.id}, 0, '{cur.getStorageStr()}')")
                    squelch.commit()
                    await character(ctx)
                    return
                elif str(reac.emoji) == '\u0031\uFE0F\u20E3':
                    cur = LanguageC()
                    curse.execute(f"INSERT INTO invs VALUES ({userr.id}, 0, '{cur.getStorageStr()}')")
                    squelch.commit()
                    await character(ctx)
                    return
                return
            else:
                return
    else:
        try:
            thing = fromInvGetChar(int(args[0]))
        except IndexError:
            await ctx.send("User does not exist or has no character!")
        except Exception:
            #print(traceback.format_exc())
            await ctx.send("Invalid User!")
            return
    if thing != []:
        cur = Charac(vals=thing[0])
        if thing[0][-1] == 'C':
            url = "https://www.pngkit.com/png/detail/101-1010012_c-programming-icon-c-programming-language-logo.png"
            charn = "C"
        elif thing[0][-1] == 'a':
            url = "https://cdn-icons-png.flaticon.com/512/226/226777.png"
            charn = "Java"
        elif thing[0][-1] == 'n':
            url = "https://cdn-icons-png.flaticon.com/512/5968/5968350.png"
            charn = "Python"
        embeda=discord.Embed(title="Character",description=f"<@{ctx.author.id}>'s {charn}")
        embeda.set_thumbnail(url=url)
        embeda.add_field(name="Stats", value=f"Max HP: **{cur.health}**\nDEF: **{cur.defense}**\nATK: **{cur.atk}**\nSTAM: **{cur.stamina}**\nSPD: **{cur.speed}**\nWeapon: **{cur.weapon}**\nArmor: **{cur.armor}**", inline=True)
        embeda.set_footer(text=f"{cur.expDisplay()}")
        await ctx.send("",embed=embeda)
    else:
        print("Hello")

@client.command()
async def adminsetchar(ctx: commands.Context, uid: str, val: str):
    curse.execute(f"UPDATE invs SET stuff = '{val}' WHERE uid = {uid}")
    squelch.commit()

@client.command()
async def ping(ctx: commands.Context):
    await ctx.send(f"{round(client.latency*1000,2)}ms")

if __name__ == '__main__':
    client.run(os.getenv('token'))
