#################
# HACK K-STATE #
################
# MODULES
from enum import EnumType
from multiprocessing import Pool
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


# MAIN LOOP
previousMetadata = None
while True:
    # first clear all clicked
    envio.clearClicked()
    envio.updateCreatures()
    potentialNewMetadata = envio.getClickedEntity(previousMetadata)
    if previousMetadata != potentialNewMetadata and potentialNewMetadata != False:
        previousMetadata = potentialNewMetadata
        nameCounter.text = f"Name: {potentialNewMetadata['name']}"
        ageCounter.text = f"Age: {potentialNewMetadata['age']}"
    app.step()
