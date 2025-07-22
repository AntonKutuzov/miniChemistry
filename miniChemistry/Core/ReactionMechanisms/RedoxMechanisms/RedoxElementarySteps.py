from miniChemistry.Core.Reactions import HalfReaction, RedoxReaction, MathReaction, IonGroupReaction
from miniChemistry.Core.Substances import Ion, Molecule, IonGroup
from miniChemistry.Core.ReactionMechanisms.IonGroupMechanisms import ionic_decomposition

from typing import Literal, List

from miniChemistry.MiniChemistryException import NotSupposedToHappen


def complete_dissociation(*ions: IonGroup|Ion|Molecule) -> List[Ion]:
    ions = list( ions )

    while any([isinstance(i, (IonGroup, Molecule)) for i in ions]):
        for i in ions:
            if isinstance(i, (IonGroup, Molecule)):
                ions.remove(i)
                ions += list( ionic_decomposition(i) )

    ions = list(set(ions))
    return ions

def redox_medium(r: HalfReaction | RedoxReaction | MathReaction) -> Literal['acidic', 'basic', 'neutral', 'unknown']:
    if Ion.proton in r.reagents:
        return 'acidic'
    elif Ion.hydroxide in r.reagents:
        return 'basic'
    elif Molecule.water in r.reagents:
        return 'neutral'
    else:
        return 'unknown'


def essential_equation(r: IonGroupReaction | RedoxReaction) -> IonGroupReaction:
    reagents = complete_dissociation(*r.reagents)
    products = complete_dissociation(*r.products)
    ions = complete_dissociation(*r.substances)

    print([i.formula() for i in reagents])
    print([i.formula() for i in products])

    for i in ions:
        if i in reagents and i in products:
            reagents.remove(i)
            products.remove(i)

    print([i.formula() for i in reagents])
    print([i.formula() for i in products])
