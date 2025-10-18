from ursina import *
import random


class Arbore(Entity):
    def __init__(self):
        super().__init__(
            model="assets/tree.obj",
            scale=0.1,
            color=Vec4(0.13, 0.25, 0.13, 1),
        )
        self.placeRandom()
        self.killMe = False

    def placeRandom(self):
        range = 20
        self.position = Vec3(
            random.randint(-1 * range, range), 0, random.randint(-1 * range, range)
        )

    def mupdate(self):
        pass
