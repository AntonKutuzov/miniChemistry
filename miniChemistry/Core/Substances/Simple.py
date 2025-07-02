from __future__ import annotations

from miniChemistry.Core.Substances.Particle import Particle
from miniChemistry.Core.Substances._SpecialAttribute import _SpecialSubstance
import miniChemistry.Core.Database.ptable as pt
from miniChemistry.Core.Substances._helpers import _string_to_elementary_composition
from miniChemistry.MiniChemistryException import NotSupposedToHappen
from miniChemistry.Utilities.Checks import type_check
from miniChemistry.Core.CoreExceptions.SubstanceExceptions import UnsupportedSubstanceSize

from chemparse import parse_formula


class Simple(Particle):
    """
    A Simple class describes a molecule (group of atoms) that consists of atoms of only one chemical element. This can
    be a single atom, representing a Simple substance (in our case that means that we can get its formula, which will
    be equivalent to its element's symbol and get some other properties of a particle, not element), or it can be a
    group of similar atoms, such as oxygen O2 or O3, chlorine Cl2, etc. Usually, in school chemistry we have 6
    simple substances that consist of two atoms. They all are listed in the cls.specials attribute.

    Since Simple consists of one chemical element, the two main properties are:
    - _element: pt.Element
    - _index: int
    Note that charge of Simples (as well as Molecules) is always zero.

    Also, since Simple and Molecule can build a real substance, we can classify them. For Simple substances we have
    two classes – metals and nonmetals. The class of a Simple substance is determined by what tuple an element of a
    Simple substance belongs to (pt.METALS or pt.NONMETALS). This classification, as well as Molecule's classification,
    will be important when we come to chemical reactions.
    """

    hydrogen = _SpecialSubstance(None, name='hydrogen')
    fluorine = _SpecialSubstance(None, name='fluorine')
    chlorine = _SpecialSubstance(None, name='chlorine')
    bromine = _SpecialSubstance(None, name='bromine')
    iodine = _SpecialSubstance(None, name='iodine')

    nitrogen = _SpecialSubstance(None, name='nitrogen')
    oxygen = _SpecialSubstance(None, name='oxygen')

    specials = _SpecialSubstance(None, name='specials')  # tuple of all the mentioned simples

    empty = _SpecialSubstance(None, name='empty')

    def __init__(self, element: pt.Element, index: int) -> None:
        composition = {element: index}

        self._element = element
        self._index = index

        super().__init__(composition, 0)

    def __hash__(self):
        return hash(self.formula())

    @classmethod
    def create_special_simples(cls) -> None:
        cls.hydrogen = Simple(pt.H, 2)
        cls.fluorine = Simple(pt.F, 2)
        cls.chlorine = Simple(pt.Cl, 2)
        cls.bromine = Simple(pt.Br, 2)
        cls.iodine = Simple(pt.I, 2)
        cls.nitrogen = Simple(pt.N, 2)
        cls.oxygen = Simple(pt.O, 2)
        cls.specials = (cls.hydrogen, cls.chlorine, cls.nitrogen, cls.oxygen, cls.bromine, cls.iodine)

        cls.empty = Simple(pt.Element('Ee', 'empty element', 0, 0, '0A', 0, 0), 0)

    @staticmethod
    def from_string(string: str) -> Simple:
        """
        Is a customized version of the Particle.from_string. Passing multi-element formulas here will cause an
        exception in "s = simple(p)".
        :param string: formula of a simple substance.
        :return: Simple's instance.
        """

        type_check([string], [str], raise_exception=True)
        string_composition = parse_formula(string)

        if len(string_composition) > 1:
            raise UnsupportedSubstanceSize(string_composition, 'Simple.from_string', variables=locals())
        else:
            elementary_composition = _string_to_elementary_composition(string_composition)
            element, index = tuple(elementary_composition.items())[0]  # .items is actually a list of key-value pairs
            return Simple(element, index)

    def formula(self) -> str:
        return self.element.symbol + (str(self.index) if self.index != 1 else '')

    @property
    def simple_class(self) -> str:
        """
        All Simple substances can be divided according to whether they are created by metallic or nonmetallic elements.
        To check this we check is the element of the Simple's instance belongs to pt.METALS or pt.NONMETALS and return
        the corresponding string.
        :return: string, either 'metal' for metallic elements or 'nonmetal' for nonmetallic elements.
        """
        if self.element in pt.METALS:
            return 'metal'
        elif self.element in pt.NONMETALS:
            return 'nonmetal'
        else:
            nsth = NotSupposedToHappen(variables=locals())
            nsth.description += (f'\nThis is exactly the case here – an element "{self.element}" belongs to neither\n'
                                 f'pt.METALS, not pt.NONMETALS, which normally is not possible.')
            raise nsth

    @property
    def simple_subclass(self) -> str:
        """Might be needed when we talk about chemical reactions. Moreover, in chemistry, if we can speak of simple's
        subclasses in the same sense as here, they would be equal to their classes (simple_class)"""
        return self.simple_class

    @property
    def index(self) -> int:
        return self._index

    @property
    def element(self) -> pt.Element:
        return self._element
