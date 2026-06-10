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
    """Сохраняет данные о космических объектах в файл."""
    with open(output_filename, 'w') as out_file:
        for i, obj in enumerate(space_objects):
            if obj.type == 'star':
                out_file.write(f"Star {obj.R} {obj.color} {obj.m} {obj.x} {obj.y} {obj.Vx} {obj.Vy}\n")
            elif obj.type == 'planet':
                out_file.write(f"Planet {obj.R} {obj.color} {obj.m} {obj.x} {obj.y} {obj.Vx} {obj.Vy}\n")
            elif obj.type == 'satellite':
                parent_index = space_objects.index(obj.parent)
                out_file.write(f"Satellite {obj.R} {obj.color} {obj.m} {obj.x} {obj.y} {obj.Vx} {obj.Vy} {parent_index}\n")


if __name__ == "__main__":
    print("This module is not for direct call!")