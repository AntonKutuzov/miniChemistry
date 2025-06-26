"""
The Substances file describes the main substance's types used in this module. In fact, the code written here is based
on real (school) chemistry, however it is still somewhat simplified to make it possible to code. There are three main
substance types in miniChemistry, those are SIMPLE, MOLECULE, and ION. They all extend an abstract class (ABC) called
Particle which defines properties and methods common to all the substances.


TERMINOLOGY
In chemistry, we call by a particle any chemical object, an atom, a molecule, an ion, etc. A substance, in contrast, is
a macro world's object like water, sugar or salt. So, the class Particle is the most general one here, and it describes
the main attributes that every particle must have. Molecule, Simple and Ion just extend the class to make it more
specific and to fit the chemical description of each class of particles.


BACKGROUND FROM CHEMISTRY
The smallest unit of substance in chemistry is called an atom. That means, we can't chemically (i.e. by using
chemical reactions, chemical methods) divide an atom. There are 118 known atom types today which are called chemical
elements (see more in 'ptable.py' file). This code does not simulate individual atoms, so we don't have a class for them.
Instead, this code starts with molecules, which are groups of atoms bonded in a specific way. Molecules can differ
based on

1) the number of atoms
2) kind of atoms
3) arrangement of atoms

That means we can have molecules that consist of (1) two, three, four and much more atoms. We can also have molecules
with the same number of atoms, but different atom types (2) (different chemical elements). Finally, it is possible that
two molecules consist of the same atoms in the same quantities, but the arrangement of the atoms is different. In the
latter case the molecules are called isomers, and (!) they are not supported by this package. Hence, molecular formula,
i.e. composition of a molecule is its unique signature of a substance.

A special case of molecules is the ones that consists of only one type of atoms (one chemical element). Their substances
are called simple (in contrast to complex substance of molecules of more than one chemical element). The class Simple
describes such molecules as separate data type, because this will be important when we come to chemical reactions.

Finally, an ion is a charged set of atoms. This can be both single atom with a charge, or it can be a group of atoms
with some charge. There are rules in chemistry by which we decide what is the charge of a group of atoms based on their
properties, however in this package mostly the charges are set by the user (the exceptions are described separately).


IMPLEMENTATION
So, this file contains (and hence this package uses) three types of substances – Molecule which describes a group of
atoms of several chemical elements with zero charge; Simple which describes a group of atoms (one or more) of the same
chemical element with zero charge; Ion, which describes a group of atoms with charge not equal to zero.

In this code any molecule consists of two ions – cation and anion (positive and negative respectively). Hence, to
define a molecule it is enough to define both ions. There are special methods to create acids, bases and oxides faster
since their ions (one out of two) are known.

Finally, each class has some special substances which are defined as class' attributes. For example, water is a special
substance for Molecule class just because water is a very common molecule. Simple class has all substances with index 2
as special substances (those are H2, N2, O2, F2, Cl2, Br2, I2). The special substances can be addressed as class
attributes, however they are themselves instances of another class which defines their __get__ method. This is done
because (as they are instances of the class contained within that class) the substances have to be defined after the
constrictor of a class is run, otherwise we get a loop. So, there is an initiation method for these substances. To avoid
complex and unreadable error messages in the cases when a user tries to use undefined special substances, their __get__
method checks whether they are initiated and if not just gives a custom error message that directly asks to call
initiation method of a given class.


CONVERTION BETWEEN THE TYPES
It might be useful to convert between the types of substances and some other data types within the module. To do this
several functions named same as the classes are defined below. They take in data types that can (logically in real
chemistry) be converted into the required data type and perform some operations for this. For example, it is common
to convert between a chemical element (pt.Element) and a simple substance (Simple), because the simple substance contains
only this element. Hence, the function would be

element = simple(pt.Al)  # Returns Simple with formula 'Al'
element = simple(pt.O)  # Returns Simple with formula 'O2'

The following functions are defined:
ion() -> Ion
simple() -> Simple
molecule() -> Molecule

and

is_gas() which will be needed for prediction of chemical reaction outputs. It uses common patterns from school chemistry
to determine whether a substance passed to the function is a gas.
NOTE: the method does not really check if this is a gas. It just uses common rules that are not strict. So, the function
can make mistakes in complicated cases.
"""

# ==================================================================================================== IMPORT STATEMENTS

from typing import Tuple, Dict, Union
from chemparse import parse_formula
from abc import ABC, abstractmethod

import miniChemistry.Core.Database.ptable as pt
from miniChemistry.Core.Database.stable import SolubilityTable

from miniChemistry.Core.CoreExceptions.SubstanceExceptions import ElementNotFound as sub_ElementNotFound
from miniChemistry.Core.CoreExceptions.SubstanceExceptions import *
from miniChemistry.Core.CoreExceptions.stableExceptions import IonNotFound
from miniChemistry.Core.CoreExceptions.ptableExceptions import ElementNotFound as pt_ElementNotFound
from miniChemistry.MiniChemistryException import NotSupposedToHappen

from miniChemistry.Utilities.Checks import type_check, single_element_cation_check, charge_check

# ============================================================================================== SPECIAL ATTRIBUTE CLASS

class _SpecialSubstance:
    """
    Needed to avoid complex error messages when a special substance is used without their initiation. Say, we try to
    use

    em = Particle.empty

    but the attribute 'empty' is not yet defined (Particle.create_special_particles() is not called). The error message
    in this case is huge and complicated. To avoid it, Particle.empty and other special substances are instances
    of _SpecialSubstance class which redefines __get__ method.
    """

    def __init__(self, attr, name: str):
        self._attr = attr
        self._name = name

    def __get__(self, instance, owner):
        if instance is not None:
            raise Exception('Please address special substances via class attribute.')

        if self._attr is not None:
            return self._attr
        else:
            string_dict = {
                Particle: 'particles',
                Molecule: 'molecules',
                Ion: 'ions'
            }
            raise TypeError(f'"{self._name}" is a special attribute, and thus cannot be None. Create special {string_dict[owner]}.')

# ======================================================================================================= PARTICLE CLASS

class Particle(ABC):
    """
    Class Particle is a general abstract class that every other (substance) class in this file inherit from. For any
    particle in chemistry it is common to have several properties:
    - composition  # number and type of atoms within the given particle
    - charge

    Also, several methods are useful when treating or defining a (any) particle (both are abstract methods)
    - from_string() -> Particle  # instance of a class from where the method is called
    # allows to create a particle based on strings containing chemical formula of a particle
    - formula() -> str
    # returns chemical formula of a particle

    The following properties are defined:
    - size -> int           # number of atoms
    - molar_mass -> float   # sum of all atomic masses of all atoms (see 'ptable.py' for atomic masses)
    - elements -> tuple     # returns a tuple of chemical elements (pt.Element) that are within a particle
    - composition -> dict   # returns number of atoms of every chemical element
    - charge -> int         # returns charge of a particle

    Also, the following magic methods are defined
    __iter__() to use keyword 'in' or loops 'for' and 'while' on a particle. Returns an iterable containing all the
    elements that are present in a particle
    __eq__() comparison is based on composition and charge of a particle. If both coincide, then they are considered
    equal. Hence, isomers are not supported.
    __hash__() used to make it possible to store particles in any kind of collection (list, dict, set, etc.). Uses
    chemical formulas of a particle as a string to produce hash.

    The class also has a method called 'create_special_particles()' which creates class attributes. In the case of
    Particle class the only attribute is 'empty' which is an equivalent of None, however it must be a particle not to
    cause problems later.
    """

    
    def __init__(self, composition: Dict[pt.Element, int], charge: int) -> None:
        single_element_cation_check(composition, charge, raise_exception=True)

        self._composition = composition
        self._charge = charge

    def __iter__(self):
        """Returns iterable containing all the elements present in the particle."""
        return self.composition.keys().__iter__()

    def __eq__(self, other) -> bool:
        """
        Two particles are equal it their compositions are the same and their charges are the same.
        NOTE: the function has this form, because exactly this form of evaluating many conditions will be useful when
        we come to chemical reactions.
        :param other: Particle
        :return: bool
        """

        try:
            conditions = [
                self.composition == other.composition,
                self.charge == other.charge
            ]
            return all(conditions)
        except AttributeError:  # in case somebody decides to compare ints, strings or anything else to Particle
            return False

    @abstractmethod
    def __hash__(self):
        pass

    @staticmethod
    @abstractmethod
    #  not used because of string-form forward reference. Used just a type_check function instead
    def from_string(*args, **kwargs):
        """
        This method is used to convert a string with molecular formula of a substance into an instance of the class
        from where the function is called.
        """
        pass

    @abstractmethod
    def formula(self, *args, **kwargs):
        """
        Used to compose a molecular formula (as str) from composition of a particle. Somewhat opposite to the
        from_string() method.
        """
        pass

    @property
    def size(self) -> int:
        return len(self.elements)

    @property
    def molar_mass(self) -> float:
        M = 0
        for element, index in self.composition.items():
            M += element.molar_mass * index
        return M

    @property
    def elements(self) -> Tuple[pt.Element, ...]:
        element_set = set(self.composition.keys())
        return tuple(element_set)

    @property
    def composition(self) -> Dict[pt.Element, int]:
        return self._composition

    @property
    def charge(self) -> int:
        return self._charge

# ========================================================================================================= SIMPLE CLASS

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
    chlorine = _SpecialSubstance(None, name='chlorine')
    bromine = _SpecialSubstance(None, name='bromine')
    iodine = _SpecialSubstance(None, name='iodine')

    nitrogen = _SpecialSubstance(None, name='nitrogen')
    oxygen = _SpecialSubstance(None, name='oxygen')

    specials = _SpecialSubstance(None, name='specials')  # tuple of all the mentioned simples

    empty = _SpecialSubstance(None, name='empty')

    
    def __init__(self, element: pt.Element, index: int) -> None:
        composition = {element : index}

        self._element = element
        self._index = index

        super().__init__(composition, 0)

    def __hash__(self):
        return hash(self.formula())

    @classmethod
    def create_special_simples(cls) -> None:
        cls.hydrogen = Simple(pt.H, 2)
        cls.chlorine = Simple(pt.Cl, 2)
        cls.bromine = Simple(pt.Br, 2)
        cls.iodine = Simple(pt.I, 2)
        cls.nitrogen = Simple(pt.N, 2)
        cls.oxygen = Simple(pt.O, 2)
        cls.specials = (cls.hydrogen, cls.chlorine, cls.nitrogen, cls.oxygen, cls.bromine, cls.iodine)

        cls.empty = Simple(pt.Element('Ee', 'empty element', 0, 0, '0A', 0, 0),  0)

    @staticmethod
    def from_string(string: str) -> 'Simple':
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

# ============================================================================================================ ION CLASS

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
    def from_string(string: str, charge: int, database_check: bool = True) -> 'Ion':
        type_check([string, charge, database_check], [str, int, bool],
                   strict_order=True, raise_exception=True)

        all_elements = None
        try:
            string_composition = parse_formula(string)
            all_elements = tuple(string_composition.keys())
            elementary_composition = _string_to_elementary_composition(string_composition)
            i = Ion(elementary_composition, charge)
        except pt_ElementNotFound:  # i.e. element is not present in the Periodic Table. Raised by Element.get_by_symbol
            not_present_elements = list()
            for element in all_elements:
                if element not in pt.TABLE_STR:
                    not_present_elements.append(element)
            raise sub_ElementNotFound(f'Element(s) with symbols {", ".join(not_present_elements)} are not found.',
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

# ======================================================================================================= MOLECULE CLASS

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

        charge_check([cation.charge*self._cation_index, anion.charge*self._anion_index],
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
                    database_check: bool = True) -> 'Molecule':
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
            nsth.description(f'\nIndex of one of the ions used to create a molecule is less than 1, which \n'
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
        formula += self._parentheses(self.cation, self._cation_index)
        formula += self._parentheses(self.anion, self._anion_index)
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
    def acid(anion: Ion) -> 'Molecule':
        type_check([anion], [Ion], raise_exception=True)
        return Molecule(Ion.proton, anion)

    @staticmethod
    def base(cation: Ion) -> 'Molecule':
        type_check([cation], [Ion], raise_exception=True)
        return Molecule(cation, Ion.hydroxide)

    @staticmethod
    def oxide(cation: Ion) -> 'Molecule':
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
        composition = update_composition(self.cation, self._cation_index, composition)
        composition = update_composition(self.anion, self._anion_index, composition)
        return composition


    @property
    def cation(self) -> Ion:
        return self._cation

    @property
    def anion(self) -> Ion:
        return self._anion

# ==================================================================================================== HELPING FUNCTIONS

def _string_to_elementary_composition(composition: Dict[str, Union[int, float]]) -> Dict[pt.Element, int]:
    """
    This function converts the result of chemparse.parse_formula() function which is Dict[str, int] into a dictionary
    that shows the number of each chemical element in a particle. For example

    >>> parse_formula('Na2SO4')
    {'Na': 2.0, 'S': 1.0, 'O': 4.0}

    Here the obtained dict will be converted into a dict where the strings with chemical element symbols are replaced
    by real chemical elements (instances of pt.Element).

    :param composition: Dict[str, int]. Usuallt obtained from chemparse.parse_formula().
    :return: Dict[pt.Element, int], composition of a particle.
    """

    elementary_composition = dict()

    for symbol, index in composition.items():
        element = pt.Element.get_by_symbol(symbol)
        index = int(index)
        elementary_composition.update({element : index})

    return elementary_composition



def _select_suitable_charge(element: pt.Element, choose_largest_charge: bool = True) -> int:
    """
    The function is intended to select an appropriate charge for an element that will be then converted into an ion.
    Possible charges of an ion consisting of the given chemical element are limited to its oxidation states (a tuple
    inside the pt.Element class). The way the function chooses the charge is not valid from chemical point of view,
    but rather is based on empirical observations that most of the common chemical reactions met in school go up to
    the largest possible oxidation state (this is the default situation when "choose_largest_charge" is set to True.

    However, in some cases it is also needed to have another charge, not the largest one. In this case the function
    chooses the opposite – the lowest charge.

    The problem, of course, is that the function cannot choose from the middle oxidation states. If such a particle is
    required, the charge of the particle must be set by hand.

    :param element: element that is to be turned into an ion (we choose charge for this element)
    :param choose_largest_charge: whether we should choose the largest of the lowest charge
    :return: an integer, representing the charge
    """

    possible_charges = list(element.oxidation_states)
    possible_charges.sort(reverse=choose_largest_charge)
    return possible_charges[0]



def _exists(i: Ion) -> bool:
    st = SolubilityTable()
    ions = st.select_ion(i.formula(remove_charge=True), i.charge)

    if ions:
        return True
    elif i.size == 1:
        oxst = i.elements[0].oxidation_states
        return i.charge in oxst
    else:
        return False

# ================================================================================================= CONVERTION FUNCTIONS

def simple(substance: Union[Ion, pt.Element]) -> Simple:
    """Converts Particle, Ion or pt.Element into Simple. Extracts the element from them and adds an index."""
    if isinstance(substance, Ion):
        if substance.size > 1:
            raise UnsupportedSubstanceSize(substance.composition, 'simple', variables=locals())
        element = substance.elements[0]
    elif isinstance(substance, pt.Element):
        element = substance  # by name "substance" now a chemical element (pt.Element) is called
    else:
        raise SubstanceConvertionError(Simple, type(substance), 'particle', variables=locals())

    if element in [special.element for special in Simple.specials]:
        index = 2
    else:
        index = 1

    return Simple(element, index)



def ion(substance: Union[Simple, pt.Element, SolubilityTable.Ion],
        charge: int = None,
        choose_largest_charge: bool = True) -> Ion:
    """
    Converts Particle, Simple, pt.Element, and SolubilityTable.Ion into Ion instance. In each of the cases the function
    determined the composition and charge needed for the constructor. If charge cannot be determined from the substance,
    a function _select_suitable_charge() is used.

    Whenever parameter "charge" is set to an integer, it is used instead of automatically determined charges.

    :param substance: Particle, Simple, pt.Element or SolubilityTable.Ion to be converted into Ion instance
    :param charge: integer (always used if given)
    :param choose_largest_charge: True if the largest possible charge has to be chosen, False is the lowest.
    :return: an instance of Ion
    """

    if isinstance(substance, Simple):
        if substance.size > 1:
            raise UnsupportedSubstanceSize(substance.composition, 'ion', variables=locals())
        else:
            element = substance.element
            chosen_charge = _select_suitable_charge(element, choose_largest_charge)
            composition = substance.composition

    elif isinstance(substance, pt.Element):
        composition = {substance : 1}
        chosen_charge = _select_suitable_charge(substance, choose_largest_charge)  # here "substance" is actually pt.Element

    elif isinstance(substance, SolubilityTable.Ion):
        string_composition = parse_formula(substance.composition)  # this is SolubilityTable.Ion.composition!
        chosen_charge = substance.charge                                  # and SolubilityTable.Ion.charge!
        composition = _string_to_elementary_composition(string_composition)

    else:
        nsth = NotSupposedToHappen(variables=locals())
        nsth.description = (f'This time you called a function "ion()" from Core.Substances(old).py and for some reason\n'
                            f'it took in the parameter "substance" while it has type {type(substance)}, whereas\n'
                            f'usually it should accept only the following data types: Particle, Simple, pt.Element,\n'
                            f'and SolubilityTable.Ion.')
        raise nsth

    return Ion(composition, (charge if charge is not None else chosen_charge))



def molecule(substance: SolubilityTable.Substance) -> Molecule:
    """
    Since in this code Molecule always consists of two ions, the only data type that can be directly converted into
    Molecule is SolubilityTable.Substance (because it has two ions).

    :param substance: substance obtained from SolubilityTable
    :return: an instance of Molecule
    """

    cation_element = pt.Element.get_by_symbol(substance.cation)
    cation = Ion({cation_element: 1}, substance.cation_charge)

    anion_composition = parse_formula(substance.anion)
    anion_pt_composition = _string_to_elementary_composition(anion_composition)
    anion = Ion(anion_pt_composition, substance.anion_charge)

    return Molecule(cation, anion)

# ====================================================================================================== is_gas FUNCTION


def is_gas(substance: Union[Molecule, Simple]) -> bool:
    """
    Thus function is based on empirical observations and is valid for many (but not all) substances within school
    chemistry. Basically, it uses common patterns from school chemistry to determine by chemical formula is a substance
    is a gas.

    NOTE: Although it may work in this code, from the point of view of chemistry, this is not a valid way to determine
    is a substance is gas.
    NOTE 2: Since this function uses only an empirical pattern, it may be wrong in some cases.

    :param substance:
    :return:
    """

    if substance.size > 2:
        return False
    elif substance in Simple.specials[:4]:  # see definition of specials class attribute
        return True
    elif substance.size == 2:
        for e1 in {pt.C, pt.N, pt.S}:
            for e2 in {pt.H, pt.O}:
                if e1 in substance.composition.keys() and e2 in substance.composition.keys():
                    return True
        else:
            return False
    else:
        return False


# ========================================================================================== CREATING SPECIAL SUBSTANCES

Simple.create_special_simples()
Ion.create_special_ions()
Molecule.create_special_molecules()

# ============================================================================================================= EXAMPLES
