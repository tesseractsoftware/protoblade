.. _SectionDef:

Definition of Blade Sections
===============================

.. _FPDFile:
Formatted Point Data File
------------------------------
Blade sections are defined in Formatted Point Data (FPD) files. The header for these file should be  two space-delimited integers :  |Npoints| and |Nsections|. |Npoints| is the number of points per section (and this must be constant for each section within the file) and |Nsections| is the number of sections contained within the file. The lines after the header must take the form of three space delimited floating point numbers which represent the X,Y and Z coordinates of each point for the section.

So for example, if the header was '100 1' then the file would contain  a single section which consints of 100 lines. Lines 2-101 in this file would then contain the X, Y and Z co-ordinates for the section.
If the head was '100 3' then the file should contain 301 lines : 2-101 are the first section, 102-201 the second section and 202-301 the third section.

An example FPD file is shown below (|Npoints| is 66 and |Nsections|  is 1):

.. include:: ../../tests/fixtures/naca0012/naca0012_lower.fpd
   :literal:


Section Definition
----------------------------------

A section is defined as a constant :term:`span` or constant radius profile. For an axial machine it is best to define each section at a constant radius where as for a radial machine it is best to define a section at constant span. Within an FPD file sections should be defined with the lowest radius/span section first.

Sections can be split into two surfaces and generally these are the :term:`pressure surface` and :term:`suction surface`. The figure below shows a section of a turbine blade with the pressure and suction surfaces split at the leading and trailing edges. Each section should start at the leading edge and finish at the trailing edge.

.. image:: _static/auto_gen/vki.png

Using FPD files it is possible to define multiple sections in one file or just a single section.

.. |Npoints| replace:: :math:`N_{points}`
.. |Nsections| replace:: :math:`N_{sections}`
