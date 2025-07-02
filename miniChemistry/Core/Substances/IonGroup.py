from __future__ import annotations

from miniChemistry.Core.Substances.Particle import Particle
from miniChemistry.Core.Substances.Ion import Ion
from miniChemistry.Core.Substances.Molecule import Molecule
import miniChemistry.Core.Database.ptable as pt
from miniChemistry.Utilities.Checks import charge_check

from typing import Dict


class IonGroup(Particle):
    def __init__(self,
                 cation: Ion,
                 cation_index: int,
                 anion: Ion,
                 anion_index: int
                 ) -> None:

        self._cation = cation
        self._anion = anion
        self._cation_index = cation_index
        self._anion_index = anion_index
        self._charge = self._get_charge()
        self._composition = self._get_composition()

        charge_check([self.charge], neutrality=False, raise_exception=True)
        super().__init__(self.composition, self.charge)

    def __hash__(self):
        return hash(self.formula())

    def _get_composition(self) -> Dict[pt.Element, int]:
        comp = dict()

        for element, index in self._cation.composition.items():
            if comp.get(element) is None:
                comp[element] = index
            else:
                comp[element] += index

        for element, index in self._anion.composition.items():
            if comp.get(element) is None:
                comp[element] = index
            else:
                comp[element] += index

        return comp

    def _get_charge(self) -> int:
        return sum(
            [self._cation.charge * self._cation_index,
             self._anion.charge * self._anion_index]
        )

    def add_cation(self) -> None:
        self._cation_index += 1

    def remove_cation(self) -> None:
        self._cation_index -= 1

    @staticmethod
    def from_string(
            cation_string: str,
            cation_charge: int,
            cation_index: int,
            anion_string: str,
            anion_charge: int,
            anion_index: int
                    ) -> IonGroup:
        cation = Ion.from_string(cation_string, cation_charge)
        anion = Ion.from_string(anion_string, anion_charge)
        return IonGroup(cation, cation_index, anion, anion_index)


    def formula(self,
                remove_charge: bool = False
                ) -> str:

        formula = ''
        formula += Molecule._parentheses(self.cation, self._cation_index)
        formula += Molecule._parentheses(self.anion, self._anion_index)

        if not remove_charge:
            formula += '(' + f'{self.charge}' + ')'

        return formula

    @property
    def cation(self) -> Ion:
        return self._cation

    @property
    def anion(self) -> Ion:
        return self._anion

    @property
    def cation_index(self) -> int:
        return self._cation_index

    @property
    def anion_index(self) -> int:
        return self._anion_index
