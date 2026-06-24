# coding: utf-8
# license: GPLv3

gravitational_constant = 6.67408E-11
"""Гравитационная постоянная Ньютона G"""


# ---------------------------------------------------------------------------
#  Исходная (ньютоновская) модель для систем, загруженных из файла.
#  Для процедурно сгенерированной системы из семи звёзд используется
#  кинематическая орбитальная модель (см. ниже).
# ---------------------------------------------------------------------------

def calculate_force(body, space_objects):
    """Вычисляет силу, действующую на тело.

    Параметры:

    **body** — тело, для которого нужно вычислить дейстующую силу.
    **space_objects** — список объектов, которые воздействуют на тело.
    """

    body.Fx = body.Fy = 0
    for obj in space_objects:
        if body == obj:
            continue  # тело не действует гравитационной силой на само себя!
        r = ((body.x - obj.x)**2 + (body.y - obj.y)**2)**0.5
        F = (gravitational_constant * body.m * obj.m) / r ** 2
        body.Fx -= (F * (body.x - obj.x)) / r
        body.Fy -= (F * (body.y - obj.y)) / r


def move_space_object(body, dt):
    """Перемещает тело в соответствии с действующей на него силой.

    Параметры:

    **body** — тело, которое нужно переместить.
    """

    ax = body.Fx / body.m
    body.Vx += ax * dt
    body.x += body.Vx * dt

    ay = body.Fy / body.m
    body.Vy += ay * dt
    body.y += body.Vy * dt


def recalculate_space_objects_positions(space_objects, dt):
    """Пересчитывает координаты объектов.

    Если хотя бы у одного тела заданы орбитальные параметры (тело получено
    процедурным генератором семи звёзд), используется кинематическая
    орбитальная модель, иначе -- исходная ньютоновская.

    Параметры:

    **space_objects** — список объектов, для которых нужно пересчитать координаты.
    **dt** — шаг по времени
    """

    if any(getattr(body, 'orbit_radius', None) is not None for body in space_objects):
        advance_orbital_system(space_objects, dt)
        return

    for body in space_objects:
        calculate_force(body, space_objects)
    for body in space_objects:
        move_space_object(body, dt)


# ---------------------------------------------------------------------------
#  Кинематическая орбитальная модель.
#  Звёзды неподвижны; планеты вращаются вокруг своей звезды по круговой
#  орбите, спутники -- вокруг своей планеты. Направление и скорость
#  вращения определяются орбитальными параметрами тела, поэтому планеты
#  одной звезды никогда не сталкиваются между собой, а спутники не
#  сталкиваются ни с планетой, ни друг с другом (у каждого своя орбита).
# ---------------------------------------------------------------------------

# Базовая угловая скорость (рад/усл.ед. времени). Подобрана так, чтобы
# движение было хорошо видно на экране: уменьшается с удалением от центра.
_base_angular_speed = 0.04
_reference_orbit = 40.0


def _direction_sign(body):
    """Знак угловой скорости тела (+1 -- против часовой, -1 -- по часовой).

    Задаётся орбитальным параметром **orbit_direction**:
    +1 -- против часовой стрелки, -1 -- по часовой стрелке.
    """
    direction = getattr(body, 'orbit_direction', 0)
    if direction < 0:
        return -1.0
    if direction > 0:
        return 1.0
    return 1.0


def _angular_velocity(body):
    """Угловая скорость тела с учётом направления вращения.

    Внутренние орбиты движутся быстрее внешних (T ~ r, мягче закона Кеплера),
    что делает картинку похожей на настоящую систему и сохраняет видимость
    движения даже у внешних планет.
    """
    radius = body.orbit_radius
    speed = _base_angular_speed * _reference_orbit / radius
    return speed * _direction_sign(body)


def _advance_planet(body, dt):
    """Сдвигает планету по её орбите вокруг звезды-владельца."""
    parent = body.orbit_parent
    body.orbit_angle += _angular_velocity(body) * dt
    ca, sa = _cos_sin(body.orbit_angle)
    body.x = parent.x + body.orbit_radius * ca
    body.y = parent.y + body.orbit_radius * sa
    # синхронизируем скорость для корректного сохранения в файл
    body.Vx = -body.orbit_radius * sa * _angular_velocity(body)
    body.Vy = body.orbit_radius * ca * _angular_velocity(body)


def _advance_satellite(body, dt):
    """Сдвигает спутник по его орбите вокруг планеты-владельца."""
    parent = body.orbit_parent
    body.orbit_angle += _angular_velocity(body) * dt
    ca, sa = _cos_sin(body.orbit_angle)
    body.x = parent.x + body.orbit_radius * ca
    body.y = parent.y + body.orbit_radius * sa


def advance_orbital_system(space_objects, dt):
    """Обновляет положения всех тел кинематической системы за шаг **dt**."""
    for body in space_objects:
        if getattr(body, 'orbit_parent', None) is None:
            continue  # звёзды неподвижны
        if body.type == 'satellite':
            _advance_satellite(body, dt)
        else:
            _advance_planet(body, dt)


def _cos_sin(angle):
    """Локальная обёртка над math.cos/sin (импортируется лениво)."""
    import math
    return math.cos(angle), math.sin(angle)


if __name__ == "__main__":
    print("This module is not for direct call!")