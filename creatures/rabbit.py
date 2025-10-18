from ursina import *
import names


class Rabbit(Entity):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            scale=0.3,
            position=position,
            rotation_x=270,
            collider="mesh",
            color=color.white,
            model="assets/rabbit.obj",
            texture_scale=(10, 10),
            on_click=self.clicked,
        )
        # all of the states that the rabbit can have
        self.modes = ["idle", "walk", "flee", "death", "babyidle", "babymake"]
        self.idleTimer = random.randint(0, 4)
        self.walkTimer = random.randint(0, 4)
        self.mode = self.modes[0]
        # clicked, if clicked the entity is selected in our invetory thing
        self.clicked = True
        # entity metadata for our little explorer
        self.metadata = {
            "name": names.get_first_name(),
            "type": "Rabbit",
            "age": 0,
            "offspring": 0,
        }
        self.directionToWalk = Vec3(random.choice([-1, 1]), 0, random.choice([-1, 1]))
        # kill me, kills the entity in a game loop
        self.killMe = False

    def update(self):
        # handle if we're not clicked
        if not self.clicked:
            self.color = color.white
        if self.mode == "idle":
            self.idleTimer -= time.dt
            if self.idleTimer <= 0:
                self.mode = self.modes[1]
                self.idleTimer = random.randint(0, 4)
        elif self.mode == "walk":
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

    def clicked(self):
        self.clicked = True
        self.color = color.yellow
