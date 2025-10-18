from ursina import *


class Sun(Entity):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            model="sphere",
            position=position,
            collider="mesh",
            color=color.yellow,
            texture_scale=(10, 10),
        )
