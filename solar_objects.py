# coding: utf-8
# license: GPLv3

class Star:
    type = "star"
    m = 0
    x = 0
    y = 0
    Vx = 0
    Vy = 0
    Fx = 0
    Fy = 0
    R = 5
    color = "red"
    image = None
    orbit_points = []      # список кортежей (x, y)
    orbit_line_id = None   # ID линии на холсте


class Planet:
    type = "planet"
    m = 0
    x = 0
    y = 0
    Vx = 0
    Vy = 0
    Fx = 0
    Fy = 0
    R = 5
    color = "green"
    image = None
    orbit_points = []
    orbit_line_id = None


class Satellite(Planet):
    type = "satellite"
    parent = None
    orbit_points = []
    orbit_line_id = None