import helpers
import ross as rs
import numpy as np

import os

from ross.units import Q_

import plotly.io as pio
pio.renderers.default = "browser"# "vscode"

rotor, DIR = helpers.LoadRotor()