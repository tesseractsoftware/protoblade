"""A set of functions to undertake geometrical manipulations."""
import math
import pathlib
import numpy as np
from numpy.typing import NDArray
from scipy.interpolate import interp1d
from typing import Tuple
from enum import Enum

cartesian_type = np.dtype([("x", np.double), ("y", np.double), ("z", np.double)])
polar_type = np.dtype([("r", np.double), ("theta", np.double), ("z", np.double)])


def load_curves_from_fpd(fname: str or pathlib.Path) -> NDArray:
    """Load a series of curves from a formatted point data (fpd) file."""
    with open(fname, 'r') as f:
        n_pts, n_curve = list(map(int, f.readline().split()))
        pts = np.array([tuple(map(float, line.split())) for line in f.readlines()], dtype=cartesian_type)

    if n_curve > 1:
        pts = np.reshape(pts, (n_curve, n_pts))

    return pts


def convert_to_polar(pts: NDArray) -> NDArray:
    """
    Create arrays for radius , Theta and Z from cartesian array.

    Args:
        pts: array of cartesian points dtype cartesian

     Returns:
        An array which can be accessed through ['z'],['r'] and['theta' for Z, Radius and Theta respectively

    """
    out = np.empty(shape=(pts['z'].shape[0],), dtype=polar_type)

    out['z'] = pts['z']
    out['r'] = (pts['x'] ** 2.0 + pts['y'] ** 2) ** 0.5
    out['theta'] = np.arctan(pts['y'] / pts['x'])

    return out


def calculate_curve_length(x: NDArray, y: NDArray) -> NDArray:
    """Create an array of curve length based on the two input arrays x,y."""
    s = np.zeros(x.shape[0])
    for i in range(1, x.shape[0]):
        dx = x[i] - x[i - 1]
        dy = y[i] - y[i - 1]
        s[i] = s[i - 1] + np.sqrt(dx * dx + dy * dy)
    return s


def reinterpolate_curve(x: NDArray, y: NDArray, s: NDArray, base: float = 1.5, N_new: int = 0) -> Tuple[
    NDArray, NDArray, NDArray]:
    """
    Reinterpolate the arrays x,y and s based on a power law to a given base.

    Args:
        x: array for axial co-ordinate
        y: array for y co-ordinate
        s: array for curve length
        base: base for power law should be >1. The higher the number the closer the clustering
        N_new : Half the number points for the newly reintpolated array. Set to 0 to keep the same as the input
    Returns
        A tuple of three arrays newly interpolated arrays : x_new,y_new,s_new

    """
    N = x.shape[0]
    fx = interp1d(s, x)
    fy = interp1d(s, y)

    del_s = max(s) - min(s)

    start = 0.0 ** (1.0 / base)
    mid = 0.5 ** (1.0 / base)
    if N_new == 0:
        N_new = N
    s_new = np.zeros(N_new)
    for i in range(1, N_new + 1):
        s_new[i - 1] = (start + (i - 1) * (mid - start) / (N_new - 1)) ** base

    s_2 = np.flipud(s_new)

    s_3 = 1 - s_2
    s_4 = np.delete(s_3, 0)

    s_new = np.concatenate((s_new, s_4)) * del_s

    x_new = np.zeros(len(s_new))
    y_new = np.zeros(len(s_new))
    for i in range(len(s_new)):
        x_new[i] = fx(s_new[i])
        y_new[i] = fy(s_new[i])

    return x_new, y_new, s_new


def calculate_curvature() -> NDArray:
    """Caluclate curvature of x,y."""
    return


def create_midlines(ps_sections, ss_sections, z_min, z_max, pitch_angle_rad,n_resample: int = 0):
    """
    Create curves to represent the midline of a pressure and section surfaces.

    Args:
        ps_sections: array of pressure surface sections N sections with M points
        ss_sections: array of suction surface sections N sections with M points
        z_min: minimum z value for the midline
        z_max: maximum z value for the midline
        pitch_angle_rad : pitch angle between blades in radians
        n_resample: number of points in the reinterpolated midpoint, set to 0 to skip reinterpolation

    Returns:
        midpoints : array of midpoint curves : Nsections with M points

    """
    mid_points = []
    N_sections = ps_sections.shape[0]
    from scipy.signal import resample
    for i in range(N_sections):
        section_ = np.concatenate((ps_sections[i], ss_sections[i][::-1]))
        section_polar = convert_to_polar(section_)
        rad = np.mean(section_polar['r'])

        z = section_polar['z']
        rt = section_polar['r'] * section_polar['theta']

        if n_resample > 0:
            z = resample(z, n_resample)
            rt = resample(rt, n_resample)
        else:
            n_resample = 200
        tol = 1e-3

        mid_points.append(create_midline(n_resample, pitch_angle_rad, rad, rt, tol, z, z_max, z_min))
    return mid_points


def create_midline(Nout, pitch_angle_rad, rad, rt, tol, z, z_max, z_min):
    """
    Find the midline between two sections based on Voronoi's algorithm.

    Args:
        Nout: Number of points in the ouput array
        pitch_angle_rad: pitch angle in radians (angle between adjacent blades)
        rad: radius of current section
        rt: array of points in the r-Theta plane
        tol: tolerance used when finding duplicate points
        z: array of points in the z plane
        z_max: maximum z value for final mid line curve
        z_min: minimum z value for final mid line curve

    Returns:
        midpoints_cart: array of midline points in cartesian co-ordinate system

    """
    from scipy.spatial import Voronoi
    from scipy.interpolate import interp1d

    blade_pitch = rad * pitch_angle_rad
    points_single = np.zeros([len(z), 2])
    points = np.zeros([len(z) * 2 - 1, 2])
    for i in range(0, len(z)):
        points[i][0] = rt[i]
        points[i][1] = z[i]
        points_single[i][0] = rt[i]
        points_single[i][1] = z[i]
    for i in range(0, len(z)):
        points[len(z) - 1 + i][0] = rt[i] + blade_pitch
        points[len(z) - 1 + i][1] = z[i]

    # look at voronoi
    vor_single = Voronoi(points_single)
    vor = Voronoi(points)

    N_vor = np.shape(vor.vertices)
    N_vor = N_vor[0]
    N_vor_single = np.shape(vor_single.vertices)
    N_vor_single = N_vor_single[0]
    mid_rt = []
    mid_z = []
    # TODO : fix this horrible thing
    for i in range(N_vor):
        duplciate = 0
        vor_rt = vor.vertices[i][0]
        vor_z = vor.vertices[i][1]
        for j in range(N_vor_single):
            if (abs(vor_z - vor_single.vertices[j][1]) < tol and abs(vor_rt - vor_single.vertices[j][0]) < tol) or \
                    (abs(vor_z - vor_single.vertices[j][1]) < tol and abs(
                        vor_rt - (vor_single.vertices[j][0] + blade_pitch)) < tol):
                duplciate = 1
        if duplciate == 0:
            if vor_z > z_min and vor_z < z_max and vor_rt > min(points[:, 0]) + blade_pitch * 0.25:
                mid_rt.append(vor_rt)
                mid_z.append(vor_z)
    N_mid = len(mid_rt)
    midpoints = np.zeros([N_mid, 2])
    for i in range(0, N_mid):
        midpoints[i][0] = mid_rt[i]
        midpoints[i][1] = mid_z[i]
    midpoints = midpoints[np.argsort(midpoints[:, 1])]

    # interpolate midpoints
    z_int = np.linspace(z_min, z_max, Nout)
    f2 = interp1d(midpoints[:, 1], midpoints[:, 0], fill_value='extrapolate')
    midpoints_out = np.zeros([Nout, 2])
    midpoints_cart = np.zeros([Nout, 3])
    for i in range(Nout):
        midpoints_out[i][1] = z_int[i]
        midpoints_out[i][0] = f2(z_int[i])

        midpoints_cart[i][2] = z_int[i]
        t = f2(z_int[i]) / rad
        midpoints_cart[i][0] = rad * np.cos(t)
        midpoints_cart[i][1] = rad * np.sin(t)

    return midpoints_cart


def extrude_radially(input: NDArray, delta_r: float) -> NDArray:
    """Take an array of X,Y,Z points and extrude radially inwards or outwards.

    Args
        input : input array to be extruded
        delta_r : amount to be extruded in metres. Positive for increase in radius, negative for decrease

    Returns
        output : output array at new radial location

    Raises
        ValueError : if new radial position is less than zero
    """

    new_r = np.hypot(input['x'], input['y']) + delta_r

    if np.where(new_r < 0)[0].size > 0:
        raise ValueError('New radius has gone below zero')

    t = np.arctan(input['y']/ input['x'])

    output = np.zeros(input.size, dtype=cartesian_type)

    output['x'] = new_r * np.cos(t)
    output['y'] = new_r * np.sin(t)
    output['z'] = input['z']

    return output
