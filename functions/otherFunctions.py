#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 16:36:54 2024

@author: Jérémy Bernard, CNRM, chercheur associé au Lab-STICC et accueilli au LOCIE
"""
import subprocess

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