from ursina import *
import names

names = names.get_first_name()


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
        self.mode = self.modes[0]
        # clicked, if clicked the entity is selected in our invetory thing
        self.clicked = True
        # entity metadata for our little explorer
        self.metadata = {
            "name": names.get_first_name(),
            "type": "rabbit",
            "age": 0,
        }

    def update(self):
        pass

    def clicked(self):
        self.clicked = True
