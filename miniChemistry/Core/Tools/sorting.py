from miniChemistry.Core.Reactions import HalfReaction
from miniChemistry.Core.Database.HalfReactionDatabase import HalfReactionDatabase
from miniChemistry.Core.Substances import Ion, Molecule, IonGroup, Simple

from typing import Tuple, Literal, List


def cation_and_anion(i1: Ion, i2: Ion) -> Tuple[Ion, Ion]:
    if i1.charge < 0 < i2.charge:
        cation = i2
        anion = i1
    elif i2.charge < 0 < i1.charge:
        cation = i1
        anion = i2
    else:
        raise Exception('The ions must have charges with different signs.')

    return cation, anion


def reduction_and_oxidation(
        hr1: HalfReaction,
        hr2: HalfReaction,
        return_first: Literal['oxidation', 'reduction'] = 'reduction'
) -> Tuple[HalfReaction, HalfReaction]:

    db = HalfReactionDatabase()
    reduction = db.compare_potentials(hr1, hr2, condition='max')
    oxidation = hr1 if reduction is hr2 else hr2

    if return_first == 'oxidation':
        return oxidation, reduction
    else:
        return reduction, oxidation


def filter_particles(
        *particles: Ion|IonGroup|Molecule|Simple,
        get: Literal['ions', 'ion groups', 'molecules', 'simples']
) -> List[Ion|IonGroup|Molecule|Simple]:

    type_dict = {
        'ions': Ion,
        'ion groups': IonGroup,
        'molecules': Molecule,
        'simples': Simple
    }

    key = lambda p: isinstance(p, type_dict[get])
    return list( filter(key, particles) )
