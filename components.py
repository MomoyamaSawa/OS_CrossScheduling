from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from enum import Enum
from config import *
import threading


class VECTOR(Enum):
    N = [0, -1]
    W = [-1, 0]
    E = [1, 0]
    S = [0, 1]


class CARTYPE(Enum):
    NomalCar = 0
    SpecialCar = 1


class CARSTATUS(Enum):
    Normal = 0
    Cross = 1
    Out = 2
    Wait = 3


class Car(QGraphicsPixmapItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._status: CARSTATUS = CARSTATUS.Normal
        self._type: CARTYPE = None
        self._resource: int = None
        self._num: int = None
        self._prev: int = None
        self._vec: VECTOR = None
        self._p:bool = False

    def SetVector(self, vec: VECTOR):
        self._vec = vec

    def GetStatus(self) -> CARSTATUS:
        return self._status

    def GetType(self) -> CARTYPE:
        return self._type

    def SetStatus(self, status: CARSTATUS):
        self._status = status

    def GetResource(self) -> int:
        return self._resource

    def GetPrev(self) -> int:
        return self._prev

    def SetPrev(self, prev: int):
        self._prev = prev

    def GetVec(self) -> VECTOR:
        return self._vec

    def SetResource(self, resource: int = None):
        self._resource = resource

    def GetP(self) -> bool:
        return self._p

    def SetP(self, p: bool):
        self._p = p

    def GetNum(self) -> int:
        return self._num

    def SetNum(self, num: int):
        self._num = num


class NormalCar(Car):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPixmap(QPixmap(MyPath["NormalCar"]).scaled(ItemSize[0], ItemSize[1]))
        self._type = CARTYPE.NomalCar
        # Get the object's bounding box
        bounding_rect = self.boundingRect()
        # Move the object's origin to the center of the bounding box
        center = bounding_rect.center()
        self.setTransformOriginPoint(center)


class SpecialCar(Car):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPixmap(QPixmap(MyPath["SpecialCar"]).scaled(50, 50))
        self._type = CARTYPE.SpecialCar
        bounding_rect = self.boundingRect()
        center = bounding_rect.center()
        offset = QPointF(center.x() - 50 / 2, center.y() - 50 / 2)
        self.setTransformOriginPoint(center)


class SIGNALSTATUS(Enum):
    Red = 0
    Green = 1


class Signal(QGraphicsPixmapItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPixmap(QPixmap(MyPath["SignalRed"]).scaled(ItemSize[0], ItemSize[1]))
        self._status = None

    def ChangeStatus(self):
        if self._status == SIGNALSTATUS.Red:
            self._status = SIGNALSTATUS.Green
            self.setPixmap(QPixmap(MyPath["SignalGreen"]).scaled(ItemSize[0], ItemSize[1]))
        else:
            self._status = SIGNALSTATUS.Red
            self.setPixmap(QPixmap(MyPath["SignalRed"]).scaled(ItemSize[0], ItemSize[1]))
        self.update()

    def SetRedStatus(self):
        self._status = SIGNALSTATUS.Red
        self.setPixmap(QPixmap(MyPath["SignalRed"]).scaled(ItemSize[0], ItemSize[1]))

    def SetGreenStatus(self):
        self._status = SIGNALSTATUS.Green
        self.setPixmap(QPixmap(MyPath["SignalGreen"]).scaled(ItemSize[0], ItemSize[1]))

    def GetStutus(self) -> SIGNALSTATUS:
        return self._status


class Cross(QGraphicsPixmapItem):
    def __init__(self, x: int, y: int, side: int, parent=None):
        super().__init__(parent)

        self._4inRange: list[QRectF] = []
        self._4outRange: list[QRectF] = []
        self._4sig: list[threading.Semaphore] = []
        self._cars: list[Car] = [None, None, None, None]
        self._block: bool = False

        self.InitRange(x, y, side)
        self.InitSig()

    def InitRange(self, x: int, y: int, side: int):
        side2 = side / 2
        self._4inRange.append(QRectF(x, y, side2, side2))
        self._4inRange.append(QRectF(x + side2, y, side2, side2))
        self._4inRange.append(QRectF(x, y + side2, side2, side2))
        self._4inRange.append(QRectF(x + side2, y + side2, side2, side2))
        self._4outRange.append(QRectF(x - side2, y, side2, side2))
        self._4outRange.append(QRectF(x + side2, y - side2, side2, side2))
        self._4outRange.append(QRectF(x, y + 2 * side2, side2, side2))
        self._4outRange.append(QRectF(x + 2 * side2, y + side2, side2, side2))

    def InitSig(self):
        for i in range(4):
            self._4sig.append(threading.Semaphore(1))

    def GetInRange(self, index: int) -> QRectF:
        return self._4inRange[index]

    def GetInRanges(self) -> list[QRectF]:
        return self._4inRange

    def GetOutRange(self, index: int =None) -> QRectF:
        return self._4outRange[index]

    def GetOutRanges(self) -> list[QRectF]:
        return self._4outRange

    def IsBlocked(self) -> bool:
        return self._block

    def GetCar(self, num: int) -> Car:
        return self._cars[num]

    def SetCar(self, num: int, car: Car):
        self._cars[num] = car

    def GetSig(self, num: int) -> threading.Semaphore:
        return self._4sig[num]


class Lane(QGraphicsPixmapItem):
    def __init__(self, startArea: QRectF, signal: Signal, vector: VECTOR, parent=None):
        super().__init__(parent)
        self._vector: VECTOR = vector
        self._signal: Signal = signal
        self._car: list[Car] = []
        self._startArea: QRectF = startArea

    def GetCars(self) -> list[Car]:
        return self._car

    def GetSignal(self) -> Signal:
        return self._signal
