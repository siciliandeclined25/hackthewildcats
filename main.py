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
# minha terra, tem a luz, e tem estrelhas
# let's make a sky
Sky()
# and simulate manhattan kansas
envio = envio.Manhattan()

# MAIN LOOP
while True:
    app.step()
