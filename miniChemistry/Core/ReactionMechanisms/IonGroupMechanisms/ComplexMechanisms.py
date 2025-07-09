from miniChemistry.Core.Substances import Molecule, Ion, IonGroup
from miniChemistry.Core.ReactionMechanisms.IonGroupMechanisms.SimpleMechanisms import ionic_addition
from miniChemistry.Core.Substances.convert import remove_group

from typing import Tuple, Callable, Literal


def ion_picking(
            m: Molecule|IonGroup,
            i: Ion
        ) -> Tuple[Molecule, Ion]:
    """
    Anion + Molecule -> Anion + Molecule
    Cation + Molecule -> Cation + Molecule

    :param m:
    :param i:
    :return:
    """

    if isinstance(m, (Molecule, IonGroup)) and isinstance(i, Ion):
        if i.is_cation:  # for cations
            new_m = ionic_addition(i, m.anion)

            if m.anion_index > 1:
                new_i = IonGroup(m.cation, m.cation_index, m.anion_index-1)
            else:
                new_i = m.cation

        elif i.is_anion:
            new_m = ionic_addition(m.cation, i)

            if m.cation_index > 1:
                new_i = IonGroup(m.anion, m.cation_index-1, m.anion_index)
            else:
                new_i = m.anion

        else:
            raise Exception(f'Ion {i.formula()} is neither cation, nor anion. (Used .is_cation and .is_anion properties.')

        return *new_m, new_i  # associate returns a tuple with one element

    elif isinstance(m, Ion) and isinstance(i, (Molecule, IonGroup)):
        return ion_picking(i, m)

    else:
        raise Exception(f'Invalid types for substances: expected "Molecule" and "Ion", got {type(i), type(m)}.')


# IonGroup  +  IonGroup is just not implemented yet!
def ionic_exchange(
        ig: IonGroup,
        m: Molecule | IonGroup,
        **kwargs
) -> Tuple[IonGroup|Ion, IonGroup|Ion, Molecule]:

    def effective_type(mig: Molecule | IonGroup) -> Literal['acid', 'base']:
        if isinstance(mig, Molecule):
            mig_type = mig.simple_class
        elif isinstance(mig, IonGroup):
            mig_type = mig._type
        else:
            raise Exception(f'Type of Particle for ionic_exchange must be "Molecule" or "IonGroup", not {type(mig)}.')

        if mig_type in {'acid', 'base'}:
            return mig_type
        else:
            raise Exception(f'Particle class must be "acid" or "base" for ionic_exchange, not {mig_type}.')

    if isinstance(ig, IonGroup) and isinstance(m, (Molecule, IonGroup)):
        if effective_type(m) == 'acid' and effective_type(ig) == 'base':
            cation = m
            anion = ig

        elif effective_type(m) == 'base' and effective_type(ig) == 'acid':
            cation = ig
            anion = m

        else:
            print(m.formula(), effective_type(m), ig.formula(), effective_type(ig))
            raise Exception(f'Molecule and IonGroup must be "acid" and "base", not members of the same class.')

    elif isinstance(ig, (Molecule, IonGroup)) and isinstance(m, IonGroup):
        return ionic_exchange(m, ig)

    else:
        raise Exception(f'Wrong types: expected "Molecule" and "IonGroup", got {type(ig), type(m)}.')

    while not any([isinstance(cation, Ion),
                   isinstance(anion, Ion)]):
        # if any of the two becomes an Ion, stop iterations.
        cation = remove_group(cation)
        anion = remove_group(anion)

    return cation, anion, Molecule.water


# Ion plus IonGroup decision
def i_ig_decision(
        i: Ion,
        ig: IonGroup
        ):

    water_like = {Ion.hydroxide, Ion.proton}
    ion = ig.cation if ig.cation in water_like else ig.anion

    if i in water_like and not i == ion:
        return ion_picking(ig, i)

    else:
        return ionic_addition(i, ig)
