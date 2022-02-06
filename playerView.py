import random
import discord
import math
import asyncio
import traceback
from typing import List
from discord.ext import commands
from characters import Character,hpScaling,Enemy

sprites = {
    'W': ':black_medium_square:',
    'O': ':white_medium_square:',
    'C': ':heart:',
    'E': ':zombie:'
}

# W: wall
# O: open
# E: enemy
# C: chest

def getBars(percentage, numcharas):
    return '[' + '=' * round(percentage * numcharas) + ' ' * (numcharas-round(percentage*numcharas)) + ']'

def getBoardEmbed(ctx: commands.Context, chara: Character, charaPos: tuple, board: dict, failed = False):
    if not failed:
        cur = ''
        for i in range(-3,4):
            for j in range(-3,4):
                if i == 0 and j == 0:
                    cur = cur + ":person_bald:"
                else:
                    cur = cur + sprites[board[(charaPos[0]+i,charaPos[1]+j)]]
            cur = cur + '\n'
        embeda = discord.Embed(title="Test Game", description=f"HP: {chara.health}/{hpScaling(chara.level,chara.character)}\n{getBars(chara.health / hpScaling(chara.level,chara.character), 15)}\n" + cur, color=0xFF0000)
        embeda.set_footer(text=f"{chara.expDisplay()}")
        return embeda
    else:
        embeda = discord.Embed(title="Test game", description=f"HP: {chara.health}/{hpScaling(chara.level,chara.character)}\n{getBars(0,15)}\n**__RUN FAILED__**\nExp Gained: xxx", color = 0x000000)
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
        #view.clear_items()
        if view.charac.health > 0:
            '''view.add_item(boardButton(0,0,'t','E' not in [view.board[(view.charaPosition[0]+1,view.charaPosition[1])], view.board[(view.charaPosition[0]-1,view.charaPosition[1])], view.board[(view.charaPosition[0],view.charaPosition[1]+1)], view.board[(view.charaPosition[0],view.charaPosition[1]-1)]]))
            view.add_item(boardButton(1,0,'w',view.board[(view.charaPosition[0],view.charaPosition[1]-1)] != 'O'))
            view.add_item(boardButton(2,0,'i','C' not in [view.board[(view.charaPosition[0]+1,view.charaPosition[1])], view.board[(view.charaPosition[0]-1,view.charaPosition[1])], view.board[(view.charaPosition[0],view.charaPosition[1]+1)], view.board[(view.charaPosition[0],view.charaPosition[1]-1)]]))
            view.add_item(boardButton(0,1,'a',view.board[(view.charaPosition[0]-1,view.charaPosition[1])] != 'O'))
            view.add_item(boardButton(1,1,'s',view.board[(view.charaPosition[0],view.charaPosition[1]+1)] != 'O'))
            view.add_item(boardButton(2,1,'d',view.board[(view.charaPosition[0]+1,view.charaPosition[1])] != 'O'))'''
            await interaction.response.edit_message(content='',embed=getBoardEmbed(view.ctx, view.charac, view.charaPosition, view.board))
        else:
            await interaction.response.edit_message(content='',embed=getBoardEmbed(view.ctx, view.charac, view.charaPosition, view.board, failed=True))


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
        self.board = board
        self.charac = chara
        self.charaPosition = (0,0)
        self.ctx = ctx
        
        # t: attack
        # i: interact
        self.butlist = [
            ['t','a','i'], 
            ['w','d','s']
        ]
        self.validmoves = getValid(self.charaPosition,self.board)
        self.add_item(boardButton(0,0,'t','t' not in self.validmoves))
        self.add_item(boardButton(1,0,'w','w' not in self.validmoves))
        self.add_item(boardButton(2,0,'i','i' not in self.validmoves))
        self.add_item(boardButton(0,1,'a','a' not in self.validmoves))
        self.add_item(boardButton(1,1,'s','s' not in self.validmoves))
        self.add_item(boardButton(2,1,'d','d' not in self.validmoves))
    def updateBoard(self, move):
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
            self.charac.fight(Enemy(self.charac,enemyLoc))
        elif move == 'e':
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
            return False
        for i in range(-3,4):
            for j in range(-3,4):
                if (self.charaPosition[0]+i,self.charaPosition[1]+j) not in self.board.keys():
                    self.board[(self.charaPosition[0]+i,self.charaPosition[1]+j)] = random.choices(['W','O','E'],weights=[3,5,2],k=1)[0]
        self.validmoves = getValid(self.charaPosition,self.board)
        self.clear_items()
        #self.add_item(boardButton(0,0,'t','t' not in self.validmoves))
        #self.add_item(boardButton(1,0,'w','w' not in self.validmoves))
        #self.add_item(boardButton(2,0,'i','i' not in self.validmoves))
        #self.add_item(boardButton(0,1,'a','a' not in self.validmoves))
        #self.add_item(boardButton(1,1,'s','s' not in self.validmoves))
        #self.add_item(boardButton(2,1,'d','d' not in self.validmoves))