"""
Equalizer is a class that is used only to equate chemical reactions. Actually, this can be thought of as a function
implemented in a form of a class for convenience. The theoretical function would have the following signature:

equate(reagents: List[Union[Simple, Molecule]], products: List[Union[Simple, Molecule]]) -> Dict[str, int]

So, it takes in instances of Simple or Molecule as reagents and products, and returns a dict with keys being substances'
formulas and values being their coefficients. For example,

>>> H2 = Simple.from_string('H2')
>>> O2 = Simple.from_string('O2')
>>> H2O = Molecule.water
>>> equalizer = Equalizer(reagents=[H2, O2], products=[H2O])
>>> equalizer.coefficients
{'H2': 2, 'O2': 1, 'H2O': 2}

In this class only keyword arguments are used to avoid confusion between reagents and products.
"""


from math import lcm
from sympy import Matrix, Rational
from typing import List, Set, Union, Dict

import miniChemistry.Core.Database.ptable as pt
from miniChemistry.Core.Substances import Simple, Molecule
from miniChemistry.Utilities.Checks import type_check_decorator
from miniChemistry.Core.CoreExceptions.ToolExceptions import CannotEquateReaction


class Equalizer:
    """
    Equalizer class has several methods and properties that split a large (theoretical) function that equates the
    reaction.
    NOTE: in fact, no instance of Reaction class is used here, since an instance of Equalizer is used in Reaction
    constructor to (surprise) equate a reaction.

    The properties that the class has are
    - reagents: List[Union[Simple, Molecule]]
    - products: List[Union[Simple, Molecule]]
    - matrix: sympy.Matrix
    - coefficients: Dict[str, int]

    The following methods are used to equate the reaction:
    _elements: takes in Simple or Molecule instances and returns a list of pt.Element instances
    _create_matrix: creates a matrix (explained below) from substance's composition
    _make_integers: converts all numbers in a Matrix to whole numbers (multiplies the matrix by a number)
    _get_coefficients: actually solves the system of equations and returns the dict

    Algorithm:
    The algorithm is based on the law of conservation of mass, i.e. the number of atoms of each element from both sides
    of the equation must be the same. Or, expressing this in mathematical terms, we can write

    sum(reagent_coefficient * element_index) - sum(product_coefficient * element_index) = 0

    So, to implement this here, we create a matrix in the following form: every column represents a substance, every
    row represents an element. For example, for a reaction H2 + O2 -> H2O the matrix will look like

        H2  O2  H2O
    H   2   0   -2
    O   0   2   -1

    Which represents two equations – the law of conservation of mass for each element. For hydrogen, it would be
    2a + 0b -2c = 0
    which means it is coefficient of H2 (a) times the index of hydrogen in H2, plus coefficient of O2 (b) times
    the index of oxygen in H2 (which is zero, because there's no oxygen in H2). Now, since water is a product, its
    coefficient must be on the other side, or it must be negative to comply with the law of conservation of mass.

    To solve this system of equations, we look for nullspace of the matrix (because this gives us the values of
    a, b, and c. We then multiply the matrix by an integer to make all values integers (whole numbers).

    Converting this into a dict, we get the result.
    """

    @type_check_decorator
    def __init__(self, *, reagents: list, products: list) -> None:
        self._reagents = reagents
        self._products = products
        self._elements = tuple(self._elements(*self.reagents, *self.products))
        self._substances = tuple(self.reagents + self.products)
        self._matrix = self._create_matrix()
        self._substance_order = self._substances
        self._coefficients = self._get_coefficients()

    @type_check_decorator
    def _elements(self, *substances: Union[Simple, Molecule]) -> Set[pt.Element]:
        """Extracts all the elements present on the given substances"""
        elements = set()
        for substance in substances:
            elements = elements.union(set(substance.elements))
        return elements

    def _create_matrix(self) -> Matrix:
        """
        To create the matrix, first a nested list must be created. Every row represents an element, and every column
        represents a substance, hence we have a nested loop, where first we define an element, and then we define a
        substance. The value assigned to a list is substance.composition[element] or, in other words, element's
        index inside the substance.

        Given the fixed positions of elements and substances in self._elements and self._substances, the matrix does
        not need to store information about elements and substances.

        :return:
        """

        element_names = [element.symbol for element in self._elements]
        substance_names = [sub.formula() for sub in self._substances]
        matrix = []

        for el_index, symbol in enumerate(element_names):
            element = self._elements[el_index]
            matrix.append([])
            for sb_index, sub in enumerate(substance_names):
                substance = self._substances[sb_index]
                multiple = -1 if substance in self.products else 1
                index = substance.composition.get(element)
                matrix[el_index].append( multiple*(index if index is not None else 0) )

        return Matrix(matrix)

    @type_check_decorator
    def _make_integers(self, m: Matrix) -> Matrix:
        """
        First converts all numbers in a matrix into sympy.Rational, then searches for the least common diviser or the
        denominators, and multiplies the numbers by it.

        :param m: matrix to contain integers
        :return: matrix multiplied by an integer, which makes all numbers IN the matrix integers
        """

        m = m.applyfunc(Rational)
        denominators = [term.q for term in m]
        lcm_for_d = lcm(*denominators)
        m = m.applyfunc(lambda x: lcm_for_d*x)
        return m

    def _get_coefficients(self) -> Dict[Union[Simple, Molecule], int]:
        """
        Creates a dict with formula–coefficient pairs. First, it solves the system of equations with Matrix.nullspace(),
        then checks that the nullspace contains one vector (otherwise, raises an exception) and converts it into a dict.

        :return: A dictionary with formula–coefficient pairs
        """

        answer_dict = dict()
        solutions = self.matrix.nullspace()

        if len(solutions) != 1:
            raise CannotEquateReaction(reagents=[r.formula() for r in self.reagents], variables=locals())

        solution = solutions[0]
        answer = self._make_integers(solution)

        for item, substance in zip(answer.tolist(), self._substance_order):
            answer_dict.update({substance: int(item[0])})  # since answer is a vector (matrix with one column), we just use [0]

        return answer_dict

    @property
    def reagents(self) -> List[Union[Simple, Molecule]]:
        return self._reagents

    @property
    def products(self) -> List[Union[Simple, Molecule]]:
        return self._products

    @property
    def matrix(self) -> Matrix:
        return self._matrix

    @property
    def coefficients(self) -> Dict[Simple|Molecule, int]:
        return self._coefficients
