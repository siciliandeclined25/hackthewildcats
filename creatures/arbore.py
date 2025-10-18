from ursina import *


class Arbore(Entity):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            model="sphere",
            scale=0.1,
            position=position,
            collider="mesh",
            color=color.green,
            texture_scale=(10, 10),
        )
