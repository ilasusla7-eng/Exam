# coding: utf-8
# license: GPLv3

"""Модуль визуализации.
Нигде, кроме этого модуля, не используются экранные координаты объектов.
Функции, создающие графические объекты и перемещающие их на экране, принимают физические координаты.
"""

header_font = "Arial-16"
"""Шрифт в заголовке"""

window_width = 1600
"""Ширина окна"""

window_height = 800
"""Высота окна"""

scale_factor = None
"""Масштабирование экранных координат по отношению к физическим.
Тип: float
Мера: количество пикселей на один метр."""


def calculate_scale_factor(max_distance):
    """Вычисляет значение глобальной переменной **scale_factor** по данной характерной длине"""
    global scale_factor
    scale_factor = 0.4 * min(window_height, window_width) / max_distance
    print('Scale factor:', scale_factor)


def scale_x(x):
    """Возвращает экранную **x** координату по **x** координате модели.
    Принимает вещественное число, возвращает целое число.
    """
    return int(x * scale_factor) + window_width // 2


def scale_y(y):
    """Возвращает экранную **y** координату по **y** координате модели.
    Принимает вещественное число, возвращает целое число.
    Направление оси развёрнуто, чтобы у модели ось **y** смотрела вверх.
    """
    # Умножаем на scale_factor, инвертируем знак (минус) и смещаем к центру экрана
    return window_height // 2 - int(y * scale_factor)


def create_star_image(space, star):
    """Создаёт отображаемый объект звезды."""
    x = scale_x(star.x)
    y = scale_y(star.y)
    r = star.R
    star.image = space.create_oval([x - r, y - r], [x + r, y + r], fill=star.color)


def create_planet_image(space, planet):
    """Создаёт отображаемый объект планеты."""
    x = scale_x(planet.x)
    y = scale_y(planet.y)
    r = planet.R
    # Рисуем круг для планеты, используя её индивидуальный цвет и радиус
    planet.image = space.create_oval([x - r, y - r], [x + r, y + r], fill=planet.color)


def create_satellite_image(space, satellite):
    """Создаёт отображаемый объект спутника (маленький круг)."""
    x = scale_x(satellite.x)
    y = scale_y(satellite.y)
    r = satellite.R
    satellite.image = space.create_oval([x - r, y - r], [x + r, y + r],
                                        fill=satellite.color)


# ---------------------------------------------------------------------------
#  Отрисовка орбит.
# ---------------------------------------------------------------------------

orbit_outline = "#444444"
"""Цвет линий орбит."""

orbit_item_tag = "orbit_line"
"""Тег, которым помечаются все графические элементы-орбиты (для скрытия)."""

show_orbits = True
"""Показывать ли орбиты на экране."""


def _draw_orbit(space, center_x, center_y, radius):
    """Рисует одну орбиту -- окружность вокруг центра в физических координатах."""
    cx = scale_x(center_x)
    cy = scale_y(center_y)
    rr = int(radius * scale_factor)
    item = space.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                             outline=orbit_outline, tag=orbit_item_tag)
    if not show_orbits:
        space.itemconfig(item, state='hidden')


def draw_orbits(space, space_objects):
    """Рисует орбиты всех тел кинематической системы.

    Для планет центром служит звезда-владелец, для спутников -- планета.
    Тела без орбитальных параметров (например, загруженные из файла под
    ньютоновской моделью) игнорируются.
    """
    space.delete(orbit_item_tag)  # удалить старые линии орбит
    for body in space_objects:
        parent = getattr(body, 'orbit_parent', None)
        radius = getattr(body, 'orbit_radius', None)
        if parent is None or radius is None:
            continue
        _draw_orbit(space, parent.x, parent.y, radius)


def set_orbits_visible(space, visible):
    """Включает/выключает отображение орбит на холсте."""
    global show_orbits
    show_orbits = visible
    state = 'normal' if visible else 'hidden'
    space.itemconfig(orbit_item_tag, state=state)


def update_system_name(space, system_name):
    """Создаёт на холсте текст с названием системы небесных тел."""
    space.create_text(30, 80, tag="header", text=system_name, font=header_font)


def update_object_position(space, body):
    """Перемещает отображаемый объект на холсте."""
    x = scale_x(body.x)
    y = scale_y(body.y)
    r = body.R
    if x + r < 0 or x - r > window_width or y + r < 0 or y - r > window_height:
        space.coords(body.image, window_width + r, window_height + r,
                     window_width + 2 * r, window_height + 2 * r)  # положить за пределы окна
    space.coords(body.image, x - r, y - r, x + r, y + r)


if __name__ == "__main__":
    print("This module is not for direct call!")