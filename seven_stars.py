# coding: utf-8
# license: GPLv3
"""Семизвёздная система — кинематическая модель.

Реализует сценарий по заданию:
  - 7 звёзд в ряд; у нечётных (1,3,5,7) по 30 планет, у чётных (2,4,6) по 15;
  - на нечётной звезде не более 4 планет на орбите, на чётной — не более 3;
  - спутники: у планет 5,10,15 чётных звёзд — по 1; у 10,20,30 нечётных — по 2;
  - планеты на чётных орбитах вращаются ПРОТИВ часовой, на нечётных — ПО часовой;
  - спутники всегда вращаются ПО часовой;
  - орбиты смежных звёзд пересекаются; столкновений нет (кинематика);
  - в интерфейсе можно включать/выключать отображение орбит.

Движение кинематическое (заданные круговые орбиты), гравитация не используется.
Запуск: python seven_stars.py
"""

import math
import tkinter


# ---------------------------------------------------------------------------
# Параметры модели (условные единицы)
# ---------------------------------------------------------------------------
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900

N_STARS = 7                 # число звёзд
STAR_SPACING = 10.0         # расстояние между соседними звёздами (D)
PLANETS_ODD = 30            # планет у нечётной звезды
PLANETS_EVEN = 15           # планет у чётной звезды
MAX_PER_ORBIT_ODD = 4       # максимум планет на орбиту у нечётной звезды
MAX_PER_ORBIT_EVEN = 3      # максимум планет на орбиту у чётной звезды

ORBIT_R0 = 2.0              # радиус первой (внутренней) орбиты
ORBIT_DR = 1.0              # шаг радиуса между орбитами
ORBIT_OMEGA = 1.5           # базовая угловая скорость планет (ω = ORBIT_OMEGA/√r)

SAT_ORBIT_R = 0.8           # радиус орбиты спутника вокруг планеты
SAT_OMEGA = 4.0             # угловая скорость спутника

# Радиусы отрисовки (в пикселах)
STAR_RADIUS_PX = 8
PLANET_RADIUS_PX = 4
SAT_RADIUS_PX = 2

# Направления вращения (Y вверх в модели):
#   +1 → против часовой (CCW),  -1 → по часовой (CW)
DIR_CCW = +1
DIR_CW = -1

# Палитры
STAR_COLORS = ["gold", "orange red", "cyan", "magenta",
               "lime green", "white", "violet"]
PLANET_COLORS = ["light blue", "light green", "salmon", "khaki",
                 "light cyan", "thistle", "peach puff", "pale green"]
SAT_COLOR = "gray70"


# ---------------------------------------------------------------------------
# Классы данных
# ---------------------------------------------------------------------------
class Star:
    """Звезда со своим списком планет. В кинематической модели неподвижна."""

    def __init__(self, number, x, y, color):
        self.number = number            # 1..7
        self.x = x
        self.y = y
        self.color = color
        self.image = None
        self.planets = []


class Planet:
    """Планета, движущаяся по круговой орбите вокруг звезды."""

    def __init__(self, parent_star, number, orbit_index, orbit_radius,
                 angle, omega, direction, color):
        self.parent_star = parent_star
        self.number = number                  # номер планеты у звезды (1..N)
        self.orbit_index = orbit_index        # номер орбиты (с 1)
        self.orbit_radius = orbit_radius
        self.angle = angle
        self.omega = omega
        self.direction = direction            # +1 CCW / -1 CW
        self.color = color
        self.x = 0.0
        self.y = 0.0
        self.image = None
        self.satellites = []


class Satellite:
    """Спутник, движущийся по круговой орбите вокруг планеты."""

    def __init__(self, parent_planet, angle, direction):
        self.parent_planet = parent_planet
        self.orbit_radius = SAT_ORBIT_R
        self.angle = angle
        self.omega = SAT_OMEGA
        self.direction = direction
        self.x = 0.0
        self.y = 0.0
        self.image = None
        self.color = SAT_COLOR

# ---------------------------------------------------------------------------
# Генератор системы по правилам задания
# ---------------------------------------------------------------------------
def generate_seven_stars_system():
    """Строит список из 7 звёзд со всеми планетами и спутниками."""
    stars = []
    for i in range(N_STARS):
        star_number = i + 1
        is_odd = (star_number % 2 == 1)
        star = Star(number=star_number,
                    x=(i - (N_STARS - 1) / 2.0) * STAR_SPACING,
                    y=0.0,
                    color=STAR_COLORS[i])

        n_planets = PLANETS_ODD if is_odd else PLANETS_EVEN
        max_per_orbit = MAX_PER_ORBIT_ODD if is_odd else MAX_PER_ORBIT_EVEN

        # Распределение планет по орбитам
        n_full_orbits = n_planets // max_per_orbit
        remainder = n_planets % max_per_orbit
        orbit_counts = [max_per_orbit] * n_full_orbits
        if remainder > 0:
            orbit_counts.append(remainder)

        planet_number = 0
        for orbit_index, m_in_orbit in enumerate(orbit_counts, start=1):
            orbit_radius = ORBIT_R0 + (orbit_index - 1) * ORBIT_DR
            # направление планеты по чётности номера орбиты:
            #   нечётная орбита → CW, чётная орбита → CCW
            direction = DIR_CCW if orbit_index % 2 == 0 else DIR_CW
            omega = ORBIT_OMEGA / math.sqrt(orbit_radius)

            for j in range(m_in_orbit):
                planet_number += 1
                phase = 2.0 * math.pi * j / m_in_orbit   # равномерно по кругу
                color = PLANET_COLORS[(orbit_index + j) % len(PLANET_COLORS)]
                planet = Planet(star, planet_number, orbit_index,
                                orbit_radius, phase, omega, direction, color)

                # Спутники по правилам задания
                if (not is_odd) and planet_number in (5, 10, 15):
                    # чётная звезда, по 1 спутнику
                    planet.satellites.append(Satellite(planet, 0.0, DIR_CW))
                elif is_odd and planet_number in (10, 20, 30):
                    # нечётная звезда, по 2 спутника (разнесены по фазе на π)
                    planet.satellites.append(Satellite(planet, 0.0, DIR_CW))
                    planet.satellites.append(Satellite(planet, math.pi, DIR_CW))

                star.planets.append(planet)

        stars.append(star)
    return stars


# ---------------------------------------------------------------------------
# Кинематика: пересчёт координат
# ---------------------------------------------------------------------------
def update_positions(stars, dt):
    """Сдвигает углы и пересчитывает декартовы координаты всех тел."""
    for star in stars:
        for planet in star.planets:
            planet.angle += planet.direction * planet.omega * dt
            planet.x = star.x + planet.orbit_radius * math.cos(planet.angle)
            planet.y = star.y + planet.orbit_radius * math.sin(planet.angle)
            for sat in planet.satellites:
                sat.angle += sat.direction * sat.omega * dt
                sat.x = planet.x + sat.orbit_radius * math.cos(sat.angle)
                sat.y = planet.y + sat.orbit_radius * math.sin(sat.angle)


# ---------------------------------------------------------------------------
# Глобальное состояние GUI
# ---------------------------------------------------------------------------
stars = []
scale_factor = 1.0
space: "tkinter.Canvas" = None  # type: ignore[assignment]
running = False
show_orbits = False
physical_time = 0.0


def to_screen_x(x):
    return int(WINDOW_WIDTH / 2 + x * scale_factor)


def to_screen_y(y):
    # инверсия, чтобы ось Y модели смотрела вверх
    return int(WINDOW_HEIGHT / 2 - y * scale_factor)


def compute_scale():
    """Автомасштаб по охвату всей системы."""
    max_abs_x = 0.0
    max_abs_y = 0.0
    for star in stars:
        for planet in star.planets:
            ax = abs(star.x) + planet.orbit_radius
            ay = planet.orbit_radius
            if ax > max_abs_x:
                max_abs_x = ax
            if ay > max_abs_y:
                max_abs_y = ay
    x_extent = 2 * max_abs_x if max_abs_x > 0 else 1.0
    y_extent = 2 * max_abs_y if max_abs_y > 0 else 1.0
    sx = WINDOW_WIDTH * 0.9 / x_extent
    sy = WINDOW_HEIGHT * 0.8 / y_extent
    return min(sx, sy)


def create_body_image(body, radius_px):
    cx = to_screen_x(body.x)
    cy = to_screen_y(body.y)
    body.image = space.create_oval(cx - radius_px, cy - radius_px,
                                   cx + radius_px, cy + radius_px,
                                   fill=body.color, outline="")


def update_body_image(body, radius_px):
    cx = to_screen_x(body.x)
    cy = to_screen_y(body.y)
    space.coords(body.image, cx - radius_px, cy - radius_px,
                 cx + radius_px, cy + radius_px)


orbit_line_ids = []


def draw_orbits():
    """Рисует орбиты планет вокруг звёзд (статичные, позади тел).
    Орбиты спутников не рисуются: они перемещаются вместе с планетами,
    поэтому отрисовывались бы с задержкой/мерцанием.
    """
    for star in stars:
        scx = to_screen_x(star.x)
        scy = to_screen_y(star.y)
        for planet in star.planets:
            r = int(planet.orbit_radius * scale_factor)
            oid = space.create_oval(scx - r, scy - r, scx + r, scy + r,
                                    outline="gray40", dash=(2, 3))
            orbit_line_ids.append(oid)
            space.tag_lower(oid)   # орбита — позади всех тел


def clear_orbits():
    for oid in orbit_line_ids:
        space.delete(oid)
    orbit_line_ids.clear()


def toggle_orbits():
    global show_orbits
    show_orbits = not show_orbits
    clear_orbits()
    if show_orbits:
        draw_orbits()

# ---------------------------------------------------------------------------
# Главный цикл анимации
# ---------------------------------------------------------------------------
def tick():
    """Один кадр: пересчёт позиций + обновление отрисовки."""
    global physical_time
    dt = 0.05
    update_positions(stars, dt)
    for star in stars:
        update_body_image(star, STAR_RADIUS_PX)
        for planet in star.planets:
            update_body_image(planet, PLANET_RADIUS_PX)
            for sat in planet.satellites:
                update_body_image(sat, SAT_RADIUS_PX)
    physical_time += dt
    time_label_var.set("%.1f секунд прошло" % physical_time)
    if running:
        space.after(30, tick)


def start():
    global running
    running = True
    start_button.config(text="Пауза", command=pause)
    tick()


def pause():
    global running
    running = False
    start_button.config(text="Старт", command=start)


# ---------------------------------------------------------------------------
# Сборка интерфейса
# ---------------------------------------------------------------------------
def main():
    global stars, scale_factor, space, time_label_var, start_button
    stars = generate_seven_stars_system()
    scale_factor = compute_scale()

    root = tkinter.Tk()
    root.title("Семь звёзд — кинематическая модель")

    space = tkinter.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
                           bg="black")
    space.pack(side=tkinter.TOP)

    # Первичная отрисовка тел (поверх орбит, поэтому орбиты сначала)
    draw_orbits_placeholder = False  # по умолчанию орбиты выключены
    for star in stars:
        create_body_image(star, STAR_RADIUS_PX)
        for planet in star.planets:
            create_body_image(planet, PLANET_RADIUS_PX)
            for sat in planet.satellites:
                create_body_image(sat, SAT_RADIUS_PX)

    frame = tkinter.Frame(root)
    frame.pack(side=tkinter.BOTTOM)

    global running
    running = False
    start_button = tkinter.Button(frame, text="Старт", command=start, width=8)
    start_button.pack(side=tkinter.LEFT, padx=4)

    orbits_check = tkinter.Checkbutton(frame, text="Орбиты",
                                       command=toggle_orbits)
    orbits_check.pack(side=tkinter.LEFT, padx=4)

    time_label_var = tkinter.StringVar()
    time_label_var.set("0.0 секунд прошло")
    time_label = tkinter.Label(frame, textvariable=time_label_var, width=24)
    time_label.pack(side=tkinter.LEFT, padx=4)

    info = tkinter.Label(frame,
                         text="Нечётные звёзды: 30 планет (≤4/орбита). "
                              "Чётные: 15 планет (≤3/орбита). "
                              "Чётная орбита → CCW, нечётная → CW, "
                              "спутник → CW.",
                         fg="gray30")
    info.pack(side=tkinter.LEFT, padx=8)

    root.mainloop()


if __name__ == "__main__":
    main()