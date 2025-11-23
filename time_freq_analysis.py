import ross as rs
import numpy as np
import helpers

from ross.units import Q_

import plotly.io as pio
pio.renderers.default = "browser"# "vscode"

rotor, directory = helpers.LoadRotor();

if helpers.PromptBool('Run and Plot Undamped Critical Speed Map?'):
    ucs = rotor.run_ucs(synchronous=True);
    ucs.plot(frequency_units='RPM').show()
    for mode_index in range(len(ucs.critical_points_modal)):
        ucs.plot_mode_3d(mode_index, frequency_units='rpm').show();
    
BALANCING_GRADE = Q_(2.5, 'mm/s'); # ISO 21940 "Balancing Quality Grade G" according to the product of e*omega, where e is unbalance/equivalent eccentricity (mm) and omega is the operating speed (rad/s)
OPERATING_SPEED = Q_(50e3, 'rpm');

print("Program exited.\n" + '_'*20);