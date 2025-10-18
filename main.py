#################
# HACK K-STATE #
################
# MODULES
from ursina import *
from ursina.prefabs.editor_camera import EditorCamera

# LOCAL MODULES
import envio

# VARIABLES
# defines the camera and app scope
app = Ursina()
ec = EditorCamera()
ec.y = 10
ec.z = 10
ec.rotation_x = 45
# minha terra, tem a luz, e tem estrelhas
# let's make a sky
Sky()
# and simulate manhattan kansas
envio = envio.Manhattan()
# UI
dayCounter = Text(
    "Days: 0",
    color=color.white,
    scale=0.1,
    parent=camera.ui,
    position=(0.01, 0.02),
)


# MAIN LOOP
while True:
    envio.updateCreatures()
    app.step()
