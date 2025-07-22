from miniChemistry.Core.Substances import Molecule, IonGroup, Ion
from miniChemistry.Core.Substances.convert import add_group, remove_group
from typing import Tuple


def _join_identical_ion(
        ig: IonGroup|Molecule
        ) -> IonGroup|Molecule:

    cation = ig.cation
    anion = ig.anion

    if isinstance(cation, IonGroup):
        if anion == Ion.hydroxide:
            return add_group(cation)
        else:
            return ig

    elif isinstance(anion, IonGroup):
        if cation == Ion.proton:
            return add_group(anion)
        else:
            return ig

    else:
        return ig


def ionic_decomposition(
                    m: Molecule|IonGroup
                ) -> Tuple[Ion, IonGroup|Ion]:
    if isinstance(m, Molecule):
        if m.simple_class == "acid":
            # return Ion.proton, IonGroup(m.anion, m.cation_index-1, m.anion_index)
            return Ion.proton, remove_group(m)

        elif m.simple_class == "base":
            # return Ion.hydroxide, IonGroup(m.cation, m.cation_index, m.anion_index-1)
            return Ion.hydroxide, remove_group(m)

        elif m.simple_class == "salt":
            return m.cation, m.anion

        else:
            raise Exception(f'The provided substance does not dissociate into ions: {m.formula()}.')

    elif isinstance(m, IonGroup):
        return m.ion, remove_group(m)


def ionic_addition(
                    i1: Ion,
                    i2: Ion|IonGroup
                ) -> Tuple[Molecule|IonGroup]:

    if i1.charge > 0 > i2.charge:
        cation, anion = i1, i2
    elif i1.charge < 0 < i2.charge:
        cation, anion = i2, i1
    else:
        raise Exception('Cannot use ions of the same charge in ionic_addition mechanism.')

    if isinstance(i1, Ion) and isinstance(i2, Ion):
        if cation == Ion.proton and abs(anion.charge) > 1:
            return IonGroup(anion, 1, 1),
        elif anion == Ion.hydroxide and abs(cation.charge) > 1:
            return IonGroup(cation, 1, 1),
        else:
            return Molecule(cation, anion),

    elif isinstance(i1, Ion) and isinstance(i2, IonGroup):
        m = Molecule(cation, anion)
        return _join_identical_ion(m),

    elif isinstance(i1, IonGroup) and isinstance(i2, Ion):
        return ionic_addition(i2, i1)

    else:
        raise Exception(f'Wrong types: expected "Ion" and "Ion" or "IonGroup", got {type(i1), type(i2)}.')
