import ross as rs

import helpers
import numpy as np
import os

from ross.units import Q_

import plotly.io as pio
pio.renderers.default = "browser"# "vscode"

from helpers import PromptBool
from helpers import PromptInt
from helpers import ToAngularFreq

RPM_GRAPH_MAX = float(90E3);
RPM_OP = float(50E3)

SPEED_RANGE = np.linspace(0, ToAngularFreq(RPM_GRAPH_MAX), 70)

figures: dict[str: dict] = {};
def SaveFigure(fig, name: str, file_extension: str | None = 'html', append_num: int | None=None) -> None:

    if name in figures:

        if append_num is None:
            append_num = 0;
        append_num += 1;
        # recursive
        return SaveFigure(fig, name + str(append_num), append_num);
    
    figures[name] = {
            'fig': fig,
            'extension': file_extension,
        };

rotor, directory = helpers.LoadRotor();

for bearing in rotor.bearing_elements:
    print(bearing.tag + " stiffness: ", bearing.K(0))

if PromptBool("Plot rotor model?"):
    rotor_fig = helpers.PlotRotor(rotor)
    SaveFigure(rotor_fig, "RotorModel");

if PromptBool("Run Critical Speeds?"):
    crit = rotor.run_critical_speed(num_modes=10);
    print("Damped: ", np.round(crit.wd(frequency_units='rpm')))
    print("Undamped: ", np.round(crit.wn(frequency_units='rpm')))
    crit.save(directory + '\\CriticalSpeeds.toml')

if PromptBool("Run modal?"):
    mode_shapes = PromptInt("How many mode shapes? (Default: 5)", accept_none=True) or 5;

    modal = rotor.run_modal(ToAngularFreq(RPM_OP), num_modes=2*mode_shapes, sparse=True);
    
    shape_figs = [];

    guh = (PromptBool("Plot 3D shapes?") and 3) or (PromptBool("Plot 2D shapes?") and 2) or 0

    if guh != 0:
        for mode, shape in enumerate(modal.shapes):
            if guh == 3:
                fig = modal.plot_mode_3d(mode, frequency_units="RPM");
            else:
                fig = modal.plot_mode_2d(mode, frequency_units="RPM");
            shape_figs.append(fig)
            SaveFigure(fig, name=str(guh) + "D_ShapeMode" + str(mode));

    for fig in shape_figs:
        fig.show()

if PromptBool("Run and plot Campbell?"):

    frequencies = PromptInt("Frequencies to run? (Default: 5)", accept_none=True) or 5;

    campbell = rotor.run_campbell(
        speed_range=SPEED_RANGE,
        frequencies=frequencies,
        frequency_type="wd"
    )

    campbell_fig = campbell.plot()
    SaveFigure(campbell_fig, "CampbellDiagram")
    campbell_fig.update_yaxes(range=[0, 90e3]);
    campbell_fig.show()

#%% Mass
shaft_mass_sum = 0
mass_sum = 0
for v in rotor.shaft_elements:
    shaft_mass_sum += v.m
for v in rotor.disk_elements:
    mass_sum += v.m
mass_sum += shaft_mass_sum

print(f"Rotor mass: %.3f kg" % mass_sum);

#%% Save figs
if PromptBool("Save result figures? (Directory: " + directory + ")"):
    
    for name, v in figures.items():
        fig = v['fig'];
        file_extension = v['extension'];

        if file_extension == 'html':
            fig.write_html(directory + "\\" + name + '.html');
        else:
            fig.write_image(directory + '\\' + name + '.' + file_extension);

print("\nProgram exited.\n" + "____"*20 + "\n")