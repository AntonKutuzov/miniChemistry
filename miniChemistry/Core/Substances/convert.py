import miniChemistry.Core.Database.ptable as pt
from miniChemistry.Core.CoreExceptions.stableExceptions import SubstanceNotFound
from miniChemistry.Core.Database.stable import SolubilityTable
from miniChemistry.Core.CoreExceptions.SubstanceExceptions import UnsupportedSubstanceSize, SubstanceConvertionError
from miniChemistry.Core.Substances._helpers import _select_suitable_charge, _string_to_elementary_composition
from miniChemistry.MiniChemistryException import NotSupposedToHappen
from miniChemistry.Core.Substances import Ion, Simple, Molecule, IonGroup

from chemparse import parse_formula


def add_group(iig: Ion | IonGroup) -> IonGroup | Molecule:
    if isinstance(iig, (Ion, IonGroup)):
        return _alter_group(iig, inc=True)
    else:
        raise Exception(f'Wrong type: expected "Ion" or "IonGroup", got {type(iig)}.')

def remove_group(mig: Molecule | IonGroup) -> Ion | IonGroup:
    if isinstance(mig, (Molecule, IonGroup)):
        return _alter_group(mig, inc=False)
    else:
        raise Exception(f'Wrong type: expected "Molecule" or "IonGroup", got {type(mig)}.')

# circular import problem. Importing inside the method breaks isinstance() which is needed later
def _alter_group(mig: Molecule|IonGroup|Ion,
                 inc: bool
                 ) -> Molecule|IonGroup|Ion:

    # from miniChemistry.Core.Substances import IonGroup, Molecule, Ion

    if isinstance(mig, Molecule):
        alter = (1 if mig.simple_class == 'acid' else 0, 1 if mig.simple_class == 'base' else 0)

        if alter == (0, 0):
            raise Exception(f'Wrong simple class: expected "acid" or "base", got: {type(mig.simple_class)}.')

        cation_index = mig.cation_index
        anion_index = mig.anion_index
        cation = mig.cation
        anion = mig.anion
        ion = mig.anion if mig.simple_class == 'acid' else mig.cation

    elif isinstance(mig, IonGroup):
        alter = (1 if mig.is_anion else 0, 1 if mig.is_cation else 0)
        cation_index = mig.cation_index
        anion_index = mig.anion_index
        cation = mig.cation
        anion = mig.anion
        ion = mig.ion

    elif isinstance(mig, Ion):
        cation_index = 1 if mig.is_cation else 0
        anion_index = 1 if mig.is_anion else 0
        alter = (anion_index, cation_index)  # we increase the one that the ion is NOT (i.e. we increase H(1) for anions and OH(-1) for cations
        ion = mig
        cation = (mig if mig.is_cation else Ion.proton)
        anion = (mig if mig.is_anion else Ion.hydroxide)

    else:
        raise Exception(f'Wrong type: expected "Ion", "Molecule" or "IonGroup", got {type(mig)}.')


    sign = 1 if inc else -1
    cation_index, anion_index = cation_index + sign*alter[0], anion_index + sign*alter[1]
    charge = cation_index * cation.charge + anion_index * anion.charge


    if any([cation_index == 0, anion_index == 0]):
        return ion
    elif not charge == 0:
        return IonGroup(ion, cation_index, anion_index)
    else:
        return Molecule(cation, anion)


def simple(substance: Ion|pt.Element) -> Simple:
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



def ion(substance: Simple | pt.Element | SolubilityTable.Ion,
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

def st_substance(m: Molecule) -> SolubilityTable.Substance:
    """
        Converts the instance of Molecule into an instance of SolubilityTable.Substance.

        :param m: instance of Molecule to convert into SolubilityTable.Substance
        :return: an instance of SolubilityTable.Substance
        """

    cation = m.cation.formula(remove_charge=True)
    anion = m.anion.formula(remove_charge=True)
    cation_charge = m.cation.charge
    anion_charge = m.anion.charge

    st = SolubilityTable()
    molecules = st.select_substance(cation, cation_charge, anion, anion_charge)

    if len(molecules) > 1:
        nsth = NotSupposedToHappen(variables=locals())
        nsth.description += (f'\nIt seems like there are two identical substances in the solubility table database.\n'
                             f'The formula is {m.formula()}.')
        raise nsth
    elif not molecules:
        raise SubstanceNotFound(substance_signature=[m.formula()], variables=locals())
    else:
        molecule = molecules[0]
        return molecule

def st_ion(i: Ion) -> SolubilityTable.Ion:
    sti = SolubilityTable.Ion(
        composition=i.formula(remove_charge=True),
        charge=i.charge
    )

    return sti

# ====================================================================================================== is_gas FUNCTION


def is_gas(substance: Molecule | Simple) -> bool:
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
