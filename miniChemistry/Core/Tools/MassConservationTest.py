from miniChemistry.Core.Substances import Molecule, Simple
from typing import List, Dict
from math import isclose


def mass_conservation_test(
                            reagents: List[Molecule|Simple],
                            products: List[Molecule|Simple],
                            coefficients: Dict[Molecule|Simple, float],
                            rel_tol = None,
                            abs_tol = None
                            ) -> bool:

    total_mass = 0

    for reagent in reagents:
        total_mass += reagent.molar_mass * coefficients[reagent]

    for product in products:
        total_mass -= product.molar_mass * coefficients[product]

    conditions = [
        rel_tol is not None and isclose(total_mass, 0, rel_tol=rel_tol),
        abs_tol is not None and isclose(total_mass, 0, abs_tol=abs_tol),
        rel_tol is None and abs_tol is None and isclose(total_mass, 0)
    ]

    if any(conditions):
        return True
    else:
        return False