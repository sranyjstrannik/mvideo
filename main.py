from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PIL import ImageGrab, Image, ImageChops
import sys, win32gui, time
import numpy as np
import win32com.client as comctl
import pyautogui

class Worker(QObject):
    def __init__(self, **kwargs):
        super(Worker,self).__init__()
        self.flag = True
        self.kwargs = kwargs
        self.time_ = 0.28
        self.mintime_ = 0.8
        self.rects = kwargs['rects']
        self.images = []
        self.lasttimes = {0: 0, 1:0, 2:0, 3:0}
        self.tasks = []
        self.currentTask = -1
        self.t_ = 0

    def get_screens(self):
        # идея какая?
        # во-первых, получаем скрины
        # во-вторых, добавляем в очередь те скрины, которые соответствуют новым кубикам
        for i in range(4):
            t = time.time()
            if (t - self.lasttimes[i]) > self.mintime_:
                img = ImageGrab.grab(self.rects[i])
                # проверяем, есть ли на фотке красный цвет
                if len([i for i in img.getdata() if i[0] > 200 and i[1] < 100 and i[2] < 100]):
                    self.images += [(t, i)]
                    self.lasttimes[i] = time.time()

    def pressXToWin(self, i):
        print("pressXToWin", i)
        if i % 2 == 0:
            pyautogui.press("up")
            if i == 0:
                pyautogui.press("left")
            else: pyautogui.press("right")
        else:
            pyautogui.press("down")
            if i == 1:
                pyautogui.press("left")
            else: pyautogui.press("right")

    def run(self):
        count = 0
        while self.flag:
            self.get_screens()
            # после этого у нас есть очередь из инфы о скринах
            # теперь нужно из этой очереди выбрать наиболее близкий и туда пойти
            try:
                q = sorted(self.images, key = lambda x: x[0])
                if self.images: print("q:", q)
                self.tasks += [q[0][1]] # добавляем задачу
                self.images.remove(q[0]) #удаляем её из списка
            except Exception as e:
                continue
            # если  список задач не пустой и прошло необходимое время
            if self.tasks and (time.time()-self.t_) > self.time_:
                self.pressXToWin(self.tasks[0])
                print("двигаемся!", self.tasks[0])
                self.tasks = self.tasks[1:]
                self.t_ = time.time()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('main.ui', self)
        self.go_ = False
        self.pushButton.clicked.connect(self.go)
        self.show()
        self.rects_ = [(315, 467, 315+40, 467+40),
                       (315, 630, 315+40, 630+40),
                       (880, 467, 880+40, 467+40),
                       (880, 630, 880+40, 630+40)]

    def go(self):
        self.go_ = not self.go_
        if self.go_:
            self.pushButton.setText("Остановить")
            self.worker = Worker(rects = self.rects_)
            self.thread_ = QThread()
            self.worker.moveToThread(self.thread_)
            self.thread_.started.connect(self.worker.run)
            self.thread_.start()
        else:
            self.pushButton.setText("Начать")
            self.worker.flag = False


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())



