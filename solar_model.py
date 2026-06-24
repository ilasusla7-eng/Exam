# coding: utf-8
# license: GPLv3

gravitational_constant = 6.67408E-11

# Настраиваемые параметры расчёта орбит
ORBIT_DT = 2000                # шаг интегрирования (секунды)
MAX_STEPS = 50_000_000          # максимальное число шагов (для Нептуна ~5.2 млн)
MAX_TRAIL_POINTS = 500000      # максимальное число точек в орбите
CLOSE_THRESHOLD = 5e8          # порог замыкания в метрах (500 тыс. км)
MIN_STEPS_TO_CLOSE = 500       # минимальное число шагов перед проверкой замыкания


def calculate_force(body, space_objects):
    body.Fx = body.Fy = 0
    for obj in space_objects:
        if body == obj:
            continue
        r = ((body.x - obj.x) ** 2 + (body.y - obj.y) ** 2) ** 0.5
        if r == 0:
            continue
        F = gravitational_constant * body.m * obj.m / (r * r)
        body.Fx -= F * (body.x - obj.x) / r
        body.Fy -= F * (body.y - obj.y) / r


def move_space_object(body, dt):
    ax = body.Fx / body.m
    body.Vx += ax * dt
    body.x += body.Vx * dt
    ay = body.Fy / body.m
    body.Vy += ay * dt
    body.y += body.Vy * dt


def recalculate_space_objects_positions(space_objects, dt):
    for body in space_objects:
        calculate_force(body, space_objects)
    for body in space_objects:
        move_space_object(body, dt)


def compute_orbits_all(space_objects):
    if not space_objects:
        return

    # --- Интеграция вперёд ---
    fwd_objects = []
    for obj in space_objects:
        new_obj = obj.__class__()
        new_obj.m = obj.m
        new_obj.x = obj.x
        new_obj.y = obj.y
        new_obj.Vx = obj.Vx
        new_obj.Vy = obj.Vy
        fwd_objects.append(new_obj)

    fwd_trajectories = {}
    start_positions = {}
    closed_forward = {}
    points_count = {}
    step_counter = {}

    for i, t_obj in enumerate(fwd_objects):
        fwd_trajectories[t_obj] = [(t_obj.x, t_obj.y)]
        start_positions[t_obj] = (space_objects[i].x, space_objects[i].y)
        closed_forward[t_obj] = False
        points_count[t_obj] = 1
        step_counter[t_obj] = 0

    for step in range(MAX_STEPS):
        # Вычисляем силы и перемещаем все тела
        for t_obj in fwd_objects:
            calculate_force(t_obj, fwd_objects)
        for t_obj in fwd_objects:
            move_space_object(t_obj, ORBIT_DT)

            if not closed_forward[t_obj] and points_count[t_obj] < MAX_TRAIL_POINTS:
                step_counter[t_obj] += 1
                # Добавляем точку
                fwd_trajectories[t_obj].append((t_obj.x, t_obj.y))
                points_count[t_obj] += 1

                # Проверка замыкания (после минимального числа шагов)
                if step_counter[t_obj] > MIN_STEPS_TO_CLOSE:
                    sx, sy = start_positions[t_obj]
                    dx = t_obj.x - sx
                    dy = t_obj.y - sy
                    dist = (dx*dx + dy*dy)**0.5
                    if dist < CLOSE_THRESHOLD:
                        closed_forward[t_obj] = True

        # Проверяем, можно ли завершить цикл (все замкнулись или достигли лимита точек)
        all_done = True
        for t_obj in fwd_objects:
            if not (closed_forward[t_obj] or points_count[t_obj] >= MAX_TRAIL_POINTS):
                all_done = False
                break
        if all_done:
            break

    # --- Интеграция назад ---
    bwd_objects = []
    for obj in space_objects:
        new_obj = obj.__class__()
        new_obj.m = obj.m
        new_obj.x = obj.x
        new_obj.y = obj.y
        new_obj.Vx = obj.Vx
        new_obj.Vy = obj.Vy
        bwd_objects.append(new_obj)

    bwd_trajectories = {}
    start_positions_bwd = {}
    closed_backward = {}
    points_count_bwd = {}
    step_counter_bwd = {}

    for i, t_obj in enumerate(bwd_objects):
        bwd_trajectories[t_obj] = []
        start_positions_bwd[t_obj] = (space_objects[i].x, space_objects[i].y)
        closed_backward[t_obj] = False
        points_count_bwd[t_obj] = 0
        step_counter_bwd[t_obj] = 0

    for step in range(MAX_STEPS):
        for t_obj in bwd_objects:
            calculate_force(t_obj, bwd_objects)
        for t_obj in bwd_objects:
            move_space_object(t_obj, -ORBIT_DT)

            if not closed_backward[t_obj] and points_count_bwd[t_obj] < MAX_TRAIL_POINTS:
                step_counter_bwd[t_obj] += 1
                bwd_trajectories[t_obj].append((t_obj.x, t_obj.y))
                points_count_bwd[t_obj] += 1

                if step_counter_bwd[t_obj] > MIN_STEPS_TO_CLOSE:
                    sx, sy = start_positions_bwd[t_obj]
                    dx = t_obj.x - sx
                    dy = t_obj.y - sy
                    dist = (dx*dx + dy*dy)**0.5
                    if dist < CLOSE_THRESHOLD:
                        closed_backward[t_obj] = True

        all_done = True
        for t_obj in bwd_objects:
            if not (closed_backward[t_obj] or points_count_bwd[t_obj] >= MAX_TRAIL_POINTS):
                all_done = False
                break
        if all_done:
            break

    # --- Объединение траекторий и сохранение в оригинальные объекты ---
    for i, orig in enumerate(space_objects):
        fwd_points = fwd_trajectories[fwd_objects[i]]
        bwd_points = bwd_trajectories[bwd_objects[i]]
        bwd_points.reverse()   # теперь от прошлого к настоящему
        full_orbit = bwd_points + fwd_points
        orig.orbit_points = full_orbit


if __name__ == "__main__":
    print("This module is not for direct call!")