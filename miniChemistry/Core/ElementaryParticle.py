from __future__ import annotations
from typing import Literal


class ElementaryParticle:
    _MASS_Da = 1.660_539_068E-27  # kg

    def __init__(self,
                 *,
                 name: str,
                 symbol: str,
                 charge: int,
                 mass_Da: float = None
                 ) -> None:
        self._name = name
        self._symbol = symbol
        self._charge = charge
        self._mass_Da = mass_Da
        self._mass_kg = mass_Da * ElementaryParticle._MASS_Da

    def __eq__(self, other: ElementaryParticle):
        return self.formula() == other.formula()

    def __str__(self):
        return f"{self._symbol}({self._charge})"

    def __hash__(self):
        return hash(self.__str__())

    @staticmethod
    def from_string(string: str) -> ElementaryParticle:
        match string:
            case 'e':
                return Electron
            case 'p':
                return Proton
            case 'n':
                return Neutron
            case _:
                raise ValueError(f'Invalid ElementaryParticle symbol: {string}.')

    def mass(self,
             units: Literal['kg', 'u', 'Da']
             ) -> float:

        match units:
            case 'kg':
                return self._mass_kg
            case 'u'|'Da':
                return self._mass_Da
            case _:
                raise Exception(f'Unsupported unit: {units}.')

    def formula(self) -> str:  # needed for compatibility with Reaction class
        return self.__str__()

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def charge(self) -> int:
        return self._charge


Electron = e = ElementaryParticle(name="electron", symbol="e", charge=-1, mass_Da=0.00055)
Proton = p = ElementaryParticle(name="proton", symbol="p", charge=1, mass_Da=1.00728)
Neutron = n = ElementaryParticle(name="neutron", symbol="n", charge=0, mass_Da=1.00867)
