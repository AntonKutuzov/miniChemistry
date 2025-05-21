"""Equate the reaction and determine the mass of water needed to obtain 25g of NaOH.
Reaction: Na + H2O -> ?"""

from miniChemistry.EXAMPLES import comment
from QCalculator import SETTINGS

SETTINGS['COMMENTS ON'] = False

"""
exercise_text = '''
The exercise is the following:
"Equate the reaction and determine the mass of water needed to obtain 25g of NaOH.
Reaction: Na + H2O -> ?"
'''

comment(exercise_text, approval='Understood >>> ')
"""

comment('Importing necessary modules...')
from miniChemistry.Core.Reaction import Reaction
from miniChemistry.Computations.ReactionCalculator import ReactionCalculator
from miniChemistry.Computations.SSDatum import SSDatum
from miniChemistry.Core.Substances import Molecule, Simple, Ion, ion
import miniChemistry.Core.Database.ptable as pt


comment('Initiating the reagents via defining ions and then molecules by using Ion and Molecule classes...')
# comment('Initiating sodium with `Simple(pt.Na, 1)`. Same for hydrogen')
Na = Simple(pt.Na, 1)
H2 = Simple(pt.H, 2)
# comment('Initiating ions with `Ion(Dict[pt.Element: int], int)`')
H_plus = Ion({pt.H: 1}, 1)
OH_minus = Ion({pt.O: 1, pt.H: 1}, -1)
# comment('Initiating molecules by using ions with `Molecule()`')
water = Molecule(H_plus, OH_minus)
NaOH = Molecule(ion(Na), OH_minus)

# comment('Creating a reaction instance via `Reaction(Na, H2O)`')
comment('Equating the reaction "Na + H2O -> ?"...')
r = Reaction(Na, water)
comment('The reaction is:', r.equation)

comment("Creating ReactionCalculator instance for calculations over the reaction")
rc = ReactionCalculator(r)

# comment("Writing data by passing `SSDatum(Na, 'mps', 25, 'g')` to rc.write()")
comment('Writing down initial data...')
rc.write(SSDatum(NaOH, 'mps', 25, 'g'))

comment('Computing moles of NaOH with `rc.compute_moles_of(NaOH)`')

if SETTINGS['COMMENTS ON']:
    comment("\n-------------------- LinearIterator output ---------------------", custom_delay=0)
    comment("--- Searching for mass of NaOH: n ---")

rc.compute_moles_of(NaOH)

if SETTINGS['COMMENTS ON']:
    comment("-------------------- LinearIterator finished ---------------------\n")

comment('The moles of sodium hydroxide are', end=' ')
comment(rc.substance(NaOH).read('n'))

comment('Deriving moles of water by using `rc.derive_moles_of(water, use=NaOH)`')
water_moles = rc.derive_moles_of(water, use=NaOH)
comment('The moles of water are', *water_moles)
comment("\nNow mass of water can be computed with `rc.compute(water, 'mps', 0.01, 'g')`")

if SETTINGS['COMMENTS ON']:
    comment("\n-------------------- LinearIterator output ---------------------", custom_delay=0)
    comment("--- Searching for mass of water: mps ---")

masses = rc.compute(SSDatum(water, 'mps', 0.01, 'g'), rounding=True)

if SETTINGS['COMMENTS ON']:
    comment("-------------------- LinearIterator finished ---------------------\n")

comment('The mass of water is', *masses)
"""
comment('\n\n==================== Second solving the exercise for 25 g of H2 =========================')
comment("Defining new ReactionCalculator instance in the same way as above")
rc = ReactionCalculator(r)

comment("Writing in 25 g of hydrogen with `rc.write(SSDatum(H2, 'mps', 25, 'g'))`")
rc.write(SSDatum(H2, 'mps', 25, 'g'))

comment('Computing moles of hydrogen and deriving moles of water by the same functions...')

if SETTINGS['COMMENTS ON']:
    comment("\n-------------------- LinearIterator output ---------------------", custom_delay=0)
    comment("--- Searching for moles of H2: n ---")
comment("The moles of hydrogen are", *rc.compute_moles_of(H2))

if SETTINGS['COMMENTS ON']:
    comment("-------------------- LinearIterator finished ---------------------\n")

comment("The moles of water are", *rc.derive_moles_of(water, use=H2))

comment("Looking for the mass of water from its moles...")


if SETTINGS['COMMENTS ON']:
    comment("\n-------------------- LinearIterator output ---------------------", custom_delay=0)
    comment("--- Searching for mass of water: mps ---")

mass_water = rc.compute(SSDatum(water, 'mps', 0.01, 'g'), rounding=True)

if SETTINGS['COMMENTS ON']:
    comment("-------------------- LinearIterator finished ---------------------\n")

comment("The mass of water is", *mass_water)
"""