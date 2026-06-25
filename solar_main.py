# coding: utf-8
# license: GPLv3

import tkinter
from tkinter.filedialog import *
from solar_vis import *
from solar_model import *
from solar_input import *

perform_execution = False
"""Флаг цикличности выполнения расчёта"""

physical_time = 0
"""Физическое время от начала расчёта.
Тип: float"""

displayed_time = None
"""Отображаемое на экране время.
Тип: переменная tkinter"""

time_step = None
"""Шаг по времени при моделировании.
Тип: float"""

space_objects = []
"""Список космических объектов."""


def execution():
    """Функция исполнения -- выполняется циклически, вызывая обработку всех небесных тел,
    а также обновляя их положение на экране.
    Цикличность выполнения зависит от значения глобальной переменной perform_execution.
    При perform_execution == True функция запрашивает вызов самой себя по таймеру через от 1 мс до 100 мс.
    """
    global physical_time
    global displayed_time
    recalculate_space_objects_positions(space_objects, time_step.get())
    for body in space_objects:
        update_object_position(space, body)
    physical_time += time_step.get()
    displayed_time.set("%.1f" % physical_time + " seconds gone")

    if perform_execution:
        space.after(101 - int(time_speed.get()), execution)


def start_execution():
    """Обработчик события нажатия на кнопку Start.
    Запускает циклическое исполнение функции execution.
    """
    global perform_execution
    perform_execution = True
    start_button['text'] = "Pause"
    start_button['command'] = stop_execution

    execution()
    print('Started execution...')


def stop_execution():
    """Обработчик события нажатия на кнопку Start.
    Останавливает циклическое исполнение функции execution.
    """
    global perform_execution
    perform_execution = False
    start_button['text'] = "Start"
    start_button['command'] = start_execution
    print('Paused execution.')


def open_file_dialog():
    """Открывает диалоговое окно выбора имени файла и вызывает
    функцию считывания параметров системы небесных тел из данного файла.
    Считанные объекты сохраняются в глобальный список space_objects
    """
    global space_objects
    global perform_execution
    perform_execution = False
    _clear_objects()
    in_filename = askopenfilename(filetypes=(("Text file", ".txt"),))
    space_objects = read_space_objects_data_from_file(in_filename)
    _attach_file_orbits(space_objects)
    _display_system(space_objects)


def _attach_file_orbits(space_objects):
    """Достраивает орбитальные параметры для тел, загруженных из файла.

    У файла нет данных об орбитах, поэтому радиус орбиты планеты/спутника
    считается как расстояние до центра притяжения: для планеты -- ближайшая
    звезда, для спутника -- его планета (.parent). Звёзды служат центрами.
    Это позволяет рисовать орбиты и для систем из файла.
    """
    import math
    stars = [o for o in space_objects if o.type == 'star']
    if not stars:
        return

    def nearest_star(obj):
        best, best_d = None, float('inf')
        for star in stars:
            d = math.hypot(obj.x - star.x, obj.y - star.y)
            if d < best_d:
                best, best_d = star, d
        return best, best_d

    for obj in space_objects:
        if obj.type == 'star':
            obj.orbit_parent = None
            obj.orbit_radius = None
            continue
        if obj.type == 'satellite':
            parent = getattr(obj, 'parent', None)
            if parent is None:
                parent, _ = nearest_star(obj)
            obj.orbit_parent = parent
            obj.orbit_radius = math.hypot(obj.x - parent.x, obj.y - parent.y)
        else:  # planet
            star, d = nearest_star(obj)
            obj.orbit_parent = star
            obj.orbit_radius = d

        # Недостающие параметры кинематической модели: начальный угол,
        # направление и номер орбиты. Начальный угол берём из текущего
        # положения тела относительно центра, направление -- по часовой
        # стрелке по умолчанию (как спутники). Без них модель падала бы.
        dx = obj.x - obj.orbit_parent.x
        dy = obj.y - obj.orbit_parent.y
        obj.orbit_angle = math.atan2(dy, dx)
        obj.orbit_direction = -1  # по часовой стрелке
        obj.orbit_number = 1



def generate_system_dialog():
    """Генерирует процедурную систему из семи звёзд и отображает её.

    Использует кинематическую орбитальную модель: звёзды неподвижны,
    планеты вращаются по своим орбитам, спутники -- вокруг планет.
    """
    global space_objects
    global perform_execution
    perform_execution = False
    _clear_objects()
    space_objects = generate_seven_star_system()
    _display_system(space_objects)
    print('Generated 7-star system:', len(space_objects), 'objects')


def toggle_orbits():
    """Включает/выключает отображение орбит по состоянию флажка в интерфейсе."""
    set_orbits_visible(space, show_orbits_var.get())


def _clear_objects():
    """Удаляет с холста изображения всех текущих объектов и линии орбит."""
    global space_objects
    for obj in space_objects:
        if getattr(obj, 'image', None) is not None:
            space.delete(obj.image)
    space.delete(orbit_item_tag)


def _display_system(objects):
    """Вычисляет масштаб и создаёт изображения для всех объектов системы.

    Звёзды и планеты получают изображения; спутники -- маленькие круги.
    Также (пере)рисовываются орбиты кинематической системы, если они есть.
    """
    max_distance = max([max(abs(obj.x), abs(obj.y)) for obj in objects])
    calculate_scale_factor(max_distance)

    for obj in objects:
        if obj.type == 'star':
            create_star_image(space, obj)
        elif obj.type == 'planet':
            create_planet_image(space, obj)
        elif obj.type == 'satellite':
            create_satellite_image(space, obj)
        else:
            raise AssertionError()

    draw_orbits(space, objects)


def save_file_dialog():
    """Открывает диалоговое окно выбора имени файла и вызывает
    функцию считывания параметров системы небесных тел из данного файла.
    Считанные объекты сохраняются в глобальный список space_objects
    """
    out_filename = asksaveasfilename(filetypes=(("Text file", ".txt"),))
    write_space_objects_data_to_file(out_filename, space_objects)


def main():
    """Главная функция главного модуля.
    Создаёт объекты графического дизайна библиотеки tkinter: окно, холст, фрейм с кнопками, кнопки.
    """
    global physical_time
    global displayed_time
    global time_step
    global time_speed
    global space
    global start_button
    global show_orbits_var

    print('Modelling started!')
    physical_time = 0

    root = tkinter.Tk()
    # космическое пространство отображается на холсте типа Canvas
    space = tkinter.Canvas(root, width=window_width, height=window_height, bg="black")
    space.pack(side=tkinter.TOP)
    # нижняя панель с кнопками
    frame = tkinter.Frame(root)
    frame.pack(side=tkinter.BOTTOM)

    start_button = tkinter.Button(frame, text="Start", command=start_execution, width=6)
    start_button.pack(side=tkinter.LEFT)

    time_step = tkinter.DoubleVar()
    time_step.set(1)
    time_step_entry = tkinter.Entry(frame, textvariable=time_step)
    time_step_entry.pack(side=tkinter.LEFT)

    time_speed = tkinter.DoubleVar()
    scale = tkinter.Scale(frame, variable=time_speed, orient=tkinter.HORIZONTAL)
    scale.pack(side=tkinter.LEFT)

    load_file_button = tkinter.Button(frame, text="Open file...", command=open_file_dialog)
    load_file_button.pack(side=tkinter.LEFT)
    save_file_button = tkinter.Button(frame, text="Save to file...", command=save_file_dialog)
    save_file_button.pack(side=tkinter.LEFT)

    # Кнопка генерации системы из семи звёзд (кинематическая модель).
    generate_button = tkinter.Button(frame, text="Generate 7 stars",
                                     command=generate_system_dialog)
    generate_button.pack(side=tkinter.LEFT)

    # Флажок включения/выключения отображения орбит.
    show_orbits_var = tkinter.BooleanVar()
    show_orbits_var.set(show_orbits)
    orbits_check = tkinter.Checkbutton(frame, text="Orbits",
                                       variable=show_orbits_var,
                                       command=toggle_orbits)
    orbits_check.pack(side=tkinter.LEFT)

    displayed_time = tkinter.StringVar()
    displayed_time.set(str(physical_time) + " seconds gone")
    time_label = tkinter.Label(frame, textvariable=displayed_time, width=30)
    time_label.pack(side=tkinter.RIGHT)

    root.mainloop()
    print('Modelling finished!')

if __name__ == "__main__":
    main()