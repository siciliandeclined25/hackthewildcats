from ursina import *


class Sun(Entity):
    def __init__(self, position=(0, 20, 0)):
        super().__init__(
            model="sphere",
            position=position,
            collider="mesh",
            color=color.yellow,
            scale=5,
            texture_scale=(10, 10),
        )
        self.radius = 20
        self.angle = 0  # 1 = increasing, -1 = decreasing
        self.speed = 0.1  # degrees per second

    def update(self):
        # move in a vertical circular path
        self.angle += self.speed * time.dt

        # circular arc: X constant, Y/Z follow a circle
        self.y = math.sin(self.angle) * self.radius
        self.z = math.cos(self.angle) * self.radius * 1.4  # slightly bigger elpises
