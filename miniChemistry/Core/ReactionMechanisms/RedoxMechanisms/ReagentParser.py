from __future__ import annotations

from miniChemistry.Core.Database.HalfReactionDatabase import HalfReactionDatabase
from miniChemistry.Core.Reactions import RedoxReaction, HalfReaction
from miniChemistry.Core.Substances import Ion, Molecule

from typing import Tuple


db = HalfReactionDatabase()

def reagents_to_hrs(*reagents: Molecule):
    substances = list()

    for r in reagents:
        s = db.match(r, 'all')
        substances += s

    return substances

def join_hrs(hr1: HalfReaction, hr2: HalfReaction) -> RedoxReaction:
    reduction = db.compare_potentials(hr1, hr2, condition='min')
    oxidation = hr1 if reduction is hr2 else hr2

    reduction = reduction.reversed()

    print(reduction.scheme)
    print(oxidation.scheme)



MnO4_m = Ion.from_string('MnO4', -1)
SO3_2m = Ion.from_string('SO3', -2)
MnO4_2m = Ion.from_string('MnO4', -2)
OH = Ion.hydroxide

KMnO4 = Molecule.from_string('K', 1, 'MnO4', -1)
H2SO3 = Molecule.from_string('H', 1, 'SO3', -2)
KOH = Molecule.from_string('K', 1, 'OH', -1)

hr1 = HalfReaction.from_string('Cr(3) + e(-1) = Cr(2)')
hr2 = HalfReaction.from_string('MnO4(-1) + H(1) + e(-1) = MnO2 + H2O')

print(hr1.scheme)
print(hr2.scheme)

join_hrs(hr1, hr2)

# reagents = [MnO4_2m, OH]

"""
for s in reagents_to_hrs(*reagents):
    print(s.equation)
"""