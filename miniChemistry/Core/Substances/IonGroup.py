from __future__ import annotations

from miniChemistry.Core.Substances.Particle import Particle
from miniChemistry.Core.Substances.Ion import Ion
from miniChemistry.Core.Substances.Molecule import Molecule
import miniChemistry.Core.Database.ptable as pt
from miniChemistry.MiniChemistryException import NotSupposedToHappen
from miniChemistry.Utilities.Checks import charge_check

from typing import Dict, Literal, Tuple, Optional


class IonGroup(Particle):
    def __init__(self,
                 ion: Ion,
                 cation_index: int,
                 anion_index: int
                 ) -> None:

        # only acids and bases are capable of partial dissociation, hence when first ion is given, another one is known.
        self._type: Literal['acid', 'base']  # is assigned in _get_missing_ion
        self._cation, self._anion = self._get_missing_ion(ion)

        self._cation_index = cation_index
        self._anion_index = anion_index
        self._charge = self._get_charge()
        self._composition = self._get_composition()

        charge_check([self.charge], neutrality=False, raise_exception=True)
        super().__init__(self.composition, self.charge, _secc_disable=True)

    def __hash__(self):
        return hash(self.formula())

    def _get_missing_ion(self, ion: Ion) -> Tuple[Ion, Ion]:
        if ion.is_cation:
            self._type = 'base'
            return ion, Ion.hydroxide
        elif ion.is_anion:
            self._type = 'acid'
            return Ion.proton, ion
        else:
            nsth = NotSupposedToHappen(variables=locals())
            nsth.description += f'\nAn ion with formula {ion.formula()} is neither a cation, nor an anion.\nUsed .is_cation and .is_anion properties.'
            raise nsth

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

    @staticmethod
    def from_string(
            ion_string: str,
            ion_charge: int,
            cation_index: int,
            anion_index: int,
    ) -> IonGroup:

        ion = Ion.from_string(ion_string, ion_charge)
        return IonGroup(ion, cation_index, anion_index)


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
    def ion(self) -> Ion:
        if self._type == 'acid':
            return self.anion
        elif self._type == 'base':
            return self.cation
        else:
            nsth = NotSupposedToHappen(variables=locals())
            nsth.description += f'\nType of IonGroup {self.formula()} is neither acid, not base.'
            raise nsth

    @property
    def index(self) -> int:
        if self._type == 'acid':
            return self.cation_index
        elif self._type == 'base':
            return self.anion_index
        else:
            nsth = NotSupposedToHappen(variables=locals())
            nsth.description += f'\nType of IonGroup {self.formula()} is neither acid, not base.'
            raise nsth

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

    @property
    def charge(self) -> int:
        return self._get_charge()

    @property
    def is_cation(self) -> bool:
        return self.charge > 0

    @property
    def is_anion(self) -> bool:
        return self.charge < 0
