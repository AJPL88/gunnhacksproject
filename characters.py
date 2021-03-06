import math
import random
import re
# Character is base for all classes
# HP stat
# DEF stat
# ATK stat
# STAMINA stat
# SPEED stat

# Damage Calculations:
# Damage taken: opponent atk - 1/3 of def
# Damage dealt: weapon atk + atk

# Leveling Calculations:
# Every level before l10 adds +1% stamina, +1% speed
# Level 1: Base Stats
# Level 3: +2 HP, +1 DEF, +1 ATK
# Every level after l10 adds +1 hp, +1 def, +0.5 atk, +1 stamina, +0.2 speed
# Every 10 levels, ascension: 

# Data Storage:
# string: LEVEL$EXP$HP$DEF$ATK$STAMINA$SPEED$WEAPON$ARMOR$CHARACTER
# Weapons will be graphics cards
# Armor will be monitors

# C Base:       10HP 10DEF  7ATK 10SPD
# Java Base:    12HP 10DEF  9ATK 10SPD
# Python Base:   9HP 10DEF 12ATK 10SPD

# SCALING IS PAINNNN

weaponBuffs = {
    'RTX3090': 1.7,
    'RTX3080Ti': 1.5,
    'RX6900XT': 1.4,
    'RX6800XT': 1.35,
    'RTX3080': 1.3,
    'RX6800': 1.25,
    'RTX3070Ti': 1.2,
}

armorBuffs = {
    '': 1,          # Basic
    '1GB': 1.1,     # 100 Coin
    '2GB': 1.2,     # 200 Coin
    '4GB': 1.3,     # 300 Coin
    '8GB': 1.4,     # 500 Coin
    '16GB': 1.5,    # 750 Coin
    '32GB': 1.6,    # 1000 Coin
    '64GB': 1.7,    # 1500 Coin
    '128GB': 1.8,   # 2500 Coin
    '256GB': 2,     # 4000 Coin
    '512GB': 4      # 7500 Coin
}

def expToNextLevel(clevel):
    if clevel < 40:
        return round((5000 / (1 + (math.e ** ( -1 * (clevel-41)/10)))) + 10.069)
    else:
        return 125*clevel - 2505

# \operatorname{floor}\left(\frac{100}{1+e^{-\frac{x}{20}}}-40\right)
# \operatorname{floor}\left(\frac{98}{1+e^{-\frac{x}{18}}}-37\right)
# \operatorname{floor}\left(\frac{101}{1+e^{-\frac{x}{29}}}-41\right)
def hpScaling(level,lang):
    if lang == 'C':
        if level < 80:
            return math.floor(98 / (1 + (math.e ** (-1 * ((level-1) / 18)))) - 37)
        else:
            return math.floor(0.2 * level + 43)
    elif lang == 'Java':
        if level < 100:
            return math.floor(100 / (1 + (math.e ** ( -1 * ((level-1) / 20)))) - 40)
        else:
            return math.floor(0.2 * level + 40)
    elif lang == 'Python':
        if level < 150:
            return math.floor(101 / (1 + (math.e ** (-1 * ((level-1) / 29)))) - 41)
        else:
            return math.floor(0.2 * level + 30)

def spdScaling(level):
    if level < 150:
        return round(math.e ** (level ** 0.3) + 9, 1)
    else:
        return round((level ** (1/1.2)) + 34.58, 1)

#\operatorname{floor}\left(4\left(e^{x^{0.21}}\right)+10\right)-4
def defScaling(level):
    return math.floor(4 * (math.e ** ((level-1) ** 0.21)) + 10) - 4

# \operatorname{floor}\left(\frac{\sqrt[0.35]{\ln\left(x+2\right)}\ln\left(x+2\right)}{6}+7\right)
# \operatorname{floor}\left(\frac{\sqrt[0.35]{\ln\left(x+2\right)}\ln\left(x+2\right)}{5.4}+9\right)
# \operatorname{floor}\left(\frac{\sqrt[0.35]{\ln\left(x+2\right)}\ln\left(x+2\right)}{5.3}+12\right)
def atkScaling(level,lang):
    if lang == 'C':
        return math.floor((((math.log(level + 2) ** (1/0.35)) * math.log(level + 2)) / 6) + 7)
    elif lang == 'Java':
        return math.floor((((math.log(level + 2) ** (1/0.35)) * math.log(level + 2)) / 5.4) + 9)
    elif lang == 'Python':
        return math.floor((((math.log(level + 2) ** (1/0.35)) * math.log(level + 2)) / 5.3) + 12)

class Character():
    def __init__(self,vals="",baseStats=""):
        if vals != "":
            los = re.split(r'[$]',vals)
            self.level = int(los[0])
            self.exp = int(los[1])
            self.health = int(los[2])
            self.defense = int(los[3])
            self.atk = int(los[4])
            self.stamina = int(los[5])
            self.speed = float(los[6])
            self.weapon = los[7]
            self.armor = los[8]
            self.character = los[9]
            self.atk = round(self.atk * weaponBuffs[self.weapon])
        else:
            self.level = 1
            self.exp = 0
            self.health = baseStats[0]
            self.defense = baseStats[1]
            self.atk = baseStats[2]
            self.stamina = 100
            self.speed = baseStats[3]
            self.weapon = "none"
            self.armor = "none"
            self.character = baseStats[4]
    def getStorageStr(self):
        return '$'.join(map(str, [self.level, self.exp, self.health, self.defense, self.atk, self.stamina, self.speed, self.weapon, self.armor, self.character]))
    def expDisplay(self):
        return f"Level {self.level}\n{self.exp}/{expToNextLevel(self.level)} EXP"
    def addExp(self,x):
        while self.exp + x > expToNextLevel(self.level):
            self.level += 1
            x -= expToNextLevel(self.level) - self.exp
            self.exp = 0
        self.exp += x
        self.health = hpScaling(self.level,self.character)
        self.defense = defScaling(self.level)
        self.atk = atkScaling(self.level,self.character)
        self.speed = spdScaling(self.level)

class Enemy():
    def __init__(self, chara: Character, loc: tuple):
        #self.hp = math.floor(50 / (1 + math.e ** (-1 * (math.sqrt(loc[0] ** 2 + loc[1] ** 2) - 30) / 10)) + 7.639)
        self.hp = math.floor(-1 * (((math.sqrt(loc[0]**2 + loc[1]**2) - 60)**2)/90) + 50)
        #self.atk = math.floor(math.e ** ((math.sqrt(loc[0] ** 2 + loc[1] ** 2) + 10) ** 0.43) / 16 + 8.1)
        self.atk = math.floor(math.e ** ((math.sqrt(loc[0] ** 2 + loc[1] ** 2) + 10) ** 0.43) / 4 + 5.1)
        #self.speed = math.floor(20 / (1 + math.e ** (-1 * (math.sqrt(loc[0] ** 2 + loc[1] ** 2) - 30) / 23)) + 4)
        self.speed = math.floor(20 / (1 + math.e ** (-1 * (math.sqrt(loc[0] ** 2 + loc[1] ** 2) - 30) / 18)) + 5)
        print(self.hp, self.atk, self.speed)
    def fight(self, chara: Character):
        batlog = "\n"
        while self.hp > 0 or chara.health > 0:
            tie = chara.speed == self.speed
            if tie:
                tie = random.choice([True,False])
            if chara.speed > self.speed or tie:
                self.hp -= round(chara.atk)
                batlog = batlog + f"{chara.character} deals {round(chara.atk)} damage to Bug\n"
                if self.hp <= 0:
                    batlog = batlog + f"{chara.character} has defeated Bug\n"
                    break
                chara.health -= round((self.atk - (chara.defense)/3) * armorBuffs[chara.armor])
                batlog = batlog + f"Bug deals {round((self.atk-(chara.defense)/3)*armorBuffs[chara.armor])} damage to {chara.character}\n"
                if chara.health <= 0:
                    batlog = batlog + f"{chara.character} has died to Bug. RIP :skull:\n\n"
                    break
            elif self.speed > chara.speed or not tie:
                chara.health -= round((self.atk - (chara.defense)/3) * armorBuffs[chara.armor])
                batlog = batlog + f"Bug deals {round((self.atk-(chara.defense)/3)*armorBuffs[chara.armor])} damage to {chara.character}\n"
                if chara.health <= 0:
                    batlog = batlog + f"{chara.character} has died to Bug. RIP :skull:\n\n"
                    break
                self.hp -= round(chara.atk)
                batlog = batlog + f"{chara.character} deals {round(chara.atk)} damage to Bug\n"
                if self.hp <= 0:
                    batlog = batlog + f"{chara.character} has defeated Bug\n"
                    break
        #print(batlog)
        if self.hp <= 0:
            batlog = batlog + str(random.choices([f"{chara.character} found an ULTRA RARE GRAPHICS CARD!\n",f"{chara.character} found a " + str(random.choice(["keyboard", "monitor", "mouse"])) + "!\n",""],weights=[1,20,70])[0])
        return batlog

class campaignEnemy():
    def __init__(self, name: str, chara: Character, stats: list):
        self.name = name
        self.hp = stats[0]
        self.atk = stats[1]
        self.speed = stats[2]
    def fight(self, chara: Character):
        batlog = "\n"
        while self.hp > 0 or chara.health > 0:
            tie = chara.speed == self.speed
            if tie:
                tie = random.choice([True,False])
            if chara.speed > self.speed or tie:
                self.hp -= round(chara.atk)
                batlog = batlog + f"{chara.character} deals {round(chara.atk)} damage to {self.name}\n"
                if self.hp <= 0:
                    batlog = batlog + f"{chara.character} has defeated {self.name}\n"
                    break
                chara.health -= round((self.atk - (chara.defense)/3) * armorBuffs[chara.armor])
                batlog = batlog + f"{self.name} deals {round((self.atk-(chara.defense)/3)*armorBuffs[chara.armor])} damage to {chara.character}\n"
                if chara.health <= 0:
                    batlog = batlog + f"{chara.character} has died to {self.name}. RIP :skull:\n\n"
                    break
            elif self.speed > chara.speed or not tie:
                chara.health -= round((self.atk - (chara.defense)/3) * armorBuffs[chara.armor])
                batlog = batlog + f"{self.name} deals {round((self.atk-(chara.defense)/3)*armorBuffs[chara.armor])} damage to {chara.character}\n"
                if chara.health <= 0:
                    batlog = batlog + f"{chara.character} has died to {self.name}. RIP :skull:\n\n"
                    break
                self.hp -= round(chara.atk)
                batlog = batlog + f"{chara.character} deals {round(chara.atk)} damage to {self.name}\n"
                if self.hp <= 0:
                    batlog = batlog + f"{chara.character} has defeated {self.name}\n"
                    break
        #print(batlog)
        if self.hp <= 0:
            batlog = batlog + str(random.choices([f"{chara.character} found an ULTRA RARE GRAPHICS CARD!\n",f"{chara.character} found a " + str(random.choice(["keyboard", "monitor", "mouse"])) + "!\n",""],weights=[1,20,70])[0])
        return batlog


class LanguageC(Character):
    def __init__(self,vals=""):
        super().__init__(vals=vals,baseStats=[12,10,7,10,"C"])
class LanguageJava(Character):
    def __init__(self,vals=""):
        super().__init__(vals=vals,baseStats=[10,10,9,10,"Java"])
class LanguagePython(Character):
    def __init__(self,vals=""):
        super().__init__(vals=vals,baseStats=[9,10,12,10,"Python"])

bob = LanguageC()
print(bob.getStorageStr())
print(bob.expDisplay())
bob.addExp(15)
print(bob.expDisplay())
print(bob.getStorageStr())