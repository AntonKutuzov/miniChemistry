"""
Predict.py contains one (actially, two) function (called "predict") that takes in reagents and returns products of a
reaction. It is a  compilation of the whole Core/ReactionMechanisms submodule which uses all reaction mechanisms and
reaction restrictions.

The file uses MechanismsAndRestrictions.csv file to determine what mechanism and what restriction to apply to the
reagents. The file was made by manually considering all possible chemical reaction types (within this module) and
contains 40 different pathways. To make this possible, all substances are divided into several so-called effective
classes (because their real classes are given by "simple_subclass" property). There are X effective classes, namely

ternary acid
binary acid
base
ternary salt
binary salt
basic oxide
acidic oxide
metal
nonmetal
water
nitrate

The water and nitrate are separate classes, because in chemistry they are also exceptions and thus do not obey the
simple rules coded in this module, and hence have to be handled separately. Each line in the csv file consists of
four items:

effective class 1, effective class 2, mechanism, restriction

That means, each combination of the effective classes for which a reaction could proceed in real life, AND which was
possible to code with the reaction mechanisms of this module, was given a mechanism and, if needed, restriction.

The code below reads this file into a dictionary with classes forming a key and mechanism with restriction forming a
value. In each class pair, they are also reversed so that the order of the reagents does not matter.

The code below contains two functions – _effective_class() which takes in a molecule and returns a string (with the
respective effective class), and predict() which actually takes in reagents and returns products. The code also contains
some commented example code, which prints all possible reaction types. Note, that if it writes that 'could not
predict reaction products" can mean either that the mechanism of the reaction is not supported, or that the reaction
would not happen in real life.
"""


import csv
from miniChemistry.Core.ReactionMechanisms.MolecularMechanisms.ExceptionalMechanisms import nitrate_decomposition, _is_nitrate
from miniChemistry.Core.ReactionMechanisms.MolecularMechanisms.SimpleMechanisms import *
from miniChemistry.Core.ReactionMechanisms.MolecularMechanisms.ComplexMechanisms import *
from miniChemistry.Core.ReactionMechanisms.MolecularMechanisms.Restrictions import *
from miniChemistry.Core.CoreExceptions.MechanismExceptions import *
from miniChemistry.Core.Substances import Molecule, Simple

from pathlib import Path


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

decision_dict = {}


# =================================================================================== reading the data from the csv file

p = Path(__file__).resolve().parent.parent
path = p / 'MechanismsAndRestrictions.csv'
# file = open(str(p.parent) + '/MechanismsAndRestrictions.csv', mode='r')
file = open(path, mode='r')

reader = csv.reader(file)
next(reader)  # skip table's header

for line in reader:
    class1, class2, mechanism, restriction = line[0].split(';')

    reaction_signature = (class1.lower(), class2.lower())
    reversed_signature = (class2.lower(), class1.lower())
    mr_dict = {'mechanism': mechanism_dict[mechanism], 'restriction': restriction_dict[restriction]}
    decision_dict[reaction_signature] = mr_dict
    decision_dict[reversed_signature] = mr_dict

file.close()
# =================================================================================== reading the data from the csv file



def _effective_class(sub: Union[Molecule, Simple, None]) -> str:
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



def predict(
        reagent1: Union[Simple, Molecule],
        reagent2: Union[Simple, Molecule, None] = None,
        *,
        ignore_restrictions: bool = False,
        ) -> Tuple[Union[Simple, Molecule], ...]:

    """
    Accepts as parameters two substances (or a substance and the None) and returns its products by calling respective
    mechanism and restriction to predict outcome of the reaction.

    :param reagent1: the first reagent, instance of Molecule or Simple
    :param reagent2: the second reagents, instance of Molecule, Simple or also None
    :param ignore_restrictions: set to True if you want to get reaction products regardless of restrictions
    :return: a tuple of Molecules and Simples. Can contain from 1 to 3 substances
    """

    # getting signature of the reaction
    signature = (_effective_class(reagent1), _effective_class(reagent2))

    # getting mechanism and restriction from the decision dict
    try:
        mechanism = decision_dict[signature]['mechanism']
        restriction = decision_dict[signature]['restriction']
    except KeyError:
        raise CannotPredictProducts(
            reagents=[reagent1.formula(), reagent2.formula() if reagent2 is not None else "None"],
            function_name="predict",
            variables=locals()
        )

    products = mechanism(reagent1, reagent2)
    no_proceed = restriction(*products, raise_exception = not ignore_restrictions)

    return products
