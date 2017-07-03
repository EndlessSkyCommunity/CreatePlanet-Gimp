#!/usr/bin/env python

from gimpfu import *
import glob
import os

pdb = gimp.pdb

def createplanet_batch(atmospherecolor, postprocessing, planetrand, planetwidth, planettype, bumplayeropacity, distance, gasopacity, atmothickness, groupundo, prefixdetection, loadfolder, savexcf):

# correct loadfolder: add (back-)slash if needed
    if not loadfolder.endswith(("/", "\\")):
        if os.name == "nt":  # we need backslashes on windows, but slashes on linux/mac
            loadfolder = loadfolder + "\\"
        else:
            loadfolder = loadfolder + "/"

# loop once for every file
    for filepath in os.listdir(os.getcwd()):

    # load and set up the image
        if filepath.endswith((".jpeg,", ".jpg")):
            image = pdb.file_jpeg_load(filepath, filepath)
        elif filepath.endswith(".png"):
            image = pdb.file_png_load(filepath, filepath)
        else:
            continue
        layer = image.active_layer

    # prepare filename
        if os.name == "nt":  # we need backslashes on windows, but slashes on linux/mac
            outputfolder = "%splanets\\" % loadfolder
        else:
            outputfolder = "%splanets//" % loadfolder
        # gimp.message(outputfolder)
        if not os.path.exists(outputfolder):
            os.makedirs(outputfolder)
        filenameext = os.path.basename(filepath)  # remove the path and only keep the actual filename with extension
        filename, dummy = os.path.splitext(filenameext )  # remove file extension. createplanet will add the correct extension, and we don't want to save an xcf as jpeg.
        outputpath = outputfolder + filename

    # set planettype and postprocessing via prefixdetection, if enabled
        if prefixdetection:
            if filename.startswith(("hp-", "otp-", "m-")):
                postprocessing = 1
            elif filename.startswith("gg-"):
                postprocessing = 2

            if filename.startswith("hp-"):
                planettype = 0
            elif filename.startswith("otp-"):
                planettype = 1
            elif filename.startswith("m-"):
                planettype = 2
            elif filename.startswith("ig-"):
                planettype = 3
            elif filename.startswith("gg-"):
                planettype = 4

    # let createplanet do the rest
        pdb.python_fu_createplanet(image, atmospherecolor, postprocessing, planetrand, planetwidth, planettype, bumplayeropacity, distance, gasopacity, atmothickness, layer, groupundo, outputpath, savexcf)



register(
    "createplanet_batch",
    N_("Apply CreatePlanet to several files at once. CreatePlanet must be installed."),
    "Use CreatePlanet with batch processing",
    "MCOfficer",
    "@Copyright 2017",
    "2017",
    N_("_Batch Create Planet..."),
    "",
    [
    (PF_COLOR, "atmospherecolor", "Athmosphere Color. Default is white, only use a slight off-white tint for gas giants.", (255,255,255)),
    (PF_RADIO, "postprocessing", "Determines what post-processing will be used. Useless with Prefix Detection enabled.", 0 , (("None", 0),("Terrestrial Planet", 1),("Gas Giant", 2))),
    (PF_BOOL, "planetrand", "Random planet size, based on planet type chosen.", False ),
    (PF_SLIDER, "planetwidth", "The width of the new planet. Habitable Planet (150-210px), Other Terrestrial Planet (100-250px), Moon (60-110px), Ice Giant (280-360px), Gas Giant (360-450px)", 1, (60, 600, 10)),
    (PF_OPTION, "planettype", "Planettype, determines the width of the output image. Only effective for random planet sizes.", 1 , ("Habitable Planet (150-210px)", "Other Terrestrial Planet (100-250px)", "Moon (60-110px)", "Ice Giant (280-360px)", "Gas Giant (360-450px)")),
    (PF_SLIDER, "bumplayeropacity", "The opacity of the bumpmap layer. Only effective for terrestrial planets.", 80, (0, 100, 1)),
    (PF_SLIDER, "distance", "The motion blur distance. Only effective for gas giants.", 150, (100, 200, 1)),
    (PF_SLIDER, "gasopacity", "The gas layer opacity. Only effective for gas giants.", 70, (0, 100, 1)),
    (PF_SLIDER, "atmothickness", "The thickness of the atmosphere, in pixels.", 1, (0, 3, 0.05)),
    (PF_BOOL, "groupundo", "Group undo steps? If this is true, you can undo the entire script at once.", False ),
    (PF_BOOL, "prefixdetection", "Prefix Detection sets planet type and post processing depending on the file's prefix. Possible prefixes are: 'hp-', 'otp-', 'm-', 'ig-', 'gg-'. Example filename: 'hp-texture00303423.jpg'.", True),
    (PF_DIRNAME, "loadfolder", "The location of your textures.", " "),
    (PF_BOOL, "savexcf", "Do you want to save the .xcf source file? This is useless when Group Undo is enabled.", True)
    ],
    [],
    createplanet_batch,
    menu="<Toolbox>/Scripts/",
    domain=("gimp20-python", gimp.locale_directory)
)

main()
