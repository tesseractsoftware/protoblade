.. _EndwallsDef:
Definition of Endwalls
=========================

The :term:`endwalls`, i.e. the bounding walls of the fluid domain, can be defined in two ways. Both of these methods rely on the assumption
of axisymmetric endwalls. The first method is called 'fpd' and the second is called 'step'


FPD Method
------------------------------------

The first method is referred to as the 'fpd' method. If we use a standard `cylindrical co-ordinate system <https://en.wikipedia.org/wiki/Cylindrical_coordinate_system>`_  then the 'fpd' method
defines the hub (low radius) and shroud (high radius) lines as a function of axial and radial co-ordinates on a plane of constant anuglar co-ordinate.
Each line is defined as a :ref:`formatted point data file <FPDFile>`.

An example set of hub and shroud files are given below. These examples feature simple constant radius endwalls each
of which is defined in the y=0 plane. Furthermore, the full configuration file where these examples come from is found in examples/axial_turbine

Example Hub FPD
*******************
.. include:: ../../examples/axial_turbine/hub.fpd
   :literal:

Example Shroud FPD
*******************
.. include:: ../../examples/axial_turbine/shroud.fpd
   :literal:

STEP Method
--------------------------

For the second method a full annulus CAD model in STEP format is provided. In this context the term full annulus
means covering an angular extent from 0 to 360 degrees. The supplied file should contain a single solid entity which
represents the domain for which the blades will be cut from. This method has the advantage that realistic CAD models
which include cavities and other features can be used as the basis for the CFD domain.

An example case that ultilises this method can be found in examples/axial_turbine_with_cavity