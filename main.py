#################
# HACK K-STATE #
################
# MODULES
from ursina import *
from ursina.prefabs.editor_camera import EditorCamera
from panda3d.core import WindowProperties
from panda3d.core import loadPrcFileData

from time import sleep

# LOCAL MODULES
import envio

loadPrcFileData("", "sync-video false")  # disables v-sync pause
loadPrcFileData("", "want-pstats false")  # optional
loadPrcFileData("", "window-type onscreen")  # ensures visible window
loadPrcFileData("", "background-yield 0")  # keeps rendering in background

# VARIABLES
# defines the camera and app scope
app = Ursina()

# window.fullscreen = True
# window.borderless = True
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
yearCounter = Text(
    "Year: 0",
    color=color.white,
    scale_x=0.07,
    scale_y=0.1,
    world=True,
    parent=camera.ui,
    position=(0.01, 0.02),
)
nameCounter = Text(
    "Name: ",
    color=color.white,
    scale_x=0.05,
    scale_y=0.07,
    parent=camera.ui,
    position=(0.01, 0.016),
)
ageCounter = Text(
    "Age: ",
    color=color.white,
    scale_x=0.05,
    scale_y=0.07,
    parent=camera.ui,
    position=(0.01, 0.014),
)

app = Ursina()


def input(key):
    if key == "space":
        print("clicked!")
        envio.paused = not envio.paused
    if key == "left mouse down":
        envio.clearClicked()


# MAIN LOOP
previousMetadata = None
globalTimeInDays = 0
while True:
    # first clear all clicked
    if envio.paused == False:
        clickedMetadata = envio.updateCreatures()
        if clickedMetadata != None:
            nameCounter.text = "Name: " + clickedMetadata["name"]
            ageCounter.text = "Age: " + str(clickedMetadata["age"])
        globalTimeInDays += 42 * time.dt
        yearCounter.text = "Year: " + str(globalTimeInDays // 365)
    app.step()
