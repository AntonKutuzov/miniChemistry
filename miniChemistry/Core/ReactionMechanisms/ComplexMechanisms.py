"""
Complex mechanisms handle the cases where simple mechanisms cannot succeed. Namely, those are reactions of basic and
acidic oxides, AND decomposition reactions of three-element molecules.

NOTE FOR CHEMISTS: The mechanisms are called "complex" because each of them uses one of the simple mechanisms. The
complex mechanisms have nothing to do with complex substances (like K[Al(OH)4]).


COMPLEX DECOMPOSITION
Complex_decomposition mechanism has to handle the following reactions:
- decomposition of 3-element salts      | Na2SO3 -> Na2O + SO2  | K3PO4 -> K2O + P2O5   |
- decomposition of oxoacids             | H2SO4 -> H2O + SO3    | H2CO3 -> H2O + CO2    |
- decomposition of bases                | NaOH -> Na2O + H2O    | Zn(OH)2 -> ZnO + H2O  |

NOTE: oxoacids are the acids that contain oxygen, e.g. H2SO4, but not HCl.

From chemical point of view, simple decomposition handles the opposite reaction of what the first case of complex
neutralization does. Looking carefully, you can see that in all three cases a 3-element molecule decomposes into two
2-element molecules, namely, always oxides.

Since simple decomposition handles only decomposition of 2-element molecules, these cases had to  be handled separately.
(And there's indeed a reason for why it wasn't convenient to join them all in one method).


COMPLEX ADDITION
Complex addition mechanism has to handle the following reactions:
- addition of basic/acidic oxide to water       | Na2O + H2O -> NaOH | SO3 + H2O -> H2SO4
- reaction of acidic and basic oxides           | Na2O + SO3 -> Na2SO4

It can be easily seen that in the first case the product is just an acid/base corresponding to the oxide (which,
in fact, is a property of these oxides). In the second case the product is equal to the product of a simple
exchange reaction between the respective acid and base.


COMPLEX NEUTRALIZATION
Complex_neutralization mechanism has to handle the following reactions:
- basic oxide + acidic oxide    | Na2O + SO2 -> Na2SO3  | ZnO + P2O5 -> Zn3(PO4)2 (redirected to complex addition)
- basic oxide + acid            | Na2O + H2SO4 -> Na2SO4 + H2O
- base + acidic oxide           | Ba(OH)2 + CO2 -> BaCO3 + H2O
- (base + acid) is considered by the simple_exchange mechanism

Complex neutralization can be thought of as an extension of the conventional neutralization reaction – acid + base.
From chemical point of view, these reactions are very similar – in all four (given above) a substance with basic
nature (base, basic oxide) reacts with a substance with acidic nature (acid, acidic oxide).

A careful look at the substances will show that the products of the three reactions follow the logic of simple exchange
when done with neutralization. Acid + base -> salt + water. So, to implement the mechanisms it is enough to run a
simple exchange reaction between the corresponding acid and/or base and return the products. With some corrections,
this approach works.

NOTE: acidic oxide + basic oxide is also available in complex neutralization reaction to maintain logical
consistency: in fact this reaction falls equally well to both kinds of reactions, so it is also available in both.
"""


from miniChemistry.Core.ReactionMechanisms.SimpleMechanisms import simple_exchange
from miniChemistry.Core.CoreExceptions.MechanismExceptions import WrongSimpleClass, WrongSimpleSubclass
from miniChemistry.MiniChemistryException import NotSupposedToHappen
from miniChemistry.Core.Database.AcidsTable import AcidsTable
from miniChemistry.Core.Database.BasesTable import BasesTable
from miniChemistry.Core.Substances import Molecule

from typing import Tuple, Any


act = AcidsTable()
bct = BasesTable()


def _oxide_to_molecule(sub: Molecule) -> Molecule:
    """
    Takes in an oxide, either basic or acidic, and returns a respective molecule – either base or acid.

    :param sub: an oxide
    :return: an acid/base
    """

    simple_subclass = sub.simple_subclass

    if simple_subclass == 'acidic oxide':
        return act.acid(sub)
    elif simple_subclass == 'basic oxide':
        return bct.base(sub)
    else:
        raise WrongSimpleSubclass(formula=sub.formula(),
                                  simple_subclass=simple_subclass,
                                  expected_subclass="'acidic oxide' or 'basic oxide'",
                                  variables=locals())



def complex_decomposition(sub: Molecule, *args: Any) -> Tuple[Molecule, Molecule]:
    """
    Computes the products of decomposition of three-element molecule into oxides. The algorithm is based on an
    observation that

    - bases decompose into basic oxides and water
    - acids decompose into acidic oxides and water
    - salts decompose into acidic and basic oxides

    All these substances can be obtained by using AcidsTable and BasesTable.

    :param sub: a 3-element molecule (instance of Molecule)
    :return: A tuple with two Molecule instances that are both oxides
    """

    simple_class = sub.simple_class

    match simple_class:
        case 'acid':
            acidic_oxide = act.acidic_oxide(sub)
            return acidic_oxide, Molecule.water

        case 'base':
            basic_oxide = bct.basic_oxide(sub)
            return basic_oxide, Molecule.water

        case 'salt':
            basic_oxide = bct.basic_oxide(sub.cation)
            acidic_oxide = act.acidic_oxide(sub.anion)
            return basic_oxide, acidic_oxide

        case _:
            raise WrongSimpleClass(formula=sub.formula(), simple_class=sub.simple_class,
                                   expected_class="'acid', 'base' or 'salt'", variables=locals())



def complex_addition(acidic_oxide: Molecule, basic_oxide: Molecule) -> Tuple[Molecule]:
    """
    Takes in two instances of Molecule, always oxides, and returns a single molecule, the result of their reaction.
    For reaction involving water the mechanism returns just the acid or base, corresponding to the non-water oxide.
    A separate function is defined to remove water from products (_remove_water()).

    For reactions that do not involve water, the oxides are converted into acid and base, and their non-water reaction
    product is returned (again, water is eliminated by using _remove_water() function).


    :param acidic_oxide: an instance of Molecule, acidic oxide or water
    :param basic_oxide: an instance of Molecule, basic oxide or water
    :return: an instance of Molecule

    NOTE: the acidic_oxide and basic_oxide can be safely swapped, as long as the subclasses are correct, the
    function will not raise an exception.
    """

    def _remove_water(sub1: Molecule, sub2: Molecule) -> Molecule:
        """Returns the substance that is not water. If there are two water molecules, raises an exception."""
        substances = {sub1, sub2}
        substances.remove(Molecule.water)

        try:
            return substances.pop()  # .pop() returns the popped element
        except KeyError:
            wsc = WrongSimpleClass(formula=f"{sub1.formula(), sub2.formula()}", simple_class='water AND water',
                                   expected_class='any AND water', variables=locals())
            wsc.description += (f'\nThe exception is raised because a complex addition mechanism received two\n'
                                f'water molecules. Check which of your reactions has water as both reagents.')
            raise wsc


    basic_oxide_subclass = basic_oxide.simple_subclass
    acidic_oxide_subclass = acidic_oxide.simple_subclass

    if acidic_oxide == Molecule.water and basic_oxide.simple_subclass == 'basic oxide':
        return _oxide_to_molecule(_remove_water(acidic_oxide, basic_oxide)),

    elif acidic_oxide.simple_subclass == 'acidic oxide' and basic_oxide == Molecule.water:
        return _oxide_to_molecule(_remove_water(acidic_oxide, basic_oxide)),

    elif acidic_oxide == Molecule.water and basic_oxide.simple_subclass == 'acidic oxide':
        return complex_addition(basic_oxide, acidic_oxide)

    elif acidic_oxide_subclass == 'basic oxide' and basic_oxide == Molecule.water:
        return complex_addition(basic_oxide, acidic_oxide)

    elif acidic_oxide_subclass == 'acidic oxide' and basic_oxide_subclass == 'basic oxide':
        acid = act.acid(acidic_oxide)
        base = bct.base(basic_oxide)
        products = simple_exchange(acid, base)
        return _remove_water(*products),  # simple exchange should always return two substances

    elif acidic_oxide_subclass == 'basic oxide' and basic_oxide_subclass == 'acidic oxide':
        return complex_addition(basic_oxide, acidic_oxide)

    else:
        if not acidic_oxide_subclass == 'acidic oxide' and not acidic_oxide == Molecule.water:
            raise WrongSimpleSubclass(formula=acidic_oxide.formula(),
                                      simple_subclass=acidic_oxide_subclass,
                                      expected_subclass="'acid' or 'acidic oxide'",
                                      variables=locals())
        if not basic_oxide_subclass == 'basic oxide' and not basic_oxide == Molecule.water:
            raise WrongSimpleSubclass(formula=basic_oxide.formula(),
                                      simple_subclass=basic_oxide_subclass,
                                      expected_subclass="'base' or 'basic oxide'",
                                      variables=locals())
        else:
            # I mean, either 'acid' and 'bas' are there, or they are not. What option is left?
            raise NotSupposedToHappen(variables=locals())



def complex_neutralization(acidic_substance: Molecule, basic_substance: Molecule) -> Tuple[Molecule, ...]:
    """
    The method takes two molecules – one of acidic nature, one of basic nature – and returns the product of their
    reaction. The algorithm involves three possible scenarios: the classes are ordered correctly, the classes are
    ordered reversely, the classes are such that the substances are passed to complex addition, and all others.

    In the first case, the function converts an oxide into an acid/base, and uses simple_exchange to predict their
    products.
    In the second case, the function returns the result of itself (recursion) with swapped reagents (i.e. now they are
    in the correct order).
    In the third case the function returns the result of complex_addition().
    In the fourth case the function raises a WrongSimpleSubclass exception.

    :param acidic_substance: an instance of Molecule, representing acid, acidic oxide, or water
    :param basic_substance: an instance of Molecule, representing base, basic oxide, or water
    :return: A tuple with one or two instances of Molecule

    NOTE: the parameters can be safely swapped (i.e. a base can be passed for acidic_substance). As long as the simple
    subclasses are correct, the function will not raise an exception.
    """

    acidic_substance_subclass = acidic_substance.simple_subclass
    basic_substance_subclass = basic_substance.simple_subclass
    subclasses = (acidic_substance_subclass, basic_substance_subclass)

    right_conditions = [ ('acid', 'basic oxide'), ('acidic oxide', 'base') ]
    wrong_conditions = [ ('base', 'acidic oxide'), ('basic oxide', 'acid') ]
    addition_conditions = [ ('acidic oxide', 'basic oxide'), ('basic oxide', 'acidic oxide') ]

    if subclasses in right_conditions:
        acid = acidic_substance if acidic_substance.simple_class == 'acid' else act.acid(acidic_substance)
        base = basic_substance if basic_substance.simple_class == 'base' else bct.base(basic_substance)
        return simple_exchange(acid, base)

    elif subclasses in wrong_conditions:
        return complex_neutralization(basic_substance, acidic_substance)

    elif subclasses in addition_conditions:
        return complex_addition(acidic_substance, basic_substance)  # the comma is needed to return a tuple

    else:
        if 'acid' not in acidic_substance_subclass:
            raise WrongSimpleSubclass(formula=acidic_substance.formula(),
                                      simple_subclass=acidic_substance_subclass,
                                      expected_subclass="'acid' or 'acidic oxide'",
                                      variables=locals())
        if 'bas' not in basic_substance_subclass:  # because this is common part for 'BASe' and 'BASic'
            raise WrongSimpleSubclass(formula=basic_substance.formula(),
                                      simple_subclass=basic_substance_subclass,
                                      expected_subclass="'base' or 'basic oxide'",
                                      variables=locals())
        else:
            # I mean, either 'acid' and 'bas' are there, or they are not. What option is left?
            raise NotSupposedToHappen(variables=locals())


"""
Testing the following reactions (reagents do not include water and nitrates or nitric acid):
    COMPLEX DECOMPOSITION
 - salt -> acidic oxide + basic oxide
 - base -> basic oxide + water
 - acid -> acidic oxide + water


    COMPLEX NEUTRALIZATION
 - base + acidic oxide -> salt + water
 - basic oxide + acidic oxide -> salt
 - basic oxide + acid -> salt + water
"""
"""
salt = Molecule.from_string('Zn', 2, 'SO4', -2)
base = Molecule.from_string('Ba', 2, 'OH', -1)
acid = Molecule.from_string('H', 1, 'CO3', -2)

acidic_oxide = Molecule.from_string('P', 5, 'O', -2)
basic_oxide = Molecule.from_string('Na', 1, 'O', -2)


decomposition_reagents = [salt, acid, base]
neutralization_reagents = [(base, acidic_oxide), (basic_oxide, acidic_oxide), (basic_oxide, acid),
                           (acidic_oxide, base), (acidic_oxide, basic_oxide), (acid, basic_oxide)]

print('COMPLEX DECOMPOSITION REACTION TESTING...')
for reagent in decomposition_reagents:
    reaction = reagent.formula() + ' -> '
    products = complex_decomposition(reagent)
    reaction += products[0].formula() + ' + ' + products[1].formula()
    print('\t', reaction)

print('NEUTRALIZATION REACTION TESTING...')
for reagents in neutralization_reagents:
    reaction = reagents[0].formula() + ' + ' + reagents[1].formula() + ' -> '
    products = complex_neutralization(*reagents)

    for p in products:
        reaction += p.formula() + ' + '

    reaction = reaction.strip(' + ')
    print('\t', reaction)
"""
