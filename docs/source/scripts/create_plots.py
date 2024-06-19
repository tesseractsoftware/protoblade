"""Set of tools to create figures and plots for documentation."""

import matplotlib.pyplot as plt
import pathlib
import numpy as np
import shutil

fixture_dir = pathlib.Path(__file__).parent.parent.parent.parent / "tests"/"fixtures"
static_dir = pathlib.Path(__file__).parent.parent / "_static"
auto_figures = static_dir/ "auto_gen"

def clean_figures():
    """Delete all saved plots and figures."""
    if auto_figures.exists():
        shutil.rmtree(auto_figures)

def create_figures():
    """Create all figures for documentation."""
    auto_figures.mkdir(parents=True,exist_ok=True)

    create_vki_blade_plot()

def create_vki_blade_plot():
    """Create XY plot of vki turbine."""
    vki_dir = fixture_dir / "vki_turbine"
    ps = np.load(vki_dir / "vki_ps_sections.npy")
    ss = np.load(vki_dir / "vki_ss_sections.npy")

    plt.figure()
    plt.plot(ps[0]['z'],-ps[0]['y'],label='Pressure Surface')
    plt.plot(ss[0]['z'],-ss[0]['y'],label='Suction Surface')
    plt.legend()
    plt.grid(True)
    plt.xlabel('X [m]')
    plt.ylabel('Y [m]')

    plt.savefig(auto_figures / 'vki.png')

def main():
    """Create all figures."""
    clean_figures()

    create_figures()

if __name__=="__main__":
    main()
