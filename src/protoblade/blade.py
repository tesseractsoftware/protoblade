"""A set of functions and classes to handle represent a turbomachinery blade."""
from __future__ import annotations
from numpy.typing import NDArray
import numpy as np
from protoblade import geom
import tomli
from atom.api import Atom, Int,List,Enum,Str,Typed,Property,Float,Tuple

ENDWALL_TYPES = ['fpd','step']

class Endwalls(Atom):
    """Hold objects required to define endwalls."""

    hub = Typed(np.ndarray)
    shroud = Typed(np.ndarray)
    type= Enum(*ENDWALL_TYPES)

    endwall_fname = Str()

class CoreBlade(Atom):
    """Core entities required to define a turbomachinery blade."""

    name = Str()
    n_blade = Int()
    units = Enum('metres','millimetres')
    axis = Tuple(Tuple(float))

class BladeConfig(CoreBlade):
    """Holds data required to config a new Blade instance."""

    ps_section_fname = Str()
    ss_section_fname = Str()
    endwall_type = Str()
    hub_fname = Str()
    shroud_fname = Str()
    endwall_fname = Str()

class Blade(CoreBlade):
    """Represents a turbomachinery blade."""

    n_sections = Property(Int)
    ps_sections = Typed(np.ndarray)
    ss_sections = Typed(np.ndarray)
    endwalls = Typed(Endwalls)


    pitch_angle_rad = Property()

    def _get_pitch_angle_rad(self) ->float:
        return 2.0 * np.pi / self.n_blade


    @classmethod
    def from_config(cls,fname:str)->Blade:
        """Create instance of class from a toml file."""
        config = BladeConfig(**_read_toml(fname))

        endwall_dict = {
            'type' : config.endwall_type,
            'hub': geom.load_curves_from_fpd(config.hub_fname) if config.endwall_type=='fpd' else None,
            'shroud': geom.load_curves_from_fpd(config.shroud_fname) if config.endwall_type =='fpd' else None,
            'endwall_fname' : config.endwall_fname,
        }

        init_dict ={'ps_sections': geom.load_curves_from_fpd(config.ps_section_fname),
                    'ss_sections' : geom.load_curves_from_fpd(config.ss_section_fname),
                    'name':config.name,
                    'n_blade':config.n_blade,
                    'endwalls':Endwalls(**endwall_dict),
                    'axis':config.axis}





        return cls(**init_dict)


def _read_toml(fname:str)->dict:
    """Read a toml configuratino file."""
    with open(fname, mode="rb") as fp:
        config = tomli.load(fp)
    config['axis'] = tuple([tuple(x) for x in config['axis']] )
    return config

#TODO: this should use the radial extrusion function
def create_sections_from_2D_profile(ps:NDArray,ss:NDArray,N_sections:int,r_extents:tuple,use_r_theta:bool=True,del_x:float=0,n_resample:int=0):
    """
    Create a set of sections from the R-Theta Z plane to the cartesian plane across a radius span.

    Args:
        ps: array of Z and r-Theta points for pressure surface
        ss: array of Z and r-Theta points for pressure surface
        N_sections: Number of sections to create across the radial span
        r_extents: radial extents of the span, the first entry of the tuple must be lower than the second
        use_r_theta: True will extrude the geometry with constant R-Theta co-ordinates across the span, False will
                        extrude the geometry with constant Theta values
        del_x: an offset to apply in the z/x-axis
        n_resample: set to a non-zero value to resample an array.

    Returns:
        ps_sections : NxM array of new pressure surface sections
        ss_sections : NxM array of new suction surface sections
    """
    x_ps = ps['x']
    rt_ps = ps['y']

    x_ss = ss['x']
    rt_ss = ss['y']
    r_min, r_max = r_extents

    if n_resample > 1:
        x_ps,rt_ps,_ = geom.reinterpolate_curve(x_ps,rt_ps,geom.calculate_curve_length(x_ps,rt_ps),base=1.5,N_new=n_resample)
        x_ss,rt_ss,_ = geom.reinterpolate_curve(x_ss,rt_ss,geom.calculate_curve_length(x_ss,rt_ss),base=1.5,N_new=n_resample)

        N_ps = x_ps.shape[0]
        N_ss = x_ss.shape[0]
    else:
        N_ps = len(x_ps)
        N_ss = len(x_ss)

    t_ps = rt_ps / r_min
    t_ss = rt_ss / r_min

    r = np.linspace(r_min, r_max, N_sections)


    ps_section=[]
    ss_section =[]
    for i in range(N_sections):
        ps_out = np.empty(shape=(N_ps,), dtype=geom.cartesian_type)
        ss_out = np.empty(shape=(N_ss,), dtype=geom.cartesian_type)
        if use_r_theta:
            theta_ps = rt_ps / r[i]
            theta_ss = rt_ss / r[i]
        else:
            theta_ps = t_ps
            theta_ss = t_ss

        ps_out['x'] = r[i] * np.cos(theta_ps)
        ps_out['y'] = r[i] * np.sin(theta_ps)
        ps_out['z'] = x_ps +del_x

        ss_out['x'] = r[i] * np.cos(theta_ss)
        ss_out['y'] = r[i] * np.sin(theta_ss)
        ss_out['z'] = x_ss +del_x

        ps_section.append(ps_out)
        ss_section.append(ss_out)

    return ps_section,ss_section