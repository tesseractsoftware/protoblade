"""Test functionality of protoblade's cad module."""
from protoblade import geom, cad, blade
import pathlib
import cadquery as cq
import pytest
import filecmp
import numpy as np
from functools import partial
file_cmp = partial(filecmp.cmp,shallow=False)

@pytest.fixture()
def vki_blade_def(vki_sections, vki_endwalls) -> blade.Blade:
    ps_sections, ss_sections = vki_sections
    hub, shroud = vki_endwalls
    endwalls = blade.Endwalls(hub=hub, shroud=shroud,type='fpd')
    return blade.Blade(ps_sections=ps_sections, ss_sections=ss_sections, n_blade=100, endwalls=endwalls,
                       axis=((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)))
@pytest.fixture()
def vki_blade_def_step(vki_sections, vki_endwalls_step) -> blade.Blade:
    ps_sections, ss_sections = vki_sections
    endwalls = blade.Endwalls(type='step',endwall_fname=str(vki_endwalls_step))
    return blade.Blade(ps_sections=ps_sections, ss_sections=ss_sections, n_blade=100, endwalls=endwalls,
                       axis=((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)))

def test_convert_array_to_list(naca0012_files):
    pts = geom.load_curves_from_fpd(naca0012_files['upper'])
    pts2 = cad._convert_array_to_list(pts)

    for pt_1, pt_2 in zip(pts, pts2):
        for i in range(3):
            assert pt_1[i] == pt_2[i]


def test_extrude_naca0012(naca0012_files, tmp_path):
    pts = cad._convert_array_to_list(geom.load_curves_from_fpd(naca0012_files['upper']))
    p = cq.Workplane("XY").spline(pts)
    s = p.mirrorX().extrude(0.2)

    fname = pathlib.Path(tmp_path) / 'naca_0012.step'
    cq.exporters.export(s, str(fname))

    assert pathlib.Path.is_file(fname)


def test_loft_turbine(vki_blade_def, tmp_path,vki_cad_fixtures):
    creator = cad.DomainCreator(vki_blade_def)
    creator.extrude_blade()

    fname = pathlib.Path(tmp_path) / 'vki.step'
    creator.export('blade', fname)
    assert pathlib.Path.is_file(fname)
    file_cmp(fname,vki_cad_fixtures['blade'])


def test_create_periodic(vki_blade_def, tmp_path,vki_cad_fixtures):
    creator = cad.DomainCreator(vki_blade_def)
    #TODO:mock the endwall creation
    creator.create_endwalls()
    creator.create_periodic()

    fname_out = pathlib.Path(tmp_path) / 'per.step'
    creator.export('per', fname_out)
    assert pathlib.Path.is_file(fname_out)
    filecmp.cmp(fname_out,vki_cad_fixtures['periodic'])


def test_create_periodic_after_extending_mid_points(vki_blade_def,tmp_path,vki_cad_fixtures):
    creator = cad.DomainCreator(vki_blade_def)
    #TODO:mock the endwall creation
    creator.create_endwalls()

    #simulate the case of too small a radius by removing sections
    creator.blade_def.ps_sections = creator.blade_def.ps_sections[1:,:]

    creator.create_periodic()
    fname_out = pathlib.Path(tmp_path) / 'per.step'
    creator.export('per', fname_out)
    assert pathlib.Path.is_file(fname_out)

def test_e2e_fpd_endwalls(vki_blade_def, tmp_path, vki_cad_fixtures):
    creator = cad.DomainCreator(vki_blade_def)
    creator.create_domain()
    fname_final = pathlib.Path(tmp_path) / 'final.step'

    creator.export('domain', fname_final)

    assert pathlib.Path.is_file(fname_final)
    filecmp.cmp(fname_final,vki_cad_fixtures['final'])

def test_e2e_step_endwalls(vki_blade_def_step,tmp_path,vki_cad_fixtures):
    creator = cad.DomainCreator(vki_blade_def_step)
    creator.create_domain()
    fname_final = pathlib.Path(tmp_path) / 'final_with_cavity.step'

    creator.export('domain', fname_final)

    assert pathlib.Path.is_file(fname_final)
    filecmp.cmp(fname_final,vki_cad_fixtures['final_with_cavity'])

def test_create_endwalls_from_fpd(vki_blade_def, tmp_path,vki_cad_fixtures):
    creator = cad.DomainCreator(vki_blade_def)

    creator.create_endwalls()

    fname_out_endwalls = pathlib.Path(tmp_path) / 'endwalls.step'
    creator.export('endwalls', fname_out_endwalls)
    filecmp.cmp(fname_out_endwalls,vki_cad_fixtures['endwalls'])

def test_create_endwalls_from_step(vki_blade_def_step, tmp_path,vki_cad_fixtures):
    creator = cad.DomainCreator(vki_blade_def_step)

    creator.create_endwalls()

    fname_out_endwalls = pathlib.Path(tmp_path) / 'endwalls.step'
    creator.export('endwalls', fname_out_endwalls)
    filecmp.cmp(fname_out_endwalls,vki_cad_fixtures['endwalls'])


def test_find_radial_extent_of_axisymmetric_object(vki_blade_def):
    creator = cad.DomainCreator(vki_blade_def)

    creator.create_endwalls()

    rmin,rmax = cad.find_radial_extent_of_axisymmetric_object(creator.endwalls)

    assert abs(rmin - 0.2584999)< 1e-6
    assert abs(rmax - 0.2865001) <1e-6
