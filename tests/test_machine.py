from protoblade import machine
import numpy as np

def test_read_blade_configs(example_machine_configs,mocker):

    #TODO: add a fixture with multiple stages and multiple blade sections
    mocker.patch('protoblade.geom.load_curves_from_fpd',return_value=np.zeros(10))

    for config in example_machine_configs:
        obj = machine._read_toml(config)
        machine.Machine.from_config_file(config)
