import miniChemistry.Core.Database.ptable as pt
from miniChemistry.Core.Database.stable import SolubilityTable

from typing import Dict
from chemparse import parse_formula


def _string_to_elementary_composition(composition: Dict[str, int|float]) -> Dict[pt.Element, int]:
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
    the largest possible oxidation state (this is the default situation when "choose_largest_charge" is set to True).

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



def _exists(i) -> bool:  # only for ions. Using Ion type causes circular import.
    st = SolubilityTable()
    ions = st.select_ion(i.formula(remove_charge=True), i.charge)

    if ions:
        return True
    elif i.size == 1:
        oxst = i.elements[0].oxidation_states
        return i.charge in oxst
    else:
        return False
