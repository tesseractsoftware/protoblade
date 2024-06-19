"""Module with classes and functions to create CAD models from protoblade classes."""
import cadquery as cq
from numpy.typing import NDArray
from typing import Tuple,List
import numpy as np
from  protoblade import  geom
from protoblade.blade import Blade
def _convert_array_to_list(pts:NDArray)-> List[Tuple]:
    return [tuple(pt) for pt in pts]

class DomainCreator:
    """Class to create a Fluid Domain that can be used in CFD analysis."""

    blade_def : Blade

    def __init__(self,blade_def:Blade):
        """Create the object from a Blade instance."""
        self.blade_def = blade_def

    def extrude_blade(self):
        """Extrude/loft the blade sections to create the main blade."""
        N_sections = self.blade_def.ps_sections.shape[0]

        ps_edges = []
        ss_edges = []
        for i in range(N_sections):
            ss_pts = _convert_array_to_list(self.blade_def.ss_sections[i])
            ss_edges.append(cq.Edge.makeSpline([cq.Vector(p) for p in ss_pts]))

            ps_pts = _convert_array_to_list(self.blade_def.ps_sections[i])
            ps_edges.append(cq.Edge.makeSpline([cq.Vector(p) for p in ps_pts]))

        blade_ss = cq.Solid.makeLoft(
            [cq.Wire.assembleEdges([edge]) for edge in ss_edges]
        )

        blade_ps = cq.Solid.makeLoft(
            [cq.Wire.assembleEdges([edge]) for edge in ps_edges]
        )

        top = cq.Solid.makeLoft(
            [cq.Wire.assembleEdges([edge]) for edge in [ps_edges[0], ss_edges[0]]]
        )

        bottom = cq.Solid.makeLoft(
            [cq.Wire.assembleEdges([edge]) for edge in [ps_edges[-1], ss_edges[-1]]]
        )

        shell = cq.Shell.makeShell([blade_ss.faces(), bottom.faces(), blade_ps.faces(), top.faces()])
        solid = cq.Solid.makeSolid(shell)


        self.blade = solid

    def create_endwalls(self):
        """Create CAD objects for the endwalls."""
        if self.blade_def.endwalls.type == 'fpd':
            hub_pts = _convert_array_to_list(self.blade_def.endwalls.hub)
            shroud_pts = _convert_array_to_list(self.blade_def.endwalls.shroud)

            self.endwalls =  cq.Workplane("XY").spline(hub_pts).polyline([hub_pts[-1], shroud_pts[-1]]).spline(
                shroud_pts[::-1]).polyline(
                [shroud_pts[0], hub_pts[0]]).close().revolve(360.0, self.blade_def.axis[0], self.blade_def.axis[1])
        else:
            self.endwalls = cq.importers.importStep(self.blade_def.endwalls.endwall_fname)

    def export(self,entity:str,fname_out:str)->None:
        """Export an entity from this class to a CAD output format.

        If the entity does not exist in the instance of this class that no export will occur

        Args:
            entity : name of entity to export
            fname_out : output file name with suffix to denote the desired output type


        """
        to_export = getattr(self,entity)
        if to_export:
            cq.exporters.export(to_export, str(fname_out))


    def create_periodic(self):
        """Create a CAD object to represent the periodic fluid domain."""
        z_min = self.endwalls.objects[0].BoundingBox().zmin
        z_max = self.endwalls.objects[0].BoundingBox().zmax

        edges = []

        #calculate radial limits
        r_min_ps = np.min(np.hypot(self.blade_def.ps_sections[0]['x'],self.blade_def.ps_sections[0]['y']))
        r_min_ss = np.min(np.hypot(self.blade_def.ss_sections[0]['x'],self.blade_def.ss_sections[0]['y']))

        endwall_min_r,endwall_max_r = find_radial_extent_of_axisymmetric_object(self.endwalls)

        if r_min_ps > endwall_min_r:
            del_r = endwall_min_r - r_min_ps
            extruded_ps = geom.extrude_radially(self.blade_def.ps_sections[0],1.1*del_r)
            ps_sections = np.concatenate((np.reshape(extruded_ps,(1,extruded_ps.shape[0])),self.blade_def.ps_sections))
        else:
            ps_sections = self.blade_def.ps_sections

        if r_min_ss > endwall_min_r:
            del_r = endwall_min_r - r_min_ss
            extruded_ss = geom.extrude_radially(self.blade_def.ss_sections[0], 1.1 * del_r)
            ss_sections = np.concatenate(
                (np.reshape(extruded_ss, (1, extruded_ss.shape[0])), self.blade_def.ss_sections))
        else:
            ss_sections = self.blade_def.ss_sections

        mid_points = geom.create_midlines(ps_sections,ss_sections,z_min,z_max,self.blade_def.pitch_angle_rad)
        for i in range(len(mid_points)):
            pts = _convert_array_to_list(mid_points[i])
            edges.append(cq.Edge.makeSpline([cq.Vector(p) for p in pts]))

        per = cq.Solid.makeLoft(
            [cq.Wire.assembleEdges([edge]) for edge in edges]
        )

        self.per  = cq.Solid.revolve(per.Faces()[0], -np.rad2deg(self.blade_def.pitch_angle_rad), self.blade_def.axis[0] , self.blade_def.axis[1])


    def create_domain(self):
        """

        Create the full CFD domain.

        This will most likely be quite time consuming as it creates each aspect and then performs Boolean operations
        to create a single solid. T

        """
        self.extrude_blade()
        self.create_endwalls()
        self.create_periodic()

        blade_wp = cq.Workplane("XY").add(self.blade)
        per_wp = cq.Workplane("XY").add(self.per)
        per_and_endwalls = per_wp & self.endwalls
        self.domain = per_and_endwalls - blade_wp


def find_radial_extent_of_axisymmetric_object(input:cq.Workplane)->(float,float):
    """
    Find the radial extent of an axisymmetric object by taking a slice at Y=0 (therefore X=R).

    Args:
        input: cad query Workplane object that contains the object of interest

    Returns:
        (rmin,rmax) , the minimum and maximum radial values respectively

    """
    result2 = \
        input \
            .split(
            cq.Workplane()
            .add(cq.Face
            .makePlane(
                5, 5,
                cq.Vector(0, 0, 0.0),
                cq.Vector(1, 0, 0)))).solids(">>X")

    result3 = \
        result2 \
            .split(
            cq.Workplane()
            .add(cq.Face
            .makePlane(
                5, 5,
                cq.Vector(0, 0, 0.0),
                cq.Vector(0, 1, 0)))).solids("<<Y")

    result4 = result3.faces(">Y")

    bb = result4.objects[0].BoundingBox()
    return (bb.xmin,bb.xmax)