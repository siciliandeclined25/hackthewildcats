# imports
from creatures import bobcat, rabbit, sun, arbore
import random


class Manhattan:
    """a small class that represents life inside of the konza prarie"""

    def __init__(self, worldChunkSize=50, kSelected=30, rSelected=2, forestCount=30):
        self.myEntities = []
        self.kSelectedCount = kSelected
        self.rSelectedCount = rSelected
        self.forestCount = forestCount
        self.createWorld()

    def createWorld(self):
        """creates and populates a simulated world and enviornment at the konza prarie"""
        # go through each k, r, and tree species
        for _ in range(self.kSelectedCount):
            self.myEntities.append(bobcat.Bobcat())
        for _ in range(self.rSelectedCount):
            self.myEntities.append(rabbit.Rabbit())
        for _ in range(self.forestCount):
            self.myEntities.append(arbore.Arbore())
        self.myEntities.append(sun.Sun())
