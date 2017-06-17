#!/usr/bin/env python

from gimpfu import *
import glob
import os

pdb = gimp.pdb

def createplanet_batch(athmospherecolor, athmospherethickness, postprocessing, bumplayeropacity, distance, gasopacity, groupundo, prefixdetection, planettype, loadfolder, fileextension, savexcf):

# correct loadfolder: add (back-)slash if needed
    if not loadfolder.endswith(("/", "\\")):
        if os.name == "nt": # we need backslashes on windows, but slashes on linux/mac
            loadfolder = loadfolder + "\\"
        else:
            loadfolder = loadfolder + "/"

# prepare the file pattern
    filepattern = loadfolder + fileextension
    filelist = glob.glob(filepattern)
    filelist.sort()
    #gimp.message(" ".join(filelist)

# loop once for every file
    for filepath in filelist:
    # load and set up the image
        if filepath.endswith((".jpeg,", ".jpg")):
            image = pdb.file_jpeg_load(filepath, filepath)
        elif filepath.endswith(".png"):
            image = pdb.file_png_load(filepath, filepath)
        layer = image.active_layer
    # prepare filename
        if os.name == "nt": # we need backslashes on windows, but slashes on linux/mac
            outputfolder = "%splanets\\" % loadfolder # add the name of a new folder
        else:
            outputfolder = "%splanets//" % loadfolder # add the name of a new folder
        gimp.message(outputfolder)
        if not os.path.exists(outputfolder):
            os.makedirs(outputfolder) # create the new folder if it doesn't exist yet
        filenameext = os.path.basename(filepath) # remove the path and only keep the actual filename with extension
        filename, dummy = os.path.splitext(filenameext) # remove file extension. createplanet will add the correct extension, and we don't want to save an xcf as jpeg.
        outputpath = outputfolder + filename
    # set planettype and postprocessing via prefixdetection, if enabled
        if prefixdetection: # set post processing based on the file prefix, if prefix detection is enabled
            if filename.startswith(("hp_", "otp_", "m")):
                postprocessing = 1
            elif filename.startswith("gg_"):
                postprocessing = 2

            if filename.startswith("hp_"):
                planettype = 0
            elif filename.startswith("otp_"):
                planettype = 1
            elif filename.startswith("m_"):
                planettype = 2
            elif filename.startswith("ig_"):
                planettype = 3
            elif filename.startswith("gg_"):
                planettype = 4
    # let createplanet do the rest
        pdb.python_fu_createplanet(image, athmospherecolor, athmospherethickness, postprocessing, bumplayeropacity, distance, gasopacity, layer, groupundo, planettype, outputpath, savexcf)



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
	(PF_COLOR, "athmospherecolor", "Athmosphere Color. Default is white, only use a slight off-white tint for gas giants.", (255,255,255)),
	(PF_SLIDER, "athmospherethickness", "The thickness used for the athmosphere.", 1.5, (0, 3, 0.05)),
	(PF_RADIO, "postprocessing", "Determines what post-processing will be used. Useless with Prefix Detection enabled.", 0 , (("None", 0),("Terrestrial Planet", 1),("Gas Giant", 2))),
	(PF_SLIDER, "bumplayeropacity", "The opacity of the bumpmap layer. Only effective for terrestrial planets.", 80, (0, 100, 1)),
	(PF_SLIDER, "distance", "The motion blur distance. Only effective for gas giants.", 150, (100, 200, 1)),
	(PF_SLIDER, "gasopacity", "The gas layer opacity. Only effective for gas giants.", 70, (0, 100, 1)),
	(PF_BOOL, "groupundo", "Group undo steps? If this is true, you can undo the entire script at once.", False ),
	(PF_BOOL, "prefixdetection", "Prefix Detection sets planet type and post processing depending on the file's prefix. Possible prefixes are: 'hp', 'otp', 'm', 'ig', 'gg' plus and underscore. Example filename: 'hp[underscore]texture00303423.jpg'.", True),
	(PF_OPTION, "planettype", "Planettype, determines the width of the output image. Useless with Prefix Detection enabled.", 1 , ("Habitable Planet (150-210px)", "Other Terrestrial Planet (100-250px)", "Moon (60-110px)", "Ice Giant (280-360px)", "Gas Giant (360-450px)")),
    (PF_STRING, "loadfolder", "The location of your textures.", ""),
	(PF_FILE, "fileextension", "Files that should be loaded. Use * to load all files in this folder.", "*.jpg"),
	(PF_BOOL, "savexcf", "Do you want to save the .xcf source file? This is useless when Group Undo is enabled.", True)
	],
	[],
	createplanet_batch,
	menu="<Toolbox>/Scripts/",
	domain=("gimp20-python", gimp.locale_directory)
)

main()
