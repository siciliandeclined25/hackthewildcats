from ursina import *


class Bobcat(Entity):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            model="sphere",
            scale=0.1,
            position=position,
            collider="mesh",
            color=color.red,
            texture_scale=(10, 10),
        )
        self.modes = ["idle", "walk", "hunt", "death", "babyidle", "babymake"]
        self.idleTimer = random.randint(0, 4)
        self.mode = self.modes[0]
        self.killMe = False

    def update(self):
        pass
