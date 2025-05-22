"""
Provide the products of the following reactions and balance them:
H2 + O2 -> ?
Na + H2O -> ?
NaOH + H2SO4 -> ?
H2CO3 -> ?
S + O2 -> ?
SO3 + H2O -> ?
"""


from miniChemistry.EXAMPLES import comment
from miniChemistry.Core.Reaction import Reaction

reactions = (
    'H2 + O2',
    'Na + Cl2',
    'NaOH + H2SO4',
    'H2CO3',
    'S + O2',
    'SO3 + H2O'
)

comment('In this example a string, containing a reaction will be converted to a Reaction instance\n'
        'and then the balanced chemical reaction will be written to the console.')

for reaction in reactions:
    comment(f'Equating {reaction}...', no_delay=True)
    r = Reaction.from_string(reaction)
    comment(r.equation)
