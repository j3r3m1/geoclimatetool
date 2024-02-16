#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Feb 2024

@author: Jérémy Bernard, CNRM, chercheur associé au Lab-STICC et accueilli au LOCIE
"""
import tempfile
import os
from pathlib import Path

GEOCLIMATE_VERSION = "1.0.0"

GEOCLIMATE_JAR_URL = f"https://github.com/orbisgis/geoclimate/releases/download/v{GEOCLIMATE_VERSION}/geoclimate-{GEOCLIMATE_VERSION}.jar"

GEOCLIMATE_JAR_NAME = f"geoclimate-{GEOCLIMATE_VERSION}.jar"

CONFIG_FILENAME = "configuration_file_{0}.json"

TEMPO_DIRECTORY = tempfile.tempdir
OUTPUT_TABLES = ["building_indicators",
                 "block_indicators",
                 "rsu_indicators",
                 "rsu_lcz",
                 "zone",
                 "building",
                 "road",
                 "rail",
                 "water",
                 "vegetation",
                 "impervious",
                 "urban_areas",
                 "rsu_utrf_area",
                 "rsu_utrf_floor_area",
                 "building_utrf",
                 "grid_indicators",
                 "sea_land_mask",
                 "building_height_missing",
                 "road_traffic",
                 "population",
                 "ground_acoustic"]

# Define names used by GeoClimate for each type of dataset
OSM = "OSM"
BDT_V2 = "BDTOPO_V2"
BDT_V3 = "BDTOPO_V3"

# Define default SRID
SRID = {OSM: 4326, BDT_V2: 2154, BDT_V3: 2154}