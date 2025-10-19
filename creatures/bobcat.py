from ursina import *
import names


class Bobcat(Entity):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            model="assets/bobcat.obj",
            scale=0.04,
            position=position,
            color=color.brown,
        )
        self.metadata = {
            "name": names.get_first_name(),
            "lastname": names.get_last_name(),
            "type": "Bobcat",
            "age": 0,
            "offspring": 0,
        }
        self.clicked = False
        self.modes = ["idle", "walk", "hunt", "death", "babyidle", "babymake"]
        self.idleTimer = random.randint(0, 4)
        self.mode = self.modes[0]
        # kill me, kills the entity in a game loop
        self.killMe = False
        self.lifeExpectancy = random.randint(4000, 5475)
        # sets a timer until pregnancy
        self.pregnancyTimer = random.randint(625, 1095)
        self.makeOffspring = False
        self.myDirection = random.randint(-1, 2)
        self.directionToWalk = Vec3(random.choice([-1, 1]), 0, random.choice([-1, 1]))
        self.walkTimer = random.randint(0, 4)
        self.nourishment = 10

    def mupdate(self):
        self.metadata["age"] += 42 * time.dt

        if self.metadata["age"] > self.lifeExpectancy:  # die when old
            self.killMe = True
        if self.metadata["age"] > self.pregnancyTimer:
            self.metadata["offspring"] += 1
            self.pregnancyTimer += random.randint(1000, 2000)
            self.makeOffspring = True
        if not self.clicked:
            self.color = color.brown
            self.walkTimer -= time.dt
            self.x += self.directionToWalk.x * time.dt
            self.z += self.directionToWalk.z * time.dt
        if self.x > 20 or self.x < -20 or self.z > 20 or self.z < -20:
            self.mode = self.modes[0]
            self.walkTimer = random.randint(0, 4)
            if self.x < 0:
                self.directionToWalk.x = 1
            elif self.x > 0:
                self.directionToWalk.x = -1
            if self.z < 0:
                self.directionToWalk.z = 1
            elif self.z > 0:
                self.directionToWalk.z = -1
        if self.walkTimer <= 0:
            self.mode = self.modes[0]
            self.walkTimer = random.randint(0, 4)
            self.directionToWalk = Vec3(
                random.choice([-1, 1]), 0, random.choice([-1, 1])
            )
