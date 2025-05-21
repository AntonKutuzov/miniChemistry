"""Find the mass of water formed during reaction of 20 g of NaOH and 24.5g of H2SO4."""

from miniChemistry.EXAMPLES import comment
from QCalculator import SETTINGS

SETTINGS['COMMENTS ON'] = False

comment('Importing necessary modules...')
from miniChemistry.Core.Reaction import Reaction
from miniChemistry.Computations.ReactionCalculator import ReactionCalculator
from miniChemistry.Computations.SSDatum import SSDatum
from miniChemistry.Core.Substances import Molecule


comment('Initiating necessary substances by using `Molecule.from_string()`...')
NaOH = Molecule.from_string('Na', 1, 'OH', -1)
comment('NaOH:', NaOH, no_delay=True)
H2SO4 = Molecule.from_string('H', 1, 'SO4', -2)
comment('H2SO4:', NaOH, no_delay=True)
H2O = Molecule.water
comment('H2O:', NaOH, '\n', no_delay=True)


comment('Modelling the reaction by passing the substances as arguments: `r = Reaction(NaOH, H2SO4)`')
r = Reaction(NaOH, H2SO4)
# also possible `r = Reaction.from_string('NaOH + H2SO4')`
comment('Reaction equation by `r.equation`', r.equation, '\n')


comment("Creating ReactionCalculator instance and writing in the data\n`rc = ReactionCalculator(r)`\n")
rc = ReactionCalculator(r)  # using initiation from a Reaction instance
comment("Writing down the data by using SSDatum class...\n", custom_delay=2)
rc.write(
            SSDatum(NaOH, 'mps', 20, 'g'),
            SSDatum(H2SO4, 'mps', 24.5, 'g')
        )


comment("Computing moles of each reagent and by using `rc.compute_moles_of()`")

if SETTINGS['COMMENTS ON']:
    comment("\n-------------------- LinearIterator output ---------------------", custom_delay=0)
    comment("--- Searching for moles of NaOH and H2SO4: n ---")
rc.compute_moles_of(NaOH, H2SO4)
if SETTINGS['COMMENTS ON']:
    comment("-------------------- LinearIterator finished ---------------------\n")

comment('The moles of the reagents are:',
      rc.substance(NaOH).read('n', 'mole'),
      rc.substance(H2SO4).read('n', 'mole'), '\n',
        no_delay=True
      )

comment('Looking for the limiting reagent by using `rc.limiting_reagent()`', custom_delay=1)
lr = rc.limiting_reagent(NaOH, H2SO4)
comment('Found',  lr, '\n')


comment("Using the limiting reagent to derive the moles of water by `rc.derive_moles_of(H2O, use=lr.substance)`")
H2O_moles = rc.derive_moles_of(H2O, use=lr.substance)
comment('The moles of water are:', *H2O_moles, '\n', custom_delay=2)


comment("Computing the mass of water formed during the reaction by using `rc.compute()`")
if SETTINGS['COMMENTS ON']:
    comment("\n-------------------- LinearIterator output ---------------------", custom_delay=0)
    comment("--- Searching for mass of water: mps ---")
mass_of_water = rc.compute(
                                SSDatum(H2O, 'mps', 0.001, 'g'),
                                rounding=True
                            )
if SETTINGS['COMMENTS ON']:
    comment("-------------------- LinearIterator finished ---------------------\n")

comment('The mass of water is', *mass_of_water)
