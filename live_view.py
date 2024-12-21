"""
live_view.py
-> handles updating the tiny live feed box in the bottom left corner.

"""
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from direct import task
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile, PNMImage
from direct.gui.OnscreenImage import OnscreenImage
import cv2
from PIL import Image
#from panda3d.core import Texture
from numpy import asarray

loadPrcFile('settings.prc')

class LiveView:
    def __init__(self, calibration=0):
        self.camera = None
        self.feed = None

        base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=True)
        self.detector = vision.PoseLandmarker.create_from_options(options)
        self.camera = cv2.VideoCapture(1)
        self.calibration = calibration
        self.threshold = 0.7

    def loadCenteredFeed(self):
        if self.calibration == 1:
            print("calibration view update?")
            self.feed = OnscreenImage(image="assets/sky.png", pos=(0, 0, -0.1), scale=(0.65, 1, 0.5))

    def calibrationUpdate(self):
        ret, frame = self.camera.read()
        frame = cv2.flip(frame, 1)
        cv2.imwrite('assets/frame.png', frame)

        texture = loader.loadTexture("assets/frame.png")
        texture.reload()
        self.feed.setImage(texture)

        image = mp.Image.create_from_file("assets/frame.png")
        detection_result = self.detector.detect(image)
        try:
            l_shoulder = detection_result.pose_landmarks[0][11]
            r_shoulder = detection_result.pose_landmarks[0][12]
        except IndexError:
            return -1

        if l_shoulder.presence < 0.8 or r_shoulder.presence < 0.8 or l_shoulder.visibility < 0.8 or r_shoulder.visibility < 0.8:
            return -1

        if (l_shoulder.z + r_shoulder.z) / 2 < -0.35 or (l_shoulder.y + r_shoulder.y) / 2 > 0.8:
            return -1
        return (l_shoulder.y + r_shoulder.y) / 2

    def terminate(self):
        self.feed.removeNode()

    def startLoad(self):
        self.feed = OnscreenImage(image="assets/sky.png", pos=(-1.4, 0, -0.83), scale=(0.17, 0.1, 0.1))

    def setThreshold(self, threshold):
        self.threshold = threshold

    def update(self):
        ret, frame = self.camera.read()
        frame = cv2.flip(frame, 1)
        cv2.imwrite('assets/frame.png', frame)

        texture = loader.loadTexture("assets/frame.png")
        texture.reload()
        self.feed.setImage(texture)

        image = mp.Image.create_from_file("assets/frame.png")
        detection_result = self.detector.detect(image)
        try:
            l_shoulder = detection_result.pose_landmarks[0][11]
            r_shoulder = detection_result.pose_landmarks[0][12]
        except IndexError:
            return -1

        if l_shoulder.presence < 0.6 or r_shoulder.presence < 0.6 or l_shoulder.visibility < 0.6 or r_shoulder.visibility < 0.6:
            return -1
        if (l_shoulder.z + r_shoulder.z) / 2 < -0.55:
            return -1

        print((l_shoulder.y + r_shoulder.y) / 2)
        if (l_shoulder.y + r_shoulder.y) / 2 > self.threshold:
            return 1
        return 0


