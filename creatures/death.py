from ursina import *
from random import uniform


class BloodParticle(Entity):
    def __init__(self, pos, **kwargs):
        super().__init__(
            model="quad",
            texture="circle",
            color=color.rgb(180, 0, 0),
            position=pos,
            scale=uniform(0.05, 0.2),
            billboard=True,
            **kwargs,
        )
        # emphasize upward motion and variety
        self.velocity = Vec3(
            uniform(-2, 2),  # sideways spread
            uniform(6, 14),  # much stronger upward velocity
            uniform(-2, 2),
        )
        self.fade = uniform(0.5, 1.2)
        self.gravity = Vec3(0, -9, 0)  # stronger gravity pull
        self.killMe = False
        self.metadata = {"type": "Death"}

    def update(self):
        self.velocity += self.gravity * time.dt
        self.position += self.velocity * time.dt
        self.color = color.rgba(
            self.color.r,
            self.color.g,
            self.color.b,
            self.color.a - self.fade * time.dt,
        )
        if self.color.a <= 0:
            destroy(self)

    @staticmethod
    def blood_explosion(pos):
        # big burst
        for _ in range(400):  # higher count for thicker blood spray
            BloodParticle(position=(pos[0], pos[1] + uniform(0, 1), pos[2]))


# demo use
if __name__ == "__main__":
    app = Ursina()

    def input(key):
        if key == "space":
            BloodParticle.blood_explosion((0, 0, 0))

    app.run()
