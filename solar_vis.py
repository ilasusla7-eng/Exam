# coding: utf-8
# license: GPLv3

header_font = "Arial-16"
window_width = 1600
window_height = 800
scale_factor = None

def calculate_scale_factor(max_distance):
    global scale_factor
    scale_factor = 0.4 * min(window_height, window_width) / max_distance

def scale_x(x):
    return int(x * scale_factor) + window_width // 2

def scale_y(y):
    return window_height // 2 - int(y * scale_factor)

def create_star_image(space, star):
    x = scale_x(star.x)
    y = scale_y(star.y)
    r = star.R
    star.image = space.create_oval([x - r, y - r], [x + r, y + r], fill=star.color)

def create_planet_image(space, planet):
    x = scale_x(planet.x)
    y = scale_y(planet.y)
    r = planet.R
    planet.image = space.create_oval([x - r, y - r], [x + r, y + r], fill=planet.color)

def update_system_name(space, system_name):
    space.create_text(30, 80, tag="header", text=system_name, font=header_font)

def update_object_position(space, body):
    x = scale_x(body.x)
    y = scale_y(body.y)
    r = body.R
    if x + r < 0 or x - r > window_width or y + r < 0 or y - r > window_height:
        space.coords(body.image, window_width + r, window_height + r,
                     window_width + 2 * r, window_height + 2 * r)
    else:
        space.coords(body.image, x - r, y - r, x + r, y + r)

def create_orbit_lines(space, space_objects):
    """Создаёт линии орбит для всех объектов и сохраняет их ID в атрибуте orbit_line_id."""
    # Удаляем старые линии
    space.delete("orbit")
    for obj in space_objects:
        if not hasattr(obj, 'orbit_points') or not obj.orbit_points:
            obj.orbit_line_id = None
            continue
        pts = []
        for x, y in obj.orbit_points:
            pts.append(scale_x(x))
            pts.append(scale_y(y))
        if len(pts) >= 4:
            line_id = space.create_line(pts, fill="gray", width=1, tag="orbit")
            obj.orbit_line_id = line_id
        else:
            obj.orbit_line_id = None

def set_orbits_visible(space, visible):
    """Показывает или скрывает все линии с тегом 'orbit'."""
    state = "normal" if visible else "hidden"
    for item in space.find_withtag("orbit"):
        space.itemconfig(item, state=state)

if __name__ == "__main__":
    print("This module is not for direct call!")