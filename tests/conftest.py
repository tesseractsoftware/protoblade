import pathlib
import pytest
import numpy as np
from protoblade import geom,blade

fixture_dir = pathlib.Path(__file__).parent / "fixtures"
naca0012_dir = fixture_dir / "naca0012"
vki_dir = fixture_dir / "vki_turbine"


@pytest.fixture()
def naca0012_files():
    return {
        'upper': naca0012_dir / "naca0012_upper.fpd",
        'lower': naca0012_dir / "naca0012_lower.fpd",
    }

@pytest.fixture()
def naca0012_interp():
    return (np.load(naca0012_dir /'x_interp.npy'),
            np.load(naca0012_dir /'y_interp.npy'),
            np.load(naca0012_dir /'s_interp.npy'))

@pytest.fixture()
def vki_files():
    return {
        'pressure': vki_dir / "vki_ps_single.fpd",
        'suction' : vki_dir / "vki_ss_single.fpd"
    }

@pytest.fixture()
def vki_sections():
   return np.load(vki_dir / "vki_ps_sections.npy"), np.load(vki_dir / "vki_ss_sections.npy")

@pytest.fixture()
def vki_endwalls():

    z_min = -0.02
    z_max = 0.03

    r_hub = 0.2585
    r_shroud = 0.2865

    N_end = 5

    hub = np.empty(shape=(N_end,), dtype=geom.cartesian_type)
    shroud = np.empty(shape=(N_end,), dtype=geom.cartesian_type)

    hub['z'] = np.linspace(z_min, z_max, N_end)
    hub['x'] = r_hub * np.ones(N_end)
    hub['y'] = np.zeros(N_end)

    shroud['z'] = np.linspace(z_min, z_max, N_end)
    shroud['x'] = r_shroud * np.ones(N_end)
    shroud['y'] = np.zeros(N_end)

    return hub,shroud

@pytest.fixture()
def vki_endwalls_step(example_directory):
    return example_directory / 'axial_turbine_with_cavity'/ 'with_cavity.step'

@pytest.fixture()
def vki_mid_lines():
    return np.load(vki_dir /'mid_lines.npy')

@pytest.fixture()
def vki_cad_fixtures():
    return {
        'blade': vki_dir/ 'blade.step',
        'endwalls': vki_dir/ 'endwalls.step',
        'final': vki_dir/ 'final.step',
        'periodic': vki_dir/ 'periodic.step',
        'final_with_cavity': vki_dir /'final_with_cavity.step'
    }


@pytest.fixture()
def example_blade_configs():
    return [
        fixture_dir / "example_blade_config.toml",
        fixture_dir / "example_blade_config_step_endwall.toml",
        ]

@pytest.fixture()
def example_directory():
    return fixture_dir.parent.parent / 'examples'