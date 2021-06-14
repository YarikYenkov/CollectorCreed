import numpy as np
from PyQt5 import QtCore
import cv2

class Steve:

    def __init__(self, field_height, field_width, picfile='Pics/Steve.png'):

        img = cv2.imread(picfile)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.face0 = cv2.resize(img, (40, 80))

        self.face = np.copy(self.face0)

        mask = []
        for i in range(self.face0.shape[0]):
            mask_line = []
            for j in range(self.face0.shape[1]):
                if not np.any(self.face0[i, j]):
                    mask_line.append(False)
                else:
                    mask_line.append(True)
            mask.append(mask_line)
        mask = np.array(mask)
        self.mask0 = np.dstack((mask, mask, mask))
        self.mask = np.copy(self.mask0)

        self.fw = field_width
        self.fh = field_height
        self.h = self.face.shape[0]
        self.w = self.face.shape[1]
        self.y = int((self.fh - self.h) / 2)
        self.x = int((self.fw - self.w) / 2)
        self.v = 10
        self.skew = 0.7
        self.up = False
        self.down = False
        self.right = False
        self.left = False
        self.look_left = False

    def move(self, event):

        if event.type() == 6:
            if event.key() == QtCore.Qt.Key_A:
                self.left = True
                if not self.look_left:
                    self.face = np.fliplr(self.face0)
                    self.mask = np.fliplr(self.mask0)
                    self.look_left = True
            if event.key() == QtCore.Qt.Key_D:
                self.right = True
                if self.look_left:
                    self.face = np.copy(self.face0)
                    self.mask = np.copy(self.mask0)
                    self.look_left = False
            if event.key() == QtCore.Qt.Key_W:
                self.up = True
            if event.key() == QtCore.Qt.Key_S:
                self.down = True
            self.update_pos()
            return

        if event.type() == 7:
            if event.key() == QtCore.Qt.Key_A:
                self.left = False
            if event.key() == QtCore.Qt.Key_D:
                self.right = False
            if event.key() == QtCore.Qt.Key_W:
                self.up = False
            if event.key() == QtCore.Qt.Key_S:
                self.down = False

    def update_pos(self):

        if self.left and self.up:
            self.x -= int(self.skew * self.v)
            self.y -= int(self.skew * self.v)
        if self.left and self.down:
            self.x -= int(self.skew * self.v)
            self.y += int(self.skew * self.v)
        if self.right and self.up:
            self.x += int(self.skew * self.v)
            self.y -= int(self.skew * self.v)
        if self.right and self.down:
            self.x += int(self.skew * self.v)
            self.y += int(self.skew * self.v)
        if self.left and not self.up and not self.down:
            self.x -= self.v
        if self.down and not self.left and not self.right:
            self.y += self.v
        if self.up and not self.left and not self.right:
            self.y -= self.v
        if self.right and not self.up and not self.down:
            self.x += self.v
        self.check_limits()

    def check_limits(self):

        if self.x < 0:
            self.x = 0
        if self.x > self.fw - self.w:
            self.x = self.fw - self.w
        if self.y < 0:
            self.y = 0
        if self.y > self.fh - self.h:
            self.y = self.fh - self.h


class Item:

    def __init__(self, fh, fw, h, w):

        items = [('Pics/Diamond.png', 15),
                 ('Pics/Medal.png', 11),
                 ('Pics/Ring.png', 13)]
        n = np.random.choice(len(items), p=[0.16, 0.5, 0.34])

        img = cv2.imread(items[n][0])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.face = cv2.resize(img, (40, 50))

        self.h = self.face.shape[0]
        self.w = self.face.shape[1]
        self.score = items[n][1]
        mask = []
        for i in range(self.h):
            mask_line = []
            for j in range(self.w):
                if not np.any(self.face[i, j]):
                    mask_line.append(False)
                else:
                    mask_line.append(True)
            mask.append(mask_line)
        mask = np.array(mask)
        self.mask = np.dstack((mask, mask, mask))

        self.sound = 'Sounds/Sound_collect_item.mp3'

        while True:
            y = np.random.randint(fh - self.h)
            x = np.random.randint(fw - self.w)
            if fh - 3 * h / 2 < y < fh + 3 * h / 2 and fw - 3 * w / 2 < x < fw + 3 * w / 2:
                continue
            else:
                break

        self.y = y
        self.x = x


class Mob(Steve):

    def __init__(self, field_height, field_width, picfile='Pics/Zombie.jpg'):

        super().__init__(field_height, field_width, picfile=picfile)

        while True:
            y = np.random.randint(self.fh - self.h)
            x = np.random.randint(self.fw - self.w)
            if self.fh - 3 * self.h / 2 < y < self.fh + 3 * self.h / 2 and \
                    self.fw - 3 * self.w / 2 < x < self.fw + 3 * self.w / 2:
                continue
            else:
                break

        self.y = y
        self.x = x

        self.v = 20
        self.skew = 0.7

        self.directions = [(False, False, False, False),
                           (False, True, False, True),
                           (False, False, False, True),
                           (True, False, False, True),
                           (False, True, False, False),
                           (True, False, False, False),
                           (False, True, True, False),
                           (False, False, True, False),
                           (True, False, True, False)]
        self.up, self.down, self.right, self.left = self.directions[np.random.randint(1, 9)]

    def move(self, count):
        if count % np.random.randint(15, 31) == 0:
            n = np.random.randint(1, 9)
            self.up, self.down, self.right, self.left = self.directions[n]
        self.update_pos()

    def check_limits(self):

        if self.x < 0:
            self.x = 0
            self.right = True
            self.left = False
        if self.x > self.fw - self.w:
            self.x = self.fw - self.w
            self.left = True
            self.right = False
        if self.y < 0:
            self.y = 0
            self.down = True
            self.up = False
        if self.y > self.fh - self.h:
            self.y = self.fh - self.h
            self.up = True
            self.down = False


class Bomb:

    def __init__(self, x, y, pic='Pics/Bomb.png', sound=None):
        self.face = None
        self.h = 50
        self.w = 50
        self.mask = None
        self.sound = None
        self.x0 = x
        self.y0 = y
        self.reinit(pic, sound)
        self.y = int(self.y0 - self.h / 2)
        self.x = int(self.x0 - self.w / 2)

    def reinit(self, pic, sound):
        img = cv2.imread(pic)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.face = cv2.resize(img, (self.h, self.w))

        mask = []
        for i in range(self.h):
            mask_line = []
            for j in range(self.w):
                if not np.any(self.face[i, j]):
                    mask_line.append(False)
                else:
                    mask_line.append(True)
            mask.append(mask_line)
        mask = np.array(mask)
        self.mask = np.dstack((mask, mask, mask))
        self.sound = sound

    def explode(self):
        self.h = 120
        self.w = 120
        self.reinit(pic='Pics/Explosion.png', sound=None)
        self.y = int(self.y0 - self.h / 2)
        self.x = int(self.x0 - self.w / 2)
