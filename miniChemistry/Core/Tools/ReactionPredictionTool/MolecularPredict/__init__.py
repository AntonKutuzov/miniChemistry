from miniChemistry.Core.ReactionMechanisms.MolecularMechanisms import *
from miniChemistry.Core.ReactionMechanisms.MolecularMechanisms.ExceptionalMechanisms import _is_nitrate
from miniChemistry.Utilities.File import File

from typing import Optional


file = File(caller=__file__, splitter=',')
file.bind('MechanismsAndRestrictions.csv')

mechanism_dict = {
    "SE": simple_exchange,
    "SA": simple_addition,
    "SD": simple_decomposition,
    "SS": simple_substitution,

    "CA": complex_addition,
    "CD": complex_decomposition,
    "CN": complex_neutralization,

    "ND": nitrate_decomposition
}

restriction_dict = {
    "WER": weak_electrolyte_restriction,
    "MAR": metal_activity_restriction,
    "MAW": metal_and_water_restriction,
    "None": lambda *args, **kwargs: True
}


def effective_class(sub: Optional[Molecule | Simple]) -> str:
    salt_acid_prefix = lambda s: 'ternary' if s.size == 3 else 'binary'

    if _is_nitrate(sub):
        return 'nitrate'
    elif sub == Molecule.water:
        return 'water'
    elif sub is None:
        return "none"

    match sub.simple_class:
        case 'oxide':
            return sub.simple_subclass
        case 'acid':
            return salt_acid_prefix(sub) + ' acid'
        case 'salt':
            return salt_acid_prefix(sub) + ' salt'
        case _:
            return sub.simple_class