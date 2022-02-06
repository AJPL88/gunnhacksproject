import random
import re
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
from playerView import getBoardEmbed, boardView

class hackBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("hax."))
    async def on_ready(self):
        print(f"Logged in as {self.user}")

client = hackBot()

tar = 445010725862244350
#rows = curse.execute("SELECT gold FROM invs WHERE uid=?", [445010725862244350]).fetchall()
#rows2 = curse.execute("SELECT uid, gold, stuff FROM invs").fetchall()
#print(rows)
#print(rows2)

def fromInvGetChar(uid: int):
    squelch = sqlite3.connect("inventories.db")
    curse = squelch.cursor()
    row = curse.execute(f"SELECT stuff FROM invs WHERE uid={uid}").fetchall()
    curse.close()
    squelch.close()
    return row[0]

@client.command()
async def sqlexec(ctx: commands.Context, val: str):
    if ctx.author.id == 445010725862244352:
        squelch = sqlite3.connect("inventories.db")
        curse = squelch.cursor()
        try:
            x = curse.execute(val)
            squelch.commit()
        except Exception:
            print(traceback.format_exc())
        curse.close()
        squelch.close()

@client.command()
async def sqlprint(ctx: commands.Context, val: str):
    if ctx.author.id == 445010725862244352:
        squelch = sqlite3.connect("inventories.db")
        curse = squelch.cursor()
        try:
            x = curse.execute(val).fetchall()
            print(x)
        except Exception:
            print(traceback.format_exc())
        curse.close()
        squelch.close()

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
    #print(args)
    squelch = sqlite3.connect("inventories.db")
    curse = squelch.cursor()
    squelch.commit()
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
    if thing != [] and args == ():
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
        gold = curse.execute(f"SELECT gold FROM invs WHERE uid={ctx.author.id}").fetchall()[0][0]
        embeda=discord.Embed(title="Character",description=f"<@{ctx.author.id}>'s {charn}")
        embeda.set_thumbnail(url=url)
        embeda.add_field(name="Stats", value=f"Max HP: **{cur.health}**\nDEF: **{cur.defense}**\nATK: **{cur.atk}**\nSTAM: **{cur.stamina}**\nSPD: **{cur.speed}**\nWeapon: **{cur.weapon}**\nArmor: **{cur.armor}**", inline=True)
        embeda.set_footer(text=f"Gold: {gold}\n{cur.expDisplay()}")
        await ctx.send("",embed=embeda)
        return
    elif thing != []:
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
        gold = curse.execute(f"SELECT gold FROM invs WHERE uid={int(args[0])}").fetchall()[0][0]
        embeda=discord.Embed(title="Character",description=f"<@{int(args[0])}>'s {charn}")
        embeda.set_thumbnail(url=url)
        embeda.add_field(name="Stats", value=f"Max HP: **{cur.health}**\nDEF: **{cur.defense}**\nATK: **{cur.atk}**\nSTAM: **{cur.stamina}**\nSPD: **{cur.speed}**\nWeapon: **{cur.weapon}**\nArmor: **{cur.armor}**", inline=True)
        embeda.set_footer(text=f"Gold: {gold}\n{cur.expDisplay()}")
        await ctx.send("",embed=embeda)
        return
    else:
        print("Hello")
    curse.close()
    squelch.close()

@client.command()
async def testplay(ctx: commands.Context):
    thing = fromInvGetChar(ctx.author.id)
    cur = Charac(vals=thing[0])
    board = {}
    for i in range(-3, 4):
        for j in range(-3, 4):
            if (i,j) != (0,0):
                board[(i,j)] = random.choices(['W','O','E'],weights=[3,5,2],k=1)[0]
    for i in [-1,0,1]:
        for j in [-1,0,1]:
            board[(i,j)] = 'O'
    embeda = getBoardEmbed(ctx, cur, (0,0), board)
    await ctx.send("",embed=embeda,view=boardView(ctx,cur,board))
    #await ctx.send("",embed=embeda)

@client.command()
async def shop(ctx: commands.Context):
    embed=discord.Embed(title="Armor Shop", description="\xa0", color=0xffff00)
    embed.add_field(name="1GB - 100 Gold", value="9% damage reduction\n\xa0\n**2GB - 200 Gold**\n17% damage reduction\n\xa0\n**4GB - 300 Gold**\n23% damage reduction\n\xa0\n**8GB - 500 Gold**\n29% damage reduction\n\xa0\n**16GB - 750 Gold**\n33% damage reduction", inline=True)
    embed.add_field(name="32GB - 1000 Gold", value="38% damage reduction\n\xa0\n**64 GB - 1500 Gold**\n41% damage reduction\n\xa0\n**128GB - 2500 Gold**\n44% damage reduction\n\xa0\n**256GB - 4000 Gold**\n50% damage reduction\n\xa0\n**512GB - 7500 Gold**\n75% damage reduction", inline=True)
    embed.set_footer(text="hax.buy <armor name>")
    await ctx.send(embed=embed)

shopPrices = { '1gb': 100, '2gb': 200, '4gb': 300, '8gb': 500, '16gb': 750, '32gb': 1000, '64gb': 1500, '128gb': 2500, '256gb': 4000, '512gb': 7500 }

@client.command()
async def buy(ctx: commands.Context, shop_id: str):
    if shop_id.lower() not in shopPrices.keys():
        await ctx.send('Invalid shop item!')
    else:
        squelch = sqlite3.connect('inventories.db')
        curse = squelch.cursor()
        bal = curse.execute(f"SELECT gold FROM invs WHERE uid={ctx.author.id}").fetchall()[0][0]
        if int(bal) < shopPrices[shop_id.lower()]:
            await ctx.send("Insufficient Funds!")
        else:
            previousChar = re.split(r"[$]", curse.execute(f"SELECT stuff FROM invs WHERE uid={ctx.author.id}").fetchall()[0][0])
            if previousChar[8] != 'none':
                if list(shopPrices.keys()).index(previousChar[8].lower()) > list(shopPrices.keys()).index(shop_id.lower()):
                    await ctx.send("Already have better Armor!")
                    curse.close()
                    squelch.close()
                    return
                elif list(shopPrices.keys()).index(previousChar[8].lower()) == list(shopPrices.keys()).index(shop_id.lower()):
                    await ctx.send("Already have this tier!")
                    curse.close()
                    squelch.close()
                    return
            previousChar[8] = shop_id.upper()
            newChar = '$'.join(previousChar)
            curse.execute(f"UPDATE invs SET stuff='{newChar}' WHERE uid={ctx.author.id}")
            curse.execute(f"UPDATE invs SET gold={bal-shopPrices[shop_id]} WHERE uid={ctx.author.id}")
            squelch.commit()
            await ctx.send(f'Successfully bought Armor: **{shop_id.upper()}**')
        curse.close()
        squelch.close()

@client.command()
async def adminsetchar(ctx: commands.Context, uid: str, val: str):
    squelch = sqlite3.connect("inventories.db")
    curse = squelch.cursor()
    curse.execute(f"UPDATE invs SET stuff = '{val}' WHERE uid = {uid}")
    squelch.commit()
    curse.close()
    squelch.close()
    
@client.command()
async def ping(ctx: commands.Context):
    await ctx.send(f"{round(client.latency*1000,2)}ms")

if __name__ == '__main__':
    client.run(os.getenv('token'))
