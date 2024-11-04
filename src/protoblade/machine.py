"""A set of functions and classes to handle represent a turbomachinery machine."""
from __future__ import annotations
from atom.api import Atom, Int, List, Enum, Str, Typed, Property, Float, Tuple
from .stage import Stage

import tomli

UNITS = ['metres', 'millimetres']


class Machine(Atom):
    name = Str()
    n_blade = Int()
    units = Enum(*UNITS)
    axis = Tuple(Tuple(float))
    stages = List(Stage)

    @classmethod
    def from_config_file(cls, fname: str) -> Machine:
        """Create instance of class from a toml file."""
        config = _read_toml(fname)

        stages_config = config.pop('stage')
        machine = cls(**config['machine'])
        stages = []
        for stage in stages_config:
            stages.append(Stage.from_config(stage['name'], stage['endwall'][0], stage['blade_section']))
        machine.stages = stages
        return machine


def _read_toml(fname: str) -> dict:
    """Read a toml configuration file."""
    with open(fname, mode="rb") as fp:
        config = tomli.load(fp)
    config['machine']['axis'] = tuple([tuple(x) for x in config['machine']['axis']])
    return config
