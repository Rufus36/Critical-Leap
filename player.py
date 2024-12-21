"""
player.py
-> Handles player vertical movement (jumps)
-> moves the terrain to give the illusion of movement

"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile
from panda3d.core import DirectionalLight, AmbientLight
from direct.gui.OnscreenImage import OnscreenImage
from gameConfig import GameConfig
from math import pi

loadPrcFile('settings.prc')

def calcAngleChange(distance, radius = 24):
    return (distance/radius) * (180 / pi)

class Player:
    def __init__(self, ShowBase):
        self.jumpPower = 100
        self.gravity = 4
        self.grounded = True

        self.base = ShowBase
        self.zVel = 0
        self.score = 0

    def loadModels(self):
        self.sprite = loader.loadModel('assets/player.glb')
        self.sprite.setScale(6)
        self.sprite.setPos(0, 80, 7.5)
        self.sprite.reparentTo(render)

        self.trainTrack = loader.loadModel('assets/train_tracks.glb')
        self.ground = loader.loadModel('assets/grass_field.glb')
        self.ground.setColorScale(1.7, 1.2, 1, 1)

    def jump(self):
        print("jumping______________________________________")
        if self.grounded:
            self.zVel = self.jumpPower
            self.grounded = False

    def checkCollisions(self, blockers):
        for i in range(min(5, len(blockers))):
            if blockers[i].getY() - self.sprite.getY() - 10 < 2 and self.grounded:
                return True
        return False

    def getScore(self):
        return int(self.score)

    def update(self, dt):
        if self.sprite.getZ() < 7.5:
            self.grounded = True
            self.sprite.setZ(7.5)
            self.zVel = 0

        if not self.grounded:
            self.zVel -= self.gravity

        self.sprite.setZ(self.sprite.getZ() + dt * self.zVel)

        #self.sprite.setY(self.sprite.getY() + dt * self.movementSpeed)
        self.sprite.setHpr(self.sprite.getH(), self.sprite.getP() - calcAngleChange(dt * GameConfig.movementSpeed), self.sprite.getR())

        self.score += dt