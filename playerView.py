import random
import re
import discord
import math
import asyncio
import traceback
from typing import List
from discord.ext import commands
import sqlite3
from characters import Character,hpScaling,Enemy,campaignEnemy

sprites = {
    'W': ':white_medium_square:',
    'O': ':black_medium_square:',
    'C': ':heart:',
    'E': ':beetle:',
    'I': ':notepad_spiral:',
    'P': ':checkered_flag:'
}

# W: wall
# O: open
# E: enemy
# C: chest

def getBars(percentage, numcharas):
    return '`[' + '=' * round(percentage * numcharas) + '\xa0' * (numcharas-round(percentage*numcharas)) + ']`'

def getBoardEmbed(ctx: commands.Context, chara: Character, charaPos: tuple, board: dict, failed = False, log = "", bugs = 0, wb = 0, gold = 0, exp = 0):
    if not failed:
        cur = ''
        for i in range(-3,4):
            for j in range(-3,4):
                if i == 0 and j == 0:
                    if chara.character == 'Java':
                        cur = cur + ":coffee:"
                    elif chara.character == 'Python':
                        cur = cur + ":snake:"
                    elif chara.character == 'C':
                        cur = cur + ":regional_indicator_c:"
                else:
                    cur = cur + sprites[board[(charaPos[0]+i,charaPos[1]+j)]]
            cur = cur + '\n'
        cur = cur + log
        if wb not in [0,False]:
            cur = f'Weapon Bonus! ATK +{round(1.1 ** wb - 1, 2)*100}%\n' + cur
        embeda = discord.Embed(title="Debugger", description=f"HP: {chara.health}/{hpScaling(chara.level,chara.character)}\n{getBars(chara.health / hpScaling(chara.level,chara.character), 15)}\n" + cur, color=0xFF0000)
        embeda.set_footer(text=f"{chara.expDisplay()}")
        return embeda
    else:
        cur = log
        #print(cur)
        embeda = discord.Embed(title="Debugger", description=f"HP: {chara.health}/{hpScaling(chara.level,chara.character)}\n{getBars(0,15)}\n{cur}**__RUN FAILED__**\nExp Gained: {exp}\nGold Gained: {gold}\nBugs Squashed: {bugs}", color = 0x000000)
        embeda.set_footer(text=f"{chara.expDisplay()}")
        return embeda

emo = {
    (1,0): discord.PartialEmoji(name='\N{UPWARDS BLACK ARROW}'),
    (0,1): discord.PartialEmoji(name='\N{LEFTWARDS BLACK ARROW}'),
    (2,1): discord.PartialEmoji(name='right_arrow',id=891019405746655253),
    (1,1): discord.PartialEmoji(name='\N{DOWNWARDS BLACK ARROW}'),
    (0,0): discord.PartialEmoji(name='\N{CROSSED SWORDS}'),
    (2,0): discord.PartialEmoji(name='\N{DOUBLE EXCLAMATION MARK}')
}

class boardButton(discord.ui.Button['boardView']):
    def __init__(self, x:int, y:int, val:str, disabled:bool):
        super().__init__(style=discord.ButtonStyle.gray,label='placeholder',row=y,disabled=disabled)
        if val != '':
            state = val
        else:
            if x == 0:
                state = 't'
            elif x == 2:
                state = 'q'
        try:
            self.emoji = emo[(x,y)]
            self.label = None
        except:
            print(traceback.format_exc())
            self.label="Error"
        self.x = x
        self.y = y
    async def callback(self,interaction=discord.Interaction):
        assert self.view is not None
        view = self.view
        state = view.butlist[self.y][self.x]
        view.updateBoard(state)
        view.clear_items()
        if view.charac.health > 0:
            view.add_item(boardButton(0,0,'t','t' not in view.validmoves))
            view.add_item(boardButton(1,0,'a','a' not in view.validmoves))
            view.add_item(boardButton(2,0,'i','i' not in view.validmoves))
            view.add_item(boardButton(0,1,'w','w' not in view.validmoves))
            view.add_item(boardButton(1,1,'d','d' not in view.validmoves))
            view.add_item(boardButton(2,1,'s','s' not in view.validmoves))
            if 't' in view.validmoves:
                asdfadsf = Enemy(view.charac,view.charaPosition)
                view.batlog = f"Enemy Details:\nHP: {asdfadsf.hp}, ATK: {asdfadsf.atk}, SPD: {asdfadsf.speed}\n" + view.batlog
            await interaction.response.edit_message(content='',embed=getBoardEmbed(view.ctx, view.charac, view.charaPosition, view.board, log=view.batlog, wb=view.weaponBonus),view=view)
        else:
            coins = 0
            exp = 0
            for i in range(view.bugsSquashed):
                coins += random.randint(10,20)
                exp += 2 * random.randint(5,20)
            view.charac.addExp(exp)
            print(view.charac.expDisplay())
            squelch = sqlite3.connect('inventories.db')
            curse = squelch.cursor()
            curse.execute(f"UPDATE invs SET stuff='{view.charac.getStorageStr()}' WHERE uid={view.ctx.author.id}")
            pgold = curse.execute(f"SELECT gold FROM invs WHERE uid={view.ctx.author.id}").fetchall()[0][0]
            curse.execute(f"UPDATE invs SET gold={pgold + coins} WHERE uid={view.ctx.author.id}")
            squelch.commit()
            curse.close()
            squelch.close()
            await interaction.response.edit_message(content='',embed=getBoardEmbed(view.ctx, view.charac, view.charaPosition, view.board, failed=True, log=view.batlog, bugs=view.bugsSquashed, gold=coins, exp=exp),view=view)


"""
(-1,-1) (0,-1) (1,-1)
(-1, 0) (0, 0) (1, 0)
(-1, 1) (0, 1) (1, 1)
"""

def getValid(pos: tuple, board: dict):
    vm = 'twiasd'
    if board[(pos[0]+1,pos[1])] != 'O':
        vm = vm.replace('d','')
    if board[(pos[0]-1,pos[1])] != 'O':
        vm = vm.replace('a','')
    if board[(pos[0],pos[1]+1)] != 'O':
        vm = vm.replace('s','')
    if board[(pos[0],pos[1]-1)] != 'O':
        vm = vm.replace('w','')
    if 'E' not in [board[(pos[0]+1,pos[1])], board[(pos[0]-1,pos[1])], board[(pos[0],pos[1]+1)], board[(pos[0],pos[1]-1)]]:
        vm = vm.replace('t','')
    if 'C' not in [board[(pos[0]+1,pos[1])], board[(pos[0]-1,pos[1])], board[(pos[0],pos[1]+1)], board[(pos[0],pos[1]-1)]]:
        vm = vm.replace('i','')
    return vm

class boardView(discord.ui.View):
    children: List[boardButton]
    def __init__(self, ctx: commands.Context, chara: Character, board: dict):
        super().__init__()
        #self.squelch = sqlite3.connect("inventories.db")
        #self.curse = self.squelch.cursor()
        self.board = board
        self.charac = chara
        self.charaPosition = (0,0)
        self.ctx = ctx
        self.batlog = ""
        self.bugsSquashed = 0
        self.weaponBonus = 0
        self.enemyInfo = ""
        
        # t: attack
        # i: interact
        self.butlist = [
            ['t','a','i'], 
            ['w','d','s']
        ]
        self.validmoves = getValid(self.charaPosition,self.board)
        self.add_item(boardButton(0,0,'t','t' not in self.validmoves))
        self.add_item(boardButton(1,0,'a','a' not in self.validmoves))
        self.add_item(boardButton(2,0,'i','i' not in self.validmoves))
        self.add_item(boardButton(0,1,'w','w' not in self.validmoves))
        self.add_item(boardButton(1,1,'d','d' not in self.validmoves))
        self.add_item(boardButton(2,1,'s','s' not in self.validmoves))
    def updateBoard(self, move):
        self.batlog = ""
        if move == 'w':
            self.charaPosition = (self.charaPosition[0], self.charaPosition[1] - 1)
        elif move == 'a':
            self.charaPosition = (self.charaPosition[0] - 1, self.charaPosition[1])
        elif move == 's':
            self.charaPosition = (self.charaPosition[0], self.charaPosition[1] + 1)
        elif move == 'd':
            self.charaPosition = (self.charaPosition[0] + 1, self.charaPosition[1])
        elif move == 't':
            enemyLoc = [self.board[(self.charaPosition[0]+1,self.charaPosition[1])], self.board[(self.charaPosition[0]-1,self.charaPosition[1])], self.board[(self.charaPosition[0],self.charaPosition[1]+1)], self.board[(self.charaPosition[0],self.charaPosition[1]-1)]].index('E')
            if enemyLoc == 0:
                enemyLoc = (self.charaPosition[0] + 1, self.charaPosition[1])
            elif enemyLoc == 1:
                enemyLoc = (self.charaPosition[0] - 1, self.charaPosition[1])
            elif enemyLoc == 2:
                enemyLoc = (self.charaPosition[0], self.charaPosition[1] + 1)
            elif enemyLoc == 3:
                enemyLoc = (self.charaPosition[0], self.charaPosition[1] - 1)
            self.batlog = Enemy(self.charac,enemyLoc).fight(self.charac)
            if self.charac.health > 0:
                self.board[enemyLoc] = 'O'
                self.bugsSquashed += 1
                if "ULTRA RARE" in self.batlog:
                    self.charac.weapon = random.choice(['RTX3090','RTX3080Ti','RX6900XT','RX6800XT','RTX3080','RX6800','RTX3070Ti'])
                elif "found a " in self.batlog:
                    self.weaponBonus += 1
                    self.charac.atk *= 1.1
        elif move == 'i':
            chestLoc = [self.board[(self.charaPosition[0]+1,self.charaPosition[1])], self.board[(self.charaPosition[0]-1,self.charaPosition[1])], self.board[(self.charaPosition[0],self.charaPosition[1]+1)], self.board[(self.charaPosition[0],self.charaPosition[1]-1)]].index('C')
            if chestLoc == 0:
                chestLoc = (self.charaPosition[0] + 1, self.charaPosition[1])
            elif chestLoc == 1:
                chestLoc = (self.charaPosition[0] - 1, self.charaPosition[1])
            elif chestLoc == 2:
                chestLoc = (self.charaPosition[0], self.charaPosition[1] + 1)
            elif chestLoc == 3:
                chestLoc = (self.charaPosition[0], self.charaPosition[1] - 1)
            self.board[chestLoc] = 'O'
            self.charac.health += 3
            if self.charac.health > hpScaling(self.charac.level,self.charac.character):
                self.charac.health = hpScaling(self.charac.level,self.charac.character)
        if self.charac.health <= 0:
            self.stop()
            #self.curse.close()
            #self.squelch.close()
            return False
        for i in range(-3,4):
            for j in range(-3,4):
                if (self.charaPosition[0]+i,self.charaPosition[1]+j) not in self.board.keys():
                    if abs(self.charaPosition[0] + i) < 25 and abs(self.charaPosition[1] + j) < 25:
                        self.board[(self.charaPosition[0]+i,self.charaPosition[1]+j)] = random.choices(['W','O','E','C'],weights=[3,5,2,2],k=1)[0]
                    else:
                        self.board[(self.charaPosition[0]+i,self.charaPosition[1]+j)] = 'W'
        self.validmoves = getValid(self.charaPosition,self.board)
def getValidCampaign(pos: tuple, board: dict):
    vm = 'twiasd'
    if board[(pos[0]+1,pos[1])] not in ['O','P']:
        vm = vm.replace('d','')
    if board[(pos[0]-1,pos[1])] not in ['O','P']:
        vm = vm.replace('a','')
    if board[(pos[0],pos[1]+1)] not in ['O','P']:
        vm = vm.replace('s','')
    if board[(pos[0],pos[1]-1)] not in ['O','P']:
        vm = vm.replace('w','')
    if 'E' not in [board[(pos[0]+1,pos[1])], board[(pos[0]-1,pos[1])], board[(pos[0],pos[1]+1)], board[(pos[0],pos[1]-1)]]:
        vm = vm.replace('t','')
    if 'C' not in [board[(pos[0]+1,pos[1])], board[(pos[0]-1,pos[1])], board[(pos[0],pos[1]+1)], board[(pos[0],pos[1]-1)]] and 'I' not in [board[(pos[0]+1,pos[1])], board[(pos[0]-1,pos[1])], board[(pos[0],pos[1]+1)], board[(pos[0],pos[1]-1)]]:
        vm = vm.replace('i','')
    return vm
class boardButton2(discord.ui.Button['campaignBoardView']):
    def __init__(self, x:int, y:int, val:str, disabled:bool):
        super().__init__(style=discord.ButtonStyle.gray,label='placeholder',row=y,disabled=disabled)
        if val != '':
            state = val
        else:
            if x == 0:
                state = 't'
            elif x == 2:
                state = 'q'
        try:
            self.emoji = emo[(x,y)]
            self.label = None
        except:
            print(traceback.format_exc())
            self.label="Error"
        self.x = x
        self.y = y
    async def callback(self,interaction=discord.Interaction):
        assert self.view is not None
        view = self.view
        state = view.butlist[self.y][self.x]
        x = view.updateBoard(state)
        #await view.ctx.send("a: " + str(x))
        if x != None:
            if view.charaPosition == (-1,3):
                view.batlog = "\nSystem: Looks like you know how to move!\nWhen you get next to an enemy, use the :crossed_swords: button to attack!\n"
            elif view.charaPosition == (4,5):
                view.batlog = "\nSystem: Wow! 4 Bugs smashed already!\nThese hearts restore +3 Health. Use the :bangbang: button to take one!\nSome bugs will drop attack buffs\n"
        view.clear_items()
        if tutorialBoard[view.charaPosition] == 'P':
            view.charac.health = 0
        if view.charac.health > 0:
            view.add_item(boardButton2(0,0,'t','t' not in view.validmoves))
            view.add_item(boardButton2(1,0,'a','a' not in view.validmoves))
            view.add_item(boardButton2(2,0,'i','i' not in view.validmoves))
            view.add_item(boardButton2(0,1,'w','w' not in view.validmoves))
            view.add_item(boardButton2(1,1,'d','d' not in view.validmoves))
            view.add_item(boardButton2(2,1,'s','s' not in view.validmoves))
            if 't' in view.validmoves:
                asdfadsf = campaignEnemy('Bug',view.charac,[10,1,9])
                view.batlog = f"Enemy Details:\nHP: {asdfadsf.hp}, ATK: {asdfadsf.atk}, SPD: {asdfadsf.speed}\n" + view.batlog
            await interaction.response.edit_message(content='',embed=getBoardEmbed(view.ctx, view.charac, view.charaPosition, view.board, log=view.batlog, wb=view.weaponBonus),view=view)
        else:
            await interaction.response.edit_message(content='',embed=getBoardEmbed(view.ctx, view.charac, view.charaPosition, view.board, failed=True, log=view.batlog, bugs=view.bugsSquashed),view=view)

tutorialBoard = {(-6,-6): "W", (-6,-5): "W", (-6,-4): "W", (-6,-3): "W", (-6,-2): "W", (-6,-1): "W", (-6,0): "W", (-6,1): "W", (-6,2): "W", (-6,3): "W", (-6,4): "W", (-6,5): "P", (-6,6): "W", (-5,-6): "W", (-5,-5): "O", (-5,-4): "E", (-5,-3): "E", (-5,-2): "E", (-5,-1): "E", (-5,0): "E", (-5,1): "E", (-5,2): "E", (-5,3): "E", (-5,4): "W", (-5,5): "O", (-5,6): "W", (-4,-6): "W", (-4,-5): "O", (-4,-4): "W", (-4,-3): "W", (-4,-2): "W", (-4,-1): "W", (-4,0): "W", (-4,1): "W", (-4,2): "W", (-4,3): "W", (-4,4): "W", (-4,5): "O", (-4,6): "W", (-3,-6): "W", (-3,-5): "O", (-3,-4): "O", (-3,-3): "O", (-3,-2): "O", (-3,-1): "O", (-3,0): "O", (-3,1): "O", (-3,2): "O", (-3,3): "O", (-3,4): "O", (-3,5): "O", (-3,6): "W", (-2,-6): "W", (-2,-5): "E", (-2,-4): "W", (-2,-3): "W", (-2,-2): "W", (-2,-1): "W", (-2,0): "W", (-2,1): "W", (-2,2): "W", (-2,3): "W", (-2,4): "W", (-2,5): "W", (-2,6): "W", (-1,-6): "W", (-1,-5): "E", (-1,-4): "W", (-1,-3): "W", (-1,-2): "W", (-1,-1): "O", (-1,0): "O", (-1,1): "O", (-1,2): "O", (-1,3): "O", (-1,4): "I", (-1,5): "O", (-1,6): "W", (0,-6): "W", (0,-5): "E", (0,-4): "W", (0,-3): "W", (0,-2): "W", (0,-1): "O", (0,0): "O", (0,1): "O", (0,2): "O", (0,3): "W", (0,4): "W", (0,5): "E", (0,6): "W", (1,-6): "W", (1,-5): "E", (1,-4): "W", (1,-3): "W", (1,-2): "W", (1,-1): "O", (1,0): "O", (1,1): "O", (1,2): "O", (1,3): "W", (1,4): "W", (1,5): "E", (1,6): "W", (2,-6): "W", (2,-5): "E", (2,-4): "W", (2,-3): "W", (2,-2): "W", (2,-1): "O", (2,0): "O", (2,1): "O", (2,2): "O", (2,3): "W", (2,4): "W", (2,5): "E", (2,6): "W", (3,-6): "W", (3,-5): "E", (3,-4): "W", (3,-3): "W", (3,-2): "W", (3,-1): "W", (3,0): "W", (3,1): "W", (3,2): "W", (3,3): "W", (3,4): "W", (3,5): "E", (3,6): "W", (4,-6): "W", (4,-5): "O", (4,-4): "O", (4,-3): "O", (4,-2): "O", (4,-1): "O", (4,0): "C", (4,1): "C", (4,2): "C", (4,3): "O", (4,4): "I", (4,5): "O", (4,6): "W", (5,-6): "W", (5,-5): "W", (5,-4): "W", (5,-3): "W", (5,-2): "W", (5,-1): "W", (5,0): "W", (5,1): "W", (5,2): "W", (5,3): "W", (5,4): "W", (5,5): "W", (5,6): "W", (6,-6): "W", (6,-5): "W", (6,-4): "W", (6,-3): "W", (6,-2): "W", (6,-1): "W", (6,0): "W", (6,1): "W", (6,2): "W", (6,3): "W", (6,4): "W", (6,5): "W", (6,6): "W", }

def getCampaignEmbed(ctx: commands.Context, chara: Character, charaPos: tuple, failed=False, wb=0, bugs=0,log=""):
    if not failed:
        cur = ''
        for i in range(-3,4):
            for j in range(-3,4):
                if i == 0 and j == 0:
                    if chara.character == 'Java':
                        cur = cur + ":coffee:"
                    elif chara.character == 'Python':
                        cur = cur + ":snake:"
                    elif chara.character == 'C':
                        cur = cur + ":regional_indicator_c:"
                else:
                    cur = cur + sprites[tutorialBoard[(charaPos[0]+i,charaPos[1]+j)]]
            cur = cur + '\n'
        cur = cur + log
        if wb not in [0,False]:
            cur = f'Weapon Bonus! ATK +{round(1.1 ** wb - 1, 2)*100}%\n' + cur
        embeda = discord.Embed(title="Debugger", description=f"HP: {chara.health}/{hpScaling(chara.level,chara.character)}\n{getBars(chara.health / hpScaling(chara.level,chara.character), 15)}\n" + cur, color=0xFF0000)
        embeda.set_footer(text=f"{chara.expDisplay()}")
        return embeda
    else:
        cur = log
        #print(cur)
        embeda = discord.Embed(title="Debugger", description=f"HP: {chara.health}/{hpScaling(chara.level,chara.character)}\n{getBars(0,15)}\n{cur}**__Tutorial Over!__**\nExp Gained: 0\nGold Gained: 0\nBugs Squashed: {bugs}", color = 0x000000)
        embeda.set_footer(text=f"{chara.expDisplay()}")
        return embeda
class campaignBoardView(discord.ui.View):
    children: List[boardButton2]
    def __init__(self, ctx: commands.Context, chara: Character):
        super().__init__()
        self.board = tutorialBoard
        self.charac = chara
        self.charaPosition = (0,0)
        self.ctx = ctx
        self.batlog = ""
        self.bugsSquashed = 0
        self.weaponBonus = 0
        self.enemyInfo = ""
        
        # t: attack
        # i: interact
        self.butlist = [
            ['t','a','i'], 
            ['w','d','s']
        ]
        self.validmoves = getValidCampaign(self.charaPosition,self.board)
        self.add_item(boardButton2(0,0,'t','t' not in self.validmoves))
        self.add_item(boardButton2(1,0,'a','a' not in self.validmoves))
        self.add_item(boardButton2(2,0,'i','i' not in self.validmoves))
        self.add_item(boardButton2(0,1,'w','w' not in self.validmoves))
        self.add_item(boardButton2(1,1,'d','d' not in self.validmoves))
        self.add_item(boardButton2(2,1,'s','s' not in self.validmoves))
    def updateBoard(self, move):
        self.batlog = ""
        if move == 'w':
            self.charaPosition = (self.charaPosition[0], self.charaPosition[1] - 1)
        elif move == 'a':
            self.charaPosition = (self.charaPosition[0] - 1, self.charaPosition[1])
        elif move == 's':
            self.charaPosition = (self.charaPosition[0], self.charaPosition[1] + 1)
        elif move == 'd':
            self.charaPosition = (self.charaPosition[0] + 1, self.charaPosition[1])
        elif move == 't':
            enemyLoc = [self.board[(self.charaPosition[0]+1,self.charaPosition[1])], self.board[(self.charaPosition[0]-1,self.charaPosition[1])], self.board[(self.charaPosition[0],self.charaPosition[1]+1)], self.board[(self.charaPosition[0],self.charaPosition[1]-1)]].index('E')
            if enemyLoc == 0:
                enemyLoc = (self.charaPosition[0] + 1, self.charaPosition[1])
            elif enemyLoc == 1:
                enemyLoc = (self.charaPosition[0] - 1, self.charaPosition[1])
            elif enemyLoc == 2:
                enemyLoc = (self.charaPosition[0], self.charaPosition[1] + 1)
            elif enemyLoc == 3:
                enemyLoc = (self.charaPosition[0], self.charaPosition[1] - 1)
            #self.batlog = Enemy(self.charac,enemyLoc).fight(self.charac)
            self.batlog = campaignEnemy("Bug", self.charac,[10,1,9]).fight(self.charac)
            if self.charac.health > 0:
                self.board[enemyLoc] = 'O'
                self.bugsSquashed += 1
                if "ULTRA RARE" in self.batlog:
                    self.charac.weapon = random.choice(['RTX3090','RTX3080Ti','RX6900XT','RX6800XT','RTX3080','RX6800','RTX3070Ti'])
                elif "found a " in self.batlog or random.randint(0,1) == 0:
                    self.weaponBonus += 1
                    self.charac.atk *= 1.1
        elif move == 'i':
            try:
                regularchest = True
                chestLoc = [self.board[(self.charaPosition[0]+1,self.charaPosition[1])], self.board[(self.charaPosition[0]-1,self.charaPosition[1])], self.board[(self.charaPosition[0],self.charaPosition[1]+1)], self.board[(self.charaPosition[0],self.charaPosition[1]-1)]].index('C')
            except ValueError:
                regularchest = False
                chestLoc = [self.board[(self.charaPosition[0]+1,self.charaPosition[1])], self.board[(self.charaPosition[0]-1,self.charaPosition[1])], self.board[(self.charaPosition[0],self.charaPosition[1]+1)], self.board[(self.charaPosition[0],self.charaPosition[1]-1)]].index('I')
            if regularchest:
                if chestLoc == 0:
                    chestLoc = (self.charaPosition[0] + 1, self.charaPosition[1])
                elif chestLoc == 1:
                    chestLoc = (self.charaPosition[0] - 1, self.charaPosition[1])
                elif chestLoc == 2:
                    chestLoc = (self.charaPosition[0], self.charaPosition[1] + 1)
                elif chestLoc == 3:
                    chestLoc = (self.charaPosition[0], self.charaPosition[1] - 1)
                self.board[chestLoc] = 'O'
                self.charac.health += 3
                if self.charac.health > hpScaling(self.charac.level,self.charac.character):
                    self.charac.health = hpScaling(self.charac.level,self.charac.character)
            else:
                if chestLoc == 0:
                    chestLoc = (self.charaPosition[0] + 1, self.charaPosition[1])
                elif chestLoc == 1:
                    chestLoc = (self.charaPosition[0] - 1, self.charaPosition[1])
                elif chestLoc == 2:
                    chestLoc = (self.charaPosition[0], self.charaPosition[1] + 1)
                elif chestLoc == 3:
                    chestLoc = (self.charaPosition[0], self.charaPosition[1] - 1)
                self.board[chestLoc] = 'O'
                self.validmoves = getValidCampaign(self.charaPosition,self.board)
                return True

        if self.charac.health <= 0:
            self.stop()
            #self.curse.close()
            #self.squelch.close()
            return False
        for i in range(-3,4):
            for j in range(-3,4):
                if (self.charaPosition[0]+i,self.charaPosition[1]+j) not in self.board.keys():
                    self.board[(self.charaPosition[0]+i,self.charaPosition[1]+j)] = 'W'
        self.validmoves = getValidCampaign(self.charaPosition,self.board)