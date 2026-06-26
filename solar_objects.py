# coding: utf-8
# license: GPLv3

class Star:
    type: str = "star"
    m: float = 0.0
    x: float = 0.0
    y: float = 0.0
    Vx: float = 0.0
    Vy: float = 0.0
    Fx: float = 0.0
    Fy: float = 0.0
    R: int = 5
    color: str = "red"
    image = None
    orbit_points: list = []      # список кортежей (x, y)
    orbit_line_id = None   # ID линии на холсте
    orbit_parent = None
    orbit_radius = None
    orbit_angle = None
    orbit_number: int = 1
    orbit_direction: int = -1
    kinematic: bool = False


class Planet:
    type: str = "planet"
    m: float = 0.0
    x: float = 0.0
    y: float = 0.0
    Vx: float = 0.0
    Vy: float = 0.0
    Fx: float = 0.0
    Fy: float = 0.0
    R: int = 5
    color: str = "green"
    image = None
    orbit_points: list = []
    orbit_line_id = None
    orbit_parent = None
    orbit_radius = None
    orbit_angle = None
    orbit_number: int = 1
    orbit_direction: int = -1
    kinematic: bool = False


class Satellite(Planet):
    type: str = "satellite"
    parent = None
    orbit_points: list = []
    orbit_line_id = None