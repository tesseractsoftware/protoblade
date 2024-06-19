"""Test examples that are stored in protoblade repo."""
import pathlib
import os
from protoblade.__main__ import main
import filecmp
from distutils.dir_util import copy_tree


def test_example_axial_turbine(example_directory,tmp_path,vki_cad_fixtures):

    copy_tree(example_directory /'axial_turbine', str(tmp_path))
    os.chdir(tmp_path)
    fname_final = pathlib.Path(tmp_path) / 'final.step'

    main('axial_turbine.toml',fname_final)

    filecmp.cmp(fname_final,vki_cad_fixtures['final'],shallow=False)

def test_example_axial_turbine_with_cavity(example_directory,tmp_path,vki_cad_fixtures):
    copy_tree(example_directory / 'axial_turbine_with_cavity', str(tmp_path))
    os.chdir(tmp_path)
    fname_final = pathlib.Path(tmp_path) / 'final_with_cavity.step'

    main('axial_turbine_with_cavity.toml', fname_final)

    filecmp.cmp(fname_final, vki_cad_fixtures['final_with_cavity'],shallow=False)