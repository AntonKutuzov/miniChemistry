from miniChemistry.Core.ReactionMechanisms.IonGroupMechanisms import *
from miniChemistry.Utilities.File import File


file = File(caller=__file__, splitter=',')
file.bind('MechanismsAndRestrictions.csv')

mechanism_dict = {
    "IA": ionic_addition,
    "ID": ionic_decomposition,
    "IP": ion_picking,
    "IE": ionic_exchange,

    "IIGD": i_ig_decision
}

restriction_dict = {
    "WER": weak_electrolyte_restriction_for_ions,
    "None": lambda *args, **kwargs: True
}


def effective_class(i: Ion|IonGroup|Molecule) -> str:
    if isinstance(i, IonGroup):
        return 'ion group'
    elif isinstance(i, Molecule):
        return 'molecule'
    elif isinstance(i, Ion):
        return 'ion'
    else:
        raise Exception(f'Wrong data type: {type(i)}.')
