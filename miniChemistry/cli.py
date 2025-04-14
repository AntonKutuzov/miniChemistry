import sys
from miniChemistry.Core.Reaction import Reaction

def cli():
    print(
        Reaction.from_string(" ".join(sys.argv[1:])).equation
    )
