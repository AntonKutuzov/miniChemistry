from miniChemistry.MiniChemistryException import MiniChemistryException

class DatumException(MiniChemistryException):
    pass


class WrongMultiplicationFactor(DatumException):
    def __init__(self, factor: str, factor_type: str, variables: dict):
        self._message = f'\nCannot multiply Datum by a variable "{factor}" of type {factor_type}.'
        self.description = (f'\nSince Datum class is expected to behave exactly like a physical quantity class, it can\n'
                            f'be multiplied either by another Datum (regardless of units), or by a number.')
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables

class WrongDivisionFactor(DatumException):
    def __init__(self, factor: str, factor_type: str, variables: dict):
        self._message = f'\nCannot divide Datum by a variable "{factor}" of type {factor_type}.'
        self.description = (f'\nSince Datum class is expected to behave exactly like a physical quantity class, it can\n'
                            f'be divided either by another Datum (regardless of units), or by a number.')
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables


class NegativesNotAllowed(DatumException):
    def __init__(self, operation: str, result: str, variables: dict):
        self._message = f'\nThe result of the {operation} operation is a negative number: {result}.'
        self.description = (f'\nThe current Datum has forbidden to take values less than 0. To allow it, set the\n'
                            f'ALLOW_NEGATIVES property to True.')
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables


class IncompatibleUnits(DatumException):
    def __init__(self, initial_units: str, final_units: str, variables: dict):
        self._message = f'\nThe units "{initial_units}" and "{final_units}" are not compatible.'
        self.description = (f'\nThis exception most often raises when trying to convert some units into some other\n'
                            f'units that the Datum cannot be converted to. E.g. it could be converting meters to \n'
                            f'kilograms.')
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables


class WrongStringFormat(DatumException):
    def __init__(self, string: str, variables: dict):
        self._message = f'\nThe string "{string}" does not follow all the rules for defining Datum instances.'
        self.description = (f'\nThe string format used to define Datum instances is the following (the <> signs denote\n'
                            f'explanation): <datum name> = <datum value as int or float> <datum units>. The spaces\n'
                            f'matter, so check that you placed spaces around the equality sign.\n'
                            f'You can also check the format by printing any Datum instance.')
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables


class WrongZeroToleranceExponentValue(DatumException):
    def __init__(self, zte: str, variables: dict):
        self._message = (f'\nThe zero tolerance exponent is expected to be an integer from 1 to 100, but has a value of\n'
                         f'{zte} with a type of {type(zte)}.')
        self.description = ''
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables
