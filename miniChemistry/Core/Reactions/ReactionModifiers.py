from miniChemistry.Core.Reactions import IonGroupReaction, MolecularReaction
from miniChemistry.Core.Substances import Molecule
from miniChemistry.Core.ReactionMechanisms.MolecularMechanisms import weak_electrolyte_restriction
from miniChemistry.Core.ReactionMechanisms.IonGroupMechanisms import complete_dissociation


def essential_equation(r: IonGroupReaction | MolecularReaction) -> IonGroupReaction:
    reagents = complete_dissociation(*r.reagents)
    essential_products = []
    essential_reagents = []

    for s in r.products:
        if isinstance(s, Molecule) and weak_electrolyte_restriction(s, raise_exception=False):
            essential_products.append(s)

    if len(essential_products) == 1:
        essential_reagents.extend(complete_dissociation(essential_products[0]))

        for reagent in essential_reagents:
            if reagent not in reagents:
                raise Exception(f'Could not find essential equation for "{r.scheme}".\n'
                                f'Could not find reagent {reagent.formula()} in the list of reagents {[i.formula() for i in reagents]}.')
    else:
        raise Exception('"essential_equation" function only accepts reactions with one weak electrolyte in the products.')


    ir = IonGroupReaction(reagents=essential_reagents, products=essential_products)
    return ir
