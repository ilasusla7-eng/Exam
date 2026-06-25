# coding: utf-8
# license: GPLv3

from solar_objects import Star, Planet, Satellite


def read_space_objects_data_from_file(input_filename):
    """Считывает данные о космических объектах из файла."""
    objects = []
    with open(input_filename) as input_file:
        for line in input_file:
            if len(line.strip()) == 0 or line[0] == '#':
                continue
            parts = line.split()
            object_type = parts[0].lower()

            if object_type == "star":
                star = Star()
                parse_star_parameters(line, star)
                objects.append(star)
            elif object_type == "planet":
                planet = Planet()
                parse_planet_parameters(line, planet)
                objects.append(planet)
            elif object_type == "satellite":
                satellite = Satellite()
                parse_satellite_parameters(line, satellite, objects)
                objects.append(satellite)
            else:
                print(f"Unknown space object: {object_type}")

    return objects


def parse_star_parameters(line, star):
    parts = line.split()
    star.R = int(parts[1])
    star.color = parts[2]
    star.m = float(parts[3])
    star.x = float(parts[4])
    star.y = float(parts[5])
    star.Vx = float(parts[6])
    star.Vy = float(parts[7])


def parse_planet_parameters(line, planet):
    parts = line.split()
    planet.R = int(parts[1])
    planet.color = parts[2]
    planet.m = float(parts[3])
    planet.x = float(parts[4])
    planet.y = float(parts[5])
    planet.Vx = float(parts[6])
    planet.Vy = float(parts[7])


def parse_satellite_parameters(line, satellite, objects):
    """Формат: Satellite <радиус> <цвет> <масса> <x> <y> <Vx> <Vy> <индекс_родителя>"""
    parts = line.split()
    satellite.R = int(parts[1])
    satellite.color = parts[2]
    satellite.m = float(parts[3])
    satellite.x = float(parts[4])
    satellite.y = float(parts[5])
    satellite.Vx = float(parts[6])
    satellite.Vy = float(parts[7])
    parent_index = int(parts[8])
    satellite.parent = objects[parent_index]


def write_space_objects_data_to_file(output_filename, space_objects):
    """Сохраняет данные о космических объектах в файл.

    Формат совпадает с файлами вроде solar_system.txt: каждая строка --
    один объект (Star/Planet/Satellite) с его параметрами. Для спутника
    в конце дописывается индекс родительской планеты в списке.
    """
    with open(output_filename, 'w') as out_file:
        for obj in space_objects:
            if obj.type == 'star':
                out_file.write(
                    f"Star {obj.R} {obj.color} {obj.m} "
                    f"{obj.x} {obj.y} {obj.Vx} {obj.Vy}\n")
            elif obj.type == 'planet':
                out_file.write(
                    f"Planet {obj.R} {obj.color} {obj.m} "
                    f"{obj.x} {obj.y} {obj.Vx} {obj.Vy}\n")
            elif obj.type == 'satellite':
                parent_index = space_objects.index(obj.parent)
                out_file.write(
                    f"Satellite {obj.R} {obj.color} {obj.m} "
                    f"{obj.x} {obj.y} {obj.Vx} {obj.Vy} {parent_index}\n")


# ---------------------------------------------------------------------------
#  Процедурная генерация системы из семи звёзд.
#  Звёзды выстроены в горизонтальный ряд; у каждой -- своё число планет,
#  распределённых по орбитам. Направление вращения зависит от чётности
#  орбиты. Для части планет создаются спутники.
# ---------------------------------------------------------------------------

import math


# Раскладка по звёздам: (число планет, максимум планет на орбиту).
# Нечётные звёзды -- 30 планет / максимум 4 на орбиту (8 орбит).
# Чётные звёзды   -- 15 планет / максимум 3 на орбите (5 орбит).
_STARS_LAYOUT = [
    (30, 4),  # 1-я звезда (нечётная)
    (15, 3),  # 2-я звезда (чётная)
    (30, 4),  # 3-я звезда (нечётная)
    (15, 3),  # 4-я звезда (чётная)
    (30, 4),  # 5-я звезда (нечётная)
    (15, 3),  # 6-я звезда (чётная)
    (30, 4),  # 7-я звезда (нечётная)
]

# Горизонтальный шаг между звёздами (физические единицы). Подобран так,
# чтобы внешние орбиты соседних звёзд пересекались ровно на 1 орбиту.
# D чуть больше 256+166-30=392, чтобы предпоследние орбиты не касались
_STAR_SPACING = 410.0

# Радиусы орбит: первая орбита и шаг между соседними орбитами.
_ORBIT_FIRST = 46.0
_ORBIT_STEP = 30.0

# Цвета звёзд по порядку.
_STAR_COLORS = ["white", "cyan", "yellow", "orange", "red",
                "magenta", "green"]

# Палитра цветов планет (циклически).
_PLANET_COLORS = ["orange", "blue", "green", "red", "brown",
                  "gray", "pink", "violet", "gold", "navy"]

# Цвета спутников.
_SATELLITE_COLORS = ["white", "lightgray", "silver"]

# Радиус орбиты спутника вокруг планеты (физические единицы). Должен быть
# достаточно велик, чтобы в экранных координатах спутник оказывался за
# пределами диска планеты.
_SATELLITE_ORBIT = 16.0


def _orbit_radius_for(orbit_number):
    """Физический радиус орбиты по её номеру (нумерация с 1)."""
    return _ORBIT_FIRST + (orbit_number - 1) * _ORBIT_STEP


def _distribute_planets_over_orbits(total, per_orbit):
    """Возвращает список чисел планет на каждой орбите.

    Число орбит -- ceil(total / per_orbit). Планеты раскладываются равномерно:
    первые орбиты получают по per_orbit, последняя -- остаток.
    """
    num_orbits = (total + per_orbit - 1) // per_orbit
    distribution = []
    remaining = total
    for _ in range(num_orbits):
        take = min(per_orbit, remaining)
        distribution.append(take)
        remaining -= take
    return distribution


def _direction_for_orbit(orbit_number):
    """Направление вращения планет на орбите.

    Чётные орбиты -- против часовой стрелки (+1), нечётные -- по часной (-1).
    """
    return +1 if orbit_number % 2 == 0 else -1


def _make_star(index):
    """Создаёт звезду под номером **index** (с 1) и помещает её в ряд."""
    star = Star()
    star.R = 11
    star.color = _STAR_COLORS[(index - 1) % len(_STAR_COLORS)]
    star.m = 1.98892E30
    # Звёзды в ряд по оси x, симметрично относительно начала координат.
    offset = (index - 4) * _STAR_SPACING  # индексы 1..7 -> смещения -3D..+3D
    star.x = offset
    star.y = 0.0
    star.Vx = 0.0
    star.Vy = 0.0
    # Звёзды в кинематической модели неподвижны.
    star.orbit_parent = None
    star.orbit_radius = None
    return star


def _make_planet(star, planet_index_in_star, orbit_number,
                 slot_in_orbit, slots_in_orbit):
    """Создаёт планету на заданной орбите звезды.

    **planet_index_in_star** -- порядковый номер планеты у звезды (с 1),
    используется для назначения спутников и цвета.
    """
    planet = Planet()
    planet.R = 6
    planet.color = _PLANET_COLORS[(planet_index_in_star - 1) % len(_PLANET_COLORS)]
    planet.m = 5.974E24
    radius = _orbit_radius_for(orbit_number)
    # Равномерно раскладываем планеты орбиты по начальному углу, чтобы они
    # не накладывались друг на друга и не сталкивались.
    angle = 2.0 * math.pi * (slot_in_orbit - 1) / slots_in_orbit
    planet.orbit_parent = star
    planet.orbit_radius = radius
    planet.orbit_angle = angle
    planet.orbit_number = orbit_number
    planet.orbit_direction = _direction_for_orbit(orbit_number)
    planet.x = star.x + radius * math.cos(angle)
    planet.y = star.y + radius * math.sin(angle)
    planet.Vx = 0.0
    planet.Vy = 0.0
    return planet


def _make_satellite(planet, satellite_index, total_satellites):
    """Создаёт спутник планеты.

    **satellite_index** -- порядковый номер спутника у планеты (с 1).
    Спутники вращаются по часовой стрелке для всех орбит (по условию).
    """
    satellite = Satellite()
    satellite.R = 2
    satellite.color = _SATELLITE_COLORS[(satellite_index - 1) % len(_SATELLITE_COLORS)]
    satellite.m = 7.347E22
    radius = _SATELLITE_ORBIT
    angle = 2.0 * math.pi * (satellite_index - 1) / total_satellites
    satellite.orbit_parent = planet
    satellite.orbit_radius = radius
    satellite.orbit_angle = angle
    satellite.orbit_number = 1
    # Спутники всегда вращаются по часовой стрелке.
    satellite.orbit_direction = -1
    satellite.parent = planet
    satellite.x = planet.x + radius * math.cos(angle)
    satellite.y = planet.y + radius * math.sin(angle)
    satellite.Vx = 0.0
    satellite.Vy = 0.0
    return satellite


def _planet_needs_satellites(star_index, planet_index_in_star):
    """Число спутников, которое нужно создать для данной планеты.

    Нечётные звёзды: у 10, 20, 30-й планеты -- по 2 спутника.
    Чётные звёзды:   у 5, 10, 15-й планеты -- по 1 спутнику.
    """
    if star_index % 2 == 1:  # нечётная звезда
        if planet_index_in_star in (10, 20, 30):
            return 2
    else:                    # чётная звезда
        if planet_index_in_star in (5, 10, 15):
            return 1
    return 0


def generate_seven_star_system():
    """Создаёт процедурно сгенерированную систему из семи звёзд.

    Возвращает список космических объектов (звёзды, планеты, спутники),
    готовый к использованию в кинематической орбитальной модели.
    """
    objects = []

    for star_index in range(1, len(_STARS_LAYOUT) + 1):
        total_planets, per_orbit = _STARS_LAYOUT[star_index - 1]
        star = _make_star(star_index)
        objects.append(star)

        orbits = _distribute_planets_over_orbits(total_planets, per_orbit)
        planet_counter = 0
        for orbit_number, planets_on_orbit in enumerate(orbits, start=1):
            for slot in range(1, planets_on_orbit + 1):
                planet_counter += 1
                planet = _make_planet(star, planet_counter, orbit_number,
                                      slot, planets_on_orbit)
                objects.append(planet)

                n_satellites = _planet_needs_satellites(star_index, planet_counter)
                for s in range(1, n_satellites + 1):
                    objects.append(_make_satellite(planet, s, n_satellites))

    return objects


if __name__ == "__main__":
    # Самопроверка генератора: печатаем сводку без запуска GUI.
    system = generate_seven_star_system()
    stars = [o for o in system if o.type == 'star']
    planets = [o for o in system if o.type == 'planet']
    satellites = [o for o in system if o.type == 'satellite']
    print(f"Stars: {len(stars)}, Planets: {len(planets)}, "
          f"Satellites: {len(satellites)}, Total: {len(system)}")
    for i, star in enumerate(stars, start=1):
        sp = [p for p in planets if p.orbit_parent is star]
        ss = [s for s in satellites if s.orbit_parent in sp]
        print(f"  Star {i} ({star.color}): planets={len(sp)}, "
              f"satellites={len(ss)}")