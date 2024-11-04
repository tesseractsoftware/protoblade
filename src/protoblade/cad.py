"""Module with classes and functions to create CAD models from protoblade classes."""
import cadquery
from numpy.typing import NDArray
from typing import Tuple,List, Literal
import numpy as np
from  protoblade import  geom, stage
from protoblade.blade import Blade
def _convert_array_to_list(pts:NDArray)-> List[Tuple]:
    return [tuple(pt) for pt in pts]

class DomainCreator:
    """Class to create a Fluid Domain that can be used in CFD analysis."""

    blade_def : Blade

    def __init__(self,
                 blade_def:Blade,
                 endwalls:stage.Endwalls,
                 units:str,
                 axis:tuple,
                 cq=cadquery
                 ):
        """Create the object from a Stage instance."""
        #TODO : probaly want this to be a stage rather than blade - actually maybe not?
        self.blade_def = blade_def
        self.endwalls = endwalls
        self.units = units
        self.axis = axis
        #TODO: add function to cut domain at a given location
        self._cq = cq # add cadquery as an object to allow for test mock to be easily added

    def extrude_blade(self):
        """Extrude/loft the blade sections to create the main blade."""
        N_sections = self.blade_def.ps_sections.shape[0]

        ps_edges = []
        ss_edges = []
        for i in range(N_sections):
            ss_pts = _convert_array_to_list(self.blade_def.ss_sections[i])
            ss_edges.append(self._cq.Edge.makeSpline([self._cq.Vector(p) for p in ss_pts]))

            ps_pts = _convert_array_to_list(self.blade_def.ps_sections[i])
            ps_edges.append(self._cq.Edge.makeSpline([self._cq.Vector(p) for p in ps_pts]))

        blade_ss = self._cq.Solid.makeLoft(
            [self._cq.Wire.assembleEdges([edge]) for edge in ss_edges]
        )

        blade_ps = self._cq.Solid.makeLoft(
            [self._cq.Wire.assembleEdges([edge]) for edge in ps_edges]
        )

        top = self._cq.Solid.makeLoft(
            [self._cq.Wire.assembleEdges([edge]) for edge in [ps_edges[0], ss_edges[0]]]
        )

        bottom = self._cq.Solid.makeLoft(
            [self._cq.Wire.assembleEdges([edge]) for edge in [ps_edges[-1], ss_edges[-1]]]
        )

        shell = self._cq.Shell.makeShell([blade_ss.faces(), bottom.faces(), blade_ps.faces(), top.faces()])
        solid = self._cq.Solid.makeSolid(shell)


        self.blade = solid

    def create_endwalls(self):
        """Create CAD objects for the endwalls."""
        if self.endwalls.type == 'fpd':
            hub_pts = _convert_array_to_list(self.endwalls.hub)
            shroud_pts = _convert_array_to_list(self.endwalls.shroud)

            self.cad_endwalls =  self._cq.Workplane("XY").spline(hub_pts).polyline([hub_pts[-1], shroud_pts[-1]]).spline(
                shroud_pts[::-1]).polyline(
                [shroud_pts[0], hub_pts[0]]).close().revolve(360.0, self.axis[0], self.axis[1])
        else:
            self.cad_endwalls = self._cq.importers.importStep(self.endwalls.step_fname)

    def export(self,entity:str,fname_out:str)->None:
        """Export an entity from this class to a CAD output format.

        If the entity does not exist in the instance of this class that no export will occur

        Args:
            entity : name of entity to export
            fname_out : output file name with suffix to denote the desired output type


        """
        to_export = getattr(self,entity)
        if to_export:
            self._cq.exporters.export(to_export, str(fname_out))


    def create_periodic(self):
        """Create a CAD object to represent the periodic fluid domain."""
        z_min = self.cad_endwalls.objects[0].BoundingBox().zmin
        z_max = self.cad_endwalls.objects[0].BoundingBox().zmax

        edges = []

        #calculate radial limits
        r_min_ps = np.min(np.hypot(self.blade_def.ps_sections[0]['x'],self.blade_def.ps_sections[0]['y']))
        r_min_ss = np.min(np.hypot(self.blade_def.ss_sections[0]['x'],self.blade_def.ss_sections[0]['y']))

        endwall_min_r,endwall_max_r = find_radial_extent_of_axisymmetric_object(self.cad_endwalls)

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
            edges.append(self._cq.Edge.makeSpline([self._cq.Vector(p) for p in pts]))

        per = self._cq.Solid.makeLoft(
            [self._cq.Wire.assembleEdges([edge]) for edge in edges]
        )

        self.per  = self._cq.Solid.revolve(per.Faces()[0], -np.rad2deg(self.blade_def.pitch_angle_rad), self.axis[0] , self.axis[1])


    def create_domain(self):
        """

        Create the full CFD domain.

        This will most likely be quite time consuming as it creates each aspect and then performs Boolean operations
        to create a single solid. T

        """
        self.extrude_blade()
        self.create_endwalls()
        self.create_periodic()

        blade_wp = self._cq.Workplane("XY").add(self.blade)
        per_wp = self._cq.Workplane("XY").add(self.per)
        per_and_endwalls = per_wp & self.cad_endwalls
        self.domain = per_and_endwalls - blade_wp


def find_radial_extent_of_axisymmetric_object(input:cadquery.Workplane)->(float,float):
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
            cadquery.Workplane()
            .add(cadquery.Face
            .makePlane(
                5, 5,
                cadquery.Vector(0, 0, 0.0),
                cadquery.Vector(1, 0, 0)))).solids(">>X")

    result3 = \
        result2 \
            .split(
            cadquery.Workplane()
            .add(cadquery.Face
            .makePlane(
                5, 5,
                cadquery.Vector(0, 0, 0.0),
                cadquery.Vector(0, 1, 0)))).solids("<<Y")

    result4 = result3.faces(">Y")

    bb = result4.objects[0].BoundingBox()
    return (bb.xmin,bb.xmax)