"""A set of functions and classes to handle represent a turbomachinery stage."""
from __future__ import annotations

import numpy as np
from atom.api import Atom, Int,List,Enum,Str,Typed,Property,Float,Tuple,Instance
from atom.atom import Atom
from atom.enum import Enum
from atom.scalars import Str
from atom.typed import Typed
from protoblade import geom
from .blade import Blade

ENDWALL_TYPES = ['fpd','step']

class Endwalls(Atom):
    """Hold objects required to define endwalls."""

    hub = Typed(np.ndarray)
    shroud = Typed(np.ndarray)
    type= Enum(*ENDWALL_TYPES)

    step_fname = Str()
    hub_fname = Str()
    shroud_fname = Str()

    @classmethod
    def from_config(cls,config:dict) -> Endwalls:
        if config['type'] not in ENDWALL_TYPES:
            raise ValueError('Invalid endwall type')

        endwall = Endwalls()
        endwall.type = config['type']

        endwall.hub =  geom.load_curves_from_fpd(config['hub_fname']) if config['type'] == 'fpd' else None
        endwall.shroud =  geom.load_curves_from_fpd(config['shroud_fname']) if config['type'] == 'fpd' else None

        endwall.step_fname = config.get('step_fname','')

        return endwall




class Stage(Atom):
    name = Str()
    blades = List(Blade)
    endwalls = Instance(Endwalls)

    @classmethod
    def from_config(
            cls,
            name,
            endwall_config,
            blade_config,
        ):
        stage = Stage()
        stage.name = name
        stage.endwalls = Endwalls.from_config(endwall_config)
        stage.blades = [Blade.from_config(config) for config in blade_config]
        return stage
