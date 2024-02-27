#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 16:36:54 2024

@author: Jérémy Bernard, CNRM, chercheur associé au Lab-STICC et accueilli au LOCIE
"""
import subprocess
from .globalVariables import *

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
        
        
def loadFile(filepath,
             layername,
             variable,
             subgroup,
             vector_min,
             vector_max,
             feedback,
             context,
             valueZero = None,
             opacity = DEFAULT_OPACITY):
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
        loadedVector.loadNamedStyle(os.path.join(resourceDir,\
                                                 "Resources",
                                                 VECTOR_STYLE_FILENAME),
                                    True)
        context.layerToLoadOnCompletionDetails(loadedVector.id()).setPostProcessor(layername)
        context.temporaryLayerStore().addMapLayer(loadedVector)
  