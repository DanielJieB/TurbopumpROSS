import ross as rs
import numpy as np
import helpers
import os

from ross.units import Q_

import plotly.io as pio
pio.renderers.default = "browser"# "vscode"

rotor, DIRECTORY = helpers.LoadRotor();
DIRECTORY_TIMEFREQ = DIRECTORY + '\\TimeFrequency';
if not os.path.isdir(DIRECTORY_TIMEFREQ):
    os.makedirs(DIRECTORY_TIMEFREQ);

# ISO 21940 "Balancing Quality Grade G" according to the product of e*omega, where e is unbalance/equivalent eccentricity (mm) and omega is the operating speed (rad/s)
BALANCING_GRADE = Q_(helpers.PromptFloat('Enter ISO Balancing Quality Grade G (Default: 2.5):', True) or 2.5, 'mm/s');
OPERATING_SPEED = Q_(50e3, 'rpm');
ROTOR_MASS = Q_(rotor.m, 'kg'); #kg

total_permissible_unbalance = (ROTOR_MASS / OPERATING_SPEED * BALANCING_GRADE).to('kg*m');
print('ISO permissible unbalance: ', total_permissible_unbalance);

node_unb: int = helpers.PromptInt('Apply imbalance at node?');

frequency_interest: list = np.linspace(0, (OPERATING_SPEED * 2).to('rad/s').m, 200).tolist();
frequency_interest.append(OPERATING_SPEED.to('rad/s').m);
frequency_interest.sort();

unb_response = rotor.run_unbalance_response(
    node=node_unb,
    unbalance_magnitude=total_permissible_unbalance,
    unbalance_phase=0,
    frequency=frequency_interest, #rad/s
    cluster_points=True,
)

DEFAULT_PROBE_NODE: int = len(rotor.nodes_pos) - 1;
probe_node: int = helpers.PromptInt(
    'Probe deflection at node? (Default: last node ' + str(DEFAULT_PROBE_NODE) + ')',
    accept_none=True) or DEFAULT_PROBE_NODE;

ubr_fig = unb_response.plot(probe=[
    rs.Probe(probe_node, angle=0)
    ],
    frequency_units='rpm',
    amplitude_units='thou',
    phase_units='deg'
    )
ubr_fig.write_html(DIRECTORY_TIMEFREQ + '\\UnbalanceResponse.html')
ubr_fig.show()

unb_deflection_fig = unb_response.plot_deflected_shape(
    speed=OPERATING_SPEED.to('rad/s').m,
    frequency_units='rpm',
    amplitude_units='thou'
    )

unb_deflection_fig.write_html(DIRECTORY_TIMEFREQ + '\\UnbalanceDeflection.html')
unb_deflection_fig.show()

print(f'Rotor total mass: {ROTOR_MASS.to('kg').m : .3f} kg')
print("Program exited.\n" + '_'*20);