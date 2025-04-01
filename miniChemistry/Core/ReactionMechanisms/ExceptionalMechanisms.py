"""
There's one reaction type in school chemistry that is too important to omit here, but which at the same time does not
fall under any of the mentioned reaction mechanisms. This reaction type is decomposition of nitrates.

In school chemistry nitrates are almost an exception. When it comes to decomposition, nitrates follow this algorithm:

- for active metals
MeNO3 -> MeNO2 + O2
- for middle active metals
Me(NO3)2 -> MeO + NO2 + O2
- for inactive metals
Me(NO3)2 -> Me + NO2 + O2

This mechanism is implemented in nitrate_decomposition() function.
"""


from miniChemistry.Core.CoreExceptions.MechanismExceptions import WrongSimpleClass, WrongIon
from miniChemistry.Core.Database.MetalActivitySeries import MetalActivitySeries
from miniChemistry.Core.Substances import Molecule, Ion, Simple, simple, Particle
import miniChemistry.Core.Database.ptable as pt
from typing import Tuple, Any

from miniChemistry.MiniChemistryException import NotSupposedToHappen
from miniChemistry.Utilities.Checks import type_check_decorator


def _is_nitrate(m: Molecule, raise_exception: bool = False) -> bool:
    NO3 = Ion({pt.N: 1, pt.O: 3}, -1)

    try:
        anion = m.anion
    except AttributeError:
        return False

    if anion == NO3:
        return True
    elif raise_exception:
        raise WrongIon(formula=m.formula(),
                       ion=m.anion.formula(),
                       expected_ion=NO3.formula(remove_charge=False),
                       variables=locals())
    else:
        return False


@type_check_decorator
def nitrate_decomposition(nitrate: Molecule, *args: Any) -> Tuple[Particle, ...]:
    if nitrate.simple_class not in {"acid", "salt"}:
        raise WrongSimpleClass(formula=nitrate.formula(), simple_class=nitrate.simple_class,
                               expected_class="'acid' or 'salt'", variables=locals())

    _is_nitrate(nitrate, raise_exception=True)

    mas = MetalActivitySeries()
    cation_element = nitrate.cation.elements[0]  # only single-element cations supported
    cation_activity = mas.activity(cation_element)

    # creating possible products
    MeNO2 = Molecule.from_string(nitrate.cation.formula(), nitrate.cation.charge, 'NO2', -1)
    MeO = Molecule.from_string(nitrate.cation.formula(), nitrate.cation.charge, 'O', -2)
    Me = simple(cation_element)
    NO2 = Molecule.from_string('N', 4, 'O', -2, database_check=False)
    O2 = Simple.oxygen

    if cation_activity == 'active':
        return MeNO2, O2
    elif cation_activity == 'middle active':
        return MeO, NO2, O2
    elif cation_activity == 'inactive':
        return Me, NO2, O2
    else:
        raise NotSupposedToHappen(variables=locals())
