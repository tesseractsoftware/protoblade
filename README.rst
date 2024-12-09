|docs| |codecov|

.. |codecov| image:: https://codecov.io/gh/tesseractsoftware/protoblade/graph/badge.svg?token=YZHI6F7OS1 
    :target: https://codecov.io/gh/tesseractsoftware/protoblade

.. |docs|  image:: https://readthedocs.org/projects/protoblade/badge/?version=latest
    :target: https://protoblade.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


.. image:: https://github.com/tesseractsoftware/protoblade/blob/main/docs/source/_static/turbine.png
   :width: 200


ProtoBlade
=================================

ProtoBlade is an open source turbomachinery design tool for creating CFD-compatible 3D CAD models. This tool is intended for use when
creating multiple prototypes (hence Proto) of turbomachinery blades (hence Blade). 3D CAD models can be created in a 'batch'
style situation which can integrated into automated unstructured meshing pipelines.

What Does ProtoBlade Do?
===================================================

ProtoBlade can automatically create CFD ready CAD models from a blade definition. A turbine example with constant radius endwalls is shown below. Three sections are supplied at three different radii (shown as points on the animation below). The final product is a CAD model of the fluid domain complete with periodic boundary faces. This could be used as the input for an unstructured meshing pipeline. For more information see examples\\axial_turbine.

.. image:: https://github.com/tesseractsoftware/protoblade/blob/main/docs/source/_static/point_to_cad.gif
   :width: 900

It is also possible to create a CFD ready CAD model from endwalls supplied as a CAD file. The example below again shows a turbine defined with three radial sections (shown as points) but this time the endwalls are defined from a CAD file and feature a cavity upstream of the blade. The output is a CFD ready CAD model complete with periodic faces. For more information see examples\\axial_turbine_with_cavity. 

.. image:: https://github.com/tesseractsoftware/protoblade/blob/main/docs/source/_static/point_to_cad_cavity.gif
   :width: 900


Why Use ProtoBlade?
=============================

ProtoBlade is open source.
----------------------------------------------------
You are free to create a fork of the project and distribute this package within your own application or design pipeline.

ProtoBlade is easy to deploy
-------------------------------------------------------

ProtoBlade is hosted on PyPI like any other Python package, or it can be installed using a pre-built installer. It can be installed and deployed using pip on any system that has a Python Interpreter of version 3.7 or higher.
Most other CAD scripting and automation tools are pinned to a certain application or Python Environment.


ProtoBlade is functional
-----------------------------------------------------

All of the ProtoBlade functionality can be accessed through the command line interface or through the Python API.


Quick Start
=========================================
Full details of how to install and use ProtoBlade are given in the docs. A quick start is outlined below.

First, create a new virtual environment an then activate it. Once this is done use pip to install ProtoBlade:

.. code:: bash

    pip install protoblade


After installing ProtoBlade you will be to able to run it from a terminal.

.. code:: bash

    python -m protoblade example.toml

Where example.toml if the filepath of the file you wish to process. The output of this process will be a a step file axial_turbine.step. This will be a 3D solid body CAD model of the turbine blade including periodic surfaces. See the animation above. 


Documentation 
================================================

Documentation for ProtoBlade can be found `here <https://protoblade.readthedocs.io/en/latest/>`_ 

Support
==================================================

Any questions, queries or features requests can be sent to support@tesseractsoftware.co.uk

Image Credit
==================================
`Turbine icons created by Freepik - Flaticon <https://www.flaticon.com/free-icons/turbine>`_
