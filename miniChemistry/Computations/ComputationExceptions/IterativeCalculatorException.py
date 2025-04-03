from miniChemistry.MiniChemistryException import MiniChemistryException


class IterativeCalculatorException(MiniChemistryException):
    pass


class IncorrectFileFormatting(IterativeCalculatorException):
    def __init__(self, file_name: str, variables: dict):
        self._message = f'\nThe file "{file_name}" has wrong formatting.'
        self.description = (f'\nThis exception is raised if either of the files (or several) associated with the\n'
                            f'IterativeCalculator class are not formatted in a correct way. Open the files and\n'
                            f'check the formatting.')
        super().__init__(variables)

    


class AssumptionFailed(IterativeCalculatorException):
    def __init__(self, assumption_symbol: str, variables: dict):
        self._message = (f'\nThe assumption "{assumption_symbol}" was not applied, because one of the conditions\n'
                         f'was not satisfied.')
        self.description = (f'\nAssumptions can define variables to be assumed, and variables to be calculated. If\n'
                            f'any of the variables to be calculated were not possible to find, this equation is raised.')
        super().__init__(variables)

    


class SolutionNotFound(IterativeCalculatorException):
    def __init__(self, target: str, variables: dict):
        self._message = f'\nCould not find the target "{target}" variable with the given conditions.'
        self.description = (f'\nCheck that you have all necessary assumptions, and that all you values are written to\n'
                            f'the class (you can always check it by "IterativeCalculator.calculator.values" property.')
        super().__init__(variables)

    


class NegativesNotAllowed(IterativeCalculatorException):
    def __init__(self, variable: str, value: float|int, variables: dict):
        self._message = f'\nThe value of the variable "{variable}" is negative, which is not allowed: {value}.'
        self.description = (f'\nIf you were using IterativeCalculator.add() method, set the "allow_negatives"\n'
                            f'attribute to True.')
        super().__init__(variables)

    
