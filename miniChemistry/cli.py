import sys
from miniChemistry.Core.MolecularReaction import MolecularReaction

def cli():
    print(
        MolecularReaction.from_string(" ".join(sys.argv[1:])).equation
    )
