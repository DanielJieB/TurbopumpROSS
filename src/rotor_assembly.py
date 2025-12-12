import helpers
import ross as rs
import numpy as np
import math
import os

from ross.units import Q_
# import plotly just to guarantee that plots will appear in the docs
import plotly

from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio

pio.renderers.default = "browser"# "vscode"

PLOT_ROTOR = True;

def safe_int(x: float, tol: float = 1e-9) -> int:
    rounded = round(x);
    return int(rounded) if math.isclose(x, rounded, abs_tol=tol) else int(rounded);

# https://asm.matweb.com/search/specificmaterial.asp?bassnum=mq304a
ss_304 = rs.Material(name="Stainless-304", rho = 8000, E = 1.93e11, Poisson=0.29);

ss_A286 = rs.Material(name="Stainless-A286", rho=7944.1327, E=Q_(28.8E6, 'psi'), Poisson=0.31)

#%%____________________PRELIMINARY SHAFT______________________
# start from turbine to lox inlet

pre_list = []

def ShaftSection(L: float, odl: float, odr: float | None = None) -> None:
    if odr is None:
        odr = odl;
    pre_list.append({"L": L, "odl": odl, "odr": odr});

def PartitionedSection(L: float, odl: float, partitions: int, odr: float | None = None):
    #return ShaftSection(L, odl=odl, odr=odr)
    if odr is None:
        odr = odl;
    SECTION_LENGTH = L / partitions;
    SLOPE = (odr - odl) / L;
    for i in range(partitions):
        if odl == odr:
            ShaftSection(SECTION_LENGTH, odl=odl, odr=odr)
        else:
            this_odl = odl + SLOPE*i*SECTION_LENGTH;
            this_odr = this_odl + SLOPE*SECTION_LENGTH;
            ShaftSection(SECTION_LENGTH, odl=this_odl, odr=this_odr);

overlaps = [];
def OverlappingSection(L: float, start: float, odl: float, idl: float, odr: float|None=None, idr: float|None=None) -> None:
    odr: float = not odr is None and odr or odl
    idr: float = not idr is None and idr or idl
    
    overlaps.append({
        'Start': start,
        'L': L,
        'odl': odl,
        'odr': odr,
        'idl': idl,
        'idr': idr
    })

# UNF 3/8-24 threads

#ShaftSection(L=0.38, odl=(3/8 + 0.330)/2)
#ShaftSection(L=3.0428, odl=0.4);
ShaftSection(L=3.0428 + 0.38, odl=0.4);
# LABY SECTION

NOTCH_WIDTH = 0.01; #in
GAP_WIDTH = 0.031; #in
GAP_DEPTH = 0.031; #in
STEP_WIDTH = 0.04; #in
STEP_SIZE = 0.011; #in

laby_od_temp = 0.63; #in
STEP_COUNT = 6;
GAPS_PER_STEP = 5;

IPS_DEDUCT = 0; #in
# Just average the diameters
PartitionedSection(L=1.5101 - IPS_DEDUCT, odl=0.63 - GAP_DEPTH, odr=0.74 - GAP_DEPTH, partitions=3)
# END OF LABY

ShaftSection(L=1.098,odl=0.47244);
ShaftSection(L=0.6721,odl=0.4);

# 1/4-28 UNF length 0.25

ShaftSection(L=0.67033849, odl=1/4)

# simple sleeve
OverlappingSection(L=0.25, start=0.25, odl=1.404, idl=0.4);
OverlappingSection(L=0.15274843, start=0.5, odl=1.404, odr=0.669, idl=0.4)

# detailed
#OverlappingSection(L=0.788, start=0.6522, odl=0.669, idl=0.4);

# simple sleeve
OverlappingSection(L=0.80648819, start=0.65269270, odl=0.669, idl=0.4);

OverlappingSection(L=0.92776339, start=1.45918089, odl=0.54468000, idl=0.4);
#OverlappingSection(L=0.5335, start=1.8536, odl=0.5447, idl=0.4);

#%% SIMPLE SHAFT
lengths = [];
odr = [];
odl = [];
for section in pre_list:
    lengths.append(Q_(section["L"], 'in'));
    odl.append(Q_(section["odl"], 'in'));
    odr.append(Q_(section["odr"], 'in'));

shaft_elements = [
    rs.ShaftElement(
        L = lengths[i],
        idl=0,
        odl=odl[i],
        odr=odr[i],
        material=ss_A286,
        gyroscopic=True,
        shear_effects=True,
        rotary_inertia=True
    )
    for i in range(len(pre_list))
];

simple_shaft = rs.Rotor(shaft_elements=shaft_elements);

#%% Put in Overlapping Shaft Elements

#%% Insert Disks and Bearings
add_nodes = [];
position_map = {};

def Mark(object: any, position_inch: float):
    if position_inch >= 4.9430:
        position_inch -= IPS_DEDUCT;
    
    position_m = position_inch * 0.0254;
    add_nodes.append(position_m);
    position_map[position_m] = object;

sleeve_nut = rs.DiskElement(
    n=0,
    m=1.362e-2,
    Id=5.402e-7,
    Ip=5.396e-7,
    tag="Sleeve Nut",
    scale_factor=0.25
)
Mark(sleeve_nut, 0.08758354);

turbine = rs.DiskElement(
    n=0,
    m=0.2915,
    Ip = 3.68E-4, 
    Id=1.848E-4,
    tag="Turbine",
    scale_factor=1.5,
    );
Mark(turbine, 0.15098510);

kero_nut = rs.DiskElement(
    n=0,
    m=0.024601,
    Ip=2.96E-6,
    Id=1.65E-6,
    tag="Kero Bearing Nut",
    scale_factor=0.3
)
Mark(kero_nut, 1.21340871);

kero_inducer = rs.DiskElement(
    n=0,
    m=7.6e-3,
    Ip = 6.24e-7,
    Id = ((4.52 + 4.02)/2)*1e-7,
    tag = "Kero Inducer",
    scale_factor=0.5,
    color = '#a324bf'
);
Mark(kero_inducer, 2.68662598425);

kero_impeller = rs.DiskElement(
    n=0,
    m=3.63e-2,
    Ip=1.154e-5,
    Id=6.469e-6,
    tag="Kero Impeller",
    scale_factor=0.7,
    color="Green"
)
Mark(kero_impeller, 3.18677735);

spacer_lox = rs.DiskElement(
    n=0,
    m=Q_(0.01405150, 'lb'),
    Ip=Q_(0.00113413, 'lb * in^2'),
    Id=Q_(0.00068003, "lb * in^2"),
    tag="Spacer LOX",
    scale_factor=0.2
)
Mark(spacer_lox, 5.88550079);

lox_impeller = rs.DiskElement(
    n=0,
    m=8.4E-2,
    Ip=1.919e-5,
    Id=1.157e-5,
    tag="LOX Impeller",
    scale_factor=0.6,
    color="#2430bf"
)
Mark(lox_impeller, 6.30276813);

lox_inducer = rs.DiskElement(
    n=0,
    m=1.9E-2,
    Ip=1.23E-6,
    Id=(9.2 + 8.3)/2*1E-7,
    tag="LOX Inducer",
    scale_factor=0.5,
    color='#94bf24'
)
Mark(lox_inducer, 6.832196456693);

retaining_nut = rs.DiskElement(
    n=0,
    m=4.491E-3,
    Ip=7.134E-8,
    Id=6.8793E-8,
    tag="Retaining Nut",
    scale_factor=0.2,
)
Mark(retaining_nut, 7.358319685039);

disk_elements = [
    sleeve_nut,
    turbine,
    kero_nut,
    kero_inducer,
    kero_impeller,
    spacer_lox,
    lox_impeller,
    lox_inducer,
    retaining_nut
]

#%% BEARINGS

bearing_alpha = 15 * np.pi / 180;

def GetEquivalentRadialLoad(alpha_rad: float, F_axial: float) -> float:
    N = F_axial / np.sin(alpha_rad);
    return N * np.cos(alpha_rad);

axial_LOX_preload = 50; #N
axial_RP1_preload = 50; #N

#TODO actually calculate this
pressfit_LOX_preload = 10; #N
pressfit_RP1_preload = 10; #N

l_preload = pressfit_LOX_preload+  GetEquivalentRadialLoad(
    alpha_rad=bearing_alpha, F_axial=axial_LOX_preload
    ); #N
k_preload = pressfit_RP1_preload + GetEquivalentRadialLoad(
    alpha_rad=bearing_alpha, F_axial=axial_RP1_preload
    ); #N   
print(l_preload)
print(k_preload)
l_preload = 164.5; #N
k_preload = 80; #N

kero_bearing1 = rs.BallBearingElement(
    n=0, n_balls=12, d_balls=5.556E-3,
    fs=k_preload, alpha=bearing_alpha, tag="KeroBearing1")

lox_bearing1 = rs.BallBearingElement(
    n=0, n_balls=10, d_balls=5.556E-3,
    fs=l_preload, alpha=bearing_alpha, tag="LOXBearing1"
)

lox_bearing2 = rs.BallBearingElement(
    n=0, n_balls=10, d_balls=5.556E-3,
    fs=l_preload, alpha=bearing_alpha, tag="LOXBearing2"
)

def IsotropicBearing(bearing: rs.BallBearingElement) -> rs.BearingElement:
    kxx = bearing.K(0)[0, 0]
    kyy = bearing.K(0)[1, 1]
    cxx = bearing.C(0)[0, 0]
    cyy = bearing.C(0)[1, 1]

    k = (kxx + kyy) / 2;
    c = (cxx + cyy) / 2;
    return rs.BearingElement(n=0, kxx=k, cxx=c);

if helpers.PromptBool('Isotropic Bearings'):
    kero_bearing1 = IsotropicBearing(kero_bearing1)
    lox_bearing1 = IsotropicBearing(lox_bearing1)
    lox_bearing2 = IsotropicBearing(lox_bearing2)

Mark(kero_bearing1, 0.84904964),

Mark(lox_bearing1, 5.13965039);

Mark(lox_bearing2, 5.53335118);

'''
lox_bearing1 = rs.BearingElement(n=0, kxx=35e6, kyy=35e6, cxx=0)
Mark(lox_bearing1, 5.13965039)
lox_bearing2 = rs.BearingElement(n=0, kxx=35e6, kyy=35e6, cxx=0)
Mark(lox_bearing2, 5.53335118)
kero_bearing1 = rs.BearingElement(n=0, kxx=35e6, kyy=35e6, cxx=0)
Mark(kero_bearing1, 0.84904964)
'''
bearing_elements = [
    kero_bearing1,
    #kero_bearing2,
    lox_bearing1,
    lox_bearing2
]

#%% FINAL ASSEMBLY
node_shaft = simple_shaft.add_nodes(add_nodes);
shaft_elements = node_shaft.shaft_elements;

add_nodes = [];

def bruh_search(inch: float, tol: float | None = 1E-3) -> bool:
    for meter in simple_shaft.nodes_pos:
        if np.isclose(Q_(meter, 'm'), Q_(inch, 'in'), tol):
            return True
    return False

for _, overlap in enumerate(overlaps):
    n1 = overlap['Start'];
    if not (bruh_search(n1)):
        add_nodes.append(n1);

overlap_insert_shaft = node_shaft.add_nodes((np.array(add_nodes) * 0.0254).tolist())
shaft_elements = overlap_insert_shaft.shaft_elements

def FindClose(from_list: any, value: float) -> float | None:
    for v in from_list:
        if abs(value - v) < 1e-5:
            return v

overlap_index = 0;

for node_i, node_pos in enumerate(overlap_insert_shaft.nodes_pos):
    key = FindClose(position_map.keys(), node_pos);
    if not key is None:
        element = position_map[key]
        element.n = node_i;

    if overlap_index == len(overlaps): continue;
    overlap = overlaps[overlap_index];
    
    if np.abs(Q_(overlap['Start'], 'in') - Q_(node_pos, 'm')) > Q_(1E-3, 'in'):
        continue
    
    overlap_index += 1;

    overlap_shaft_elem = rs.ShaftElement(
        L=Q_(overlap['L'], 'in'),
        idl=Q_(overlap['idl'], 'in'),
        idr=Q_(overlap['idr'], 'in'),
        odl=Q_(overlap['odl'], 'in'),
        odr=Q_(overlap['odr'], 'in'),
        material=ss_A286,
        n=node_i,
        gyroscopic=True,
        shear_effects=True,
        rotary_inertia=True
        );
    shaft_elements.append(overlap_shaft_elem);

rotor_model = rs.Rotor(
    shaft_elements=shaft_elements,
    disk_elements=disk_elements,
    bearing_elements=bearing_elements)

rotor_fig = helpers.PlotRotor(rotor_model, show=helpers.PromptBool("Show rotor plot?"))

print(f'Total rotor mass: {rotor_model.m : .3f} kg');

name: str = input("Enter model name? (Default: \'Default\')\n")

if name == '':
    name = 'Default'
directory: str = os.getcwd() + '\\Results\\'+ name;
if not os.path.isdir(directory):
    os.makedirs(directory);

rotor_model.save(directory + '\\MODEL.json');

rotor_fig.write_html(directory + '\\RotorModel.html');

print("Rotor model created in " + directory);