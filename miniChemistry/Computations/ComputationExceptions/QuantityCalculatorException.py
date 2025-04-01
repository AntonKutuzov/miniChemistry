from miniChemistry.MiniChemistryException import MiniChemistryException


class QuantityCalculatorException(MiniChemistryException):
    pass


class UnknownVariableException(QuantityCalculatorException):
    def __init__(self, variable_name: str, variables: dict):
        self._message = f'\nThe variable "{variable_name}" is not in a list of QuantityCalculator.'
        self.description = (f'\nTo add a variable to the QuantityCalculator, open the "formulas.txt" and\n'
                            f'"units_and_names.txt" files. To the "formulas.txt" file add the formula with this\n'
                            f'variable, and to the "units_and_names.txt" add the symbol, name, and units of the \n'
                            f'variable.')
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables


class VariableHasValue(QuantityCalculatorException):
    def __init__(self, variable_name: str, variables: dict):
        self._message = f'\nThe variable "{variable_name}" already has a value.'
        self.description = (f'\nThe variable "{variable_name}" already has a value. You cannot rewrite the values of\n'
                            f'variables in QuantityCalculator by "write_value()" method. Instead use "erase_value()"\n'
                            f'first and then you can use "write_value()".')
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables


class ValueNotFoundException(QuantityCalculatorException):
    def __init__(self, variable_name: str, variables: dict):
        self._message = f'\nThe variable "{variable_name}" does not have a value.'
        self.description = f'\n'
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables


class SolutionNotFound(QuantityCalculatorException):
    def __init__(self, target_name: str, variables: dict):
        self._message = (f'\nCould not find any solutions for "{target_name}" with the given set of equations and \n'
                         f'the given set of variables.')
        self.description = f'\n'
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables
