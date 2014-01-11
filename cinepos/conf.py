__author__ = 'lukegb'

import os
import importlib

settings_module = os.environ.get('CINEPOS_SETTINGS_MODULE', 'cinepos.settings')
settings = importlib.import_module(settings_module, 'cinepos')
