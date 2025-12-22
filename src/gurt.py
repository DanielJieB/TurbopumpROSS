import helpers
import ross as rs
import numpy as np

import os

from ross.units import Q_

import plotly.io as pio
pio.renderers.default = "browser"# "vscode"

Q_ = rs.Q_
steel = rs.Material("steel", E=211e9, G_s=81.2e9, rho=7810)
L = 0.25
N = 6
idl = 0
odl = 0.05

shaft = [rs.ShaftElement(L=L, idl=idl, odl=odl, material=steel) for i in range(N)]
bearings = [
    rs.BearingElement(
        n=0, kxx=1e6, kyy=1e6, kxy=0.5e6, kyx=0.5e6, cxx=0, scale_factor=2
    ),
    rs.BearingElement(
        n=len(shaft), kxx=1e6, kyy=1e6, kxy=0.5e6, kyx=0.5e6, cxx=0, scale_factor=2
    ),
]
disks = [
    rs.DiskElement.from_geometry(
        n=2, material=steel, width=0.07, i_d=odl, o_d=0.28, scale_factor="mass"
    ),
    rs.DiskElement.from_geometry(
        n=4, material=steel, width=0.07, i_d=odl, o_d=0.35, scale_factor="mass"
    ),
]

rotor = rs.Rotor(shaft_elements=shaft, disk_elements=disks, bearing_elements=bearings)
rotor.plot_rotor()
campbell = rotor.run_campbell(
    speed_range=Q_(list(range(0, 4500, 50)), "RPM"), frequencies=7
)
campbell.plot(frequency_units="RPM")
modal = rotor.run_modal(speed=Q_(4000, "RPM"), num_modes=14)
for mode in range(7):
    modal.plot_mode_3d(mode, frequency_units="Hz").show()
for mode in range(7):
    modal.plot_orbit(mode, nodes=[2, 4]).show()