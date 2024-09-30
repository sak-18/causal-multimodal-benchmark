"""Generate text for the CANDLE based on Multimodal3DIdent dataset."""

import argparse
import csv
import os
import json
import random

SIZES = {
1.5 : 'small',
2   : 'medium',
2.5 : 'large',
}

COLORS = {
  "red": [
    "red",
    "maroon",
    "cherry red"
    ],
  "blue": [
    "blue",
    "teal",
    "navy blue",
  ],
  "yellow": [
    "yellow",
    "mustard",
    "canary yellow"
  ],
  "purple": [
    "purple",
    "violet",
    "orchid purple"
  ],
  "orange": [
    "orange",
    "amber",
    "carrot orange",
  ]
}


PHRASES = {
    0: 'A {SIZE} {OBJECT} of {COLOR} color is visible.',
    1: 'A {COLOR} {OBJECT} is shown in {SIZE} size.',
    2: 'A {COLOR} colored {OBJECT} which is {SIZE} in size is shown.',
    3: 'The picture is of a {SIZE} {OBJECT} in {COLOR} color.',
    4: 'There is a {SIZE} {COLOR} object in the form of a {OBJECT}.'}

# Define the folder containing the JSON files
folder_path = '/home/svishnu6/causal-multimodal-benchmark/datasets/CANDLE'

# List all files in the folder
files = os.listdir(folder_path)

# Filter out the JSON files
json_files = [file for file in files if file.endswith('.json')]

# Read all JSON files and store the data in a list
json_data = []

# Read all JSON files, process and save them with the new description
for json_file in json_files:
    try:
        with open(os.path.join(folder_path, json_file), 'r') as file:
            data = json.load(file)
        
        scene = data.get('scene')
        lights = data.get('lights')
        objects = data.get('objects', {})

        descriptions = []

        for obj_key, obj_value in objects.items():
            object_type = obj_value.get('object_type')
            init_color = obj_value.get('color')
            #fill the color stocastically
            stochastic_color = random.choice(list(COLORS[init_color]))
            size = obj_value.get('size')
            rotation = obj_value.get('rotation')
            bounds = obj_value.get('bounds')

            # Select a random phrase
            phrase_template = random.choice(list(PHRASES.values()))
            # Format the selected phrase with the object details
            formatted_phrase = phrase_template.format(SIZE=SIZES[size], OBJECT=object_type, COLOR=stochastic_color)

            # Add the formatted phrase to the list of descriptions
            descriptions.append(formatted_phrase)

        # Join all descriptions into a single string
        full_description = ' '.join(descriptions)

        # Add the full description to the JSON data
        data['description'] = full_description

        # Save the modified JSON data to the same file, overwriting it
        with open(os.path.join(folder_path, json_file), 'w') as file:
            json.dump(data, file, indent=4)

        print(f"Processed and saved: {json_file}")

    except Exception as e:
        print(f"Error processing {json_file}: {e}")

print("All JSON files have been processed and saved with the new descriptions.")
