"""Equate the reaction and determine the masses of water needed to obtain 25 g of each product: Na + H2O"""

from miniChemistry.EXAMPLES import comment


comment('Importing necessary modules...')
from miniChemistry.Core.Reaction import Reaction
from miniChemistry.Computations.ReactionCalculator import ReactionCalculator
from miniChemistry.Computations.SSDatum import SSDatum
from miniChemistry.Core.Substances import Molecule, Simple, Ion, ion
import miniChemistry.Core.Database.ptable as pt


comment('Initiating the reagents via defining ions and then molecules...')
comment('Initiating sodium with `Simple(pt.Na, 1)`. Same for hydrogen')
Na = Simple(pt.Na, 1)
H2 = Simple(pt.H, 2)
comment('Initiating ions with `Ion(Dict[pt.Element: int], int)`')
H_plus = Ion({pt.H: 1}, 1)
OH_minus = Ion({pt.O: 1, pt.H: 1}, -1)
comment('Initiating molecules by using ions with `Molecule()`')
water = Molecule(H_plus, OH_minus)
NaOH = Molecule(ion(Na), OH_minus)

comment('Creating a reaction instance via `Reaction(Na, H2O)`')
r = Reaction(Na, water)
comment(r.equation)


comment(
    "\nThis exercise contains two separate small exercises. Both ask to find\n"
    "the mass of water we need to form 25 g of each product. The thing is that\n"
    "the products are different and they will result in different amounts of\n"
    "water. Hence, these exercises have to be solved with different\n"
    "`ReactionCalculator` instances – one for NaOH and one for H2.",
    approval='\nContinue (Press "Enter") >>> '
)

comment('\n--- First solving the exercise for 25 g of NaOH ---')
comment("Creating ReactionCalculator instance and writing in the data\n`rc = ReactionCalculator(r)`\n")
rc = ReactionCalculator(r)

comment("Writing data by passing `SSDatum(Na, 'mps', 25, 'g')` to rc.write()")
rc.write(SSDatum(NaOH, 'mps', 25, 'g'))

comment('Computing moles of sodium hydroxide with `rc.compute_moles_of(NaOH)`')
rc.compute_moles_of(NaOH)
comment('The moles of sodium hydroxide are', end=' ')
comment(rc.substance(NaOH).read('n'))

comment('Deriving moles of water by using `rc.derive_moles_of(water, use=NaOH)`')
water_moles = rc.derive_moles_of(water, use=NaOH)
comment('The moles of water are', *water_moles)
comment("Now mass of water can be computed with `rc.compute(water, 'mps', 0.01, 'g')`")
masses = rc.compute(SSDatum(water, 'mps', 0.01, 'g'))
comment('The mass of water is', *masses)

comment('\n--- Second solving the exercise for 25 g of H2 ---')
comment("Defining new ReactionCalculator instance in the same way as above")
rc = ReactionCalculator(r)

comment("Writing in 25 g of hydrogen with `rc.write(SSDatum(H2, 'mps', 25, 'g'))`")
rc.write(SSDatum(H2, 'mps', 25, 'g'))

comment('Computing moles of hydrogen and deriving moles of water by the same functions...')
comment("The moles of hydrogen are", *rc.compute_moles_of(H2))
comment("The moles of water are", *rc.derive_moles_of(water, use=H2))

comment("Looking for the mass of water from its moles...")
mass_water = rc.compute(SSDatum(water, 'mps', 0.01, 'g'))
comment("The mass of water is", *mass_water)
