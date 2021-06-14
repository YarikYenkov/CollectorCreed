import numpy as np
import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QLCDNumber, QRadioButton
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5 import QtCore
from PyQt5.Qt import QTimer
from MyMob import Steve, Item, Mob, Bomb
import pygame
import cv2


# c:\Users\user\AppData\Local\Programs\Python\Python38\Scripts\jupyter notebook --notebook-dir=D:\Collector_Creed
class MyEvents(QtCore.QObject):

    keyPressed = QtCore.pyqtSignal(QtCore.QEvent)


class MyGame(QWidget):

    def __init__(self, win_height, win_width):
        super().__init__()

        self.game_started = False

        self.item_count = 10
        self.time_count = 0
        self.score = 0

        self.items = []
        self.bomb = 0  # 0 - no bomb, 1 - bomb, 2 - explosion
        self.mode = 1  # 1 - normal, 2 - timer 100s, 3 - survival

        self.field = QLabel(self)
        self.field.move(220, 10)
        self.field_height = win_height - 20
        self.field_width = win_width - 240

        self.mob_count = 3
        self.hero = Steve(self.field_height, self.field_width)
        self.mobs = [Mob(self.field_height, self.field_width) for _ in range(self.mob_count)]

        field_list = ['Pics/Grass.png', 'Pics/Stone.jpg', 'Pics/Dirt.jpg']
        i = np.random.choice(len(field_list))
        file_name = field_list[i]

        img = cv2.imread(file_name)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.field_data0 = cv2.resize(img, (1860, 840))
        self.field_data0 = np.resize(self.field_data0, (self.field_height, self.field_width, 3))
        self.field_data = np.copy(self.field_data0)
        self.field_data_items = np.copy(self.field_data0)
        self.show_field()

        self.you_win_sound = 'Sounds/Sound_win.mp3'
        self.game_over_sound = 'Sounds/Sound_loss.mp3'
        self.start_sound = 'Sounds/Sound_start.mp3'

        img = cv2.imread('Pics/Game_Over.jpg')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.game_over_pic = cv2.resize(img, (500, 150))
        img = cv2.imread('Pics/You_Win.png')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.you_win_pic = cv2.resize(img, (500, 150))

        self.lcd_score = QLCDNumber(self)
        self.lcd_score.setGeometry(10, 820, 200, 60)
        self.lcd_score.display(self.score)

        self.lcd_item_count = QLCDNumber(self)
        self.lcd_item_count.setGeometry(50, 90, 120, 60)
        self.lcd_item_count.display(self.item_count)

        self.lcd_mob_count = QLCDNumber(self)
        self.lcd_mob_count.setGeometry(50, 280, 120, 60)
        self.lcd_mob_count.display(self.mob_count)

        self.lcd_time_count = QLCDNumber(self)
        self.lcd_time_count.setGeometry(10, 930, 200, 60)
        self.lcd_time_count.display(self.item_count)

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.display_time)

        self.bomb_timer = QTimer(self)
        self.bomb_timer.setInterval(2500)
        self.bomb_timer.timeout.connect(self.explode)

        lbl1 = QLabel('Item count', self)
        lbl1.setGeometry(20, 10, 200, 30)
        lbl1.setFont(QFont('Arial', 14))

        lbl4 = QLabel('Mob count', self)
        lbl4.setGeometry(20, 200, 200, 30)
        lbl4.setFont(QFont('Arial', 16))

        lbl5 = QLabel('Mode', self)
        lbl5.setGeometry(20, 410, 200, 30)
        lbl5.setFont(QFont('Arial', 16))

        lbl2 = QLabel('Score', self)
        lbl2.setGeometry(10, 780, 200, 30)
        lbl2.setFont(QFont('Arial', 17))
        lbl2.setAlignment(QtCore.Qt.AlignCenter)

        lbl3 = QLabel('Time', self)
        lbl3.setGeometry(10, 890, 200, 30)
        lbl3.setFont(QFont('Arial', 17))
        lbl3.setAlignment(QtCore.Qt.AlignCenter)

        lbl6 = QLabel('Controls:\nWASD - walk\nF - plant bomb', self)
        lbl6.setGeometry(10, 570, 350, 100)
        lbl6.setFont(QFont('Arial', 16))

        btn_add10 = QPushButton('+ 10', self)
        btn_add10.setGeometry(10, 50, 95, 30)
        btn_add10.setFont(QFont('Arial', 20))
        btn_add10.clicked.connect(self.item_add10)

        btn_add = QPushButton('+ 1', self)
        btn_add.setGeometry(115, 50, 95, 30)
        btn_add.setFont(QFont('Arial', 20))
        btn_add.clicked.connect(self.item_add)

        btn_add_mob = QPushButton('+ 1', self)
        btn_add_mob.setGeometry(50, 240, 120, 30)
        btn_add_mob.setFont(QFont('Arial', 20))
        btn_add_mob.clicked.connect(self.mob_add)

        btn_sub = QPushButton('Reset', self)
        btn_sub.setGeometry(50, 160, 120, 30)
        btn_sub.setFont(QFont('Arial', 16))
        btn_sub.clicked.connect(self.item_sub)

        btn_sub_mob = QPushButton('Reset', self)
        btn_sub_mob.setGeometry(50, 350, 120, 30)
        btn_sub_mob.setFont(QFont('Arial', 16))
        btn_sub_mob.clicked.connect(self.mob_sub)

        self.mode1 = QRadioButton('Normal', self)
        self.mode1.setChecked(True)
        self.mode1.setGeometry(10, 450, 150, 30)
        self.mode1.setFont(QFont('Arial', 16))
        self.mode1.toggled.connect(self.mode_select)

        self.mode2 = QRadioButton('60 seconds', self)
        self.mode2.setChecked(False)
        self.mode2.setGeometry(10, 490, 150, 30)
        self.mode2.setFont(QFont('Arial', 16))
        self.mode2.toggled.connect(self.mode_select)

        self.btn_start = QPushButton('START', self)
        self.btn_start.setGeometry(10, 710, 200, 60)
        self.btn_start.setFont(QFont('Arial', 20))
        self.btn_start.clicked.connect(self.start)

        self.setGeometry(0, 0, win_width, win_height)
        self.setWindowTitle('Collectors Creed')

        self.mx = pygame.mixer
        self.mx.init()
        self.key_press_event = MyEvents()
        self.show()

    def mob_add(self):
        self.mob_count += 1
        if self.mob_count >= 10:
            self.mob_count = 10
        self.lcd_mob_count.display(self.mob_count)

    def item_add(self):
        self.item_count += 1
        if self.item_count >= 99:
            self.item_count = 99
        self.lcd_item_count.display(self.item_count)

    def item_add10(self):
        self.item_count += 10
        if self.item_count >= 99:
            self.item_count = 99
        self.lcd_item_count.display(self.item_count)

    def item_sub(self):
        self.item_count = 0
        self.lcd_item_count.display(self.item_count)

    def mob_sub(self):
        self.mob_count = 0
        self.lcd_mob_count.display(self.mob_count)

    def display_time(self):
        if self.game_started:
            for mob in self.mobs:
                mob.move(self.time_count)
            self.time_count += 1
            self.handle_mob()
        if self.game_started:
            self.field_data_items = np.copy(self.field_data)
            self.set_hero()
            self.show_field()
            if self.mode == 2 and self.time_count == 600:
                self.stop(win=False)
            if self.time_count % 10 == 0:
                self.lcd_score.display(self.score)
                self.lcd_time_count.display(self.time_count // 10)

    def mode_select(self):
        if self.mode1.isChecked():
            self.mode = 1
        elif self.mode2.isChecked():
            self.mode = 2

    def start(self):
        if self.btn_start.underMouse():
            self.items = []
            self.field_data = np.copy(self.field_data0)
            for i in range(self.item_count):
                self.items.append(Item(self.field_height, self.field_width, self.hero.h, self.hero.w))
            for item in self.items:
                self.set_item(item)
            self.field_data_items = np.copy(self.field_data)
            self.hero = Steve(self.field_height, self.field_width)
            self.mobs = [Mob(self.field_height, self.field_width) for _ in range(self.mob_count)]
            self.set_hero()
            self.show_field()
            self.timer.start()
            self.game_started = True
            self.mx.music.load(self.start_sound)
            self.mx.music.play()

    def stop(self, win=True):
        if win:
            pic = self.you_win_pic
            sound = self.you_win_sound
        else:
            pic = self.game_over_pic
            sound = self.game_over_sound
        self.game_started = False
        self.timer.stop()
        self.bomb_timer.stop()
        self.field_data_items = np.copy(self.field_data)
        h = pic.shape[0]
        w = pic.shape[1]
        x = int((self.field_width - w) / 2)
        y = int((self.field_height - h) / 2)
        self.field_data_items[y:y + h, x:x + w] = pic
        self.show_field()
        self.mx.music.load(sound)
        self.mx.music.play()

    def set_hero(self):
        self.field_data_items[self.hero.y:self.hero.y + self.hero.h,
                              self.hero.x:self.hero.x + self.hero.w] = \
            np.where(self.hero.mask,
                     self.hero.face,
                     self.field_data_items[self.hero.y:self.hero.y + self.hero.h,
                                           self.hero.x:self.hero.x + self.hero.w])
        for mob in self.mobs:
            self.field_data_items[mob.y:mob.y + mob.h,
                                  mob.x:mob.x + mob.w] = \
                np.where(mob.mask,
                         mob.face,
                         self.field_data_items[mob.y:mob.y + mob.h,
                                               mob.x:mob.x + mob.w])

    def set_item(self, item):
        self.field_data[item.y:item.y + item.h,
                        item.x:item.x + item.w] = \
            np.where(item.mask,
                     item.face,
                     self.field_data[item.y:item.y + item.h,
                                     item.x:item.x + item.w])

    def show_field(self):
        q_img = QImage(self.field_data_items,
                       self.field_width, self.field_height, 3 * self.field_width,
                       QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.field.setPixmap(pixmap)

    def keyPressEvent(self, event):
        if self.game_started:
            if event.key() == QtCore.Qt.Key_F:
                if self.bomb == 0:
                    self.bomb = 1
                    self.items.append(Bomb(self.hero.x, self.hero.y))
                    self.bomb_timer.start()
                    self.set_item(self.items[-1])
            else:
                self.hero.move(event)
                self.handle_item()
        if self.game_started:
            self.field_data_items = np.copy(self.field_data)
            self.set_hero()
            self.show_field()

    def keyReleaseEvent(self, event):
        if self.game_started:
            self.hero.move(event)
            self.field_data_items = np.copy(self.field_data)
            self.set_hero()
            self.show_field()

    @staticmethod
    def detect_collision(obj1, obj2):
        condition = [obj1.x < obj2.x < obj1.x + obj1.w and
                     obj1.y < obj2.y < obj1.y + obj1.h,
                     obj1.x < obj2.x + obj2.w < obj1.x + obj1.w and
                     obj1.y < obj2.y + obj2.h < obj1.y + obj1.h,
                     obj1.x < obj2.x + obj2.w < obj1.x + obj1.w and
                     obj1.y < obj2.y < obj1.y + obj1.h,
                     obj1.x < obj2.x < obj1.x + obj1.w and
                     obj1.y < obj2.y + obj2.h < obj1.y + obj1.h]
        return any(condition)

    def handle_mob(self):
        for mob in self.mobs:
            for item in self.items:
                if isinstance(item, Bomb):
                    if self.bomb == 2:
                        if self.detect_collision(item, mob):
                            self.mobs.remove(mob)
                            if not self.mobs:
                                self.stop()
                            break
            if self.detect_collision(self.hero, mob):
                self.stop(win=False)
                break

    def handle_item(self):
        if not self.game_started:
            return
        for item in self.items:
            if isinstance(item, Item):
                if self.detect_collision(self.hero, item):
                    self.score += item.score
                    self.lcd_score.display(self.score)
                    self.mx.music.load(item.sound)
                    self.mx.music.play()
                    self.items.remove(item)
                    break
        else:
            return
        self.field_data = np.copy(self.field_data0)
        if len(self.items) == 0:
            self.stop()
        else:
            for item in self.items:
                self.set_item(item)
            self.field_data_items = np.copy(self.field_data)

    def explode(self):
        print('explode')
        if self.bomb == 1:
            for item in self.items:
                if isinstance(item, Bomb):
                    item.explode()
                    self.bomb = 2
                    self.set_item(item)
                    self.bomb_timer.stop()
                    self.bomb_timer.setInterval(1000)
                    self.bomb_timer.start()
                    print('1')
        elif self.bomb == 2:
            print('2')
            self.bomb_timer.stop()
            self.bomb = 0
            self.field_data = np.copy(self.field_data0)
            for item in self.items:
                if isinstance(item, Bomb):
                    self.items.remove(item)
                else:
                    self.set_item(item)
        self.field_data_items = np.copy(self.field_data)
        self.set_hero()
        self.show_field()


if __name__ == '__main__':
    window_width = 1920
    window_height = 1080 - 80
    app = QApplication(sys.argv)
    ex = MyGame(window_height, window_width)
    sys.exit(app.exec_())
