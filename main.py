# local files
from live_view import LiveView
from world import World
from player import Player

from direct.gui.OnscreenText import OnscreenText
from direct.showbase.Transitions import Transitions
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile, MouseButton
from panda3d.core import DirectionalLight, AmbientLight
from direct.gui.OnscreenImage import OnscreenImage

loadPrcFile('settings.prc')


class MotionDash(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.world = World()
        self.player = Player(self)
        self.live = LiveView()
        self.calibration_view = LiveView(1)
        self.gameState = "title"  # either "title", "calibration", "gameplay", or "gameover"

        self.live_tick = 0
        self.calibration_timer = 50
        self.setCamera()
        self.titleImg = None
        self.calText = None
        self.warningText = None
        self.jumpThreshold = 0.72

        self.paused = False

        base.win.getGsg().setGamma(5)
        taskMgr.add(self.update, 'update')
        self.onSwitchToTitle()

    def setCamera(self):
        self.disableMouse()
        self.camera.setPos(0, -30, 30)
        self.camera.setHpr(0, -2, 0)

    def onSwitchToTitle(self):
        base.setBackgroundColor(1, 1, 1)
        self.titleImg = OnscreenImage(image="assets/title.png", pos=(0, 0, -0.1), scale=(1.396, 1, 0.8))

    def onSwitchToCalibration(self):
        self.titleImg.removeNode()
        self.calibration_view.loadCenteredFeed()
        self.calImg = OnscreenImage(image="assets/calibration_text.png", pos=(0, 0, 0.2), scale=(1.396, 1, 0.8))

    def onSwitchToGameplay(self):
        self.live_tick = 0
        self.calImg.removeNode()
        self.calText.destroy()

        self.calibration_view.terminate()

        self.scoreText = OnscreenText(text=f'Score: 0', pos=(0.9, 0.9), scale=0.1, mayChange=True)
        self.world.startLoad()
        self.player.loadModels()
        self.live.startLoad()

    def restartGameplay(self):
        self.live_tick = 0
        self.scoreText = OnscreenText(text=f'Score: 0', pos=(0.9, 0.7), scale=0.1, mayChange=True)
        self.world.redoBlockers()

    def onSwitchToGameover(self):
        self.scoreText.destroy()
        self.gameOver = OnscreenImage(image="assets/killscreen.png", pos=(0, 0, 0), scale=(1, 1, 0.6))
        self.finalScore = OnscreenText(text=f'Final Score: {self.player.getScore()}', pos=(0, -0.4), scale=0.2)

    def clearGameOver(self):
        self.gameOver.removeNode()
        self.finalScore.destroy()

    def update(self, task):
        dt = globalClock.getDt()

        if self.gameState == "title":
            if base.mouseWatcherNode.hasMouse() and base.mouseWatcherNode.isButtonDown(MouseButton.one()):
                self.gameState = "calibration"
                self.onSwitchToCalibration()

        elif self.gameState == "calibration":
            res = self.calibration_view.calibrationUpdate()
            if res != -1:
                self.calibration_timer -= 1
                print('redrawing...')
                if self.calText:
                    self.calText.destroy()
                self.calText = OnscreenText(text='Hold Still...', fg=(1, 0, 0, 1), pos=(0, -0.9), scale=0.3, mayChange=True)
            else:
                if self.calText:
                    self.calText.destroy()

            if self.calibration_timer == 0:
                if res != -1:
                    self.jumpThreshold = res + 0.15
                    print("___________Threshold is: _______", self.jumpThreshold)
                    self.gameState = "gameplay"
                    self.onSwitchToGameplay()
                else:
                    self.calibration_timer = 50

        elif self.gameState == "gameplay":
            if self.live_tick % 5 == 0:
                res = self.live.update()
                if res == -1:
                    if self.warningText:
                        self.warningText.destroy()
                    self.warningText = OnscreenText(text='Keep whole body in frame to resume', fg=(1, 0, 0, 1), pos=(0, 0), scale=0.3, mayChange=True)
                    self.paused = True
                else:
                    if self.warningText:
                        self.warningText.destroy()
                    self.paused = False
                    if res == 1:
                        self.player.jump()
            if not self.paused:
                blockers = self.world.update(self.camera, dt)
                self.player.update(dt)
                self.scoreText.setText(f'Score: {self.player.getScore()}')
                gameOver = self.player.checkCollisions(blockers)
                if gameOver:
                    self.gameState = "gameover"
                    self.onSwitchToGameover()
            else:
                # pause screen stuff here
                pass
            self.live_tick += 1
        elif self.gameState == "gameover":
            if base.mouseWatcherNode.hasMouse() and base.mouseWatcherNode.isButtonDown(MouseButton.one()):
                self.gameState = "gameplay"
                self.clearGameOver()
                self.restartGameplay()
        return task.cont


game = MotionDash()
game.run()
