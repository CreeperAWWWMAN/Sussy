#!/usr/bin/env python
'''
Exports layers to images and outputs a Spine JSON file
http://esotericsoftware.com/spine-json-format

Run from the GIMP menu option: File -> Export to Spine

'''

import json
import math
import os.path

import gimpfu
from gimp import pdb

include_nonvisible_layers = True

def spine_export(img, active_layer, compression, dir_name):
    ''' Plugin entry point
    '''

    # Set up the initial JSON format
    output = {
        'skeleton': {
            'hash': 'NYDebVH+Ht9WSskWgX4h79z2c4w',
            'spine': '3.5.03-beta',
            'width': 768,
            'height': 1024,
            'fps': 30,
            'images': './'
        },
        'bones': [{'name': 'root'}],
        'slots': [],
        'skins': {'default': {}},
        'animations': {}
    }
    slots = output['slots']
    attachments = output['skins']['default']

    # Iterate through the layers, extracting their info into the JSON output
    # and saving the layers as individual images
    for layer in img.layers:
        if layer.visible or include_nonvisible_layers:
            to_save = process_layer(img, layer, slots, attachments)
            save_layers(img, to_save, compression, dir_name)

    # Write the JSON output
    name = os.path.splitext(os.path.basename(img.filename))[0]
    with open(os.path.join(dir_name, '%s.json' % name), 'w') as json_file:
        json.dump(output, json_file, indent=0)

def process_layer(img, layer, slots, attachments):
    ''' Extracts the Spine info from each layer, recursing as necessary on
        layer groups. Returns all the layers it processed in a flat list.
    '''
    processed = []

    # If this layer is a layer has sublayers, recurse into them
    if hasattr(layer, 'layers'):
        for sublayer in layer.layers:
            processed = process_layer(img, sublayer, slots, attachments) + processed
    else:
        layer_name = layer.name

        slots.insert(0, {
            'name': layer_name,
            'bone': 'root',
            'attachment': layer_name,
        })
        x, y = layer.offsets

        # Compensate for GIMP using the top left as the origin, vs Spine
        # using the center.
        x += math.floor(layer.width / 2)
        y += math.floor(layer.height / 2)

        # Center the image on Spine's x origin,
        x -= math.floor(img.width / 2)

        # Compensate for GIMP's y axis going from top to bottom, vs Spine
        # going bottom to top
        y = img.height - y

        attachments[layer_name] = {layer_name: {
            'x': x,
            'y': y,
            'rotation': 0,
            'width': layer.width,
            'height': layer.height,
        }}
        processed.insert(0, layer)

    return processed

def save_layers(img, layers, compression, dir_name):
    ''' Takes a list of layers and saves them in `dir_name` as PNGs,
        naming the files after their layer names.
    '''

    for layer in layers:
        tmp_img = pdb.gimp_image_new(img.width, img.height, img.base_type)
        tmp_layer = pdb.gimp_layer_new_from_drawable(layer, tmp_img)
        tmp_layer.name = layer.name
        tmp_img.add_layer(tmp_layer, 0)
        filename = '%s.png' % layer.name
        fullpath = os.path.join(dir_name, filename)
        tmp_img.resize_to_layers()
        pdb.file_png_save(
            tmp_img,
            tmp_img.layers[0],
            fullpath,
            filename,
            0, # interlace
            compression, # compression
            1, # bkgd
            1, # gama
            1, # offs
            1, # phys
            1 # time
        )

gimpfu.register(
    # name
    "spine-export",
    # blurb
    "Spine export",
    # help
    "Exports layers to images and outputs a Spine JSON file",
    # author
    "Carlo Cabanilla",
    # copyright
    "Carlo Cabanilla",
    # date
    "2014",
    # menupath
    "<Image>/File/Export/Export to Spine",
    # imagetypes
    "*",
    # params
    [
        (gimpfu.PF_ADJUSTMENT, "compression", "PNG Compression level:", 9, (0, 9, 1)),
        (gimpfu.PF_DIRNAME, "dir", "Directory", "/tmp")
    ],
    # results
    [],
    # function
    spine_export
)

gimpfu.main()
