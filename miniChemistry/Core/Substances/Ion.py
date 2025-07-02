from __future__ import annotations

from miniChemistry.Core.CoreExceptions.stableExceptions import IonNotFound
from miniChemistry.Core.CoreExceptions.ptableExceptions import Pt_ElementNotFound
from miniChemistry.Core.CoreExceptions.SubstanceExceptions import Sub_ElementNotFound
from miniChemistry.Core.Substances.Particle import Particle
from miniChemistry.Core.Substances._SpecialAttribute import _SpecialSubstance
import miniChemistry.Core.Database.ptable as pt
from miniChemistry.Core.Substances._helpers import _string_to_elementary_composition, _exists
from miniChemistry.Utilities.Checks import charge_check, type_check

from typing import Dict
from chemparse import parse_formula


class Ion(Particle):
    """
    An ion is a particle that has nonzero charge. As charge can be positive and negative, we can divide ions by whether
    they are positively or negatively charged. The first ones are called cations, the second ones – anions.

    There are three special ions that are also made special attributes in this code. Those are proton (or positively
    charged hydrogen), hydroxide (negatively charged OH particle), and oxygen (negatively charged oxygen atom, O(-2)).
    These three ions define a class of Molecule's instance if they are present in a molecule.
    """

    proton = _SpecialSubstance(None, name='proton')
    hydroxide = _SpecialSubstance(None, name='hydroxide')
    oxygen = _SpecialSubstance(None, name='oxygen')

    def __init__(self, composition: Dict[pt.Element, int], charge: int) -> None:
        charge_check([charge], neutrality=False, raise_exception=True)
        super().__init__(composition, charge)

    def __hash__(self):
        return hash(self.formula(remove_charge=False))

    @classmethod
    def create_special_ions(cls) -> None:
        cls.proton = Ion({pt.H: 1}, 1)
        cls.hydroxide = Ion({pt.O: 1, pt.H: 1}, -1)
        cls.oxygen = Ion({pt.O: 1}, -2)

    @staticmethod
    def from_string(string: str, charge: int, database_check: bool = True) -> Ion:
        type_check([string, charge, database_check], [str, int, bool],
                   strict_order=True, raise_exception=True)

        all_elements = None
        try:
            string_composition = parse_formula(string)
            all_elements = tuple(string_composition.keys())
            elementary_composition = _string_to_elementary_composition(string_composition)
            i = Ion(elementary_composition, charge)
        except Pt_ElementNotFound:  # i.e. element is not present in the Periodic Table. Raised by Element.get_by_symbol
            not_present_elements = list()
            for element in all_elements:
                if element not in pt.TABLE_STR:
                    not_present_elements.append(element)
            raise Sub_ElementNotFound(f'Element(s) with symbols {", ".join(not_present_elements)} are not found.',
                                      variables=locals())

        if database_check and not _exists(i):
            raise IonNotFound(ion_signature=[i.formula(remove_charge=False)], variables=locals())

        return i

    def formula(self, remove_charge: bool = False) -> str:
        formula = ''

        for element, index in self._composition.items():
            formula += element.symbol + (str(index) if not index == 1 else '')
        if not remove_charge:
            formula += '(' + str(self.charge) + ')'

        return formula

    @property
    def is_cation(self) -> bool:
        return self.charge > 0

    @property
    def is_anion(self) -> bool:
        return self.charge < 0
