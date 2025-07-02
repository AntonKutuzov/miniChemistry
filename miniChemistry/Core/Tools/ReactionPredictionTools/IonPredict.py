from miniChemistry.Core.Substances import Molecule, Ion, IonGroup, st_substance
from miniChemistry.Core.Database.stable import SolubilityTable
from typing import Set, Tuple


def solubility_check(m: Molecule,
                     *,
                     solubilities: Set[str] = None,
                     avoid: Set[str] = None
                     ) -> bool:
    st = SolubilityTable()
    s = st_substance(m)
    s_list = st.select_substance(*s)

    if len(s_list) > 1:
        raise Exception(f'Got more than one substance from {m.formula()} in the solubility table.')
    else:
        if solubilities and avoid:
            raise Exception('"Solubility_check" either accepts "solubilities" keyword or "avoid", not both.')
        if solubilities:
            return s_list[0].solubility in solubilities
        elif avoid:
            return s_list[0].solubility not in avoid
        else:
            raise Exception('No solubilities were provided for "Solubility_Check".')



def dissociate(
                    m: Molecule|IonGroup,
                    completely: bool = False
                ) -> Tuple[Ion, IonGroup|Ion]:
    if m.cation_index == 1 or completely:
        new_i1 = m.cation
        new_i2 = m.anion
    elif m.cation_index > 1:
        new_i1 = m.cation
        new_i2 = IonGroup(m.cation, m.cation_index - 1, m.anion, m.anion_index)
    else:
        raise Exception(f'Got non-positive cation index in molecule: {m.formula()}.')

    return new_i1, new_i2


def associate(
                    cation: Ion, anion: Ion|IonGroup|Molecule,
                    completely: bool = False
                ) -> Molecule|IonGroup:
    if isinstance(anion, IonGroup):
        if completely:
            return Molecule(cation, anion.anion)
        else:
            return IonGroup(cation=cation, cation_index=anion.cation_index+1, anion=anion.anion, anion_index=1)
    elif isinstance(anion, Ion):
        if completely or abs(cation.charge) == abs(anion.charge):
            return Molecule(cation, anion)
        else:
            return IonGroup(cation=cation, cation_index=1, anion=anion, anion_index=1)
    else:
        raise Exception(f'Wrong anion type: expected Ion or IonGroup, got {type(anion)}.')


def _ionic_addition(i1: Ion, i2: Ion) -> Molecule:
    return Molecule(i1, i2)  # only if m is insoluble

def _ionic_substitution(m: Molecule, i: Ion) -> Tuple[Molecule, Ion]:
    if i.charge > 0:  # for cations
        new_m = _ionic_addition(i, m.anion)
        new_i = m.cation
    else:             # for anions
        new_m = _ionic_addition(m.cation, i)
        new_i = m.anion

    return new_m, new_i


def ion_predict(*reagents,
                ignore_restrictions: bool = False,
                complete_reaction: bool = False,
                dissociation_set: Set[str] = None,
                association_set: Set[str] = None
                ) -> Tuple[Ion|IonGroup, Ion] | Tuple[IonGroup] | Tuple[Molecule]:

    if dissociation_set is None:
        dss = {'SS', 'NS', 'ND', 'RW'}
    else:
        dss = dissociation_set  # dissociation solubility set

    if association_set is None:
        ass = {'SL'}
    else:
        ass = association_set  # association solubility set

    if len(reagents) == 1:
        if not ignore_restrictions and solubility_check(reagents[0], solubilities=dss):
            raise Exception('Molecules that are not soluble do not dissociate.')
        return dissociate(*reagents, completely=complete_reaction)

    elif len(reagents) > 1:
        product = associate(*reagents, completely=complete_reaction)
        if not ignore_restrictions and solubility_check(product, solubilities=ass):
            raise Exception('Molecule obtained after association is soluble.')
        else:
            return product,  # comma is needed to treat the return value as a tuple

    else:
        raise Exception('To predict a reaction, at least one reagents is needed.')
