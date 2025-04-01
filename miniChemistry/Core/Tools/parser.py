from typing import Dict, List, Union, Tuple
from chemparse import parse_formula
import miniChemistry.Core.Database.ptable as pt
from miniChemistry.Core.CoreExceptions.ToolExceptions import InvalidFormula
from miniChemistry.Core.Database.stable import SolubilityTable
from miniChemistry.Core.CoreExceptions.stableExceptions import OutOfOptions
from miniChemistry.Core.Substances import Simple, Molecule
from miniChemistry.Utilities.Checks import type_check_decorator
from miniChemistry.MiniChemistryException import NoArgumentForFunction


@type_check_decorator
def parse_ion(ion_formula: str) -> Tuple[str, int]:
    """
    A form of writing ions accepted in this module is <ion formula>(<ion charge>). For example, an ion consisting of
    sodium ation with charge equal to +1 will be written as "Na(1)". An oxygen atom with charge equal to -2 will be
    written as "O(-2)".

    Sometimes it is needed to parse the ion's formula into its composition and charge separately. Hence, the formula
    converts "O(-2)" into "O" (str) and -2 (int), and "Na(1)" into "Na" (str) and 1 (int).

    :param ion_formula: formula of an ion, including ion's charge
    :return: formula of an ion WITHOUT the charge, and the charge separately
    """

    try:
        formula, charge = ion_formula.split('(')
        charge = charge.strip(')')
        charge = int(charge)
    except ValueError:
        ifm = InvalidFormula(ion_formula, variables=locals())
        ifm.description += ('This exception is raised from a function called "parse_ion", which looks for\n'
                            'parentheses in the formula and splits it. If you pass a formula of an ion\n'
                            'and forget a charge (i.e. you pass for example "O", but not "O(-2)", you\n'
                            'will get this exception.')
        raise ifm

    return formula, charge

@type_check_decorator
def split_to_elements(formula: str) -> List[str]:
    """
    The function disassembles the formula given into elementary strings (if we can say so) needed for this module. Namely,
    the function separates all the elements, numbers and braces into separate strings and returns a list of them.

    For example, a formula "H2O" will be converted into ['H', '2', 'O'], formula "Al2(SO4)3" will be converted into
    ['Al', '2', '(', 'S', 'O', '4', ')', '3'].

    NOTE: numbers are also returned as strings, not integers.
    NOTE 2: multiple-symbol numbers, i.e. all numbers larger than 9 are written as a single string

    :param formula: formula to be split into elements
    :return: a list of strings containing separately elements, numbers and braces
    """

    element_list = list()
    element = ''

    for symbol in formula:
        if symbol.isupper():
            if not element:
                element += symbol
            else:
                element_list.append(element)
                element = symbol

        elif symbol.islower():
            element += symbol
            element_list.append(element)
            element = ''

        elif symbol in '[]()':
            if element:
                element_list.append(element)
                element = ''
            element_list.append(symbol)

        elif symbol.isnumeric():
            if element.isnumeric():
                element += symbol
            elif element:
                element_list.append(element)
                element = symbol
            else:
                element = symbol

        else:
            raise Exception(f'Symbol "{symbol}" should not be in molecular formula of a compound.')

    if element:
        element_list.append(element)

    for element in element_list:
        if element.isalpha():
            pt.Element.get_by_symbol(element)

    return element_list


@type_check_decorator
def index_ratios(formula: str = '', round_to: int = 2, composition: Dict[str, Union[int, float]] = None) -> Dict[str, float]:
    """
    The function returns the relative number of elements in a given substance (formula). It takes the largest index
    found in a formula and divides by it all other indices. In this way it returns a dict of element symbols with
    corresponding number from 0 (not including) to 1 (including, and always present).

    For example, for a substance "H2O" the returned dict would be
    index_ratios('H2O')
    {'H': 1.0, 'O': 0.5}

    But for Al2(SO4)3, which can also be written as Al2S3O12 the returned dict would be
    index_ratios('Al2(SO4)3')
    {'O': 1.0, 'S': 0.25, 'Al': 0.17}

    :param formula: substance's formula (as a string)
    :param round_to: number of digits the ratios are rounded up to, 2 by default
    :param composition: use in the case you want to pass to the function only a part of the molecule
    :return: a dict with key=element (str), value=ratio of the element's index to the largest index (float)
    """

    if not formula and not composition:
        raise NoArgumentForFunction(function_name='index_ratios', variables=locals())

    if composition is None:
        string_composition = parse_formula(formula)
    else:
        string_composition = composition
    ratios = dict()
    max_index = max(string_composition.values())

    for key, value in zip(string_composition.keys(), string_composition.values()):
        ratios.update({key : round(value/max_index, round_to)})

    return ratios


@type_check_decorator
def _remove_first_element(formula: str, return_string: bool = False, return_composition: bool = False,
                          return_first_element: bool = False) -> Dict[str, Union[str, Dict[str, float]]]:
    element_list = split_to_elements(formula)
    first_element = element_list[0]
    rest = element_list[1:]
    return_dict = dict()

    counter = 0
    for element in rest:
        if element.isalpha() or element in '()':
            break
        else:
            counter += 1

    formula = ''.join(rest[counter:])

    if return_string:
        return_dict['formula'] = formula
    if return_composition:
        return_dict['composition'] = parse_formula(formula)
    if return_first_element:
        return_dict['first element'] = first_element

    return return_dict



@type_check_decorator
def get_anion(formula: str) -> SolubilityTable.Ion:
    """
    Extracts an anion from a substance's formula. Returns anion's formula and charge separately if the corresponding
    anion was met in the solubility table.

    NOTE: this function as well as get_cation() is based on a common rule that cations always go first, AND as
    assumption that this module does not support molecules with several cations or anions. Hence, this function will
    perform wrong with such substances as CaClBr, or NaHSO4. Also, it will misunderstand such exceptions to this
    rule as NH3 and PH3. It will treat hydrogen as anion, so ammonia must be written according to convention, i.e. as H3N.

    :param formula: formula of a substance for which an anion has to be extracted.
    :return: a tuple containing formula of the anion and its charge.
    """

    anion_composition = _remove_first_element(formula, return_composition=True)['composition']

    try:
        substance_ratios = index_ratios(composition=anion_composition)
    except NoArgumentForFunction:
        raise InvalidFormula(formula, variables=locals())

    # checking anion in the solubility table
    st = SolubilityTable()
    st.begin()

    for compound in st:
        anion = compound.anion
        anion_ratio = index_ratios(formula=anion)

        if substance_ratios == anion_ratio:
            st.end()
            return SolubilityTable.Ion(composition=compound.anion, charge=compound.anion_charge)
    else:
        st.end()
        raise OutOfOptions(formula=formula, function_name='get_anion', variables=locals())


@type_check_decorator
def get_cations(formula: str) -> List[SolubilityTable.Ion]:
    """
    Since there are elements that form multiple cations, such as Al(1) and Al(3), it is very hard to deduce what
    charge the cation has in the molecule, as this requires knowledge about indices of both cation and anion that is
    quite hard to obtain.

    Instead, this function just searches for all cations of that element and returns a list of them.

    :param formula: formula for which cations must be found.
    :return: a list of SolubilityTable.Ion instances, cations formed by the first chemical element in the formula.
    """

    first_element = _remove_first_element(formula, return_first_element=True)['first element']

    st = SolubilityTable()
    st.begin()
    possible_cations = st.select_ion(cation=first_element)
    st.end()

    if possible_cations:
        return possible_cations
    else:
        raise OutOfOptions(formula, function_name='get_cations', variables=locals())


@type_check_decorator
def parse_simple_molecule(simple_formula: str) -> Simple:
    """
    Converts a formula of a simple substance into an instance of Simple class. Since the formula of a simple substance
    always consists of one element and one number, it can be split. First, the first (and the only) element is removed
    by _remove_first_element and, second, the rest of the formula is slices to get the number as a string. The number
    is converted into an integer, and if the length of the formula is equal to the length of the element,
    which actually means that there's no number, then the number is set to 1.

    :param simple_formula: formula of a simple substance to be converted into Simple instance.
    :return: an instance of Simple.
    """

    composition = parse_formula(simple_formula)

    if len(composition) > 1:
        ivf = InvalidFormula(simple_formula, variables=locals())
        ivf.description += '\nNOTE: You passed a molecular formula of a complex substance to a function that parses simple molecules.'
        raise ivf
    elif len(composition) == 0:
        ivf = InvalidFormula(simple_formula, variables=locals())
        ivf.description += '\nNOTE: You passed a an empty string to a function that parses simple molecules.'
        raise ivf

    element = _remove_first_element(simple_formula, return_first_element=True)['first element']
    index = int(simple_formula[len(element):] if len(element) < len(simple_formula) else '1')
    real_element = pt.Element.get_by_symbol(element)

    return Simple(real_element, index)


@type_check_decorator
def parse_complex_molecule(formula: str) -> Molecule:
    def create_molecule(cation: SolubilityTable.Ion, anion: SolubilityTable.Ion) -> Molecule:
        m = Molecule.from_string(cation.composition, cation.charge, anion.composition, anion.charge)
        return m

    composition = parse_formula(formula)

    if len(composition) == 1:
        ivf = InvalidFormula(formula, variables=locals())
        ivf.description += '\nNOTE: You passed a molecular formula of a simple substance to a function that parses complex molecules.'
        raise ivf
    elif len(composition) == 0:
        ivf = InvalidFormula(formula, variables=locals())
        ivf.description += '\nNOTE: You passed a an empty string to a function that parses simple molecules.'
        raise ivf

    cations = get_cations(formula)
    anion = get_anion(formula)

    for cation in cations:
        m = create_molecule(cation, anion)  # cannot use Molecule's constructor, because cation and anion are instances of SolubilityTable.Ion
        if m.formula() == formula:
            return m
    else:
        raise InvalidFormula(formula, variables=locals())


@type_check_decorator
def parse(formula: str) -> Union[Simple, Molecule]:
    string_composition = parse_formula(formula)

    if len(string_composition) > 1:
        return parse_complex_molecule(formula)
    else:
        return parse_simple_molecule(formula)


"""
formula = "S8"
molecule = parse_complex_molecule(formula)
print(molecule.formula())
"""
