from miniChemistry.MiniChemistryException import MiniChemistryException
from typing import List


class ReactionException(MiniChemistryException):
    pass


class WrongNumberOfReagents(ReactionException):
    def __init__(self, reagents: List[str], variables: dict):
        self._message = f'\nThe number of reagents is not valid: {len(reagents)}.'
        self.description = (f'\nMiniChemistry module can only predict reactions with only one or two reagents. The reagents\n'
                            f'passed to the function are: {", ".join(reagents)}')
        super().__init__(variables)

    


class WrongReactionConstructorParameters(ReactionException):
    def __init__(self, variables: dict):
        self._message = f'\nThe constructor of Reaction class accepts either positional OR keyword arguments.'
        self.description = (f'\nFor the constructor of the Reaction class you need to pass either only reagents, each\n'
                            f'as a separate parameter, OR two lists – first reagents, second products.')
        super().__init__(variables)

    