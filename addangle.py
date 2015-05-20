import math

def get_angle(vector):
    x = vector[0]
    y = vector[1]
    if x > 0:
        if y < 0:
            return 360. + (180. / math.pi) * math.atan(y/x)
        if y > 0:
            return (180. / math.pi) * math.atan(y/x)
        if y == 0:
            return 0
    if x < 0:
        return 180. + (180. / math.pi) * math.atan(y/x)
    if x == 0 and y > 0:
        return 90
    if x == 0 and y < 0:
        return 270

def get_vector(angle):
    x = math.cos(angle)
    y = math.sin(angle)
    return (x,y)

def addangle(vector,angle):
    x = vector[0]
    y = vector[1]
    offset = math.pi * angle / 180.
    current_angle = math.pi * get_angle(vector) / 180.
    return get_vector(current_angle + offset)


