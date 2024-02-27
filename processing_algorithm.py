# -*- coding: utf-8 -*-

"""
/***************************************************************************
 GeoClimate Workflow
                                 A QGIS plugin
 This plugin execute the GeoClimate workflows
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-02-06
        copyright            : (C) 2023 by Jérémy Bernard
        email                : jeremy.bernard@zaclys.net
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Jérémy Bernard'
__date__ = '2024-02-06'
__copyright__ = '(C) 2024 by Jérémy Bernard'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessingAlgorithm,
                       QgsProcessingParameterMatrix,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterString,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterBoolean,
                       QgsRasterLayer,
                       QgsVectorLayer,
                       QgsProject,
                       QgsProcessingContext,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFile,
                       QgsProcessingException,
                       QgsLayerTreeGroup,
                       QgsProcessingParameterExtent,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem,
                       QgsGeometry)
from qgis.utils import iface
from pathlib import Path
from qgis.PyQt.QtGui import QIcon
import inspect
#import unidecode
from .functions.globalVariables import *
from .functions.otherFunctions import runProcess, loadFile, downloadLastGeoClimate,\
    downloadLastStyles, Renamer
import json
import glob

class GeoClimateProcessorAlgorithm(QgsProcessingAlgorithm):
    """ Create a GeoClimate config file and run the corresponding workflow    
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    # Input variables
    # Input dataset used for the workflow
    INPUT_DATASET = "INPUT_DATASET"
    # Input directory
    INPUT_DIRECTORY = "INPUT_DIRECTORY"
    # Tick if you want to estimate missing OSM building height
    ESTIMATED_HEIGHT = "ESTIMATED_HEIGHT"
    # Tick if you want to produce a LCZ map"
    LCZ_CALC = "LCZ_CALC"
    # Tick if you want to produce the UTRF classification
    UTRF_CALC = "UTRF_CALC"
    # Tick if you want to calculate WRF inputs
    WRF_INPUTS = "WRF_INPUTS"
    # Tick if you want to calculate TEB inputs
    TEB_INPUTS = "TEB_INPUTS"
    # Quick calculation of the SVF
    SVF_SIMPLIFIED = "SVF_SIMPLIFIED"
    # Location to process
    LOCATION = "LOCATION"
    # Extent if extent is used instead of location
    EXTENT = "EXTENT"
    # Warning: seems to not work in any folder of the temp...
    OUTPUT_DIRECTORY = "OUTPUT_DIRECTORY"
    # Whether or not inputs and outputs are loaded at the end
    LOAD_INPUTS = "LOAD_INPUTS"
    LOAD_OUTPUTS = "LOAD_OUTPUTS"
    # Language of the style for the loaded layers
    STYLE_LANGUAGE = "STYLE_LANGUAGE"
    
    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        
        # We add the input parameters
        self.addParameter(
            QgsProcessingParameterEnum(
                self.INPUT_DATASET, 
                self.tr('What data do you want to use as input'),
                list(DATASETS.columns.tolist()),
                defaultValue=0,
                optional = False))
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.INPUT_DIRECTORY,
                self.tr('If your data are BDT, select the folder containing the data'),
                defaultValue = "",
                optional = True))
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ESTIMATED_HEIGHT,
                self.tr('Tick if you want to estimate missing OSM building height'),
                defaultValue = True)) 
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.LCZ_CALC,
                self.tr('Tick if you want to produce a LCZ map"'),
                defaultValue = False)) 
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.UTRF_CALC,
                self.tr('Tick if you want to produce the UTRF classification'),
                defaultValue = False)) 
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.WRF_INPUTS,
                self.tr('Tick if you want to calculate the WRF spatial inputs'),
                defaultValue = False)) 
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.TEB_INPUTS,
                self.tr('Tick if you want to calculate the TEB spatial inputs'),
                defaultValue = False)) 
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SVF_SIMPLIFIED,
                self.tr('Tick if you want a quick (but less accurate) calculation of the SVF'),
                defaultValue = True)) 
        self.addParameter(
            QgsProcessingParameterString(
                self.LOCATION,
                self.tr('A place name to run (recommended: commune name)'),
                defaultValue = "",
                optional = True))
        self.addParameter(
            QgsProcessingParameterExtent(
                self.EXTENT,
                self.tr('Clipping extent'),
                optional = True))
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_DIRECTORY,
                self.tr('Directory to save the outputs'),
                defaultValue = ""))
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.LOAD_INPUTS,
                self.tr('Tick if you want to automatically load the input data once calculation completed'),
                defaultValue = False)) 
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.LOAD_OUTPUTS,
                self.tr('Tick if you want to automatically load the output data once calculation completed'),
                defaultValue = True)) 
        self.addParameter(
            QgsProcessingParameterEnum(
                self.STYLE_LANGUAGE, 
                self.tr('If input or output data loaded, what language do you want for the legend ?'),
                list(STYLE_LANGUAGE.keys()),
                defaultValue=0,
                optional = False))

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        
        inputDataset = self.parameterAsInt(parameters, self.INPUT_DATASET, context)
        inputDirectory = self.parameterAsString(parameters, self.INPUT_DIRECTORY, context)
        estimatedHeight = self.parameterAsBoolean(parameters, self.ESTIMATED_HEIGHT, context)
        lczCalc = self.parameterAsBoolean(parameters, self.LCZ_CALC, context)
        utrfCalc = self.parameterAsBoolean(parameters, self.UTRF_CALC, context)
        wrfInputs = self.parameterAsBoolean(parameters, self.WRF_INPUTS, context)
        tebInputs = self.parameterAsBoolean(parameters, self.TEB_INPUTS, context)
        svfSimplified = self.parameterAsBoolean(parameters, self.SVF_SIMPLIFIED, context)
        location = self.parameterAsString(parameters, self.LOCATION, context)
        bbox = self.parameterAsExtent(parameters, self.EXTENT, context)
        bbox_crs_ini = self.parameterAsExtentCrs(parameters, self.EXTENT, context)
        outputDirectory = self.parameterAsString(parameters, self.OUTPUT_DIRECTORY, context)
        loadInputs = self.parameterAsBoolean(parameters, self.LOAD_INPUTS, context)
        loadOutputs = self.parameterAsBoolean(parameters, self.LOAD_OUTPUTS, context)
        styleLanguage = self.parameterAsInt(parameters, self.STYLE_LANGUAGE, context)
        
        #prefix = unidecode.unidecode(weatherScenario).replace(" ", "_")
        
        # Log some errors is some combinations of parameters are not valid
        if location and not bbox.isNull():
            raise QgsProcessingException("You should fill a location OR select an extent, not both !!")
        elif not location and bbox.isNull():
            raise QgsProcessingException("You should specify a location or select an extent !!")

        # Get the input dataset used by the workflow
        inputDataset = DATASETS.columns.tolist()[inputDataset]
        if ((inputDataset == BDT_V2) or (inputDataset == BDT_V3)) and not inputDirectory:
            raise QgsProcessingException(f"You have selected {inputDataset}. You need to provide the input data.")
        if (inputDataset == OSM) and inputDirectory:
            raise QgsProcessingException(f"You have selected {inputDataset}. You do not need to provide the input data.")
        
        # Get the output language used for the loaded files
        styleLanguage = STYLE_LANGUAGE[list(STYLE_LANGUAGE.keys())[styleLanguage]]
        
        # Get the plugin directory
        plugin_directory = self.plugin_dir = os.path.dirname(__file__)
        
        # Download the last stable GeoClimate version
        # GeoClimate path of the last version
        geoclim_jar_path = os.path.join(plugin_directory, 'Resources', GEOCLIMATE_JAR_NAME)
        downloadLastGeoClimate(geoclim_jar_path = geoclim_jar_path,
                               feedback = feedback)
        
        # Check that the last sld style has been downloaded
        downloadLastStyles(plugin_directory = plugin_directory,
                           feedback = feedback,
                           language = styleLanguage)
        
        # Recover the bbox coordinates if exists
        if not bbox.isNull():
            # Get the bbox srid
            if not bbox_crs_ini:
                mapRenderer = iface.mapCanvas().mapRenderer()
                bbox_crs_ini=mapRenderer.destinationCrs()
            # Get the srid as an integer
            bbox_srid_ini = bbox_crs_ini.postgisSrid()

            
            # The bbox coordinates should be in the correct srid, otherwise should be reprojected
            if bbox_srid_ini != DATASETS.loc["srid", inputDataset]:
                bbox_transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:3111"),
                                                        QgsCoordinateReferenceSystem("EPSG:4326"),
                                                        QgsProject.instance())
                # The rectangle has to be converted to geometry before transform...
                bbox_geom = QgsGeometry.fromRect(bbox)
                bbox_geom.transform(bbox_transform)
                # The geometry has to be converted back to rectangle to get x and y min and max...
                bbox = bbox_geom.boundingBox()
            
            # Create the bbox as required by GeoClimate
            bbox_coord = [bbox.xMinimum(),
                          bbox.yMinimum(),
                          bbox.xMaximum(),
                          bbox.yMaximum()]
            
            # The location argument in the GeoClimate config file is replaced by
            # the bbox coordinates
            location = bbox_coord
            
        if feedback:
            feedback.setProgressText("Start GeoClimate calculations")
            if feedback.isCanceled():
                feedback.setProgressText("Calculation cancelled by user")
                return {}
        
        # Create the outputDirectory if not exists
        if not os.path.exists(outputDirectory):
            if os.path.exists(Path(outputDirectory).parent.absolute()):
                os.mkdir(outputDirectory)
            else:
                raise QgsProcessingException('The output directory does not exist, neither its parent directory')
        config_file_path = os.path.join(outputDirectory, 
                                        CONFIG_FILENAME.format(str(location).replace(',','_')))
        
        # Fill in the indicator use list
        estimateHeight = False
        indicatorUse = []
        if lczCalc:
            indicatorUse.append("LCZ")
        if tebInputs:
            indicatorUse.append("TEB")
        if utrfCalc:
            indicatorUse.append("UTRF")
        if wrfInputs:
            indicatorUse.append("WRF")


        # Create the json configuration file used by GeoClimate
        config_file_content = {
            "description": "GeoClimate configuration file created using the QGIS plug-in GeoClimateTool",
            "input": {
                "locations": [
                    location
                ],
                "area": 10000
            },
            "output": {
                "folder": outputDirectory,
                "tables": INPUT_TABLES.columns.tolist() + OUTPUT_TABLES.columns.tolist()
            },
            "parameters": {
                "rsu_indicators": {
                    "indicatorUse": indicatorUse,
                    "svfSimplified": svfSimplified,
                    "estimateHeight": estimateHeight
                }
            }
        }
        
        # Add the informations that are only needed for BDT data
        if inputDirectory:
            config_file_content["input"]["folder"] = inputDirectory

        # Serializing json
        json_object = json.dumps(config_file_content, indent=4)
         
        # Writing to sample.json
        with open(config_file_path, "w") as outfile:
            outfile.write(json_object)
        
        # Define the java command line to be executed
        java_cmd = f'java -jar {geoclim_jar_path} -w {inputDataset} -f {config_file_path}'
        
        # Execute the GeoClimate workflow and log informations
        try: 
            for line in runProcess(java_cmd.split()):
                feedback.setProgressText(line.decode("utf8"))
            executed = True
        except:
            executed = False
            
        
        # ######################################################################
        # ######################## LOAD DATA INTO QGIS #########################
        # ######################################################################
        if executed:
            global layernames
            # Get the real output directory (since GeoClimate has created folders within
            # the QGIS plugin output directory)
            geoclim_out_dir = "_".join([DATASETS.loc["folder_prefix",inputDataset],
                                       str(location).replace("[", "")\
                                           .replace(']', "").replace(",","_")\
                                               .replace(" ", "_")])
            real_output_dir = os.path.join(outputDirectory, 
                                           geoclim_out_dir,
                                           "*.geojson")
            # List the files in the output GeoClimate directory
            list_result_files = glob.glob(real_output_dir)
            # # Load data into QGIS
            if loadInputs:
                layernames = {}
                for i, fp in enumerate(list_result_files):
                    f = fp.split(os.sep)[-1].split(".")[0]
                    if INPUT_TABLES.columns.to_list().count(f) > 0:
                        layernames[i] = Renamer(f)
                        loadFile(filepath = fp,
                                 layername = layernames[i],
                                 styleFileName = os.path.join(LAYER_SLD_DIR.format(plugin_directory, 
                                                                                   styleLanguage), 
                                                              INPUT_TABLES.loc["style", f] + STYLE_EXTENSION),
                                 context = context,
                                 feedback = feedback)
            if loadOutputs:
                layernames = {}
                for i, fp in enumerate(list_result_files):
                    f = fp.split(os.sep)[-1].split(".")[0]
                    if OUTPUT_TABLES.columns.to_list().count(f) > 0:
                        layernames[i] = Renamer(f)
                        loadFile(filepath = fp,
                                 layername = layernames[i],
                                 styleFileName = os.path.join(LAYER_SLD_DIR.format(plugin_directory, 
                                                                                   styleLanguage), 
                                                              OUTPUT_TABLES.loc["style", f] + STYLE_EXTENSION),
                                 context = context,
                                 feedback = feedback)
        # global layernames
        # layernames = {}
        # i = 0
        # for tp in [DAY_TIME, NIGHT_TIME]:
        #     layernames[i] = Renamer(f"{scenarioDirectory.split(os.sep)[-1]} and {weatherScenario}: Park impact on air temperature at {tp}:00 (°C)")
        #     # Load the vector layer with a given style
        #     loadCoolParksVector(filepath = output_dt_path[tp] + ".geojson",
        #                         layername = layernames[i],
        #                         variable = None,
        #                         subgroup = QgsLayerTreeGroup("parameter not used..."),
        #                         vector_min = deltaT_min_value,
        #                         vector_max = deltaT_max_value,
        #                         feedback = feedback,
        #                         context = context,
        #                         valueZero = 0,
        #                         opacity = DEFAULT_OPACITY)
        #     i += 1
        
        # # Load building results into QGIS
        # for var in BUILDING_LEGEND_PROCESS.index:
        #     layernames[i] = Renamer(f"{scenarioDirectory.split(os.sep)[-1]} and {weatherScenario}: {BUILDING_LEGEND_PROCESS[var]}")
        #     loadCoolParksVector(filepath = output_build_path,
        #                         layername = layernames[i],
        #                         variable = var,
        #                         subgroup = QgsLayerTreeGroup("parameter not used..."),
        #                         vector_min = gdf_build[var].min(),
        #                         vector_max = gdf_build[var].max(),
        #                         feedback = feedback,
        #                         context = context,
        #                         valueZero = 0,
        #                         opacity = 1)
        #     i += 1
        
        # # Return the output file names
        # return {self.OUTPUT_DIRECTORY: scenarioDirectory + os.sep + OUTPUT_PROCESSOR_FOLDER + os.sep + prefix}
        # Return the output file names
        return {self.OUTPUT_DIRECTORY: outputDirectory}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'coolparkstool_process'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('GeoClimate workflow')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
    
    def shortHelpString(self):
        return self.tr('The GeoClimateTool "GeoClimate workflows" module is used '+
                       'to:\n'+
                       '    - download data from OSM or load from BDTopo and convert to GeoClimate input files,\n'+
                       '    - calculates spatial indicators and typology from these files,\n'
        '\n'
        '\n'
        '---------------\n'
        'Full manual available via the <b>Help</b>-button.')

    def helpUrl(self):
        url = "https://github.com/j3r3m1/geoclimatetool"
        return url
    
    def icon(self):
        cmd_folder = Path(os.path.split(inspect.getfile(inspect.currentframe()))[0]).parent
        icon = QIcon(str(cmd_folder) + "/icons/CoolParksTool.png")
        return icon

    def createInstance(self):
        return GeoClimateProcessorAlgorithm()
