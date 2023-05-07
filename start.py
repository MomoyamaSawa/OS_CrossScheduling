import sys, random, threading
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from components import *
from config import *
from qfluentwidgets import *


class MyWidget(QWidget):
    _sigStart = pyqtSignal(int)
    _sigStop = pyqtSignal()
    _sigReset = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)

        self._startButton = PrimaryPushButton("Start")
        self._startButton.clicked.connect(
            lambda: self._sigStart.emit(int(self._comboBox.currentText()))
        )
        self._stopButton = PushButton("Stop")
        self._stopButton.clicked.connect(self._sigStop.emit)
        self._resetButton = PushButton("Reset")
        self._resetButton.clicked.connect(self._sigReset.emit)

        self._label = QLabel("设置速度")
        self._comboBox = ComboBox(self)
        self._comboBox.addItems(["5", "4", "3", "2"])
        self._comboBox.setCurrentIndex(1)
        self._comboBox.currentTextChanged.connect(self.__onChangeCombo)

        self.__initLayer()

    def __initLayer(self):
        self._layout.addWidget(self._startButton)
        self._layout.addWidget(self._stopButton)
        self._layout.addWidget(self._resetButton)
        self._layout.addWidget(self._label)
        self._layout.addWidget(self._comboBox)

    def __onChangeCombo(self):
        content = "新设置的速度会在重置后再开始时生效，越小的速度越容易观察到死锁的发生"
        w = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title="Info",
            content=content,
            orient=Qt.Orientation.Vertical,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self,
        )
        w.show()


class ImageScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__Init()

    def Start(self, speed):
        if self._isStarted:
            return
        self._isStarted = True
        global Speed
        Speed = speed
        self._signalTimer.start(SignalTime)
        self._carTimer.start(CarTime)
        self._frameTimer.start(FrameTime)

    def Stop(self):
        self._isStarted = False
        self._signalTimer.stop()
        self._carTimer.stop()
        self._frameTimer.stop()

    def Reset(self):
        self.clear()
        self.__Init()

    def __Init(self):
        self._background = QGraphicsPixmapItem(
            QPixmap(MyPath["Background"]).scaled(SceneSize[0], SceneSize[1])
        )
        self.addItem(self._background)

        self._nSignal = Signal()
        self._sSignal = Signal()
        self._wSignal = Signal()
        self._eSignal = Signal()
        self.addItem(self._nSignal)
        self.addItem(self._sSignal)
        self.addItem(self._wSignal)
        self.addItem(self._eSignal)

        self._nLane = Lane(QRectF(355, 630, 50, 50), self._nSignal, VECTOR.N)
        self._sLane = Lane(QRectF(295, 20, 50, 50), self._sSignal, VECTOR.S)
        self._wLane = Lane(QRectF(630, 295, 50, 50), self._wSignal, VECTOR.W)
        self._eLane = Lane(QRectF(20, 355, 50, 50), self._eSignal, VECTOR.E)
        self._cross = Cross(250, 250, 200)

        self._exSpecialCar = SpecialCar()
        self.exNormalCar = NormalCar()
        self.addItem(self.exNormalCar)
        self.addItem(self._exSpecialCar)
        label = QLabel("特种车(警车，救护车，消防车)")
        self.proxy1 = QGraphicsProxyWidget()
        self.proxy1.setWidget(label)
        self.addItem(self.proxy1)
        label = QLabel("普通车")
        self.proxy2 = QGraphicsProxyWidget()
        self.proxy2.setWidget(label)
        self.addItem(self.proxy2)

        self._signalTimer = QTimer()
        self._signalTimer.timeout.connect(self.__UpdateSignalStatus)
        self._carTimer = QTimer()
        self._carTimer.timeout.connect(self.__UpdateCar)
        self._frameTimer = QTimer()
        self._frameTimer.timeout.connect(self.__Update)
        self._isStarted = False

        self.__initLayout()
        self.__InitSignal()

    def __initLayout(self):
        self._background.setPos(0, 0)
        self._nSignal.setPos(420, 10)
        self._sSignal.setPos(225, 645)
        self._wSignal.setPos(10, 225)
        self._eSignal.setPos(645, 420)
        self._exSpecialCar.setPos(500, 20)
        self.exNormalCar.setPos(500, 70)
        self.proxy1.setPos(550, 20)
        self.proxy2.setPos(550, 70)

    def __InitSignal(self):
        self._nSignal.SetRedStatus()
        self._sSignal.SetRedStatus()
        self._wSignal.SetGreenStatus()
        self._eSignal.SetGreenStatus()

    def __UpdateSignalStatus(self):
        self._nSignal.ChangeStatus()
        self._sSignal.ChangeStatus()
        self._wSignal.ChangeStatus()
        self._eSignal.ChangeStatus()

    def __UpdateCar(self):
        """
        Random car generation in four lanes
        """
        lane: Lane = None
        # Traverse all four lanes
        for lane in self._nLane, self._eLane, self._sLane, self._wLane:
            # Check if there is a car at the beginning of the lane, if there is a car then do not generate
            if lane == self._nLane:
                if not (
                    len(lane._car) == 0
                    or lane._car[-1].pos().y() < lane._startArea.y() - ItemSize[1]
                ):
                    continue
            elif lane == self._sLane:
                if not (
                    len(lane._car) == 0
                    or lane._car[-1].pos().y() > lane._startArea.y() + ItemSize[1]
                ):
                    continue
            elif lane == self._wLane:
                if not (
                    len(lane._car) == 0
                    or lane._car[-1].pos().x() < lane._startArea.x() - ItemSize[0]
                ):
                    continue
            elif lane == self._eLane:
                if not (
                    len(lane._car) == 0
                    or lane._car[-1].pos().x() > lane._startArea.x() + ItemSize[0]
                ):
                    continue
            # Generate different cars or no cars based on random numbers
            random_float = random.random()
            if random_float > NoCarProbability:
                if random_float < NoCarProbability + NormalCarProbability:
                    lane._car.append(NormalCar())
                else:
                    lane._car.append(SpecialCar())
                if lane == self._nLane:
                    lane._car[-1].setRotation(-90)
                    lane._car[-1].SetVector(VECTOR.N)
                elif lane == self._sLane:
                    lane._car[-1].setRotation(90)
                    lane._car[-1].SetVector(VECTOR.S)
                elif lane == self._wLane:
                    lane._car[-1].setRotation(180)
                    lane._car[-1].SetVector(VECTOR.W)
                elif lane == self._eLane:
                    lane._car[-1].setRotation(0)
                    lane._car[-1].SetVector(VECTOR.E)
                lane._car[-1].setPos(lane._startArea.x(), lane._startArea.y())
                global CarNum
                lane._car[-1].SetNum(CarNum)
                CarNum += 1
                self.addItem(lane._car[-1])

    def __Update(self):
        """
        Update the position of all cars every frame
        """
        lane: Lane = None
        # Traverse all four lanes
        for lane in self._nLane, self._sLane, self._wLane, self._eLane:
            prevCar: Car = None
            car: Car = None
            for car in lane.GetCars():
                if car is not None:
                    rect: QRectF = car.sceneBoundingRect()

                    if car.GetStatus() == CARSTATUS.Wait:
                        prevCar = car
                        continue

                    # Check if the car is about to leave the intersection, to free up resources
                    elif (
                        rect.intersects(self._cross.GetOutRange(0))
                        or rect.intersects(self._cross.GetOutRange(1))
                        or rect.intersects(self._cross.GetOutRange(2))
                        or rect.intersects(self._cross.GetOutRange(3))
                    ) and car.GetStatus() == CARSTATUS.Cross:
                        if rect.intersects(self._cross.GetOutRange(0)):
                            self.__Out(car, 0)
                        elif rect.intersects(self._cross.GetOutRange(1)):
                            self.__Out(car, 1)
                        elif rect.intersects(self._cross.GetOutRange(2)):
                            self.__Out(car, 2)
                        elif rect.intersects(self._cross.GetOutRange(3)):
                            self.__Out(car, 3)

                    # Check if the car is in the intersection
                    elif (
                        rect.intersects(self._cross.GetInRange(0))
                        or rect.intersects(self._cross.GetInRange(1))
                        or rect.intersects(self._cross.GetInRange(2))
                        or rect.intersects(self._cross.GetInRange(3))
                    ) and car.GetStatus() != CARSTATUS.Out:
                        # Check whether the traffic light allows the car just entering the intersection to pass
                        if car.GetType() == CARTYPE.SpecialCar:
                            pass
                        elif car.GetStatus() == CARSTATUS.Normal:
                            if lane.GetSignal().GetStutus() == SIGNALSTATUS.Red:
                                prevCar = car
                                continue
                        # To request resources
                        if (
                            rect.intersects(self._cross.GetInRange(0))
                            and car.GetResource() != 0
                            and car.GetPrev() != 0
                        ):
                            t = threading.Thread(target=self.__Go, args=(car, 0))
                            t.start()
                        if (
                            rect.intersects(self._cross.GetInRange(1))
                            and car.GetResource() != 1
                            and car.GetPrev() != 1
                        ):
                            t = threading.Thread(target=self.__Go, args=(car, 1))
                            t.start()
                        if (
                            rect.intersects(self._cross.GetInRange(2))
                            and car.GetResource() != 2
                            and car.GetPrev() != 2
                        ):
                            t = threading.Thread(target=self.__Go, args=(car, 2))
                            t.start()
                        if (
                            rect.intersects(self._cross.GetInRange(3))
                            and car.GetResource() != 3
                            and car.GetPrev() != 3
                        ):
                            t = threading.Thread(target=self.__Go, args=(car, 3))
                            t.start()
                    # If it is not a vehicle that is about to leave the intersection,
                    # or a vehicle at the intersection, then it is a vehicle on the road
                    # to maintain a safe distance from the car in front of you.
                    # Otherwise, no movement
                    elif car.GetStatus() != CARSTATUS.Out and prevCar is not None:
                        if (
                            (
                                car.GetVec() == VECTOR.N
                                and car.pos().y() - prevCar.pos().y()
                                < ItemSize[1] + SafeDistance
                            )
                            or (
                                car.GetVec() == VECTOR.S
                                and car.pos().y() - prevCar.pos().y()
                                > -(ItemSize[1] + SafeDistance)
                            )
                            or (
                                car.GetVec() == VECTOR.W
                                and car.pos().x() - prevCar.pos().x()
                                < ItemSize[0] + SafeDistance
                            )
                            or (
                                car.GetVec() == VECTOR.E
                                and car.pos().x() - prevCar.pos().x()
                                > -(ItemSize[0] + SafeDistance)
                            )
                        ):
                            prevCar = car
                            continue
                    # The car can be moved under the following conditions
                    if (
                        car.GetStatus() == CARSTATUS.Normal
                        or car.GetStatus() == CARSTATUS.Out
                        or (
                            car.GetStatus() == CARSTATUS.Cross
                            and car.GetResource() != None
                        )
                    ) :
                        # If the car that grabbed the resource during the deadlock resolution process
                        # has not yet entered the intersection, release the resource
                        # to the car that is inside the intersection
                        if (
                            self._cross.IsBlocked() == True
                            and car.GetResource() != None
                            and car.GetP() == False
                        ):
                            self._cross.SetCar(car.GetResource(), None)
                            self._cross.GetSig(car.GetResource()).release()
                            car.SetResource(None)
                            car.SetStatus(CARSTATUS.Normal)
                        # Next is the normal movement of the car
                        else:
                            x, y = 0, 0
                            if car.GetVec() == VECTOR.N:
                                x, y = 0, -1
                            elif car.GetVec() == VECTOR.S:
                                x, y = 0, 1
                            elif car.GetVec() == VECTOR.W:
                                x, y = -1, 0
                            elif car.GetVec() == VECTOR.E:
                                x, y = 1, 0
                            car.moveBy(x * Speed, y * Speed)
                            # Delete if out of range
                            if (
                                car.pos().y() < 0
                                or car.pos().y() > 650
                                or car.pos().x() < 0
                                or car.pos().x() > 650
                            ):
                                self.removeItem(car)
                                lane._car.remove(car)
                    prevCar = car
        # Detecting deadlocks
        i = [0, 0, 0, 0]
        if (
            self._cross.GetCar(0) != None
            and self._cross.GetCar(0).GetVec() == VECTOR.S
            and self._cross.GetCar(0).GetStatus() == CARSTATUS.Wait
        ):
            i[0] = 1
        if (
            self._cross.GetCar(1) != None
            and self._cross.GetCar(1).GetVec() == VECTOR.W
            and self._cross.GetCar(1).GetStatus() == CARSTATUS.Wait
        ):
            i[1] = 1
        if (
            self._cross.GetCar(2) != None
            and self._cross.GetCar(2).GetVec() == VECTOR.E
            and self._cross.GetCar(2).GetStatus() == CARSTATUS.Wait
        ):
            i[2] = 1
        if (
            self._cross.GetCar(3) != None
            and self._cross.GetCar(3).GetVec() == VECTOR.N
            and self._cross.GetCar(3).GetStatus() == CARSTATUS.Wait
        ):
            i[3] = 1
        # Deadlock resolution
        if i == [1, 1, 1, 1]:
            self._cross._block = True
            # Four cars marked with deadbolts
            self._cross.GetCar(0).SetP(True)
            self._cross.GetCar(1).SetP(True)
            self._cross.GetCar(2).SetP(True)
            self._cross.GetCar(3).SetP(True)
            self._cross.GetSig(0).release()
            self._cross.GetSig(1).release()
            self._cross.GetSig(2).release()
            self._cross.GetSig(3).release()
        else:
            self._cross._block = False

    def __Go(self, car: Car, areaID: int):
        """
        Get the resources of a block
        """
        car.SetStatus(CARSTATUS.Wait)
        self._cross.GetSig(areaID).acquire()
        print(f"({areaID}): " + str(car.GetNum()))
        self._cross.SetCar(areaID, car)
        car.SetStatus(CARSTATUS.Cross)
        if car.GetResource() != None:
            if car.GetP() == False:
                self._cross.SetCar(car.GetResource(), None)
                self._cross.GetSig(car._resource).release()
            car.SetPrev(car.GetResource())
        car.SetResource(areaID)

    def __Out(self, car: Car, areaID: int):
        self._cross.SetCar(areaID, None)
        self._cross.GetSig(areaID).release()
        car.SetStatus(CARSTATUS.Out)
        car.SetResource(None)


class Main(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Main")
        self._layout = QHBoxLayout(self)
        self._leftWindow = MyWidget(self)
        self._rightWindow = QGraphicsView(self)
        scene = ImageScene()
        self._rightWindow.setScene(scene)
        self._rightWindow.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.__initSlots()
        self.__initLayout()

    def __initSlots(self):
        self._leftWindow._sigStart.connect(self._rightWindow.scene().Start)
        self._leftWindow._sigStop.connect(self._rightWindow.scene().Stop)
        self._leftWindow._sigReset.connect(self._rightWindow.scene().Reset)

    def __initLayout(self):
        self.setGeometry(0, 0, 1020, 720)
        self._leftWindow.setFixedSize(300, 300)
        self._rightWindow.setFixedSize(720, 720)
        self._rightWindow.setSceneRect(0, 0, SceneSize[0], SceneSize[1])
        self._layout.addWidget(self._leftWindow)
        self._layout.addWidget(self._rightWindow)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    start = Main()
    start.show()
    app.exec()
