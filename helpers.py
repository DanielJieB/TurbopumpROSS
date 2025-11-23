import ross as rs
import numpy as np
import os

def LoadRotor() -> tuple[rs.Rotor, str]:
    name: str = input("Load model (Default: \'Default\')?:\n")
    if name == '': name = 'Default'
    directory = os.getcwd() + '\\Results\\' + name;

    if not os.path.isdir(directory):
        raise ValueError('In valid directory name');

    return rs.Rotor.load(directory + "\\MODEL.json"), directory;

def PlotRotor(rotor: rs.Rotor):
    fig = rotor.plot_rotor(length_units='in', check_sld=True)
    fig.update_layout(
        yaxis=dict(
            showgrid=True,
            dtick=0.5,
            scaleanchor='x',  # link y-axis scale to x-axis
        ),
        xaxis=dict(
            dtick=0.5,
            showgrid=True,
            #scaleratio=1,
            scaleanchor=None,
        ),
    )
    fig.show();
    return fig

def PromptBool(message: str) -> bool:
    value = None;
    while value is None:
        response = input(message + "\nEnter \'y\' or \'n\'\n");
        #print('\n')
        if response == 'y' or response == 'Y':
            value = True
        elif response == 'n' or response == 'N':
            value = False
    print('...\n')
    return value

def PromptInt(message: str, accept_none: bool=False) -> int | None:
    value = None
    APPEND = "\nEnter an integer" + (accept_none and " (optional)" or '') + '\n';
    while value is None:
        response = input(message + APPEND);
        #print('\n')
        try:
            value = int(response)
        except ValueError:
            if accept_none:
                print('...\n')
                return None;
            continue
    print('...\n')
    return value;

def ToAngularFreq(rpm: float) -> float:
    return rpm/60 * 2 * np.pi;
