from ursina import *
from random import uniform


class BloodParticle(Entity):
    def __init__(self, pos, **kwargs):
        super().__init__(
            model="quad",
            texture="circle",
            color=color.rgb(180, 0, 0),
            position=pos,
            scale=uniform(0.05, 0.15),
            billboard=True,
            **kwargs,
        )
        # random direction and speed
        self.velocity = Vec3(uniform(-2, 2), uniform(1, 4), uniform(-2, 2))
        self.fade = uniform(0.5, 1.2)
        self.gravity = Vec3(0, -4, 0)
        self.killMe = False

    def update(self):
        self.velocity += self.gravity * time.dt
        self.position += self.velocity * time.dt
        self.color = color.rgba(
            self.color.r, self.color.g, self.color.b, self.color.a - self.fade * time.dt
        )
        if self.color.a <= 0:
            destroy(self)

    def blood_explosion(self, pos):
        for _ in range(200):  # number of particles
            BloodParticle(position=(pos[0], pos[1] + 3, pos[2]))
