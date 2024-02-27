#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Feb 2024

@author: Jérémy Bernard, CNRM, chercheur associé au Lab-STICC et accueilli au LOCIE
"""
import tempfile
import os
import pandas as pd

GEOCLIMATE_VERSION = "1.0.0"

GEOCLIMATE_JAR_URL = f"https://github.com/orbisgis/geoclimate/releases/download/v{GEOCLIMATE_VERSION}/geoclimate-{GEOCLIMATE_VERSION}.jar"

GEOCLIMATE_JAR_NAME = f"geoclimate-{GEOCLIMATE_VERSION}.jar"

STYLE_LANGUAGE = {"English": "en", "French": "fr"}

STYLE_GITHUB = {"repo": "orbisgis/geoclimate",
                "branch": "master",
                "directory": "geoindicators/src/main/resources/styles/{0}/sld"}

LAYER_SLD_DIR = os.path.join("{0}", "Resources", "Styles", "{1}")

STYLE_EXTENSION = ".sld"

INPUT_TABLES = pd.DataFrame({"zone" : [""],
                             "building" : [""],
                             "road" : [""],
                             "rail" : [""],
                             "water" : [""],
                             "vegetation" : [""],
                             "impervious" : [""],
                             "urban_areas" : [""],
                             "sea_land_mask" : [""],
                             "population" : [""]},
                            index = ["style"])
OUTPUT_TABLES = pd.DataFrame({"building_indicators" : [""],
                              "block_indicators" : [""],
                              "rsu_indicators" : [""],
                              "rsu_lcz" : ["rsu_lcz_primary"],
                              "rsu_utrf_area" : [""],
                              "rsu_utrf_floor_area" : [""],
                              "building_utrf" : [""],
                              "grid_indicators" : ["rsu_lcz_primary"],
                              "building_height_missing" : [""],
                              "road_traffic" : [""],
                              "ground_acoustic" : [""]},
                             index = ["style"])

CONFIG_FILENAME = "configuration_file_{0}.json"

TEMPO_DIRECTORY = tempfile.tempdir

# Define names used by GeoClimate for each type of dataset
OSM = "OSM"
BDT_V2 = "BDTOPO_V2"
BDT_V3 = "BDTOPO_V3"

# Define default SRID
SRID = {OSM: 4326, BDT_V2: 2154, BDT_V3: 2154}