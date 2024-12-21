"""
world.py
-> Sets skybox and basic lighting.

"""

from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile, Fog
from panda3d.core import DirectionalLight, AmbientLight
from direct.gui.OnscreenImage import OnscreenImage
import random
from gameConfig import GameConfig
from panda3d.core import Loader
from player import Player
loadPrcFile('settings.prc')
class Bridge:
    def __init__(self, y_loc):
        self.next_loc = y_loc
        self.bridge_tile_width = 20
        self.colorIndex = 0
        self.bridge_tiles = []
        self.length = random.randint(1, 5) * 3

        self.lightBrown = loader.loadModel('assets/bridge_tile.glb')
        self.lightBrown.setColorScale(0.5, 0.3, 0.1, 1)

        self.midBrown = loader.loadModel('assets/bridge_tile.glb')
        self.midBrown.setColorScale(0.721, 0.451, 0.200, 1)

        self.darkBrown = loader.loadModel('assets/bridge_tile.glb')
        self.darkBrown.setColorScale(0.396, 0.263, 0.129, 1)

        self.railingBlock = loader.loadModel('assets/bridge_tile.glb')
        self.railingBlock.setColorScale(0.588, 0.412, 0.098, 1)
        self.railingBlock.setScale(1, 5, self.length * 2)
        self.railingBlock.setHpr(0, 90, 0)

        self.waterBlock = loader.loadModel('assets/bridge_tile.glb')
        self.waterBlock.setColorScale(0.278, 0.839, 1, 1)
        self.waterBlock.setScale(1000, 5, self.length * 2)
        self.waterBlock.setHpr(0, 90, 0)


        self.bridge_colors = [self.lightBrown, self.midBrown, self.darkBrown]
        for i in self.bridge_colors:
            i.setHpr(0, 90, 0)
            i.setScale(16, 2, 2)

        self.createBridge()

    def createBridge(self):
        for i in range(2):
            newRailing = render.attachNewNode('new-railing-placeholder')
            newRailing.setPos(-32 if i == 0 else 32, self.next_loc - 64 + 19.5 * self.length, -1.5)
            self.railingBlock.instanceTo(newRailing)
            self.bridge_tiles.append(newRailing)

        newWater = render.attachNewNode('new-water-placeholder')
        newWater.setPos(0, self.next_loc - 64 + 19.5 * self.length, -15)
        self.waterBlock.instanceTo(newWater)
        self.bridge_tiles.append(newWater)

        for i in range(self.length):
            newTile = render.attachNewNode('new-tile-placeholder')
            newTile.setPos(0, self.next_loc - 46, -4.9)

            self.next_loc += self.bridge_tile_width * 2
            self.bridge_colors[abs(self.colorIndex)].instanceTo(newTile)
            self.bridge_tiles.append(newTile)

            self.colorIndex += 1
            if self.colorIndex >= 2:
                self.colorIndex = -2

    def getNextLoc(self):
        return self.next_loc - 1

    def move(self, amount):
        max_y = 0
        for i in self.bridge_tiles:
            if i.getY() > max_y:
                max_y = i.getY()
            i.setY(i.getY() - amount)
        if max_y < 50:
            for i in self.bridge_tiles:
                i.removeNode()
            return False
        return True

class World:
    def __init__(self):
        self.segmentLength = 260
        self.movementSpeed = 50

        self.visibleTracks = 10
        self.tile_width = 64
        self.tracks = []
        self.strip_colors = []
        self.ground_tiles = []
        self.bridges = []
        self.blockers = []
        self.lastBlocker = 500

        self.next_loc = 0

    def startLoad(self):
        self.loadModels()
        self.generateRoad()
        self.setLights()
        self.setFog()
        self.setSkybox()

    def loadModels(self):
        self.trainTrack = loader.loadModel('assets/train_tracks.glb')
        self.trainTrack.setHpr(0, 90, 0)

        self.lightGreen = loader.loadModel('assets/grass_strip.glb')
        self.lightGreen.setColorScale(0.255, 0.596, 0.039, 1)

        self.midGreen = loader.loadModel('assets/grass_strip.glb')
        self.midGreen.setColorScale(0.149, 0.545, 0.027, 1)

        self.darkGreen = loader.loadModel('assets/grass_strip.glb')
        self.darkGreen.setColorScale(0.074, 0.522, 0.063, 1)

        self.blocker = loader.loadModel('assets/blocker.glb')
        self.blocker.setHpr(0, 90, 0)


        self.strip_colors = [self.lightGreen, self.midGreen, self.darkGreen]
        for i in self.strip_colors:
            i.setHpr(0, 90, 90)
            i.setScale(32, 16, 24)

    def generateRoad(self):
        for i in range(self.visibleTracks):
            newTrack = render.attachNewNode('new-track-placeholder')
            newTrack.setPos(0, i * self.segmentLength, 0)
            self.tracks.append(newTrack)
            self.trainTrack.instanceTo(newTrack)

        colorIndex = 0
        for i in range(int(self.visibleTracks * 2)):
            if random.random() < 0.1:
                b = Bridge(self.next_loc)
                self.next_loc = b.getNextLoc()
                self.bridges.append(b)

            newTile = render.attachNewNode('new-tile-placeholder')
            newTile.setPos(0, self.next_loc, -12)
            self.next_loc += self.tile_width * 2
            self.strip_colors[abs(colorIndex)].instanceTo(newTile)
            colorIndex += 1
            if colorIndex >= 2:
                colorIndex = -2
            self.ground_tiles.append(newTile)

        for x in range(int(self.visibleTracks * self.segmentLength / 2)):
            if random.random() < 0.01 and x * 2 - self.lastBlocker > 360:
                newBlocker = render.attachNewNode('new-blocker-placeholder')
                newBlocker.setPos(0, x * 2, 0)
                self.blocker.instanceTo(newBlocker)
                self.blockers.append(newBlocker)
                self.lastBlocker = x * 2


    def setLights(self):
        mainLight = DirectionalLight('main light')
        mainNodePath = render.attachNewNode(mainLight)
        mainNodePath.setHpr(30, -60, 0)
        render.setLight(mainNodePath)

        ambientLight = AmbientLight('ambient light')
        ambientLight.setColor((0.3, 0.3, 0.3, 1))
        ambientNodePath = render.attachNewNode(ambientLight)
        render.setLight(ambientNodePath)

    def setSkybox(self):
        skybox = loader.loadModel('assets/skybox/skybox.egg')
        skybox.setScale(20)
        skybox.setPos(0, 0, 21)
        skybox.setBin('background', 1)
        skybox.setDepthWrite(0)
        skybox.setLightOff()
        skybox.reparentTo(render)

    def setFog(self):
        color = (0.4, 0.8, 0.8)
        expFog = Fog("expfog node")
        expFog.setColor(*color)
        expFog.setExpDensity(0.0006)

        render.attachNewNode(expFog)
        render.setFog(expFog)

    def redoBlockers(self):
        self.blockers.pop(0)

    def update(self, camera, dt):

        for i in self.tracks:
            i.setY(i.getY() - dt * GameConfig.movementSpeed)
            if i.getY() + self.segmentLength < camera.getY():
                i.setY(i.getY() + self.visibleTracks * self.segmentLength)

        self.next_loc -= dt * GameConfig.movementSpeed
        for i in self.ground_tiles:
            i.setY(i.getY() - dt * GameConfig.movementSpeed)
            if i.getY() < camera.getY():
                i.setY(self.next_loc)
                self.next_loc += 2 * self.tile_width
                if random.random() < 0.1:
                    b = Bridge(self.next_loc)
                    self.next_loc = b.getNextLoc()
                    self.bridges.append(b)

        for i in self.bridges:
            res = i.move(dt * GameConfig.movementSpeed)
            if not res:
                self.bridges.remove(i)

        for i in range(len(self.blockers)):
            self.blockers[i].setY(self.blockers[i].getY() - dt * GameConfig.movementSpeed)
            if self.blockers[i].getY() < camera.getY():
                self.blockers.pop(i)
                newBlocker = render.attachNewNode('new-blocker-placeholder')
                newBlocker.setPos(0, self.blockers[i].getY() + self.visibleTracks * self.segmentLength, 0)
                self.blocker.instanceTo(newBlocker)
                self.blockers.append(newBlocker)

        return self.blockers
