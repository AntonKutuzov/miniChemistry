from __future__ import annotations

from miniChemistry.Core.Substances.Particle import Particle
from miniChemistry.Core.Substances.Ion import Ion
from miniChemistry.Core.Substances._SpecialAttribute import _SpecialSubstance
import miniChemistry.Core.Database.ptable as pt
from miniChemistry.Utilities.Checks import charge_check, type_check
from miniChemistry.MiniChemistryException import NotSupposedToHappen

from typing import Dict, Tuple


class Molecule(Particle):
    """
    Molecule in this package always consists of two ions – positive and negative, called respectively cation and anion.
    Hence, to initiate the Molecule instance, it is enough to provide two ions. A Molecule should always be electrically
    neutral (have a zero charge), so a charge_check() function is used to ensure that two ions cancel each other's
    charge (this function raises an exception if, for example, two positive ions are passed to the constructor).

    Knowing that molecules consist of two ions, we can create a simple classification method. There are four main
    substance classes in chemistry – acids, bases, oxides and salts. In this module
    ACIDS are Molecules with cation equal to Simple.proton.
    BASES are Molecules with anion equal to Simple.hydroxide.
    OXIDES are Molecules with anion equal to Simple.oxygen.
    SALT are all other Molecules.

    These classes will be necessary when we will come to prediction of chemical reactions.
    """

    water = _SpecialSubstance(None, name='water')

    def __init__(self, cation: Ion, anion: Ion) -> None:
        self._cation = cation
        self._anion = anion
        self._cation_index, self._anion_index = self._indices(cation, anion)

        charge_check([cation.charge * self.cation_index, anion.charge * self.anion_index],
                     neutrality=True, raise_exception=True)

        super().__init__(self.composition, 0)

    def __hash__(self):
        return hash(self.formula())

    @classmethod
    def create_special_molecules(cls) -> None:
        """NOTE: if you try to call this method before you called Ion.create_special_ions() you will get an error."""
        cls.water = Molecule(Ion.proton, Ion.hydroxide)

    def _indices(self, cation: Ion, anion: Ion) -> Tuple[int, int]:
        """
        Determines the indices of each ion in a molecule. The key principle here is the rule that any molecule must be
        electrically neutral, i.e. must have a zero charge. Hence, if our molecule consists of two ions X(+n) and Y(-m),
        we need to find such two numbers a and b for which
        an + b(-m) = 0
        With a, b being whole positive numbers.
        As you can guess, the numbers a and b are indices for each ion, i.e. the molecule will look at the end like
        XaYb with a and b denoting the amount of ions X and Y respectively (same as number 2 in Ca(OH)2 means that there
        are 2 OH(-) ions).

        To do this we find the least common multiple of both charges (their absolute values) and then divide the lcm
        by the absolute values of the charges. What we get at the end are two natural numbers representing the indices
        for ions.

        :param cation: positively charged ion (Ion instance with positive charge)
        :param anion: negatively charged ion
        :return: tuple of integers with cation's index first and anion's index second
        """

        from math import lcm

        cation_charge = abs(cation.charge)
        anion_charge = abs(anion.charge)

        n = lcm(cation_charge, anion_charge)  # least common multiple

        cation_index = int(n / cation_charge)  # the expression in the int() should always yield a whole number
        anion_index = int(n / anion_charge)

        return cation_index, anion_index

    @staticmethod
    def from_string(cation_string: str, cation_charge: int, anion_string: str, anion_charge: int,
                    database_check: bool = True) -> Molecule:
        """
        Creates a Molecule's instance from strings.

        :param cation_string: formula of cation without charge.
        :param cation_charge: charge of the cation.
        :param anion_string: formula of anion without charge.
        :param anion_charge: charge of the anion.
        :param database_check: True if ions should be checked in the SolubilityTable database.
        :return: an instance of Molecule
        """

        type_check([cation_string, cation_charge, anion_string, anion_charge, database_check],
                   [str, int, str, int, bool], strict_order=True, raise_exception=True)
        cation_particle = Ion.from_string(cation_string, cation_charge, database_check)
        anion_particle = Ion.from_string(anion_string, anion_charge, database_check)
        return Molecule(cation_particle, anion_particle)

    @staticmethod
    def _parentheses(i: Ion, index: int) -> str:
        """
        The logic here is quite simple. If an ion consists of only one element, we just append this number (index)
        after the element's symbol into the formula. If the ion consists of more than one element, we need to
        take the elements in parentheses and then put the index.

        Finally, if the index itself is equal to 1, we don't put it there, so we just append the ion's formula.

        :param i:
        :param index:
        :return:
        """

        if index > 1:
            if i.size > 1:
                return '(' + i.formula(remove_charge=True) + ')' + str(index)
            else:
                return i.formula(remove_charge=True) + str(index)
        elif index == 1:
            return i.formula(remove_charge=True)
        else:
            nsth = NotSupposedToHappen(variables=locals())
            nsth.description += (f'\n\nIndex of one of the ions used to create a molecule is less than 1, which \n'
                             f'normally is not possible.')
            raise nsth

    def formula(self) -> str:
        """
        Assembles a formula of a molecule from formulas of the two ions used to build it. The function includes an
        inner function called modification() that assembles appropriate string for addition to formula string.

        NOTE: since water is a very common compound, and consists of two ions – H(+) and OH(-) – technically it should
        have a formula of HOH (ion H plus ion OH), however the actual formula is H2O.
        NOTE 2: water is a good example that is both ions contain the same elements (which is a rare case, but still)
        they won't be written together (as H2 in H2O), but separately (as it would have been in HOH).

        :return:
        """

        if self == Molecule.water:
            return 'H2O'

        formula = ''
        formula += self._parentheses(self.cation, self.cation_index)
        formula += self._parentheses(self.anion, self.anion_index)
        return formula

    @property
    def simple_class(self) -> str:
        """
        Returns simple class of a molecule based on its composition. More about classes and subclasses of Molecule
        instances can be read in description of the class.

        NOTE: water is special here again, because it is indeed an oxide, but the conditions imposed here for acids and
        hydroxides will return True for water as well. This is normal and explains by chemistry (this is not the code's
        mistake or error due to simplification).

        :return:
        """

        if self == Molecule.water:
            return 'oxide'

        elif self.cation == Ion.proton:
            return 'acid'
        elif self.anion == Ion.hydroxide:
            return 'base'
        elif self.anion == Ion.oxygen:
            return 'oxide'
        else:
            return 'salt'

    @property
    def simple_subclass(self) -> str:
        if self == Molecule.water:
            return 'amphoteric oxide'

        if self.simple_class == 'oxide':
            for element in self.elements:
                if not element == pt.O and element in pt.METALS and self._cation.charge < 4:
                    return 'basic oxide'
                elif not element == pt.O and element in pt.METALS and 4 < self._cation.charge < 6:
                    return 'amphoteric oxide'
                elif not element == pt.O and element in pt.METALS and self._cation.charge > 5:
                    return 'acidic oxide'
                elif not element == pt.O and element not in pt.METALS:
                    return 'acidic oxide'
        else:
            return self.simple_class

    @staticmethod
    def acid(anion: Ion) -> Molecule:
        type_check([anion], [Ion], raise_exception=True)
        return Molecule(Ion.proton, anion)

    @staticmethod
    def base(cation: Ion) -> Molecule:
        type_check([cation], [Ion], raise_exception=True)
        return Molecule(cation, Ion.hydroxide)

    @staticmethod
    def oxide(cation: Ion) -> Molecule:
        type_check([cation], [Ion], raise_exception=True)
        return Molecule(cation, Ion.oxygen)

    @property
    def composition(self) -> Dict[pt.Element, int]:
        """Assembles composition of a molecule from composition of individual ions. Since each ion has an index, AND
        every element has an index within a given ion, the total number of atoms of a certain element is given by a
        multiple of both indices."""

        def update_composition(i: Ion, ion_ind: int, com: dict) -> Dict[pt.Element, int]:
            for el, ind in i.composition.items():
                if el in com:
                    com[el] += ind * ion_ind  # this is addition (+=)
                else:
                    com[el] = ind * ion_ind  # this is assigning (=)
            return com

        composition = dict()
        composition = update_composition(self.cation, self.cation_index, composition)
        composition = update_composition(self.anion, self.anion_index, composition)
        return composition

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
