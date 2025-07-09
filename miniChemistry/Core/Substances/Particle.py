import miniChemistry.Core.Database.ptable as pt
from miniChemistry.Utilities.Checks import single_element_cation_check

from abc import ABC, abstractmethod
from typing import Dict, Tuple


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

    def __init__(self,
                 composition: Dict[pt.Element, int],
                 charge: int,
                 _secc_disable: bool = False
                 ) -> None:

        if not _secc_disable:
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
        except AttributeError:
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
