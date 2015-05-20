

class Block(object):

    def __init__(self,x,y,angle):
        self.size = 60
        pygame.Rect.__init__(self,x + self.size/2,y + self.size/2,self.size,self.size)
        self.angle = angle
        self.baseangle = angle
        self.field = 90
        self.highlimit = self.baseangle + self.field/2
        if self.highlimit > 360:
            self.highlimit -= 360
        self.lowlimit = self.baseangle - self.field/2
        if self.lowlimit > 0:
            self.lowlimit += 360
        self.health = 200
        self.maxhealth = 200
        self.damage = 0
        self.baseimage = None
        self.gunimage = None
        self.hasgun = True
        self.closerange = 100
        self.farrange = 800
        self.target = None


class Wall(Block):

    def __init__(self,x,y,angle):
        Block.__init__(self,x,y,angle)
        self.baseimage = None
        self.hasgun = False


class LaserTurret(Block):

    def __init__(self,x,y,angle):
        Block.__init__(self,x,y,angle)
        self.baseimage = pygame.image.load(None)
        self.gunimage = pygame.image.load(None)
        self.hasgun = True
        self.rof = 40
        self.count = self.rof

    def get_angle(self):
        return 360 - addangle.get_angle((self.xpos - self.target.xpos,self.ypos - self.target.ypos))

    def get_target(self):
        targetlist = []
        for robot in robots:
            dist = math.sqrt((self.xpos - robot.xpos)**2 + (self.ypos - robot.ypos)**2)
            angle = 360 - addangle.get_angle(self.xpos - self.robot.xpos,self.ypos - self.robot.ypos)
            if dist > self.closerange and dist < self.farrange:
                if self.highlimit > self.lowlimit:
                    if angle > self.lowlimit and angle < self.highlimit:
                        targetlist.append(robot)
                else:
                    if angle > self.lowlimit or angle < self.highlimit:
                        targetlist.append(robot)
        if len(targetlist) == 0:
            self.target = None
        else:
            targetnum = random.randint(0,len(targetlist))
            self.target = targetlist[targetnum]
    
    def fire(self, x, y, direction):
        # fires a single bullet
        LazerBullets.append(LazergunBullet(x,y,direction))
        #Adding sound effects - Jon - [04/27/2010]
        sound_effect3 = pygame.mixer.Sound('Music/lazergun.ogg')
        sound_effect3.set_volume(.1)
        sound_effect3.play()
        
