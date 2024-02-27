#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 16:36:54 2024

@author: Jérémy Bernard, CNRM, chercheur associé au Lab-STICC et accueilli au LOCIE
"""
import subprocess
from .globalVariables import *
from urllib.request import urlretrieve
from pathlib import Path
import subprocess
import platform
from github import Github
import ghDownload as ghd

from qgis.PyQt.QtGui import QColor
from qgis.core import (QgsProject, 
                       QgsApplication,
                       QgsGradientColorRamp,
                       QgsGradientStop,
                       QgsColorRampShader,
                       QgsRasterShader, 
                       QgsRasterLayer,
                       QgsVectorLayer,
                       QgsSingleBandPseudoColorRenderer,
                       QgsProcessingContext,
                       QgsSymbol,
                       QgsRendererRange,
                       QgsGraduatedSymbolRenderer,
                       QgsProcessingLayerPostProcessorInterface)


class Renamer(QgsProcessingLayerPostProcessorInterface):
    def __init__(self, layer_name):
        self.name = layer_name
        super().__init__()
        
    def postProcessLayer(self, layer, context, feedback):
        layer.setName(self.name)

def runProcess(exe):
    """Function to run subprocesses using shell and getting live log.

		Parameters
		_ _ _ _ _ _ _ _ _ _ 

			exe: list
				List of key words composing the execution command (e.g. ['echo', 'Hello world'])
        
    Source of the code: https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output    
    """
    
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while(True):
        # returns None while subprocess is running
        retcode = p.poll() 
        line = p.stdout.readline()
        yield line
        if retcode is not None:
            break
        
def downloadLastGeoClimate(plugin_directory, feedback):
    """Function to download the last GeoClimate version if not locally saved.

		Parameters
		_ _ _ _ _ _ _ _ _ _ 

			plugin_directory: string
				Directory where is located the plugin algorithm file
            feedback: QGIS feedback object
                QGIS feedback object used to log message to the user
    """
    # GeoClimate path of the last version
    geoclim_jar_path = os.path.join(plugin_directory, 'Resources', GEOCLIMATE_JAR_NAME)
    
    list_loc_geoc_vers = glob.glob(os.path.join(plugin_directory, 'Resources', "geoclimate*.jar"))
    if list_loc_geoc_vers:
        # Remove all potential old GeoClimate versions
        list_old_geoc_vers = list_loc_geoc_vers.copy()
        if list_loc_geoc_vers.count(geoclim_jar_path)>0:
            list_old_geoc_vers.remove(geoclim_jar_path)
        for path_old_v in list_old_geoc_vers:
            os.remove(path_old_v)
        
        # Download the last GeoClimate version if not already downloaded
        if not os.path.exists(geoclim_jar_path):
            if feedback:
                feedback.setProgressText("You do not have the last GeoClimate version. Downloading...")
                if feedback.isCanceled():
                    feedback.setProgressText("Calculation cancelled by user")
                    return {}
            urlretrieve(GEOCLIMATE_JAR_URL, geoclim_jar_path)
    else:
        if feedback:
            feedback.setProgressText("You do not have the last GeoClimate version. Downloading...")
            if feedback.isCanceled():
                feedback.setProgressText("Calculation cancelled by user")
                return {}
        urlretrieve(GEOCLIMATE_JAR_URL, geoclim_jar_path)
        
def downloadLastStyles(plugin_directory, feedback, language):
    """Function to download the last GeoClimate version if not locally saved.

		Parameters
		_ _ _ _ _ _ _ _ _ _ 

			plugin_directory: string
				Directory where is located the plugin algorithm file
            feedback: QGIS feedback object
                QGIS feedback object used to log message to the user
            language: string
                Language used for the legend style
    """
    if feedback:
        feedback.setProgressText("Try downloading last valid GeoClimate styles")
        if feedback.isCanceled():
            feedback.setProgressText("Calculation cancelled by user")
            return {}
    
    # GeoClimate path of the last version
    style_path = LAYER_SLD_DIR.format(plugin_directory, language)
    
    # Get the url of the GeoClimate styles
    url_styles = STYLE_GITHUB["directory"].format(language)
    
    github = Github(None)
    try:
        repository = github.get_repo(STYLE_GITHUB["repo"])
    except:
        feedback.pushwarning("""The GeoClimate github repository cannot be reached.\n
                             You may not have the last GeoClimate styles.\n
                             Please verify your internet connection.""")
        pass
    
    if repository:
        sha = ghd.get_sha_for_tag(repository, STYLE_GITHUB["branch"])
        ghd.download_directory(repository = repository,
                               sha = sha,
                               server_path = url_styles,
                               computer_dir = style_path)

        
def loadFile(filepath,
             layername,
             styleFileName):
    loadedVector = \
        QgsVectorLayer(filepath, 
                       "",
                       "ogr")

    if not loadedVector.isValid():
        feedback.pushWarning("Vector layer failed to load!")
    else:
        context.addLayerToLoadOnCompletion(loadedVector.id(),
                                           QgsProcessingContext.LayerDetails("",
                                                                              QgsProject.instance(),
                                                                              ''))
        # Load a predefined style if exists
        if styleFileName.split(os.path)[-1] != STYLE_EXTENSION:
            loadedVector.loadNamedStyle(styleFileName,
                                        True)
        context.layerToLoadOnCompletionDetails(loadedVector.id()).setPostProcessor(layername)
        context.temporaryLayerStore().addMapLayer(loadedVector)
