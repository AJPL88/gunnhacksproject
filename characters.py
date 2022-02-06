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

# C Base:       10HP 10DEF  7ATK 13SPD
# Java Base:    12HP 10DEF  9ATK 10SPD
# Python Base:   9HP 10DEF 12ATK  7SPD

def expToNextLevel(clevel):
    return round((5000 / (1 + ( 2.7182818285 ** ( -1 * (clevel-40)/10)))) + 10.069)

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
    def getStorageStr(self):
        return '$'.join(map(str, [self.level, self.exp, self.health, self.defense, self.atk, self.stamina, self.speed, self.weapon, self.armor]))

class Warrior(Character):
    def __init__(self,vals=""):
        super().__init__(vals=vals,baseStats=[1])