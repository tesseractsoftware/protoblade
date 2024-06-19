"""Set of tests for geom module."""
import math

import pytest

from protoblade import geom
import numpy as np


def test_read_from_fpd(naca0012_files):
    for file in naca0012_files.values():
        pnts = geom.load_curves_from_fpd(file)

        for item in ['x', 'y', 'z']:
            assert len(pnts[item]) == 66


def test_reinterpolate_curve(naca0012_files,naca0012_interp):
    naca = geom.load_curves_from_fpd(naca0012_files['upper'])
    s = geom.calculate_curve_length(naca['x'], naca['y'])
    x, y, s_new = geom.reinterpolate_curve(naca['x'], naca['y'], s, base=1.5)

    save = False
    if save:
        np.save('x_interp',x)
        np.save('y_interp',y)
        np.save('s_interp',s_new)
    else:
        np.testing.assert_array_equal(x,naca0012_interp[0])
        np.testing.assert_array_equal(y,naca0012_interp[1])
        np.testing.assert_array_equal(s_new,naca0012_interp[2])




def test_convert_to_polar():
    pts = np.array([(1., 1., 1.), (2., 2., 2.), (3., 3., 3.)], dtype=geom.cartesian_type)

    polar = geom.convert_to_polar(pts)

    np.testing.assert_array_equal(polar['r'], np.array([2.0 ** 0.5, 8.0 ** 0.5, 18 ** 0.5]))
    np.testing.assert_array_equal(polar['theta'], np.array([np.pi / 4] * 3))
    np.testing.assert_array_equal(polar['z'], np.array([1.0, 2.0, 3.0]))


def test_calculate_curve_length():
    N = 20
    x = np.linspace(0, 1, N)
    y = np.linspace(1, 2, N)

    s = geom.calculate_curve_length(x, y)

    np.testing.assert_array_almost_equal(s, np.asarray([0., .07443229, 0.14886459, 0.22329688, 0.29772917, 0.37216146,
                                                        0.44659376, 0.52102605, 0.59545834, 0.66989063, 0.74432293,
                                                        0.81875522, 0.89318751, 0.96761981, 1.0420521, 1.11648439,
                                                        1.19091668, 1.26534898, 1.33978127, 1.41421356]))


def test_make_mid_point_curve(vki_sections):

    ps_sections, ss_sections = vki_sections

    section_1 = np.concatenate((ps_sections[0], ss_sections[0][::-1]))
    section_1_polar = geom.convert_to_polar(section_1)
    rad = np.mean(section_1_polar['r'])
    n_blade = 100
    Nout = 200
    pitch_angle_rad = 2.0 * np.pi / n_blade

    z = section_1_polar['z']
    rt = section_1_polar['r'] * section_1_polar['theta']


    tol = 1e-3
    z_min = np.min(ps_sections[0]['z'])
    z_max = np.max(ps_sections[0]['z'])

    delta_z = z_max - z_min

    geom.create_midline(Nout, pitch_angle_rad, rad, rt, tol, z, z_max + delta_z * 0.1, z_min - delta_z * 0.1)

def test_make_mid_points(vki_sections,vki_mid_lines):
    ps_sections, ss_sections = vki_sections

    z_min = np.min(ps_sections[0]['z'])
    z_max = np.max(ps_sections[0]['z'])


    delta_z = z_max - z_min
    n_blade = 100
    pitch_angle_rad = 2.0 * np.pi / n_blade

    mid_lines = geom.create_midlines(ps_sections, ss_sections, z_min - delta_z * 0.1, z_max + delta_z * 0.1,pitch_angle_rad, 200)
    np.testing.assert_array_equal(mid_lines,vki_mid_lines)

    #now try without resampling
    mid_lines = geom.create_midlines(ps_sections, ss_sections, z_min - delta_z * 0.1, z_max + delta_z * 0.1,pitch_angle_rad)
    assert mid_lines[0].shape[0] != 0

def test_extrude_radially(vki_sections):
    ps_section = vki_sections[0]

    for del_r in [-0.05,0.05]:

        extruded = geom.extrude_radially(ps_section[0],del_r)

        np.testing.assert_array_almost_equal(
            np.hypot(extruded['x'],extruded['y']),
            np.hypot(ps_section[0]['x'],ps_section[0]['y']) + del_r,
        )

    with pytest.raises(ValueError) as excinfo:
        geom.extrude_radially(ps_section[0], -100)
    assert 'New radius has gone below zero' in str(excinfo.value)
