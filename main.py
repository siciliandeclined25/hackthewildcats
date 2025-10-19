#################
# HACK K-STATE #
################
# MODULES
from ursina import *
from ursina.prefabs.editor_camera import EditorCamera
from panda3d.core import WindowProperties
from panda3d.core import loadPrcFileData
from creatures import bobcat
from time import sleep
import csv
import webbrowser

# LOCAL MODULES
import envio

# Open AI Voice Agent in browser
webbrowser.open('https://elevenlabs.io/app/talk-to?agent_id=agent_0101k7vyy29heqr9rvy4fmqs6psv')

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
predCounter = Text(
    "Predators: ",
    color=color.white,
    scale_x=0.05,
    scale_y=0.07,
    parent=camera.ui,
    position=(0.01, 0.012),
)
rabCounter = Text(
    "Prey: ",
    color=color.white,
    scale_x=0.05,
    scale_y=0.07,
    parent=camera.ui,
    position=(0.01, 0.01),
)

app = Ursina()


def input(key):
    if key == "space":
        print("clicked!")
        envio.paused = not envio.paused
    if key == "p":  # adds a predator
        mybob = bobcat.Bobcat()
        envio.myEntities.append(mybob)
        envio.predators.append(mybob)
        rabbits = [
            rabbit for rabbit in envio.myEntities if rabbit.metadata["type"] == "Rabbit"
        ]
        try:
            newPrey = random.choice(rabbits).position
            mybob.look_at(newPrey)
            mybob.animate_position(
                newPrey, duration=6, curve=curve.linear
            )  # move over time
            mybob.nourishment = 10
        except IndexError:
            pass
    if key == "left mouse down":
        envio.clearClicked()


# CSV ingreation
def logCSV(t, prey, predators, filename="data.csv"):
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        if f.tell() == 0:  # write header once
            writer.writerow(["time", "prey", "predators"])
        writer.writerow([t, prey, predators])


# MAIN LOOP
previousMetadata = None
previousGlobalTimeCSV = 0
globalTimeInDays = 0
while True:
    # first clear all clicked
    if envio.paused == False:
        clickedMetadata = envio.updateCreatures()
        if clickedMetadata != None:
            nameCounter.text = (
                "Name: " + clickedMetadata["name"] + " " + clickedMetadata["lastname"]
            )
            ageCounter.text = "Age: " + str(clickedMetadata["age"] // 365)
        globalTimeInDays += 42 * time.dt
        yearCounter.text = "Year: " + str(globalTimeInDays // 365)
        predCounter.text = "Predators: " + str(len(envio.predators))
        preyCText = str(
            len(
                [
                    rabbit
                    for rabbit in envio.myEntities
                    if rabbit.metadata["type"] == "Rabbit"
                ]
            )
        )
        rabCounter.text = "Prey: " + preyCText
        # handle csv input
        print(globalTimeInDays // 365)
        print("&")
        print(previousGlobalTimeCSV)
        print("eeee")
        if globalTimeInDays // 365 != previousGlobalTimeCSV:
            previousGlobalTimeCSV = globalTimeInDays // 365
            logCSV(globalTimeInDays // 365, preyCText, len(envio.predators))
    app.step()
