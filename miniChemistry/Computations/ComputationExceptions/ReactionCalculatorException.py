from miniChemistry.MiniChemistryException import MiniChemistryException


class ReactionCalculatorException(MiniChemistryException):
    pass


class InvalidConstructorArguments(ReactionCalculatorException):
    def __init__(self, variables: dict):
        self._message = f'\nReactionClaculator constructor received wrong parameters.'
        self.description = (f'\nThe arguments passed to the ReactionCalculator constructor did not match any of the\n'
                            f'predefined sets of variables that can be used to initialize the instance. Those are\n'
                            f'- an instance of Reaction (positional argument)\n'
                            f'- instance(s) of Molecule and/or Simple. Will be treated as reagents (positional arguments)\n'
                            f'- lists of Molecule and/or Simple instances (keyword arguments: "reagents" and "products")\n'
                            f'- string with a reaction scheme (positional argument)')
        super().__init__(variables)

    

class InitializationError(ReactionCalculatorException):
    def __init__(self, init_type: str, variables: dict):
        self._message = f'\nInitialization of ReactionCalculator failed.'
        self.description = (f'\nYou tried to initialize the ReactionCalculator class by using {init_type}. Check\n'
                            f'that you passed correct variables. In case you used only reagents or a string, consider\n'
                            f'passing to the constructor a Reaction instance.')
        super().__init__(variables)

    


class ComputationException(ReactionCalculatorException):
    def __init__(self, target: str, substance: str, variables: dict):
        self._message = f'\nFailed to compute the target "{target}" for "{substance}".'
        self.description = (f'\nThis exception means that IterativeCalculator used for {substance} did not manage\n'
                            f'to compute the target variables with the given conditions. Change the conditions\n'
                            f'or the target variable. Check that the substance is correct.')
        super().__init__(variables)

    

