class Bank(object):

    """ The pool from which players draw their extra health and scrap. """
    
    def __init__(self):
        self.health_pool = 100 # Starting health pool
        self.scrap_pool = 10 # Starting scrap
        
