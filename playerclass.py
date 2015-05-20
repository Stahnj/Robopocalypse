class Player(object):

    def __init__(self):
        self.xpos = WINDOWWIDTH / 2
        self.ypos = WINDOWHEIGHT / 2
        self.size = 40.
        self.angle = 90.
        self.health = 100
        self.maxhealth = 100
        self.canmove = True
        self.damage = 0
        self.controller = pygame.joystick.Joystick(num)
        self.controller.init()
        self.movespeed = 6.
        self.healing = False
        self.repairing = False
        self.being_healed = False
        self.weapon = None
        self.image = None
        self.id = num + 1
        self.bufftimer = 0
        self.hold_start = False

    def get_vel(self):
        # returns the x and y velocities of the player in a tuple
        magnitude = self.controller.get_axis(Left_LR)**2+self.controller.get_axis(Left_UD)**2
        if magnitude > 0.055:
            xvel = (self.movespeed * self.controller.get_axis(Left_LR) * -1 * abs(self.controller.get_axis(Left_LR))) / magnitude
            yvel = (self.movespeed * self.controller.get_axis(Left_UD) * -1 * abs(self.controller.get_axis(Left_UD))) / magnitude
            return (xvel,yvel)
        return (0,0)

    def get_angle(self):
        # returns the player's angle of rotation
        if abs(self.controller.get_axis(Right_LR))**2+abs(self.controller.get_axis(Right_UD))**2 > 0.055:
            return addangle.get_angle((self.controller.get_axis(Right_LR),-1 * self.controller.get_axis(Right_UD)))

    def is_shooting(self):
        # returns whether or not the player is shooting
        if self.canmove and self.controller.get_axis(Right_LR)**2+self.controller.get_axis(Right_UD)**2 > 0.5:
            return True
        return False
    
    def is_holding(self):
        # returns whether or not the player is performing the hold action (A button)
        if self.controller.get_button(A_Button) == 1:
            return True
        return False

    def colliding_with(self,other):
        # returns whether or not the player is colliding with another object
        dist = math.sqrt((self.xpos - other.xpos)**2 + (self.ypos - other.ypos)**2)
        if dist <= (self.size + other.size):
            return True
        return False
