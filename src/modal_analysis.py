import helpers
import ross as rs
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

rotor, DIRECTORY = helpers.LoadRotor();
DIRECTORY_MODAL = DIRECTORY + '\\Modal';
if not os.path.isdir(DIRECTORY_MODAL):
    os.makedirs(DIRECTORY_MODAL);

for bearing in rotor.bearing_elements:
    print(bearing.tag + " stiffness: ", bearing.K(0))

if PromptBool('Run and Plot Undamped Critical Speed Map?'):
    ucs = rotor.run_ucs(synchronous=True);
    ucs_plot = ucs.plot(frequency_units='RPM')
    ucs_plot.show()
    SaveFigure(ucs_plot, 'UndampedCriticalSpeedMap');
    #for mode_index in range(len(ucs.critical_points_modal)):
        #ucs.plot_mode_3d(mode_index, frequency_units='rpm').show();

if PromptBool("Run Critical Speeds?"):
    crit = rotor.run_critical_speed(num_modes=10);
    print("Damped: ", np.round(crit.wd(frequency_units='rpm')))
    print("Undamped: ", np.round(crit.wn(frequency_units='rpm')))
    crit.save(DIRECTORY_MODAL + '\\CriticalSpeeds.toml')

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
    trace_list = [];
    for _, t in enumerate(campbell_fig.data):
        if t.name == 'Torsional':
            continue
        trace_list.append(t)
    campbell_fig.data = tuple(trace_list)

    campbell_fig.update_layout(
        {'title': {'text': 'Campbell Diagram', 'x': 0.5, 'xanchor': 'center'}}
        )

    campbell_fig.show()
    SaveFigure(campbell_fig, "CampbellDiagram")

#%% Save figs
if PromptBool("Save result figures? (Directory: " + DIRECTORY_MODAL + ")"):
    
    for name, v in figures.items():
        fig = v['fig'];
        file_extension = v['extension'];

        if file_extension == 'html':
            fig.write_html(DIRECTORY_MODAL + "\\" + name + '.html');
        else:
            fig.write_image(DIRECTORY_MODAL + '\\' + name + '.' + file_extension);

print("\nProgram exited.\n" + "____"*20 + "\n")