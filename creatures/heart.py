from ursina import *


class FloatingHeart(Entity):
    def __init__(self, pos=(0, 0, 0), **kwargs):
        super().__init__(
            model="assets/heart.obj",
            color=color.rgba(255, 0, 0, 255),
            rotation_x=270,
            position=pos,
            scale=0.1,
            billboard=True,
            **kwargs,
        )
        self.lifetime = 2
        self.speed = 0.5

    def mupdate(self):
        self.position += Vec3(0, self.speed, 0) * time.dt
        self.color = color.rgba(
            self.color.r,
            self.color.g,
            self.color.b,
            self.color.a - (255 / self.lifetime) * time.dt,
        )
        if self.color.a <= 0:
            destroy(self)
