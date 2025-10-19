# imports
from enum import EnumType
import csv
from creatures import bobcat, rabbit, sun, arbore, grass, death, heart
import random
from ursina import *
import os


class Manhattan:
    """a small class that represents life inside of the konza prarie"""

    def __init__(self, worldChunkSize=50, kSelected=2, rSelected=15, forestCount=30):
        self.myEntities = []
        self.kSelectedCount = kSelected
        self.rSelectedCount = rSelected
        self.forestCount = forestCount
        self.worldChunkSize = worldChunkSize
        self.createWorld()
        self.paused = False
        self.predators = []
        # metadata clicked handler

    def clearClicked(self):
        for entity in self.myEntities:
            try:
                entity.clicked = False
            except AttributeError:
                pass

    def getClickedEntity(self, previousMetadata):
        for entity in self.myEntities:
            try:
                if entity.clicked == True:
                    return entity.metadata
            except AttributeError:
                pass
        nonemeta = False
        return nonemeta

    def createWorld(self):
        """creates and populates a simulated world and enviornment at the konza prarie"""
        # go through each k, r, and tree species
        # for _ in range(self.kSelectedCount):
        # self.myEntities.append(bobcat.Bobcat())
        for _ in range(self.rSelectedCount):
            self.myEntities.append(rabbit.Rabbit())
        for _ in range(self.forestCount):
            self.myEntities.append(arbore.Arbore())
        # now let's make cubes of dirt, in a sizexsize with a z of 1
        self.myEntities.append(grass.Grass(self.worldChunkSize, self.worldChunkSize))

        self.myEntities.append(sun.Sun())

    def updateCreatures(self):
        clickedMetadata = None

        # update entity positions
        for entity in self.myEntities:
            entity.mupdate()
            # handles birth
            try:
                if entity.makeOffspring and len(self.myEntities) < 75:
                    self.myEntities.append(rabbit.Rabbit())
                    os.system("afplay /System/Library/Sounds/Pop.aiff &")
                    print("BIRTH!")
                    entity.makeOffspring = False
                    # destroy(entity)
            except AttributeError:
                pass
            # handle running away in fear
            for predators in self.predators:
                # sneakily, make sure that the predator is following an entity
                if entity.metadata["type"] == "Rabbit":  # only for rabbtis
                    if (
                        entity.position - predators.position
                    ).length() < 3 and predators.nourishment < 3:
                        # too late, get eaten and die
                        self.myEntities.remove(entity)
                        # add blood from entity
                        # don't add it to the list because i don't want to track it's existance
                        death.BloodParticle(entity.position)
                        os.system("afplay /System/Library/Sounds/Basso.aiff &")

                        # and remove it
                        destroy(entity)
                        rabbits = [
                            rabbit
                            for rabbit in self.myEntities
                            if rabbit.metadata["type"] == "Rabbit"
                        ]
                        try:
                            newPrey = random.choice(rabbits).position
                            predators.look_at(newPrey)
                            predators.animate_position(
                                newPrey, duration=6, curve=curve.linear
                            )  # move over time
                            predators.nourishment = 7
                            print("i was fed dont fret my brother")
                        except IndexError:
                            pass

                        break
                    if entity.mode != "flee":  # see what the entity mode is
                        if (entity.position - predators.position).length() < 5:
                            entity.mode = "flee"  # aka run for your life
                            fleeDirection = (
                                entity.position - predators.position
                            ).normalized()
                            entity.directionToWalk += fleeDirection * time.dt * 2

                    elif entity.mode == "flee":  # redudant but verbose
                        if (
                            entity.position - predators.position
                        ).length() > 5 and entity.metadata["type"] == "Rabbit":
                            # no worries, now we're all dandy
                            entity.mode = "walk"  # just idle animation
                            entity.directionToWalk = Vec3(
                                random.choice([-1, 1]), 0, random.choice([-1, 1])
                            )
                            entity.walkTimer = random.randint(0, 4)

            # handles death
            # dying from starvation
            if entity.metadata["type"] == "Bobcat" and entity.nourishment <= 0:
                print("hungry!!!")

                entity.killMe = True
            if entity.killMe:
                # remove the entity from update
                self.myEntities.remove(entity)
                if entity.metadata["type"] == "Bobcat":
                    self.predators.remove(entity)
                # add blood from entity
                # don't add it to the list because i don't want to track it's existance
                death.BloodParticle(entity.position)
                os.system("afplay /System/Library/Sounds/Basso.aiff &")

                # and remove it
                destroy(entity)

                print(entity.metadata["name"] + " just died. RIP 🥀")
            # there's a lot of tries because i don't want to make a parent class
            # and have these attriibutes pass
            try:
                if entity.clicked == True:
                    clickedMetadata = entity.metadata
            except AttributeError:
                pass
        return clickedMetadata
