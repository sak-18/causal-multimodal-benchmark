# imports specific to Blender's python API
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

import os
import random
import math
import json
import logging
import sys
import itertools
import argparse

parser = argparse.ArgumentParser(description='Render CANDLE')
parser.add_argument('--gpu-id', default=0, type=int)
parser.add_argument('--start', default=0, type=int)
parser.add_argument('--output-dir', default='./images/', type=str)
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])

logging.basicConfig(level=logging.INFO)
os.close(1)

camera_jitter = 0.5
data_dir = "./data/"
output_dir = args.output_dir 
number_of_objects = 1
start = args.start

# configuration of the various factors to render. Modify as necessary
scenes = ["indoor", "outdoor", "playground", "bridge", "city square", "hall", "grassland", "garage", "street", "beach", "station", "tunnel", "moonlit grass", "dusk city", "skywalk", "garden"]
lights = ["left", "middle", "right"]

properties = {
    "object_type": ["cube", "sphere", "cylinder", "cone", "torus"],
    "color": ["red", "blue", "yellow", "purple", "orange"],
    "size": [1.5, 2, 2.5],
    "rotation": [0, 15, 30, 45, 60, 90],
}

# bounds of valid locations where the foreground object can be placed
bounds = {
    "indoor": {
        "xmin": -4.5,
        "xmax": 4.5,
        "ymin": -15,
        "ymax": 0
    },
    "outdoor": {
        "xmin": -4.5,
        "xmax": 4.5,
        "ymin": -20,
        "ymax": 0
    },
    "playground": {
        "xmin": -4.5,
        "xmax": 4.5,
        "ymin": -20,
        "ymax": 0
    },
    "bridge": {
        "xmin": -4.5,
        "xmax": 4.5,
        "ymin": -20,
        "ymax": 0
    },
    "city square": {
        "xmin": -4.5,
        "xmax": 4.5,
        "ymin": -20,
        "ymax": 0
    },
    "hall": {
        "xmin": -4.5,
        "xmax": 4.5,
        "ymin": -15,
        "ymax": 0
    },
    "grassland": {
        "xmin": -4.5,
        "xmax": 4.5,
        "ymin": -15,
        "ymax": -2
    },
    "garage": {
        "xmin": -4.5,
        "xmax": 4.5,
        "ymin": -20,
        "ymax": 0
    },
    "street": {
        "xmin": -4.5,
        "xmax": 4.5,
        "ymin": -20,
        "ymax": 0
    },
    "beach": {
        "xmin": -4.5,
        "xmax": 4.5,
        "ymin": -20,
        "ymax": 0
    },
    "station": {
        "xmin": -4.5,
        "xmax": 4.5,
        "ymin": -20,
        "ymax": 0
    },
    "tunnel": {
        "xmin": -4.5,
        "xmax": 4.5,
        "ymin": -20,
        "ymax": 0
    },
    "moonlit grass": {
        "xmin": -4.5,
        "xmax": 4.5,
        "ymin": -20,
        "ymax": 0
    },
    "dusk city": {
        "xmin": -4.5,
        "xmax": 4.5,
        "ymin": -20,
        "ymax": 0
    },
    "skywalk": {
        "xmin": -4.5,
        "xmax": 4.5,
        "ymin": -20,
        "ymax": 0
    },
    "garden": {
        "xmin": -4.5,
        "xmax": 4.5,
        "ymin": -20,
        "ymax": 0
    },
}

# position of light in 3D space (x, y, z)
light_position = {
    "left": [5, -5, 7],
    "middle": [0, 0, 7],
    "right": [-5, 5, 7]
}

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

obs = [*properties.values()] * number_of_objects
causes = list(itertools.product(scenes, lights, *obs))

for image, cause in enumerate(itertools.islice(causes, start, len(causes)), start=start):
    scene = cause[0]
    light = cause[1]
    bpy.ops.wm.open_mainfile(filepath=os.path.join(data_dir, "scenes", scene + ".blend"))

    bpy.ops.wm.append(filename=os.path.join(data_dir, "lights", "lights.blend", "Object", "Point"))
    bpy.context.view_layer.objects.active = bpy.data.objects["Point"]
    bpy.ops.transform.translate(value=light_position[light])

    bpy.context.scene.render.engine='CYCLES'
    bpy.context.scene.render.resolution_x = 320
    bpy.context.scene.render.resolution_y = 240
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.tile_x = 256
    bpy.context.scene.render.tile_y = 256
    bpy.context.scene.cycles.samples = 128
    bpy.context.scene.cycles.transparent_min_bounces = 2
    bpy.context.scene.cycles.transparent_max_bounces = 2

    bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
    # bpy.context.preferences.addons['cycles'].preferences.compute_device = 'CUDA_0'
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.preferences.addons["cycles"].preferences.get_devices()
    for d in bpy.context.preferences.addons["cycles"].preferences.devices:
        d["use"] = False
    bpy.context.preferences.addons["cycles"].preferences.devices[args.gpu_id]["use"] = True
    # for d in bpy.context.preferences.addons["cycles"].preferences.devices:
        # logging.info(d["name"] + str(d["use"]))

    res_x = 320
    res_y = 240
    camera = bpy.data.objects['Camera']

    ground_truth = {}
    ground_truth["scene"] = scene
    ground_truth["lights"] = light
    ground_truth["objects"] = {}

    locations = []
    for object_id in range(number_of_objects):
        object_type, material, size_value, angle = cause[4*object_id+2:4*object_id+6]

        bpy.ops.wm.append(filename=os.path.join(data_dir, "objects", object_type + ".blend", "Object", object_type.capitalize()))

        new_object_name = '%s_%d' % (object_type.capitalize(), object_id)
        bpy.data.objects[object_type.capitalize()].name = new_object_name
        bpy.context.view_layer.objects.active = bpy.data.objects[new_object_name]

        bpy.context.object.rotation_euler[2] = angle

        bpy.ops.transform.resize(value=(size_value, size_value, size_value))

        while True:
            loc = Vector([random.uniform(bounds[scene]["xmin"], bounds[scene]["xmax"]), random.uniform(bounds[scene]["ymin"], bounds[scene]["ymax"]), 0])
            if any((p - loc).length < size_value * 2 for p in locations):
                continue
            locations.append(loc)
            break
        bpy.ops.transform.translate(value=(loc[0], loc[1], 0))

        bpy.ops.wm.append(filename=os.path.join(data_dir, "materials", material + ".blend", "Material", material.capitalize()))
        bpy.context.object.data.materials.append(bpy.data.materials[material.capitalize()])

        object = bpy.data.objects[new_object_name]
        object_bounds = [object.matrix_world @ Vector(x) for x in object.bound_box]
        object_bounds = [world_to_camera_view(bpy.context.scene, bpy.data.objects['Camera'], coord) for coord in object_bounds]
        object_bounds = [(round(x * res_x), round(y * res_y)) for x, y, _ in object_bounds]
        x, y = zip(*object_bounds)
        object_bounds = [(min(x), min(y)), (max(x), max(y))]


        object_dict = {
            "object_type": object_type,
            "color": material,
            "size": size_value,
            "rotation": angle,
            "bounds": object_bounds
        }
        ground_truth["objects"][new_object_name] = object_dict

    bpy.context.view_layer.objects.active = bpy.data.objects["Point"]
    bpy.ops.transform.translate(value=[light_position[light][0], (bounds[scene]["ymin"] + bounds[scene]["ymax"]) // 2, light_position[light][2]])

    bpy.data.objects['Camera'].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects['Camera']
    for axis in ['X', 'Y']:
        bpy.ops.transform.rotate(value=math.radians(random.uniform(-camera_jitter, camera_jitter)), orient_axis=axis, orient_type='LOCAL', orient_matrix_type='LOCAL')

    bpy.context.scene.render.filepath = os.path.join(output_dir, str(image) + ".jpg")
    bpy.ops.render.render(write_still=True)

    logging.info(str(image) + str(ground_truth))
    with open(os.path.join(output_dir, str(image) + ".json"), "w") as f:
        json.dump(ground_truth, f, indent=4)
