from miniChemistry.Core.ReactionMechanisms.MolecularMechanisms import *
from miniChemistry.Core.ReactionMechanisms.RedoxMechanisms.BasicRedoxAddition import basic_redox_addition
from miniChemistry.Utilities.File import File

from typing import Optional


file = File(caller=__file__, splitter=',')
file.bind('MechanismsAndRestrictions.csv')

mechanism_dict = {
    "BRA": basic_redox_addition,
}

restriction_dict = {
    "None": lambda *args, **kwargs: True
}


def effective_class(sub: Optional[Molecule | Simple]) -> str:
    return 'any'