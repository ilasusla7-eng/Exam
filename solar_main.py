# coding: utf-8
# license: GPLv3

import tkinter
from tkinter.filedialog import *
from solar_vis import *
from solar_model import *
from solar_input import *

perform_execution = False
physical_time = 0
displayed_time = None
time_step = None
space_objects = []
show_orbits = True

def execution():
    global physical_time, displayed_time
    dt = time_step.get()
    if dt != 0:
        recalculate_space_objects_positions(space_objects, dt)
    for body in space_objects:
        update_object_position(space, body)
    physical_time += dt
    displayed_time.set("%.1f" % physical_time + " seconds gone")
    if perform_execution:
        space.after(101 - int(time_speed.get()), execution)

def start_execution():
    global perform_execution
    perform_execution = True
    start_button['text'] = "Pause"
    start_button['command'] = stop_execution
    execution()

def stop_execution():
    global perform_execution
    perform_execution = False
    start_button['text'] = "Start"
    start_button['command'] = start_execution

def toggle_orbits():
    global show_orbits
    show_orbits = not show_orbits
    orbit_button['text'] = "Orbits: On" if show_orbits else "Orbits: Off"
    set_orbits_visible(space, show_orbits)

def recompute_orbits():
    """Пересчёт орбит с фиксированными параметрами (не зависит от time_step)."""
    compute_orbits_all(space_objects)
    create_orbit_lines(space, space_objects)
    set_orbits_visible(space, show_orbits)

def open_file_dialog():
    global space_objects, perform_execution
    perform_execution = False
    for obj in space_objects:
        if obj.image:
            space.delete(obj.image)
    in_filename = askopenfilename(filetypes=(("Text file", ".txt"),))
    if not in_filename:
        return
    space_objects = read_space_objects_data_from_file(in_filename)
    max_distance = max([max(abs(obj.x), abs(obj.y)) for obj in space_objects])
    calculate_scale_factor(max_distance)
    for obj in space_objects:
        if obj.type == 'star':
            create_star_image(space, obj)
        elif obj.type == 'planet':
            create_planet_image(space, obj)
        else:
            raise AssertionError()
    recompute_orbits()   # вычисляем и рисуем орбиты

def save_file_dialog():
    out_filename = asksaveasfilename(filetypes=(("Text file", ".txt"),))
    if out_filename:
        write_space_objects_data_to_file(out_filename, space_objects)

def main():
    global physical_time, displayed_time, time_step, time_speed, space, start_button, orbit_button
    print('Modelling started!')
    physical_time = 0

    root = tkinter.Tk()
    space = tkinter.Canvas(root, width=window_width, height=window_height, bg="black")
    space.pack(side=tkinter.TOP)

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

    orbit_button = tkinter.Button(frame, text="Orbits: On", command=toggle_orbits, width=10)
    orbit_button.pack(side=tkinter.LEFT)

    displayed_time = tkinter.StringVar()
    displayed_time.set(str(physical_time) + " seconds gone")
    time_label = tkinter.Label(frame, textvariable=displayed_time, width=30)
    time_label.pack(side=tkinter.RIGHT)

    root.mainloop()
    print('Modelling finished!')

if __name__ == "__main__":
    main()