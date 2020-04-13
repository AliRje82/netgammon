from abc import ABC, abstractmethod
from dataclasses import dataclass

import color


@dataclass
class Coordinates(ABC):
    width: int
    height: int

    @abstractmethod
    def __getitem__(self, item):
        pass


@dataclass
class DiceCoordinates(Coordinates):
    width: int = 30
    height: int = 30
    red_x1: int = 330
    red_x2: int = 360
    white_x1: int = 110
    white_x2: int = 140
    y: int = 270

    def __getitem__(self, item):
        dice_color, dice = item
        if dice_color == color.RED:
            if dice == 0:
                return self.red_x1, self.y
            elif dice == 1:
                return self.red_x2, self.y
        elif dice_color == color.WHITE:
            if dice == 0:
                return self.white_x1, self.y
            elif dice == 1:
                return self.white_x2, self.y


@dataclass
class PointCoordinates(Coordinates):
    red_y: int
    white_y: int
    home_x: int
    outer_x: int
    x_step: int = 35

    @abstractmethod
    def __getitem__(self, point):
        if 1 <= point <= 6:
            x = self.home_x + (6 - point) * self.x_step
            return x, self.red_y
        if 7 <= point <= 12:
            x = self.outer_x + (12 - point) * self.x_step
            return x, self.red_y
        if 13 <= point <= 18:
            x = self.outer_x + (point - 13) * self.x_step
            return x, self.white_y
        if 19 <= point <= 24:
            x = self.home_x + (point - 19) * self.x_step
            return x, self.white_y


@dataclass
class PointPiecesCoordinates(PointCoordinates):
    width: int = 26
    height: int = 26
    red_y: int = 43
    white_y: int = 530
    home_x: int = 275
    outer_x: int = 25

    def __getitem__(self, item):
        point, piece_pos = item
        piece_pos = piece_pos if point in range(13) else -piece_pos
        x, y = super().__getitem__(point)
        y += piece_pos * self.height
        return x, y


@dataclass
class FromPointCoordinates(PointCoordinates):
    width: int = 30
    height: int = 210
    home_x: int = 273
    outer_x: int = 23
    red_y: int = 15
    white_y: int = 375
    bar_x: int = 250

    def __getitem__(self, point):
        if point == 0:
            return self.bar_x, self.white_y
        elif point == 25:
            return self.bar_x, self.red_y
        return super().__getitem__(point)


@dataclass
class ToPointCoordinates(PointCoordinates):
    width: int = 30
    height: int = 30
    home_x: int = 273
    outer_x: int = 23
    red_y: int = 247
    white_y: int = 323
    bear_off_x: int = 455
    bear_off_y: int = 285

    def __getitem__(self, point):
        if point in {0, 25}:
            return self.bear_off_x, self.bear_off_y
        return super().__getitem__(point)


FROM_COORDS = FromPointCoordinates()
TO_COORDS = ToPointCoordinates()
PIECE_COORDS = PointPiecesCoordinates()
DICE_COORDS = DiceCoordinates()