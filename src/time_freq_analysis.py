import helpers
import ross as rs
import numpy as np
import os
import random

from ross.units import Q_

import plotly.io as pio
pio.renderers.default = "browser"# "vscode"

rotor, DIRECTORY = helpers.LoadRotor();
DIRECTORY_TIMEFREQ = DIRECTORY + '\\TimeFrequency';
if not os.path.isdir(DIRECTORY_TIMEFREQ):
    os.makedirs(DIRECTORY_TIMEFREQ);

save_figs = []
def SaveFig(fig, name: str) -> None:
    save_figs.append({'fig': fig, 'name': name})

# ISO 21940 "Balancing Quality Grade G" according to the product of e*omega, where e is unbalance/equivalent eccentricity (mm) and omega is the operating speed (rad/s)
BALANCING_GRADE = Q_(helpers.PromptFloat('Enter ISO Balancing Quality Grade G (Default: 2.5):', True) or 2.5, 'mm/s');
OPERATING_SPEED = Q_(50e3, 'rpm');
ROTOR_MASS = Q_(rotor.m, 'kg'); #kg

offset_components = [
    'Kero Impeller',
    'Kero Inducer',
    'LOX Impeller',
    'LOX Inducer',
    #'Turbine'
]

imb_nodes = [];
imb_amp = [];
imb_phase = [];
TOTAL_PERMISSIBLE_IMB = (ROTOR_MASS / OPERATING_SPEED * BALANCING_GRADE).to('kg*m')

U_x_sum = Q_(0, 'kg*m')
U_y_sum = Q_(0, 'kg*m')

SAME_PHASE: bool = helpers.PromptBool('Same orientation imbalance?')

for i in range(len(rotor.disk_elements)):
    disk_elm = rotor.disk_elements[i];

    element_name: str = disk_elm.tag;

    if element_name in offset_components:
        imb_nodes.append(disk_elm.n);

        amplitude = Q_(disk_elm.m, 'kg') * (Q_(0.5, 'thou').to('m'));

        phase = 0 if SAME_PHASE else random.uniform(0, 2*np.pi);

        U_x_sum += amplitude * np.cos(phase)
        U_y_sum +=amplitude * np.sin(phase)

        imb_amp.append(amplitude.m);
        imb_phase.append(Q_(phase, 'rad'))

        print(f'{element_name} imbalance: {amplitude.to('g*mm').m: .3f} g*mm')

U = np.sqrt(U_x_sum**2 + U_y_sum**2)
achieved_grade = U * OPERATING_SPEED / ROTOR_MASS
print(f'Achieved balancing grade: ISO G{achieved_grade.to('mm/s'): .2f}')


#imb_phase = [0] * len(imb_nodes)

OPERATING_SPEED = Q_(50e3, 'rpm');
frequency_interest: list = np.linspace(0, Q_(45e3, 'rpm').to('rad/s').m, 15).tolist() + np.linspace(Q_(45e3, 'rpm').to('rad/s').m, Q_(80e3, 'rpm').to('rad/s').m, 130).tolist() + np.linspace(Q_(80e3, 'rpm').to('rad/s').m, Q_(1e5, 'rpm').to('rad/s').m, 10).tolist();
frequency_interest.append(OPERATING_SPEED.to('rad/s').m);
frequency_interest.sort();

print(imb_nodes)
unb_response = rotor.run_unbalance_response(
    imb_nodes, imb_amp, imb_phase,
    frequency=frequency_interest)

LAST_NODE: int = len(rotor.nodes_pos) - 1;

probes = [];
probe_node: int = None

while probe_node != -1:
    if probe_node is not None:
        probes.append(rs.Probe(probe_node, 0));
    
    probe_node = helpers.PromptInt(
    'Probe deflection at node? (last node: ' + str(LAST_NODE) + ')',
    accept_none=True) or -1;

if probe_node is None: rs.Probe(LAST_NODE, 0);

ubr_fig = unb_response.plot(probe=probes,
    frequency_units='rpm',
    amplitude_units='thou',
    phase_units='deg'
    )
SaveFig(ubr_fig, 'UnbalanceResponseBodeNode.html');
#ubr_fig.write_html(DIRECTORY_TIMEFREQ + '\\UnbalanceResponseBodeNode' + str(DEFAULT_PROBE_NODE) + '.html')
ubr_fig.show()

unb_deflection_fig = unb_response.plot_deflected_shape(
    speed=OPERATING_SPEED.to('rad/s').m,
    frequency_units='rpm',
    amplitude_units='thou'
    #shape2d_kwargs=dict(amplitude_units='thou'),
    #shape3d_kwargs=dict(amplitude_units='m')
    )

SaveFig(unb_deflection_fig, 'UnbalanceDeflection.html')
#unb_deflection_fig.write_html(DIRECTORY_TIMEFREQ + '\\UnbalanceDeflection.html')
unb_deflection_fig.show()

deflected_shape = unb_response.plot_deflected_shape_3d(
    speed=OPERATING_SPEED.to('rad/s').m,
    )
SaveFig(deflected_shape, 'DeflectionShape3D.html')
deflected_shape.show()

if helpers.PromptBool('Save figures?'):
    for v in save_figs:
        fig = v['fig'];
        fig.write_html(DIRECTORY_TIMEFREQ + '\\' + v['name']);

print(f'Rotor total mass: {ROTOR_MASS.to('kg').m : .3f} kg')
print("Program exited.\n" + '_'*20);