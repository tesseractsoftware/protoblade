Usage
====================
After installing ProtoBlade you will be to able to run it from a terminal.

.. code:: bash

    protoblade example.toml

Where example.toml if the filepath of the file you wish to process.

Full details of the command line interface are given below.

.. argparse::
   :module: protoblade.cli
   :func: create_parser
   :prog: protoblade