from ursina import *
from ursina import texture
from ursina.entity import TextureStage


class Grass(Entity):
    def __init__(self, x, z):
        super().__init__(
            model="cube",
            scale=1,
            scale_x=x,
            scale_y=1,
            scale_z=z,
            x=0,
            z=0,
            y=0,
            # color=color.green,
            collider="mesh",
            color=Vec4(0.31, 0.47, 0.24, 1),
        )
        self.killMe = False

    def mupdate(self):
        pass
