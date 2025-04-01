"""
Simple mechanisms are four types of reactions defined within this Python package. The reaction types described copy the
common reaction classification by the number of reacting substances. Although, here the primary definition of the
reaction type is not the number of reacting substances, but rather their number AND type. Subsequently,

simple_addition(sub1: Simple, sub2: Simple) -> Molecule
simple_decomposition(sub: Molecule) -> Tuple[Simple, Simple]
simple_substitution(sub1: Union[Simple, Molecule], sub2: Union[Simple, Molecule]) -> Tuple[Simple, Molecule]
simple_exchange(sub1: Molecule, sub2: Molecule) -> Tuple[Molecule, Molecule]

NOTE: signature of the simple_addition() reaction is different from the given here. Here the signatures are simplified
to demonstrate what defines a reaction within the set classification.
"""


from miniChemistry.Core.CoreExceptions.SubstanceExceptions import ChargeError
from miniChemistry.Core.CoreExceptions.MechanismExceptions import *
from miniChemistry.Core.Substances import Simple, Molecule, ion, simple
from miniChemistry.Utilities.Checks import type_check_decorator
import miniChemistry.Core.Database.ptable as pt
from miniChemistry.Core.Database.stable import SolubilityTable
from typing import List, Tuple, Any

from miniChemistry.Utilities.UtilityExceptions import KeywordNotAllowed


# ==================================================================================================== PRIVATE FUNCTIONS
def _select_ions(element: pt.Element, ion_type: str = 'both') -> List[SolubilityTable.Ion]:
    """
    Takes in a pt.Element instance and returns all ions found in SolubilityTable database in a list.

    :param element: element (instance of pt.Element) for which ions will be found
    :param ion_type: One of three: 'cation' to search for positive ions, 'anion' – for negative, and 'both' – for all
    :return: a list of SolubilityTable.Ion instances which all are ions of the given chemical element
    """

    st = SolubilityTable()
    st.begin()

    if ion_type == 'cation':
        ions = st.select_ion(cation=element.symbol)
    elif ion_type == 'anion':
        ions = st.select_ion(anion=element.symbol)
    elif ion_type == 'both':
        ions = st.select_ion(element.symbol)
    else:
        raise KeywordNotAllowed(func_name='_select_ions', variables=locals())

    st.end()
    return ions


# ================================================================================================== REACTION MECHANISMS
@type_check_decorator
def simple_addition(sub1: Simple, sub2: Simple, large_charge_difference: bool = True) -> Tuple[Molecule]:
    """
    Simple addition reaction by its definition is Simple + Simple -> Molecule. That means
    1) Only Molecules with two chemical elements can be formed in this reaction
    2) Each element (of both Simple sub1, and sub2) must be converted into a positive or negative ion. Solubility
    table is used as a database to select ions.

    :param sub1: one of the reagents, Simple
    :param sub2: another reagent, Simple
    :param large_charge_difference: boolean indicating whether the charge difference of the selected ions is the largest
    :return: A Tuple containing one Molecule instance (composed of two ions derived from Simple instances)
    """

    # select ions of the given element
    sub1_ions = _select_ions(sub1.element)
    sub2_ions = _select_ions(sub2.element)

    # check REN and select cations and anions (cations – for the element with lower REN)
    if sub1.element.ren < sub2.element.ren:
        cations = [cation for cation in sub1_ions if cation.charge > 0]
        anions = [anion for anion in sub2_ions if anion.charge < 0]
    else:
        cations = [cation for cation in sub2_ions if cation.charge > 0]
        anions = [anion for anion in sub1_ions if anion.charge < 0]

    # sort the lists according to 'large_charge_difference'
    if len(cations) > 1:
        cations.sort(reverse=large_charge_difference, key=lambda i: i.charge)
    if len(anions) > 1:
        anions.sort(reverse=not large_charge_difference, key=lambda i: i.charge)

    for cation in cations:
        for anion in anions:
            c = ion(substance=cation, charge=cation.charge)
            a = ion(substance=anion, charge=anion.charge)
            try:
                molecule = Molecule(c, a)
                return molecule,
            except ChargeError:
                continue
    else:
        raise CannotPredictProducts(reagents=[sub1.formula(), sub2.formula()], function_name='simple_addition', variables=locals())



@type_check_decorator
def simple_decomposition(sub: Molecule, *args: Any) -> Tuple[Simple, Simple]:
    """
    Simple decomposition reaction is defined as Molecule -> Simple + Simple. Since the simple() function from Substance.py
    can convert ions to simples, the implementation is very simple.

    The simple() function raises UnsupportedSubstanceSize when any of the ions of the Molecule instance has more than
    one element (hence, cannot be converted to Simple instance).

    :param sub: an instance of Molecule
    :param args: used to keep signature of the function
    :return: Tuple of two instances of Simple. First instance is formed from cation, second instance from anion.
    """

    if sub == Molecule.water:  # because water is defined here as H–OH, but actually can behave also like H2–O
        return Simple.hydrogen, Simple.oxygen

    sub1 = simple(sub.cation)
    sub2 = simple(sub.anion)

    return sub1, sub2


@type_check_decorator
def simple_substitution(sub1: (Simple, Molecule), sub2: (Simple, Molecule)) -> Tuple[Simple, Molecule]:
    """
    Simple substitution is defined as Simple + Molecule -> Simple + Molecule. In this reaction type an instance in
    Simple becomes a cation for Molecule reagent, and Molecule reagent's cation becomes an instance of Simple.
    Since the order of substances can have two options (Simple and Molecule AND Molecule and Simple), the last case
    just returns result of that same function with reversed arguments order.

    :param sub1: an instance of Simple
    :param sub2: an instance of Molecule
    :return: a tuple of Simple and Molecule
    """

    if isinstance(sub1, Simple) and isinstance(sub2, Molecule):
        new_simple = simple(sub2.cation)
        new_ion = ion(sub1)
        new_molecule = Molecule(new_ion, sub2.anion)
        return new_simple, new_molecule
    elif isinstance(sub2, Simple) and isinstance(sub1, Molecule):
        return simple_substitution(sub2, sub1)
    else:
        # in fact, this should be never called due to type_check_decorator
        raise CannotPredictProducts(reagents=[sub1, sub2], function_name='simple_substitution', variables=locals())


@type_check_decorator
def simple_exchange(sub1: Molecule, sub2: Molecule) -> Tuple[Molecule, Molecule]:
    """
    Simple exchange reaction is defined as Molecule + Molecule -> Molecule + Molecule. Since this is just an ion
    exchange reaction, the ions just have to be swapped.

    :param sub1: the first instance of Molecule
    :param sub2: the second instance of Molecule
    :return: a tuple of resultant instances of Molecule
    """

    new_molecule_1 = Molecule(sub1.cation, sub2.anion)
    new_molecule_2 = Molecule(sub2.cation, sub1.anion)

    return new_molecule_1, new_molecule_2


# ============================================================================================================== TESTING
"""
Testing the following reactions (reagents do not include water and nitrates or nitric acid):
    SIMPLE EXCHANGE
 - salt + salt -> salt + salt
 - salt + base -> salt + base
 - salt + acid -> salt + acid
 - base + acid -> salt + water

    SIMPLE SUBSTITUTION
 - salt + metal -> salt + metal
 - acid + metal -> salt + hydrogen

    SIMPLE DECOMPOSITION
 - binary salt -> metal + nonmetal
 - binary acid -> metal + nonmetal
 - oxide -> metal + oxygen

    SIMPLE ADDITION
 - metal + nonmetal -> (binary) salt
 - nonmetal + nonmetal -> (binary) salt or oxide
"""
"""
salt1 = Molecule.from_string('Na', 1, 'SO4', -2)
salt2 = Molecule.from_string('Zn', 2, 'PO4', -3)
binary_salt = Molecule.from_string('Cu', 2, 'Cl', -1)
oxide = Molecule.from_string('Fe', 3, 'O', -2)

acid = Molecule.from_string('H', 1, 'CO3', -2)
base = Molecule.from_string('Ba', 2, 'OH', -1)
binary_acid = Molecule.from_string('H', 1, 'Cl', -1)

metal = simple(pt.Zn)
nonmetal = simple(pt.S)

exchange_reagents = [(salt1, salt2), (salt1, base), (salt2, acid), (acid, base)]
substitution_reagents = [(salt1, metal), (acid, metal)]
decomposition_reagents = [binary_acid, binary_salt, oxide]
addition_reagents = (metal, nonmetal)

print('SIMPLE EXCHANGE REACTION TESTING...')
for reagents in exchange_reagents:
    reaction = reagents[0].formula() + ' + ' + reagents[1].formula() + ' -> '
    products = simple_exchange(*reagents)
    reaction += products[0].formula() + ' + ' + products[1].formula()
    print('\t', reaction)

print('\nSIMPLE SUBSTITUTION REACTION TESTING...')
for reagents in substitution_reagents:
    reaction = reagents[0].formula() + ' + ' + reagents[1].formula() + ' -> '
    products = simple_substitution(*reagents)
    reaction += products[0].formula() + ' + ' + products[1].formula()
    print('\t', reaction)

print('\nSIMPLE DECOMPOSITION REACTION TESTING...')
for reagent in decomposition_reagents:
    reaction = reagent.formula() + ' -> '
    products = simple_decomposition(reagent)
    reaction += products[0].formula() + ' + ' + products[1].formula()
    print('\t', reaction)

print('\nSIMPLE ADDITION REACTION TESTING...')
reaction = addition_reagents[0].formula() + ' + ' + addition_reagents[1].formula() + ' -> '
products = simple_addition(*addition_reagents)
reaction += products[0].formula()
print('\t', reaction)
"""
