#! Robopocolypse 1.1
#  [4-27-10]
#  View system - Matthew Belland
#    -Including the Camera class and its implementation
#    -Keeps the game screen generally focused on the players




import pygame, os, sys, math, time, random, addangle
from pygame.locals import *

# set up pygame
#MusicStarting - Jon - [04/23/10]
pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_volume(1.0)
pygame.mixer.music.load('Music/songfornoone.ogg')
pygame.mixer.music.play()



# set up fonts and colors
titleFontsize = 72
titleFont = pygame.font.SysFont('Batang.ttf',titleFontsize)
messageFontsize = 48
messageFont = pygame.font.SysFont('perfectdarkzero.ttf', messageFontsize)
statFontsize = 24
statFont = pygame.font.SysFont('perfectdarkzero.ttf', statFontsize)
#Wave Font - Jon - [04/27/10]
waveFontsize = 48
waveFont = pygame.font.SysFont('perfectdarkzero.ttf',waveFontsize)
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)

#! set up window
AREAWIDTH = 2400/2
AREAHEIGHT = 1600/2
WINDOWWIDTH = 1200
WINDOWHEIGHT = 800
areaSurface = pygame.Surface((AREAWIDTH, AREAHEIGHT), 0, 32)
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('ROBOPOCALYPSE')

# set up controller variables - Travis
if sys.platform == 'win32' or sys.platform == 'win64':
    Windows = True
else:
    Windows = False

if Windows == True:
    LStickX = 0
    LStickY = 1
    RStickX = 4
    RStickY = 3
    AButton = 0
    Start = 7
else:
    #Mac
    LStickX = 0
    LStickY = 1
    RStickX = 2
    RStickY = 3
    AButton = 11
    Start = 4


#Effects
    effects = ['slow','speed','magnet','stun']


def effect_func(character,effect,time):

    if effect == 'slow':
        character.movespeed -= 4
    if effect == 'speed':
        character.movespeed += 4
        pygame.mixer.Sound('Music/speedboost.ogg')
    if effect == 'stun':
        character.canmove = False
    character.effect = effect
    character.effect_timer = time
        
        


def remove_effect(character,effect):

    if effect == 'slow':
        character.movespeed += 4
    if effect == 'speed':
        character.movespeed -= 4
    if effect == 'stun':
        character.canmove = True
    character.effect = None


# CLASSES

class Character(object):

    """ An entity that moves such as a player or enemy; has an xy position, 
    a size, a movement speed, an angle of rotation, health, maximum     
    health, a boolean movement variable, an amount of damage taken. """

    def __init__(self):
        self.xpos = AREAWIDTH / 2
        self.ypos = AREAHEIGHT / 2
        self.size = 40
        self.movespeed = 2
        self.angle = 90
        self.health = 100
        self.maxhealth = 100
        self.canmove = True
        self.damage = 0
        self.image = None
        self.effect = None
        self.effect_timer = 0

    def drop_pickup(self):
        # drops a pickup upon the character's death based on probabilities
        # that are dependent on the number of players
        for key in pickup_probs.keys():
            if random.randint(1,1000) <= pickup_probs[key]:
                if key == 'health':
                    pickups.append(MedSupplies(self.xpos,self.ypos))
                if key == 'scrap':
                    pickups.append(Scrap(self.xpos,self.ypos))
                if key == 'mg':
                    pickups.append(MGPickup(self.xpos,self.ypos))
                if key == 'sg':
                    pickups.append(SGPickup(self.xpos,self.ypos))
                if key == 'EMP':
                    pickups.append(EMPPickup(self.xpos,self.ypos))
                if key == "Lazergun":
                    pickups.append(LazergunPickup(self.xpos, self.ypos))
                if key == 'Boost':
                    pickups.append(Boost(self.xpos,self.ypos))
                break


class Player(Character):

    """ A playable character; has a controller, a boolean healing variable,
    a weapon, an image file, and an id number. """

    def __init__(self,num):
        Character.__init__(self)
        self.controller = pygame.joystick.Joystick(num)
        self.controller.init()
        self.movespeed = 6
        self.healing = False
        self.being_healed = False
        self.weapon = None
        self.image = pygame.image.load('dude%d.png' % (num + 1))
        self.id = num + 1
        # size values added by Matt [4-27-10]
        self.width = 90
        self.height = 90

    def get_vel(self):
        # returns the x and y velocities of the player in a tuple
        magnitude = self.controller.get_axis(LStickX)**2+self.controller.get_axis(LStickY)**2
        if magnitude > 0.055:
            xvel = (self.movespeed * self.controller.get_axis(LStickX) * -1 * abs(self.controller.get_axis(LStickX))) / magnitude
            yvel = (self.movespeed * self.controller.get_axis(LStickY) * -1 * abs(self.controller.get_axis(LStickY))) / magnitude
            return (xvel,yvel)
        return (0,0)

    def get_angle(self):
        # returns the player's angle of rotation
        if abs(self.controller.get_axis(RStickX))**2+abs(self.controller.get_axis(RStickY))**2 > 0.055:
            return addangle.get_angle((self.controller.get_axis(RStickX),-1 * self.controller.get_axis(RStickY)))

    def is_shooting(self):
        # returns whether or not the player is shooting
        if self.canmove and abs(self.controller.get_axis(RStickX))**2+abs(self.controller.get_axis(RStickY))**2 > 0.5:
            return True
        return False
    
    def is_holding(self):
        # returns whether or not the player is performing the hold action (A button)
        if self.controller.get_button(AButton) == 1:
            return True
        return False


class RoboGrunt(Character):

    """ Standard robotic foe. Folloes a random player. Does damage only by
    touching the player. """
    
    def __init__(self,x,y):
        Character.__init__(self)
        self.xpos = x
        self.ypos = y
        self.movespeed = 3
        self.health = 8
        self.maxhealth = 8
        self.strength = 8 # Damage done by the robot
        self.image = pygame.image.load('Roboinfantry.png')
        self.target = None # Player to follow
        self.has_gun = False # Boolean gun variable
        self.get_target()
        self.kickback = 10
        self.worth = 100
        #self.attacktimer = 40

    def get_vel(self):
        # Outputs the direction the grunt must travel to approach a given player.
        dist = math.sqrt((self.xpos - self.target.xpos)**2 + (self.ypos - self.target.ypos)**2)
        xvel = self.movespeed * (self.xpos - self.target.xpos) / dist
        yvel = self.movespeed * (self.ypos - self.target.ypos) / dist
        return (xvel,yvel)

    def get_angle(self):
        # Outputs the angle to which the grunt must be turned if it is to walk forward.
        vels = self.get_vel()
        return 360 - addangle.get_angle((vels))

    def get_target(self):
        # Targets closest player
        targetdist = 0
        for player in players:
            dist = math.sqrt((self.xpos - player.xpos)**2 + (self.ypos - player.ypos)**2)
            if targetdist == 0 or dist < targetdist:
                self.target = player
                targetdist = dist


class LaserBot(Character):

    """ A robot that attacks from a distance. Has a rate of fire. """

    def __init__(self,x,y):
        Character.__init__(self)
        self.xpos = x
        self.ypos = y
        self.movespeed = 4
        self.health = 8
        self.maxhealth = 8
        self.strength = 5
        self.image = pygame.image.load('Robogun.png')
        self.target = None
        self.has_gun = True
        self.rof = 80
        self.count = 80
        self.get_target()
        self.kickback = 10
        self.worth = 200

    def get_vel(self):
        dist = math.sqrt((self.xpos - self.target.xpos)**2 + (self.ypos - self.target.ypos)**2)
        if dist > 600 or self.xpos < 0 or self.xpos > WINDOWWIDTH or self.ypos < 0 or self.ypos > WINDOWHEIGHT:
            k = 1
        elif dist < 150 and self.xpos > 0 and self.xpos < WINDOWWIDTH and self.ypos > 0 and self.ypos < WINDOWHEIGHT:
            k = -1
        else:
            k = 0
        xvel = k * self.movespeed * (self.xpos - self.target.xpos) / dist
        yvel = k * self.movespeed * (self.ypos - self.target.ypos) / dist
        return (xvel,yvel)

    def get_angle(self):
        return 360 - addangle.get_angle((self.xpos - self.target.xpos,self.ypos - self.target.ypos))

    def shoot_laser(self):
        # Fires a bullet
        dist = math.sqrt((self.xpos - self.target.xpos)**2 + (self.ypos - self.target.ypos)**2)
        x = self.xpos
        y = self.ypos
        direction = ((self.xpos - self.target.xpos)/dist,(self.ypos - self.target.ypos)/dist)
        robobullets.append(RoboBullet(x,y,direction))
        #Adding sound effects - Jon - [04/27/2010]
        sound_effect1 = pygame.mixer.Sound('Music/lasershot.ogg')
        sound_effect1.set_volume(.1)
        sound_effect1.play()
        

    def is_shooting(self):
        # Boolean shoot function; only True if bot is not moving
        if self.get_vel() == (0,0):
            return True
        return False

    def get_target(self):
        # Targets closest player
        targetdist = 0
        for player in players:
            dist = math.sqrt((self.xpos - player.xpos)**2 + (self.ypos - player.ypos)**2)
            if targetdist == 0 or dist < targetdist:
                self.target = player
                targetdist = dist

class TheBoss(Character):

    """ A robot that attacks from a distance. Has a rate of fire. """

    def __init__(self,x,y):
        Character.__init__(self)
        self.xpos = x
        self.ypos = y
        self.movespeed = 6
        self.health = 40
        self.maxhealth = 40
        self.strength = 9
        self.image = pygame.image.load('boss.png')
        self.target = None
        self.has_gun = True
        self.rof = 60
        self.count = 80
        self.get_target()
        self.kickback = 20
        self.worth = 1000

    def get_vel(self):
        dist = math.sqrt((self.xpos - self.target.xpos)**2 + (self.ypos - self.target.ypos)**2)
        if dist > 600 or self.xpos < 0 or self.xpos > WINDOWWIDTH or self.ypos < 0 or self.ypos > WINDOWHEIGHT:
            k = 1
        elif dist < 150 and self.xpos > 0 and self.xpos < WINDOWWIDTH and self.ypos > 0 and self.ypos < WINDOWHEIGHT:
            k = 1
        else:
            k = 1
        xvel = k * self.movespeed * (self.xpos - self.target.xpos) / dist
        yvel = k * self.movespeed * (self.ypos - self.target.ypos) / dist
        return (xvel,yvel)

    def get_angle(self):
        return 360 - addangle.get_angle((self.xpos - self.target.xpos,self.ypos - self.target.ypos))

    def shoot_laser(self):
        # Fires a bullet
        dist = math.sqrt((self.xpos - self.target.xpos)**2 + (self.ypos - self.target.ypos)**2)
        x = self.xpos
        y = self.ypos
        direction = ((self.xpos - self.target.xpos)/dist,(self.ypos - self.target.ypos)/dist)
        robobullets.append(RoboBullet(x,y,direction))
        #Adding sound effects - Jon - [04/27/2010]
        sound_effect1 = pygame.mixer.Sound('Music/lasershot.ogg')
        sound_effect1.set_volume(.1)
        sound_effect1.play()
        

    def is_shooting(self):
        return True

    def get_target(self):
        # Targets closest player
        targetdist = 0
        for player in players:
            dist = math.sqrt((self.xpos - player.xpos)**2 + (self.ypos - player.ypos)**2)
            if targetdist == 0 or dist < targetdist:
                self.target = player
                targetdist = dist




# Jon and Matt [4-27-10]
class RoboLeech(Character):

    """ A robot that chases a player very quickly. """

    def __init__(self,x,y):
        Character.__init__(self)
        self.xpos = x
        self.ypos = y
        self.movespeed = 8
        self.health = 1
        self.maxhealth = 1
        self.strength = 1
        self.image = pygame.image.load('RoboLeech.png')
        self.target = None
        self.has_gun = False
        self.rof = 0
        self.count = 80
        self.get_target()
        self.kickback = 0
        self.worth = 150

    def get_vel(self):
        # Outputs the direction the grunt must travel to approach a given player.
        dist = math.sqrt((self.xpos - self.target.xpos)**2 + (self.ypos - self.target.ypos)**2)
        xvel = self.movespeed * (self.xpos - self.target.xpos) / dist
        yvel = self.movespeed * (self.ypos - self.target.ypos) / dist
        return (xvel,yvel)

    def get_angle(self):
        # Outputs the angle to which the grunt must be turned if it is to walk forward.
        vels = self.get_vel()
        return 360 - addangle.get_angle((vels))

    def get_target(self):
        # Targets closest player
        targetdist = 0
        for player in players:
            dist = math.sqrt((self.xpos - player.xpos)**2 + (self.ypos - player.ypos)**2)
            if targetdist == 0 or dist < targetdist:
                self.target = player
                targetdist = dist



class RoboBomb(Character):

    """ A robot that blows up """

    def __init__(self,x,y):
        Character.__init__(self)
        self.xpos = x
        self.ypos = y
        self.movespeed = 5
        self.health = 16
        self.maxhealth = 16
        self.strength = 20
        self.image = pygame.image.load('RoboBomb.png')
        self.target = None
        self.has_gun = False
        self.rof = 1
        self.count = 80
        self.get_target()
        self.kickback = 15
        self.worth = 200

    def get_vel(self):
        # Outputs the direction the grunt must travel to approach a given player.
        dist = math.sqrt((self.xpos - self.target.xpos)**2 + (self.ypos - self.target.ypos)**2)
        xvel = self.movespeed * (self.xpos - self.target.xpos) / dist
        yvel = self.movespeed * (self.ypos - self.target.ypos) / dist
        return (xvel,yvel)

    def get_angle(self):
        # Outputs the angle to which the grunt must be turned if it is to walk forward.
        vels = self.get_vel()
        return 360 - addangle.get_angle((vels))

    def get_target(self):
        # Targets closest player
        targetdist = 0
        for player in players:
            dist = math.sqrt((self.xpos - player.xpos)**2 + (self.ypos - player.ypos)**2)
            if targetdist == 0 or dist < targetdist:
                self.target = player
                targetdist = dist
    def blowup(self):
        # blows itself up
        
        x = self.xpos
        y = self.ypos
        
        

        #Adding sound effects - Jon - [04/27/2010]
        sound_effect1 = pygame.mixer.Sound('Music/lasershot.ogg')
        sound_effect1.set_volume(.1)
        sound_effect1.play()




        
class Weapon(object):

    """ Weapons in the game. Has an amount of ammunition, a rate of fire, and a
    count - the time before it can fire again. """

    def __init__(self):
        self.ammo = 500
        self.rof = 8
        self.count = self.rof

class Rifle(Weapon):

    """ A standard weapon. Has infinite ammo and a rate of fire of 8. """

    def __init__(self):
        Weapon.__init__(self)
        self.ammo = float('infinity')

    def fire(self,x,y,direction):
        # fires a single bullet
        bullets.append(RifleBullet(x,y,direction))
        #Adding sound effects - Jon - [04/27/2010]
        sound_effect2 = pygame.mixer.Sound('Music/rifle.ogg')
        sound_effect2.set_volume(.1)
        sound_effect2.play()


class MachineGun(Weapon):

    """ A rapid-fire weapon. Holds 400 bullets and has a rate of fire of 3. """
    
    def __init__(self):
        Weapon.__init__(self)
        self.ammo = 400
        self.rof = 3

    def fire(self,x,y,direction):
        # fires a single bullet
        bullets.append(MGBullet(x,y,direction))
        #Adding sound effects - Jon - [04/27/2010]
        sound_effect3 = pygame.mixer.Sound('Music/machinegun.ogg')
        sound_effect3.set_volume(.1)
        sound_effect3.play()


class ShotGun(Weapon):

    """ A shotgun. Has a much slower rate of fire and less ammo. """

    def __init__(self):
        Weapon.__init__(self)
        self.ammo = 100
        self.rof = 25
        self.count = self.rof

    def fire(self,x,y,direction):
        # fires five equally-spaced bullets within ten degrees of the
        # aiming direction
        new_directions = []
        new_directions.append(addangle.addangle(direction,-10))
        new_directions.append(addangle.addangle(direction,-6.6))
        new_directions.append(addangle.addangle(direction,-3.3))
        new_directions.append((direction))
        new_directions.append(addangle.addangle(direction,3.3))
        new_directions.append(addangle.addangle(direction,6.6))
        new_directions.append(addangle.addangle(direction,10))
        for element in new_directions:
            bullets.append(SGBullet(x,y,element))
        #Adding sound effects - Jon - [04/27/2010]
        sound_effect4 = pygame.mixer.Sound('Music/shotgun.ogg')
        sound_effect4.set_volume(.1)
        sound_effect4.play()
#EMP-Author: Jon - [04/26/10]
class EMP(Weapon):

    """An EMP takes out all the robots (except the boss) on the screen. """

    
    def __init__(self):
        Weapon.__init__(self)
        self.ammo = 1
        self.rof = 1
        self.count = self.rof

    def fire(self,x,y,direction):
        for robot in robots:
            robot.health = 0
        #Adding sound effects - Jon - [04/27/2010]
        sound_effect5 = pygame.mixer.Sound('Music/emp.ogg')
        sound_effect5.set_volume(.1)
        sound_effect5.play()

#! Lazergun - Jon - [04/27/2010]
class Lazergun(Weapon):

    """Shoots through all enemies"""

    def __init__(self):
        Weapon.__init__(self)
        self.ammo = 50
        self.rof = 5
        self.count = self.rof

    def fire(self, x, y, direction):
        # fires a single bullet
        LazerBullets.append(LazergunBullet(x,y,direction))
        #Adding sound effects - Jon - [04/27/2010]
        sound_effect3 = pygame.mixer.Sound('Music/lazergun.ogg')
        sound_effect3.set_volume(.4)
        sound_effect3.play()
        
        
        


class Bullet(object):

    """The projectile fired from a particular gun. """

    def __init__(self,x,y,direction):
        self.xpos = x
        self.ypos = y
        self.size = 3
        self.direction = direction
        self.movespeed = 20
        self.strength = 4

class RifleBullet(Bullet):

    """ Standard rifle bullet. """

    def __init__(self,x,y,direction):
        Bullet.__init__(self,x,y,direction)

    def draw(self):
        pygame.draw.circle(areaSurface,WHITE,(self.xpos,self.ypos),self.size,0)


class MGBullet(Bullet):

    """ Machine gun bullet, weaker but faster than rifle bullets."""
    
    def __init__(self,x,y,direction):
        Bullet.__init__(self,x,y,direction)
        self.strength = 2
        self.movespeed = 25

    def draw(self):
        pygame.draw.circle(areaSurface,WHITE,(self.xpos,self.ypos),self.size,0)


class SGBullet(Bullet):

    """ Shotgun shot, smaller, weaker, and faster than MG bullets. """

    def __init__(self,x,y,direction):
        Bullet.__init__(self,x,y,direction)
        self.size = 2
        self.strength = 2
        self.movespeed = 30

    def draw(self):
        pygame.draw.circle(areaSurface,WHITE,(self.xpos,self.ypos),self.size,0)


class RoboBullet(Bullet):

    """ Robot ammo - slow, but large and powerful. """

    def __init__(self,x,y,direction):
        Bullet.__init__(self,x,y,direction)
        self.size = 12
        self.movespeed = 8
        self.strength = 15

    def draw(self):
        pygame.draw.circle(areaSurface,RED,(self.xpos,self.ypos),self.size,0)

class BossBullet(Bullet):

    def __init__(self, x, y, direction):
        Bullet.__init__(self, x, y, direction)
        self.size = 18
        self.movespeed = 10
        self.strength = 24

    def draw(self):
        pygame.draw.circle(areaSurface, RED, (self.xpos, self.ypos), self.size,0)




#! LazergunBullet - Jon - 04/27/10
class LazergunBullet(Bullet):

    def __init__(self, x, y, direction):
        Bullet.__init__(self, x, y, direction)
        self.size = 10
        self.movespeed = 20
        self.strength = 15
        self.angle = addangle.get_angle(direction)

    def draw(self):
        image = pygame.image.load('laserbullet.bmp')
        image.set_colorkey(WHITE)
        image = pygame.transform.rotate(image,360-self.angle)
        rect = pygame.Rect(self.xpos - self.size/2,self.ypos - self.size/2,self.size,self.size)
        areaSurface.blit(image,rect)


class Bank(object):

    """ The pool from which players draw their extra health and scrap. """

    def __init__(self):
        self.health_pool = 100 # Starting health pool
        self.scrap_pool = 10 # Starting scrap


class Pickup(object):

    """ Things that you can pick up like weapons, med supplies, and scrap. """

    def __init__(self,x,y):
        self.xpos = x
        self.ypos = y
        self.size = 30

class MedSupplies(Pickup):

    """ Adds to the health pool. """

    def __init__(self,x,y):
        Pickup.__init__(self,x,y)
        possible_values = [10,20,30,40,50]
        self.value = possible_values[random.randint(0,4)]
        self.image = pygame.image.load('medpack.bmp')

    def func(self,player):
        if difficulty == 1:
            players[0].health += self.value
        else:
            playerbank.health_pool += self.value

        sound_effect12 = pygame.mixer.Sound('Music/healthpack.ogg')
        sound_effect12.set_volume(1.0)
        sound_effect12.play()

class Scrap(Pickup):

    """ Adds to the scrap pool. """

    def __init__(self,x,y):
        Pickup.__init__(self,x,y)
        possible_values = [1,2,3,4,5]
        self.value = possible_values[random.randint(0,4)]
        self.image = pygame.image.load('scrap.png')

    def func(self,player):
        playerbank.scrap_pool += self.value

class Boost(Pickup): #-Travis & Tom

    """ Makes the player faster for a short duration """

    def __init__(self, x, y):
        Pickup.__init__(self, x, y)
        self.image = pygame.image.load('Boost.png')
    def func(self,player):
        effect_func(player,'speed',600)

    sound_effect13 = pygame.mixer.Sound('Music/speedboost.ogg')
    sound_effect13.set_volume(1.0)
    sound_effect13.play()

class MGPickup(Pickup):

    """ Gives the player a new machine gun. """

    def __init__(self,x,y):
        Pickup.__init__(self,x,y)
        self.image = pygame.image.load('MachineGun.png')

    def func(self,player):
        player.weapon = MachineGun()

class SGPickup(Pickup):

    """ Gives the player a new shotgun. """

    def __init__(self,x,y):
        Pickup.__init__(self,x,y)
        self.image = pygame.image.load('Shotgun.png')

    def func(self,player):
        player.weapon = ShotGun()


#EMP Pickup - Jon - [04/26/10]
class EMPPickup(Pickup):

    """Gives the player an EMP"""

    def __init__(self,x,y):
        Pickup.__init__(self,x,y)
        self.image = pygame.image.load('emp.bmp')

    def func(self,player):
        player.weapon = EMP()

#!LazerGunPickup - Jon - 04/27/10
class LazergunPickup(Pickup):

    """Gives the player a Lasergun!"""

    def __init__(self, x, y):
        Pickup.__init__(self, x, y)
        self.image = pygame.image.load('lazergun.png')

    def func(self,player):
        player.weapon= Lazergun()


class Explosion(object):

    def __init__(self,x,y):
        self.xpos = x
        self.ypos = y
        self.size = 80.
        self.image = pygame.image.load('Explosion.png')
        self.time = 12.

    def draw(self):
        scale = self.time/12.
        rect = pygame.rect.Rect(self.xpos - scale*self.size/2,self.ypos - scale*self.size/2, scale*self.size, scale*self.size)
        image = pygame.transform.rotozoom(self.image,0,scale)
        image.set_colorkey(BLACK)
        areaSurface.blit(image,rect)


#! View class - Matt [4-27-10]
class cameraView():
    def __init__(self, width = WINDOWWIDTH, height = WINDOWHEIGHT):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
    def setLeft(self, x):
        self.x = x
    def setTop(self, y):
        self.y = y
    def setRight(self, x):
        self.x = x - self.width
    def setBottom(self, y):
        self.y = y - self.height
    def getLeft(self):
        return self.x
    def getTop(self):
        return self.y
    def getRight(self):
        return self.x + self.width
    def getBottom(self):
        return self.y + self.height

# On-screen message system - Matt [4-28-10]
class screenMessage():
    def __init__(self, text, textRect, counter):
        self.text = text
        self.textRect = textRect
        self.counter = counter
    def draw(self):
        windowSurface.blit(self.text,self.textRect)
        self.counter -= 1


# set up lists of players, bullets, robots, and pickups
players = []
total_score = 0
bullets = []
robobullets = []
LazerBullets = []
BossBullets=[]
robots = []
pickups = []
explosions = []
messages = []
#playlist [Jon - 4/23/10]
playlist = ['Music/mapoftheproblematique.ogg', 'Music/uprising.ogg',
            'Music/hysteria.ogg', 'Music/sunburn.ogg',
            'Music/panicswitch.ogg',  'Music/hypnotize.ogg', 'Music/chopsuey.ogg',
            'Music/genocide.ogg','Music/alliwant.ogg', 
            'Music/stylo.ogg','Music/comforteagle.ogg']

injury_playlist = ['Music/injury.ogg', 'Music/curse.ogg', 'Music/ouch.ogg',
                   'Music/dierobotbitch.ogg', 'Music/getoffme.ogg', 'Music/grunt.ogg'
                   'Music/myarm.ogg', 'Music/timeout']
random.shuffle(playlist)



# set up the bank and healing rate
playerbank = Bank()
healrate = 1

# laserbot probability
lbprob = 7
# roboleech probability
rlprob = 50

# set up gameplay variables
game_start = False
game_pause = False


# GAME LOOP

song_number = 0

pygame.joystick.init()

#! Matt [4-27-10]
camera = cameraView()
pygame.display.toggle_fullscreen()

while True:
    # check for QUIT
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit(0)
    #Playlist loop - Jon [04/26/10]    
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load(playlist[song_number])
        pygame.mixer.music.play()
        song_number +=1
            
       
            

    # initialize controllers
    for controller in range(pygame.joystick.get_count()):
        if not pygame.joystick.Joystick(controller).get_init():
            pygame.joystick.Joystick(controller).init()

    # create background image
    background = pygame.transform.scale(pygame.image.load('background.bmp'),(AREAWIDTH,AREAHEIGHT))
    areaSurface.blit(background,pygame.Rect(0,0,AREAWIDTH,AREAHEIGHT))

    # displays menu screen
    if not game_start:

        windowSurface.fill(BLACK)
        
        # displays menu text
        #Title Picture - Jon - [04/27/10]
        main_text = pygame.image.load('title.png')
        textRect = main_text.get_rect()
        textRect.centerx = 600
        textRect.centery = 150
        windowSurface.blit(main_text, textRect)
        #windowSurface.set_colorkey(BLACK) # Jon - [4/27/10]
        
        #Begin Picture - Jon - [04/27/10]
        start_text = pygame.image.load('startbegin.png')
        textRect = start_text.get_rect()
        textRect.centerx = 600
        textRect.centery = 200
        windowSurface.blit(start_text,textRect)

        controller_text = pygame.image.load('controller.png')
        textRect = controller_text.get_rect()
        textRect.centerx = 630
        textRect.centery = 600
        windowSurface.blit(controller_text, textRect)



        for controller in range(pygame.joystick.get_count()):
            if pygame.joystick.Joystick(controller).get_button(Start) == 1:
                # starts the game if a player presses 'Start'
                game_start = True
                #Stopping Menu Music and starting Game Music - Jon - [04/26/10]
                pygame.mixer.music.stop()
                #Displaying Wave 1 - Jon and Matt [04/27/10]
                max_wave = 0
                if 1 > max_wave:
                    font = pygame.font.Font("batman.ttf", 36)
                    text = font.render("Wave 1", True, WHITE)
                    textRect = text.get_rect()
                    textRect.centerx = windowSurface.get_rect().centerx
                    textRect.centery = windowSurface.get_rect().centery + messageFontsize
                    messages.append(screenMessage(text, textRect, 100))
                
                # set up counts
                game_pause_count = 0
                game_over_count = 0
                # sets up game clock
                game_seconds = 0
                game_clock = pygame.time.Clock()
                # set up controllers, starting points, starting weapons,
                # images, and player id's
                for i in range(pygame.joystick.get_count()):
                    pygame.joystick.Joystick(i).init()
                    players.append(Player(i))
                    players[i].xpos = (i + 1) * AREAWIDTH / 5
                    players[i].weapon = Rifle()
                    
                # sets up difficulty variable
                difficulty = len(players)
                
                # sets up pickup probabilities
                pickup_probs = {'health': 8 + 5 * difficulty,
                                'Boost': 4 + 5 * difficulty,
                                #'scrap': 40 + 10 * difficulty,
                                'mg': 10 + 5 * difficulty,
                                'sg': 8 + 5 * difficulty,
                                'EMP': 1 + difficulty,
                                'Lazergun': 1.5 + 5*difficulty}

                # set up how often robots spawn
                base_robotspawntime = 28 - 5 * difficulty
                robotcount = 28 - 5 * difficulty
                
        pygame.display.update()
                
                
    if game_start:

        game_pause_count += 1

        if game_pause:
            for controller in range(pygame.joystick.get_count()):
                # toggles pause if the player presses start
                if pygame.joystick.Joystick(controller).get_button(Start) == 1:
                    if game_pause_count >= 25:
                        game_pause = False
                        game_pause_count = 0
                        game_clock.tick(40)
          
                        
        if not game_pause:
            
            for controller in range(pygame.joystick.get_count()):
                # toggles pause if the player presses start
                if pygame.joystick.Joystick(controller).get_button(Start) == 1:
                    if game_pause_count >= 25:
                        game_pause = True
                        game_pause_count = 0
                        game_clock.tick(40)
                        
            robotspawntime = base_robotspawntime

            #for n in range(5):
             #   if game_seconds > 300:
              #      for robot in robots:
               #         robot.health = 0
               # side = random.randint(0,3)
               # spawnx = camera.getLeft() + random.randint(0,WINDOWWIDTH)
               # spawny = camera.getTop() - 50
               # robots.append(TheBoss(spawnx, spawny))


            for n in range(1,5):
                # creates a break between waves
                if game_seconds < n * 120 and game_seconds > (n * 120 - 5):
                    robotcount = 0
                    #Display Which Wave You are on - Jon and Matt - [04/27/2010]
                    if n > max_wave:
                        max_wave = n
                        next_wave_text = font.render('Wave '+str(n+1), True, WHITE)
                        textRect = next_wave_text.get_rect()
                        textRect.centerx = windowSurface.get_rect().centerx
                        textRect.centery = windowSurface.get_rect().centery
                        messages.append(screenMessage(next_wave_text, textRect, 100))
                    
                # makes each wave harder
                if game_seconds > n * 120:
                    robotspawntime = (base_robotspawntime - (n * 3))

            # spawn robots from a random side of the screen
            # Camera adaptation added by Matt [4-27-10]
            if robotcount >= robotspawntime:
                side = random.randint(0,3)
                if side == 0:
                    spawnx = camera.getLeft() + random.randint(0,WINDOWWIDTH)
                    spawny = camera.getTop() - 50
                if side == 1:
                    spawnx = camera.getLeft() + WINDOWWIDTH + 50
                    spawny = camera.getTop() + random.randint(0,WINDOWHEIGHT)
                if side == 2:
                    spawnx = camera.getLeft() + random.randint(0,WINDOWWIDTH)
                    spawny = camera.getTop() + WINDOWHEIGHT + 50
                if side == 3:
                    spawnx = camera.getLeft() - 50
                    spawny = camera.getTop() + random.randint(0,WINDOWHEIGHT)
                if random.randint(1,100) >= lbprob:
                    robots.append(RoboGrunt(spawnx,spawny))
                elif random.randint(1,100) >= rlprob:
                    robots.append(RoboLeech(spawnx,spawny))
                else:
                    robots.append(LaserBot(spawnx,spawny))
                robotcount = 0


            for player in players:
                # determines if player can move
                if player.healing or player.being_healed:
                    player.canmove = False
                else:
                    player.canmove = True
                # move player
                if player.canmove:
                    totalvel = player.get_vel()
                    player.xpos -= totalvel[0]
                    player.ypos -= totalvel[1]
                    # rotate player
                    if player.get_angle() != None:
                        player.angle = player.get_angle()
                # pick up pickups
                for pickup in pickups:
                    if (pickup.xpos - player.xpos)**2 + (pickup.ypos - player.ypos)**2 <= pickup.size**2:
                        pickup.func(player)
                        pickups.remove(pickup)
                # deal damage from robots
                for robot in robots:
                    if (robot.xpos - player.xpos)**2 + (robot.ypos - player.ypos)**2 <= ((robot.size + player.size)/2)**2:
                        player.damage += robot.strength
                        player.xpos -= robot.kickback * robot.get_vel()[0]
                        player.ypos -= robot.kickback * robot.get_vel()[1]
                        #! Sound Effect - Jon 
                        sound_effect7 = pygame.mixer.Sound(random.choice(injury_playlist))
                        sound_effect7.set_volume(1.0)
                        sound_effect7.play()
                for bullet in robobullets:
                    if (bullet.xpos - player.xpos)**2 + (bullet.ypos - player.ypos)**2 <= ((bullet.size + player.size)/2)**2:
                        player.damage += bullet.strength
                        player.xpos -= 8 * bullet.direction[0]
                        player.ypos -= 8 * bullet.direction[1]
                        robobullets.remove(bullet)
                        #Sound Effect - Jon
                        sound_effect8 = pygame.mixer.Sound(random.choice(injury_playlist))
                        sound_effect8.set_volume(1.0)
                        sound_effect8.play()

                for bullet in BossBullets:
                    if (bullet.xpos - player.xpos)**2 + (bullet.ypos - player.ypos)**2 <= ((bullet.size + player.size)/2)**2:
                        player.damage += bullet.strength
                        player.xpos -= 8 * bullet.direction[0]
                        player.ypos -= 8 * bullet.direction[1]
                        robobullets.remove(bullet)
                        #Sound Effect - Jon
                        sound_effect9 = pygame.mixer.Sound(random.choice(injury_playlist))
                        sound_effect9.set_volume(1.0)
                        sound_effect9.play()
                    

                player.health -= player.damage
                for other_player in players:
                    if other_player != player:
                        # heals other players
                        if player.is_holding():
                            if not player.being_healed or not other_player.healing:
                                if (player.xpos - other_player.xpos)**2 + (player.ypos - other_player.ypos)**2 <=  (5 + player.size + other_player.size)**2:
                                    player.healing = True
                                    other_player.being_healed = True
                                    break
                                else:
                                    player.healing = False
                                    other_player.being_healed = False
                        elif other_player.is_holding():
                            # determines if player is being healed
                            if not other_player.being_healed or not player.healing:
                                if (player.xpos - other_player.xpos)**2 + (player.ypos - other_player.ypos)**2 <=  (5 + player.size + other_player.size)**2:
                                    other_player.healing = True
                                    player.being_healed = True
                                    break
                                else:
                                    other_player.healing = False
                                    player.being_healed = False
                        else:
                            player.healing = False
                            player.being_healed = False
                    else:
                        player.healing = False
                        player.being_healed = False                    
                # heal player
                if player.health < player.maxhealth:
                    if playerbank.health_pool >0:
                        if player.being_healed:
                            player.health += healrate
                            playerbank.health_pool -= healrate
                if player.health > player.maxhealth:
                    player.health = player.maxhealth
                if player.health < 0:
                    player.health = 0
                player.damage = 0
                if player.health <= 0:
                    # remove dead player
                    players.remove(player)
                    #more sound effects - Jon
                    sound_effect9 = pygame.mixer.Sound('Music/no.ogg')
                    sound_effect9.set_volume(1.0)
                    sound_effect9.play()
                if player.is_shooting():
                    # fire player's weapon
                    if player.weapon.ammo > 0:
                        if player.weapon.count >= player.weapon.rof:
                            bullet_magnitude = player.controller.get_axis(RStickY)**2 + player.controller.get_axis(RStickX)**2
                            bullet_direction = (-1 * player.controller.get_axis(RStickX) / bullet_magnitude, -1 * player.controller.get_axis(RStickY) / bullet_magnitude)
                            
                            player.weapon.fire(player.xpos+16,player.ypos+16,bullet_direction)
                            player.weapon.count = 0
                            player.weapon.ammo -= 1
                            if player.weapon.ammo < 0:
                                player.weapon.ammo = 0
                            if player.weapon.ammo == 0:
                                player.weapon = Rifle()
                player.weapon.count += 1


            for robot in robots:
                # acquire new target if previous target has died; if a laserbot,
                # target closest player
                if robot.target == None or robot.target.health == 0 or robot.has_gun:
                    robot.get_target()
                # move robot
                robot.xpos -= robot.get_vel()[0]
                robot.ypos -= robot.get_vel()[1]
                # rotate robot
                if robot.get_angle() != None:
                    robot.angle = robot.get_angle()
                # fire robot weapons
                if robot.has_gun:
                    if robot.is_shooting():
                        if robot.count >= robot.rof:
                            robot.shoot_laser()
                            robot.count = 0
                    robot.count += 1
                # deal damage from bullets
                for bullet in bullets:
                    if (robot.xpos - bullet.xpos)**2 + (robot.ypos - bullet.ypos)**2 <= (robot.size -5)**2:
                        robot.damage += bullet.strength
                        robot.xpos -= 6 * bullet.direction[0]
                        robot.ypos -= 6 * bullet.direction[1]
                        bullets.remove(bullet)
                robot.health -= robot.damage
                robot.damage = 0
                if robot.health <= 0:
                    #Add robot to total score - Jon - 04/27/10
                    total_score += robot.worth
                    # drop pickups
                    robot.drop_pickup()
                    # generate explosion
                    explosions.append(Explosion(robot.xpos,robot.ypos))
                    # remove dead robot
                    robots.remove(robot)
                #! Lazer bullet for loop - Jon - 04/27/10
                for bullet in LazerBullets:
                    if (robot.xpos - bullet.xpos)**2 + (robot.ypos - bullet.ypos)**2 <= (robot.size -5)**2:
                        robot.damage += bullet.strength
                        robot.xpos -= 6 * bullet.direction[0]
                        robot.ypos -= 6 * bullet.direction[1]
                robot.health -= robot.damage
                robot.damage = 0

            for bullet in bullets:
                # move bullets
                bullet.xpos -= bullet.movespeed * bullet.direction[0]
                bullet.ypos -= bullet.movespeed * bullet.direction[1]
                if bullet.xpos < 0 or bullet.xpos > AREAWIDTH or bullet.ypos < 0 or bullet.ypos > AREAHEIGHT:
                    bullets.remove(bullet)

            for bullet in robobullets:
                # move RoboBullets
                bullet.xpos -= bullet.movespeed * bullet.direction[0]
                bullet.ypos -= bullet.movespeed * bullet.direction[1]
                if bullet.xpos < 0 or bullet.xpos > AREAWIDTH or bullet.ypos < 0 or bullet.ypos > AREAHEIGHT:
                    robobullets.remove(bullet)

               #! Jon did this on 04/27/20
            for bullet in LazerBullets:
                # move LazerBullets
                bullet.xpos -= bullet.movespeed * bullet.direction[0]
                bullet.ypos -= bullet.movespeed * bullet.direction[1]
                if bullet.xpos < 0 or bullet.xpos > WINDOWWIDTH or bullet.ypos < 0 or bullet.ypos > WINDOWHEIGHT:
                    LazerBullets.remove(bullet)

            for bullet in BossBullets:
                bullet.xpos -= bullet.movespeed * bullet.direction[0]
                bullet.ypos -= bullet.movespeed * bullet.direction[1]
                if bullet.xpos < 0 or bullet.xpos > WINDOWWIDTH or bullet.ypos < 0 or bullet.ypos > WINDOWHEIGHT:
                    BossBullets.remove(bullet)
                

            

            for explosion in explosions:
                # increment explosion count
                explosion.time -= 1
                if explosion.time <= 0:
                    explosions.remove(explosion)

            # update time
            if len(players) > 0:
                game_seconds += game_clock.tick(40)/1000.

            # update robot count
            robotcount += 1

        #update player effects (Boost, etc.) Travis & Tom
        for player in players:
            player.effect_timer -= 1
            if player.effect_timer <= 0:
                remove_effect(player,player.effect)
                player.effect_timer = 0

        #& player boundaries - Matt [4-28-10]
        #& Needs to be placed higher up
            if player.xpos < 0:
                player.xpos = 0
            elif player.xpos > AREAWIDTH-player.width:
                player.xpos = AREAWIDTH-player.width
            if player.ypos < 0:
                player.ypos = 0
            elif player.ypos > AREAHEIGHT-player.height:
                player.ypos = AREAHEIGHT-player.height

        #! update view - Matt [4-27-10]            
        xs = []
        ys = []
        for player in players:
            xs.append(player.xpos)
            ys.append(player.ypos)
        if not(xs == []):
            xmin = min(xs)-60 # Extra summed integers tweak the distance
            xmax = max(xs)+60 # at which the screen moves. - Matt [4-27-10]
            ymin = min(ys)-60
            ymax = max(ys)+60
            if xmin < camera.getLeft() and not (xmax > camera.getRight()) and xmin >= 0:
                camera.setLeft(xmin)
            elif xmax > camera.getRight() and not (xmin < camera.getLeft()) and xmin <= AREAWIDTH:
                camera.setRight(xmax)
            if ymin < camera.getTop() and not (ymax > camera.getBottom()) and ymin >= 0:
                camera.setTop(ymin)
            elif ymax > camera.getBottom() and not (ymin < camera.getTop()) and ymin <= AREAHEIGHT:
                camera.setBottom(ymax)

        #! draw everything - Tom [v1.0], -> areaSurface by Matt [4-27-10]
        for pickup in pickups:
            pickup_rect = pygame.Rect(pickup.xpos-pickup.size,pickup.ypos-pickup.size,2 * pickup.size,2 *pickup.size)
            current_image = pickup.image
            current_image.set_colorkey(BLACK)
            areaSurface.blit(pickup.image,pickup_rect)
        for bullet in bullets:
            bullet.draw()
        for bullet in robobullets:
            bullet.draw()
        for bullet in LazerBullets:
            bullet.draw()
        for bullet in BossBullets:
            bullet.draw()
        for player in players:
            player_rect = pygame.Rect(player.xpos-player.size,player.ypos-player.size,player.size*2,player.size*2)
            current_image = pygame.transform.rotate(player.image,player.angle)
            current_image.set_colorkey(BLACK)
            areaSurface.blit(current_image,player_rect)
        for robot in robots:
            robot_rect = pygame.Rect(robot.xpos-robot.size,robot.ypos-robot.size,robot.size*2,robot.size*2)
            current_image = pygame.transform.rotate(robot.image,robot.angle)
            current_image.set_colorkey(BLACK)
            areaSurface.blit(current_image,robot_rect)
        for explosion in explosions:
            explosion.draw()

        #! clip to screen - Matt [4-27-10]
        windowSurface.fill(BLACK)
        #areaSurface.set_clip(pygame.Rect(camera.getLeft(), camera.getTop(), camera.width, camera.height))
        windowSurface.blit(areaSurface, pygame.Rect(0,0,WINDOWWIDTH, WINDOWHEIGHT), (camera.getLeft(), camera.getTop(), camera.width, camera.height))
        areaSurface.fill(BLACK)

        # fix negatives in health and scrap pools and display
        if len(players) > 0:
            if playerbank.health_pool < 0:
                playerbank.health_pool = 0
            #if playerbank.scrap_pool < 0:
             #   playerbank.scrap_pool = 0
            bankstats = statFont.render('Med Supplies: %d'
                                        #Scrap: %d'
                                        %(playerbank.health_pool
                                         #,playerbank.scrap_pool
                                         ), True, WHITE, BLACK)
            #if len(players) == 1:
                #bankstats = statFont.render('Scrap: %d' % (playerbank.scrap_pool), True, WHITE, BLACK)
            bankstatsRect = bankstats.get_rect()
            bankstatsRect.centerx = WINDOWWIDTH / 2
            bankstatsRect.centery = statFontsize
            windowSurface.blit(bankstats, bankstatsRect)
            
        # display player health and ammo
        for player in players:
            text1 = statFont.render('Player: %d' % (player.id), True, WHITE, BLACK)
            text1Rect = text1.get_rect()
            text1Rect.centerx = (player.id) * WINDOWWIDTH / 5
            text1Rect.centery = WINDOWHEIGHT - (3 * statFontsize)
            windowSurface.blit(text1, text1Rect)        
            text2 = statFont.render('Health: %d' % (player.health), True, WHITE, BLACK)
            text2Rect = text2.get_rect()
            text2Rect.centerx = (player.id) * WINDOWWIDTH / 5
            text2Rect.centery = WINDOWHEIGHT - (2 * statFontsize)
            windowSurface.blit(text2, text2Rect)
            if player.weapon.ammo == float('infinity'):
                text3 = statFont.render('Ammo: Infinite', True, WHITE, BLACK)
            else:
                text3 = statFont.render('Ammo: %d' % (player.weapon.ammo), True, WHITE, BLACK)
            text3Rect = text3.get_rect()
            text3Rect.centerx = (player.id) * WINDOWWIDTH / 5
            text3Rect.centery = WINDOWHEIGHT - (statFontsize)
            windowSurface.blit(text3, text3Rect)

        for message in messages:
                message.draw()
                if message.counter <= 0:
                    messages.remove(message)

        # display time
        second = game_seconds
        minute = 0
        while second >= 60:
            second -= 60
            minute += 1
        if second < 10:
            timertext = messageFont.render('%d:0%d' % (minute,second),True, WHITE, BLACK)
        else:
            timertext = messageFont.render('%d:%d' % (minute,second),True, WHITE, BLACK)
        timertextRect = timertext.get_rect()
        timertextRect.top = 0
        timertextRect.left = 0
        windowSurface.blit(timertext,timertextRect)

         # display points - Jon - 04/27/10
        scoretext = messageFont.render('Score: %d' %(total_score), True, WHITE, BLACK)
        scoretextRect = scoretext.get_rect()
        scoretextRect.top = 0
        scoretextRect.left = 990
        windowSurface.blit(scoretext, scoretextRect)

        # display pause message
        if game_pause:
            pause_text = messageFont.render('GAME PAUSED', True, WHITE, BLACK)
            textRect = pause_text.get_rect()
            textRect.centerx = windowSurface.get_rect().centerx
            textRect.centery = windowSurface.get_rect().centery
            windowSurface.blit(pause_text, textRect)

        # end the game if all players are killed
        if len(players) == 0:
            robots = []
            robotcount = 0
            bullets = []
            robobullets = []
            pickups = []
            game_pause = False
            #Fadeout Stuff - Jon & Matt - [04/26/10]
            pygame.mixer.music.fadeout(5000)
            
            game_over_text = messageFont.render('GAME OVER   TOTAL SCORE: %d' %(total_score), True, WHITE, BLACK)
            textRect = game_over_text.get_rect()
            textRect.centerx = windowSurface.get_rect().centerx
            textRect.centery = windowSurface.get_rect().centery
            windowSurface.blit(game_over_text, textRect)
            
            #Fadeout Stuff - Jon & Matt - [04/26/10]
            pygame.display.update()
            pygame.time.wait(5000)

            game_start = False
            pygame.mixer.music.load('Music/songfornoone.ogg')
            pygame.mixer.music.play()


    pygame.display.update()
