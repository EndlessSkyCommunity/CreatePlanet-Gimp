#!/usr/bin/env python

import os
from os.path import expanduser
from os.path import isabs
from sys import platform
import random
from math import radians

from gimpfu import *

"""
Insert your default file path here. If you are on windows, remember to escape the backslashes with another backslash.
This is relative to your home directory. You can also pass an absolute path if you so choose
Example: Desktop\\test.png
"""
DEFAULT_PATH = "planet.png"

if(isabs(DEFAULT_PATH)):
	pass
elif platform == "win32":
	DEFAULT_PATH = expanduser("~\\" + DEFAULT_PATH)
else:
	DEFAULT_PATH = expanduser("~/" + DEFAULT_PATH)

pdb = gimp.pdb

def maptoobject(image, layer):  # outsourced into a second method, because it might be needed twice
    pdb.plug_in_map_object(
    # image, drawable, maptype=sphere
    image, layer, 1,
    # viewpoint x, y, z
    0.5, 0.5, 1,
    # position x, y, z
    0.5, 0.5, 0,
    # first-axis x, y, z
    1, 0, 0,
    # second-axis x, y, z
    0, 1, 0,
    # rotation-angle x, y, z
    0, 0, 0,
    # lighttype=none
    2,
    # light color (r, g, b)
    (0, 0, 0),
    # light position x, y, z
    -0.5, -0.5, 2,
    # light direction x, y, z
    -1, -1, 1,
    # ambientintesity, diffuseintesity, diffusereflectivity, specularreflectivity
    0.3, 1, 0.5, 0.5,
    # highlight, antialiasing, tiled, newimage, transparentbackground, radius
    27, 1, 0, 0, 1, 0.25,
    # scale x, y, z
    0.5, 0.5, 0.5,
    # cylinderlegth, 8 drawables used by cylinders & boxes
    0, layer, layer, layer, layer, layer, layer, layer, layer
    )

"""
Returns an array with the outputwidth(s). The array always contains either 1 or 2 ints, depending on generate2x.
The first element is always the actual size, the second one the 2x size (if prompted).
"""
def get_outputwidth(planetrand, planettype, generate2x, planetwidth):
    outputwidth = []
    planetint = int(planetwidth)
    if planetrand:
        if planettype == 0:
            planetint = random.randint(150, 210)
        if planettype == 1:
            planetint = random.randint(100, 250)
        if planettype == 2:
            planetint = random.randint(60, 100)
        if planettype == 3:
            planetint = random.randint(280, 360)
        if planettype == 4:
            planetint = random.randint(360, 450)
    outputwidth.append(planetint)
    if generate2x:
        outputwidth.append(planetint * 2)
    return outputwidth


def createplanet(image, atmospherecolor, postprocessing, planetrand, planetwidth, planettype, bumplayeropacity, distance, gasopacity, gasangle, atmothickness, texturelayer, groupundo, filename, savexcf, generate2x):

    if groupundo:
        image.undo_group_start()

# check if image is in RGB, if not then change type
    if pdb.gimp_image_base_type(image) is not 0:
        pdb.gimp_image_convert_rgb(image)

# prevent some weird resizing errors
    image.resize_to_layers()

# rescale the image to square
    if image.width < image.height:
        pdb.gimp_image_rotate(image, 0)
    width = image.width
    image.resize(width, width, 0, 0)
    texturelayer.scale(width, width, 0, 0)
    if width > 1920:  # scale it to 1920x1920, if necessary
        image.resize(1920, 1920, 0, 0)
        texturelayer.scale(1920, 1920, 0, 0)
        width = image.width

# map the texture to a sphere to create the planet
    maptoobject(image, texturelayer)
    planetlayer = image.active_layer

# add a black background
    black = gimp.Layer(image, "black background", width, width, RGB_IMAGE, 100, NORMAL_MODE)
    pdb.gimp_image_insert_layer(image, black, None, 2)

# select the planet
    pdb.gimp_image_set_active_layer(image, planetlayer)
    pdb.gimp_context_set_sample_threshold(1)
    pdb.gimp_image_select_contiguous_color(image, 0, planetlayer, width / 2, width / 2)

# create a new layer with a black disk
    shadow1 = gimp.Layer(image, "shadow 1", width, width, RGBA_IMAGE, 100, NORMAL_MODE)
    image.add_layer(shadow1, 0)
    pdb.gimp_context_set_foreground((0, 0, 0))
    pdb.gimp_bucket_fill(shadow1, 0, 0, 100, 255, 0, width / 2, width / 2)

# create a new layer with the atmosphere
    atmosphere = gimp.Layer(image, "atmosphere", width, width, RGBA_IMAGE, 100, NORMAL_MODE)
    image.add_layer(atmosphere, 0)
    pdb.gimp_selection_border(image, atmothickness)
    pdb.gimp_context_set_foreground(atmospherecolor)
    pdb.gimp_bucket_fill(atmosphere, 0, 0, 100, 255, 0, 1, 1)
    pdb.gimp_selection_none(image)
    pdb.plug_in_gauss_rle(image, atmosphere, width / 100, width / 100, width / 100, run_mode=1)

# make the disk a shadow
    pdb.plug_in_gauss_rle(image, shadow1, width / 10, width / 10, width / 10)
    pdb.gimp_layer_set_mode(shadow1, 3)  # multiply=3
    pdb.gimp_layer_set_opacity(shadow1, 80)
    shadow1.set_offsets(0, -width / 11)  # move it a bit upwards

# a second shadow layer, further up and more blurry
    shadow2 = pdb.gimp_layer_new_from_drawable(shadow1, image)
    image.add_layer(shadow2, 0)
    image.lower_layer(shadow2)
    pdb.gimp_layer_set_name(shadow2, "shadow 2")
    pdb.plug_in_gauss_rle(image, shadow2, width / 5, width / 5, width / 5)
    shadow2.set_offsets(0, - width / 8)  # move it further upwards

# prepare the eraser
    pdb.gimp_context_set_brush("2. Hardness 050")
    pdb.gimp_context_set_brush_angle(0)
    pdb.gimp_context_set_brush_aspect_ratio(0)
    pdb.gimp_context_set_brush_size(width / 2)  # choose a soft, big brush

# erase the atmosphere above the dark side
    planetedge = width / 3.4  # the shortest possible distance between the image edge and the planet's surface
    counter = 0
    while counter < 4:  # loop 4 times
        pdb.gimp_eraser(atmosphere, 2, (width / 2, planetedge), 1, 1)  # stroke point 1
        pdb.gimp_eraser(atmosphere, 2, (planetedge, planetedge), 0, 1)  # stroke point 2
        pdb.gimp_eraser(atmosphere, 2, (width - planetedge, planetedge), 0, 1)  # stroke point 3
        counter = counter + 1
    # what exactly happens here? imagine a square around the outside of the planet. there are 3 important points: the upper corners
    # and the middle of the upper edge. now the script takes 4 strokes on each of these points, with the eraser defined above.

# add bumpmap for terrestrial planets
    if postprocessing == 1:
        bumplayer = pdb.gimp_layer_new_from_drawable(planetlayer, image)
        image.add_layer(bumplayer, 0)
        pdb.plug_in_emboss(image, bumplayer, 90, 60, 4, 1)
        pdb.gimp_context_set_sample_threshold(1)
        pdb.gimp_image_select_contiguous_color(image, 0, planetlayer, width / 2, width / 2)
        pdb.gimp_selection_invert(image)
        pdb.gimp_selection_border(image, 2)
        pdb.gimp_edit_clear(bumplayer)
        pdb.gimp_layer_set_mode(bumplayer, 5)
        pdb.gimp_layer_set_opacity(bumplayer, bumplayeropacity)
        counter = 0
        while counter < 3:
            image.lower_layer(bumplayer)
            counter = counter + 1

# add gas layer for gas giants
    if postprocessing == 2:
        gaslayer = pdb.gimp_layer_copy(texturelayer, FALSE)
        pdb.gimp_image_insert_layer(image, gaslayer, None, 0)
        pdb.plug_in_mblur(image, gaslayer, 0, distance, 0, 0, 0)
        maptoobject(image, gaslayer)
        image.remove_layer(gaslayer)
        gaslayer = image.active_layer
        pdb.gimp_layer_set_opacity(gaslayer, gasopacity)
        counter = 0
        while counter < 3:
            image.lower_layer(gaslayer)
            counter = counter + 1
        if gasangle is not 0:
            pdb.gimp_item_transform_rotate(gaslayer, radians(float(gasangle)), TRUE, 0, 0)

# crop the image around the planet
    cropoff = int(round(width / 4.3))  # minimal distance between the edge of the image and the atmosphere, with tolerance
    cropheight = int(round(width / 1.86))  # height and width of the selection
    image.crop(cropheight, cropheight, cropoff, cropoff)

# prep filename - even if we don't save anything now, we will use it later
    if not filename:
        filename = pdb.gimp_image_get_name(image)  # if not specified, use image name
    filename, dummy = os.path.splitext(filename)  # remove file extension
    rawfilename = filename.decode("utf-8", "ignore")  # rawfilename must be UTF-8

# save a .xcf file, if specified
    if savexcf:
        pdb.gimp_xcf_save(0, image, image.active_layer, filename + ".xcf", rawfilename + ".xcf")

# merge layers
    pdb.gimp_layer_set_visible(black, FALSE)
    pdb.gimp_layer_set_visible(texturelayer, FALSE)
    pdb.gimp_layer_set_visible(planetlayer, TRUE)
    image.merge_visible_layers(0)

# save as png (twice, if prompted)
    outputwidth = get_outputwidth(planetrand, planettype, generate2x, planetwidth)
    if len(outputwidth) > 1:
        image.scale(outputwidth[1], outputwidth[1])
        pdb.file_png_save_defaults(image, image.active_layer, filename + "@2x.png", rawfilename + "@2x.png")
    image.scale(outputwidth[0], outputwidth[0])
    pdb.file_png_save_defaults(image, image.active_layer, filename + ".png", rawfilename + ".png")


    if groupundo:
        image.undo_group_end()


"""
WRAPPERS
"""

def createplanet_gas(image, atmospherecolor, planetrand, planetwidth, distance, gasopacity, gasangle, atmothickness, texturelayer, groupundo, filename, savexcf, generate2x):
    createplanet(image, atmospherecolor, 2, planetrand, planetwidth, 4, 0, distance, gasopacity, gasangle, atmothickness, texturelayer, groupundo, filename, savexcf, generate2x)

def createplanet_ice(image, atmospherecolor, planetrand, planetwidth, atmothickness, texturelayer, groupundo, filename, savexcf, generate2x):
    createplanet(image, atmospherecolor, 0, planetrand, planetwidth, 3, 0, 0, 0, 0, atmothickness, texturelayer, groupundo, filename, savexcf, generate2x)

def createplanet_terrestrials(image, planetrand, planettype, planetwidth, bumplayeropacity, atmothickness, texturelayer, groupundo, filename, savexcf, generate2x):
    createplanet(image, (0, 0, 0), 1, planetrand, planetwidth, planettype, bumplayeropacity, 0, 0, 0, atmothickness, texturelayer, groupundo, filename, savexcf, generate2x)


"""
REGISTRATION
"""

register(
    "createplanet",
    N_("Create a planet sprite using the given texture."),
    "Create a planet sprite using the given texture. See the Forum Post for more info.",
    "MCOfficer",
    "@Copyright 2017",
    "2017",
    N_("_Universal..."),
    "",
    [
    (PF_IMAGE, "image", "Input image", None),
    (PF_COLOR, "atmospherecolor", "Atmosphere Color. Default is white, only use a slight off-white tint for gas giants.", (255, 255, 255)),
    (PF_RADIO, "postprocessing", "Determines what post-processing will be used", 0, (("None", 0), ("Terrestrial Planet", 1), ("Gas Giant", 2))),
    (PF_BOOL, "planetrand", "Random planet size, based on planet type chosen.", False ),
    (PF_SLIDER, "planetwidth", "The width of the new planet. Habitable Planet (150-210px), Other Terrestrial Planet (100-250px), Moon (60-110px), Ice Giant (280-360px), Gas Giant (360-450px)", 1, (60, 600, 10)),
    (PF_OPTION, "planettype", "Planettype, determines the width of the output image. Only effective for random planet sizes.", 1, ("Habitable Planet (150-210px)", "Other Terrestrial Planet (100-250px)", "Moon (60-110px)", "Ice Giant (280-360px)", "Gas Giant (360-450px)")),
    (PF_SLIDER, "bumplayeropacity", "The opacity of the bumpmap layer. Only effective for terrestrial planets.", 80, (0, 100, 1)),
    (PF_SLIDER, "distance", "The motion blur distance. Only effective for gas giants.", 150, (100, 200, 1)),
    (PF_SLIDER, "gasopacity", "The gas layer opacity. Only effective for gas giants.", 70, (0, 100, 1)),
    (PF_SLIDER, "gasangle", "The rotation of the gas layer. Only effective for gas giants.", 0, (-180, 180, 1)),
    (PF_SLIDER, "atmothickness", "The thickness of the atmosphere, in pixels.", 1, (0, 3, 0.05)),
    (PF_DRAWABLE, "texturelayer", "Select your texture layer here.", None),
    (PF_BOOL, "groupundo", "Group undo steps? If this is true, you can undo the entire script at once.", False ),
    (PF_FILE, "filename", "The name of the output file. Leave empty to use the texture name.", DEFAULT_PATH),
    (PF_BOOL, "savexcf", "Do you want to save the .xcf source file? This is useless when Group Undo is enabled.", True),
    (PF_BOOL, "generate2x", "Generate an additional 2x version of the sprite.", True)
    ],
    [],
    createplanet,
    menu="<Toolbox>/CreatePlanet/",
    domain=("gimp20-python", gimp.locale_directory)
)

register(
    "createplanet-gas",
    N_("Create a gas giant sprite using the given texture."),
    "Create a gas giant sprite using the given texture. See the Forum Post for more info.",
    "MCOfficer",
    "@Copyright 2017",
    "2017",
    N_("_Gas Giant..."),
    "",
    [
    (PF_IMAGE, "image", "Input image", None),
    (PF_COLOR, "atmospherecolor", "Atmosphere Color. Default is white, only use a slight off-white tint for gas giants.", (255, 255, 255)),
    (PF_BOOL, "planetrand", "Random planet size", False ),
    (PF_SLIDER, "planetwidth", "The width of the new planet. Only applies if random planet size is disabled.", 1, (360, 450, 5)),
    (PF_SLIDER, "distance", "The motion blur distance. Only effective for gas giants.", 150, (100, 200, 1)),
    (PF_SLIDER, "gasopacity", "The gas layer opacity. Only effective for gas giants.", 70, (0, 100, 1)),
    (PF_SLIDER, "gasangle", "The rotation of the gas layer.", 0, (-180, 180, 1)),
    (PF_SLIDER, "atmothickness", "The thickness of the atmosphere, in pixels.", 1, (0, 3, 0.05)),
    (PF_DRAWABLE, "texturelayer", "Select your texture layer here.", None),
    (PF_BOOL, "groupundo", "Group undo steps? If this is true, you can undo the entire script at once.", False ),
    (PF_FILE, "filename", "The name of the output file. Leave empty to use the texture name.", DEFAULT_PATH),
    (PF_BOOL, "savexcf", "Do you want to save the .xcf source file? This is useless when Group Undo is enabled.", True),
    (PF_BOOL, "generate2x", "Generate an additional 2x version of the sprite.", True)
    ],
    [],
    createplanet_gas,
    menu="<Toolbox>/CreatePlanet/",
    domain=("gimp20-python", gimp.locale_directory)
)

register(
    "createplanet-ice",
    N_("Create a ice giant sprite using the given texture."),
    "Create a ice giant sprite using the given texture. See the Forum Post for more info.",
    "MCOfficer",
    "@Copyright 2017",
    "2017",
    N_("_Ice Giant..."),
    "",
    [
    (PF_IMAGE, "image", "Input image", None),
    (PF_COLOR, "atmospherecolor", "Atmosphere Color. Default is white, only use a slight off-white tint for gas giants.", (255, 255, 255)),
    (PF_BOOL, "planetrand", "Random planet size", False ),
    (PF_SLIDER, "planetwidth", "The width of the new planet. Only applies if random planet size is disabled.", 1, (280, 360, 5)),
    (PF_SLIDER, "atmothickness", "The thickness of the atmosphere, in pixels.", 1, (0, 3, 0.05)),
    (PF_DRAWABLE, "texturelayer", "Select your texture layer here.", None),
    (PF_BOOL, "groupundo", "Group undo steps? If this is true, you can undo the entire script at once.", False ),
    (PF_FILE, "filename", "The name of the output file. Leave empty to use the texture name.", DEFAULT_PATH),
    (PF_BOOL, "savexcf", "Do you want to save the .xcf source file? This is useless when Group Undo is enabled.", True),
    (PF_BOOL, "generate2x", "Generate an additional 2x version of the sprite.", True)
    ],
    [],
    createplanet_ice,
    menu="<Toolbox>/CreatePlanet/",
    domain=("gimp20-python", gimp.locale_directory)
)

register(
    "createplanet-terrestrials",
    N_("Create a terrestrial using the given texture."),
    "Create a terrestrial using the given texture. See the Forum Post for more info.",
    "MCOfficer",
    "@Copyright 2017",
    "2017",
    N_("_Terrestrials..."),
    "",
    [
    (PF_IMAGE, "image", "Input image", None),
    (PF_BOOL, "planetrand", "Random planet size, based on planet type chosen.", False ),
    (PF_RADIO, "planettype", "Planettype, determines the width of the output image. Only effective for random planet sizes.", 1, (("Habitable Planet (150-210px)", 0), ("Other Terrestrial Planet (100-250px)", 1), ("Moon (60-110px)", 2))),
    (PF_SLIDER, "planetwidth", "The width of the new planet (Habitable Planet: 150-210px, Other Terrestrial Planet: 100-250px, Moon: 60-110px). Only apples if random planet size is disabled.", 1, (60, 250, 5)),
    (PF_SLIDER, "bumplayeropacity", "The opacity of the bumpmap layer. Only effective for terrestrial planets.", 80, (0, 100, 1)),
    (PF_SLIDER, "atmothickness", "The thickness of the atmosphere, in pixels.", 1, (0, 3, 0.05)),
    (PF_DRAWABLE, "texturelayer", "Select your texture layer here.", None),
    (PF_BOOL, "groupundo", "Group undo steps? If this is true, you can undo the entire script at once.", False ),
    (PF_FILE, "filename", "The name of the output file. Leave empty to use the texture name.", DEFAULT_PATH),
    (PF_BOOL, "savexcf", "Do you want to save the .xcf source file? This is useless when Group Undo is enabled.", True),
    (PF_BOOL, "generate2x", "Generate an additional 2x version of the sprite.", True)
    ],
    [],
    createplanet_terrestrials,
    menu="<Toolbox>/CreatePlanet/",
    domain=("gimp20-python", gimp.locale_directory)
)

main()
