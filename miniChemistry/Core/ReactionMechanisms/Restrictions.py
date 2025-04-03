"""
In some cases, where the common mechanisms (which means, also those that are described in this module) predict the
outcome, the products might not form, or might react back to reagents. Iin both cases (in this module, not in
chemistry) we would say that the reaction will not proceed.

To estimate whether the reaction products can be formed, several checks are imposed on the reagents or the products. There
are three tests that in this module are called "reaction restrictions". Namely, those are

- Weak electrolyte restriction. There is a rule in chemistry that the ion exchange reaction (simple exchange in this
module) proceeds only if a weak electrolyte is formed. Namely, those usually are either water, or gas, or precipitate
(insoluble substance).

- Metal strength restriction. Another rule, which follows from the metal activity series, is that only the metals that
are more active than hydrogen, can react with acids. Another formulation (more general) is that more active metal tends
to replace less active in a molecule (salt or acid). Hence, it has to be checked that the metal to be placed is more
active than the metal in the molecule.

- Metal and water restriction. This is an exception to the previous rule. In some cases water can be treated as a weak
acid. That means, it can also react with metals, forming the same products as real acids do. However, due to low strength
of water as an acid, it only reacts with active metals. Hence, if there's a reaction of water with metal, it has to be
checked that the metal is among active metals.

Since those are tests, that indicate whether a reaction will proceed, they return a boolean value with True for "yes"
and False for "no". The signatures are the following:

weak_electrolyte_restriction(*products: Union[Simple, Molecule], raise_exception: bool = False) -> bool
metal_activity_restriction(*products: Union[Simple, Molecule], raise_exception: bool = False) -> bool
metal_and_water_restriction(sub: [Simple, Molecule], metal: [Simple, Molecule], raise_exception: bool = False) -> bool

NOTE: some reactions do not need restrictions and always proceed.
"""


from miniChemistry.Core.CoreExceptions.stableExceptions import SubstanceNotFound
from miniChemistry.Core.Database.MetalActivitySeries import MetalActivitySeries
from miniChemistry.Core.Substances import Molecule, Simple, is_gas, simple
from miniChemistry.Core.Database.stable import SolubilityTable
from miniChemistry.MiniChemistryException import NotSupposedToHappen

from miniChemistry.Core.CoreExceptions.MechanismExceptions import WeakElectrolyteNotFound, LessActiveMetalReagent, WrongSimpleClass, \
    WrongMetalActivity
from typing import Union



def _molecule_to_stable_substance(m: Molecule) -> SolubilityTable.Substance:
    """
    Converts the instance of Molecule into an instance of SolubilityTable.Substance.

    :param m: instance of Molecule to convert into SolubilityTable.Substance
    :return: an instance of SolubilityTable.Substance
    """

    cation = m.cation.formula(remove_charge=True)
    anion = m.anion.formula(remove_charge=True)
    cation_charge = m.cation.charge
    anion_charge = m.anion.charge

    st = SolubilityTable()
    st.begin()
    molecules = st.select_substance(cation, cation_charge, anion, anion_charge)
    st.end()

    if len(molecules) > 1:
        nsth = NotSupposedToHappen(variables=locals())
        nsth.description += (f'\nIt seems like there are two identical substances in the solubility table database.\n'
                             f'The formula is {m.formula()}.')
        raise nsth
    elif not molecules:
        raise SubstanceNotFound(substance_signature=[m.formula()], variables=locals())
    else:
        molecule = molecules[0]
        return molecule




def weak_electrolyte_restriction(*products: Union[Simple, Molecule], raise_exception: bool = False) -> bool:
    """
    Checks the product for presence of a weak electrolyte (water, gas or precipitate)
    NOTE: due to implementation of a function is_gas, this check may sometimes give false results.

    :param products: instances of Simple or Molecule which has to be checked for presence of a weak electrolyte
    :param raise_exception: True if exception has to be raised in case of absence of a weak electrolyte
    :return: True if electrolyte is present and False if not (True if reaction will proceed, False if not)
    """

    for product in products:
        if product == Molecule.water:
            return True
        elif is_gas(product):
            return True
        else:
            m = _molecule_to_stable_substance(product)
            if m.solubility in {'NS', 'SS'}:
                return True
            else:
                continue
    else:
        if raise_exception:
            raise WeakElectrolyteNotFound(products=[p.formula() for p in products], variables=locals())
        else:
            return False




def metal_activity_restriction(sub: Union[Simple, Molecule], metal: Union[Simple, Molecule], raise_exception: bool = False) -> bool:
    """
    Checks that the activity of a Simple metal is larger than the activity of a metal from Molecule instance.
    NOTE: sub and metal parameters can be safely swapped.

    :param sub: instance of Molecule
    :param metal: instance of Simple (necessarily metal)
    :param raise_exception: True if exception is to be raised when (Simple) metal has lower activity
    :return: True if the (Simple) metal has larger activity, else False (True if reaction will proceed, False if not)
    """

    if isinstance(sub, Molecule) and isinstance(metal, Simple):
        mas = MetalActivitySeries()
        molecule_metal = simple(sub.cation)
        active_one = mas.more_active(molecule_metal.element, metal.element)

        if active_one == metal.element:
            return True
        elif raise_exception:
            raise LessActiveMetalReagent(metal=metal.formula(), molecule=sub.formula(), variables=locals())
        else:
            return False

    elif isinstance(sub, Simple) and isinstance(metal, Molecule):
        return metal_activity_restriction(metal, sub)

    else:
        nsth = NotSupposedToHappen(variables=locals())
        nsth.description += (f'\nIf you see this message that means something is wrong with the type_check_decorator,\n'
                             f'because usually it should have raised a DecoratedTypeError due to wrong data types.')
        raise nsth



def metal_and_water_restriction(*products: Union[Molecule, Simple], raise_exception: bool = False) -> bool:
    """
    Checks that metal that reacted with water is active. Since product of a reaction of metal with water is a base,
    the function takes base's cation and check's activity of its metal.

    :param products: instances of Molecule and Simple where a base (Molecule) is to be found
    :param raise_exception: True if exception is to be raised if the metal is not active, else False
    :return: True if the metal is active, False if not (True if reaction will proceed, False if not)
    """

    for product in products:
        if product.simple_class == 'base':
            mas = MetalActivitySeries()
            metal = product.cation.elements[0]  # must always be 1
            activity = mas.activity(metal)

            if activity == 'active':
                return True
            elif raise_exception:
                raise WrongMetalActivity(metal=metal.symbol, variables=locals())
            else:
                return False
    else:
        raise WrongSimpleClass(formula=','.join([p.formula() for p in products]),
                               simple_class=','.join([p.simple_class for p in products]),
                               expected_class='base',
                               variables=locals())
