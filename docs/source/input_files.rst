Input Files
===================================

There are three types of files that are required to create a CFD-ready geometry:

* Configuration file or TOML file (extension .toml)
* Blade section files (extension of .fpd)
* Endwall definition files (extension of either .fpd or .step )

Configuration File
----------------------------------------------

This file is a project/configuration file that coordinates the entire process. It defines high-level setting used by
Protoblade as well as specifying the filenames and options to used for the blade and endwall sections.

This is formatted using `TOML <https://toml.io/en/>`_  and is split into logical sections. The majority of sections are defined
using the Table TOML structure. These are a set of key-value pairs. Moreover, the input file makes use of array tables to allow for multiple stage machines.
For completeness an example TOML file is shown at the end of this section.


Example Configuration File
----------------------------------------------

.. include:: ../../tests/fixtures/example_blade_config.toml
   :literal:

Machine
************************

These settings are at the highest level and apply to the whole machine that is being modelled, i.e. all stages and all blade sections.

* name - A human readable name used to identify this geometry. This name will be used as the base filename when exporting CAD files
* units - The units of all input files (section and endwall)  and the units of the final CAD model output. Valid options are 'metres' or 'millimetres'
* axis - Two points which define the axis of rotation. This defined in the form [ [X1,Y1,Z1], [X2,Y2,Z2] ].

Stage
*****************************

Each machine is comprised of stages, and each stage is comprised of multiple blade sections. Following the TOML specification stages are defined as an array of tables.
Working in this ways means a single configuration file can be used to specify a multistage machine with multiple blade sections within in each stage.
A typical use case would be a single stage with two sections, e.g. a stator and a rotor.  Endwalls are defined at a stage level i.e. a separate endwall file is required for each stage.

* name - A unique name for this stage.

Endwall
^^^^^^^^^^^^^^^^^^^^^^^^^^

This subsection defines the endwall that is used for a given stage.

* endwall_type. The type of endwall to be used. Set to 'fpd' to use a fpd to define the endwalls or 'step' to use a cad file.

If endwall_type is 'fpd' then an additional two variables must be defined :

* hub_fname - the file name of the fpd file to be used for the hub (relative to TOML file)
* shroud_fname - the file name of the fpd file to be used for the shroud (relative to TOML file)

If the endwall type is 'step' then an additional variable must be defined:

* endwall_fname - The filename of the CAD file which defines the endwall geometry (filepath relative to the TOML file location)

Blade Sections
***************************

A blade section is where the main blade geometry is defined. The settings outlined below will apply to each individual section.

* name - Identifying name for this blade section. It must be unique within the stage context, but can be duplicated in other stages.
* n_blade  - The number of blades which make a full annulus.
* ps_section_name - The name of the fpd file to be used for the pressure surface (filepath relative to TOML file location)
* ss_section_name - The name of the fpd file to be used for the suction surface (file[ath ]relative to TOML file location)
* interface_location - The location in metres for the axial interface between this current section and the downstream section.
  If there is only a single section then this can be left empty.







Blade Section Files
--------------------------------------------

These are the files that define the blade geometry, see :ref:`this section for a more detailed overview <SectionDef>`.

Endwall defintion files
----------------------------------------
These are the files that define the :term:`endwalls` for the geometry, see :ref:`this section for a more detailed overview <EndwallsDef>`.
