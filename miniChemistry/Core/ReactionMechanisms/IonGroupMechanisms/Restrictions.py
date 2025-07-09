from miniChemistry.Core.CoreExceptions.MechanismExceptions import WeakElectrolyteNotFound
from miniChemistry.Core.Substances import IonGroup, Molecule, Ion, st_substance


"""NOTE FOR CHEMISTS: this code treats as equivalent terms "weak electrolyte" and "insoluble" and
"strong electrolyte" and "soluble". This is indeed not true in chemistry in general, however with
ionic substances (Molecule here consists of two ions always), this is true for majority of 
substances."""


def weak_electrolyte_restriction_for_ions(
        *products: Ion|IonGroup|Molecule,
        raise_exception: bool = True
        ) -> bool:

    for product in products:
        if product == Molecule.water:
            return True
        elif isinstance(product, Molecule) and st_substance(product).solubility in {'NS', 'SS'}:
            return True
        else:
            continue

    else:
        if raise_exception:
            raise WeakElectrolyteNotFound(products=[p.formula() for p in products], variables=locals())
        else:
            return False


def strong_electrolyte_restriction_for_ions(
        *products: Ion|IonGroup|Molecule,
        raise_exception: bool = True
        ) -> bool:

    return not weak_electrolyte_restriction_for_ions(*products, raise_exception=raise_exception)

