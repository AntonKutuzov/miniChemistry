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
