# coding: utf-8

class SpaceBody:
    """Базовый родительский класс для всех космических объектов"""
    m: float = 0.0
    x: float = 0.0
    y: float = 0.0
    Vx: float = 0.0
    Vy: float = 0.0
    Fx: float = 0.0
    Fy: float = 0.0
    R: int = 5
    color: str = "white"
    image = None
    orbit_points: list = []      
    orbit_line_id = None   
    orbit_parent = None
    orbit_radius = None
    orbit_angle = None
    orbit_number: int = 1
    orbit_direction: int = -1


class Star(SpaceBody):
    type: str = "star"
    R: int = 11
    color: str = "red"


class Planet(SpaceBody):
    type: str = "planet"
    color: str = "green"


class Satellite(Planet):
    type: str = "satellite"
    parent = None