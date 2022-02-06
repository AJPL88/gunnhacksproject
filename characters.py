import math
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
            return math.floor(100 / (1 + (math.e ** ( -1 * (level / 20)))) - 40)
        else:
            return math.floor(0.2 * level + 43)
    elif lang == 'Java':
        if level < 100:
            return math.floor(98 / (1 + (math.e ** (-1 * (level / 18)))) - 37)
        else:
            return math.floor(0.2 * level + 40)
    elif lang == 'Python':
        if level < 150:
            return math.floor(101 / (1 + (math.e ** (-1 * (level / 29)))) - 41)
        else:
            return math.floor(0.2 * level + 30)

def spdScaling(level):
    if level < 150:
        return round(math.e ** (level ** 0.3) + 9, 1)
    else:
        return round((level ** (1/1.2)) + 34.58, 1)

#\operatorname{floor}\left(4\left(e^{x^{0.21}}\right)+10\right)-4
def defScaling(level):
    return math.floor(4 * (math.e ** (level ** 0.21)) + 10) - 4

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
            self.exp = int(los[0])
            self.health = int(los[2])
            self.defense = int(los[3])
            self.atk = int(los[4])
            self.stamina = int(los[5])
            self.speed = int(los[6])
            self.weapon = los[7]
            self.armor = los[8]
            self.character = los[9]
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

class LanguageC(Character):
    def __init__(self,vals=""):
        super().__init__(vals=vals,baseStats=[10,10,7,13,"C"])
class LanguageJava(Character):
    def __init__(self,vals=""):
        super().__init__(vals=vals,baseStats=[12,10,9,10,"Java"])
class LanguagePython(Character):
    def __init__(self,vals=""):
        super().__init__(vals=vals,baseStats=[9,10,12,7,"Python"])

bob = LanguageC()
print(bob.getStorageStr())
print(bob.expDisplay())
bob.addExp(1000000000)
print(bob.expDisplay())
print(bob.getStorageStr())