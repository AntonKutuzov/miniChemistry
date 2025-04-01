from miniChemistry.MiniChemistryException import MiniChemistryException

class CompatibilityTableException(MiniChemistryException):
    pass


class SubstanceNotFound(CompatibilityTableException):
    """Raised when an acid is not found in a compatibility table. Is raised by AcidsTable class."""
    def __init__(self, substance_type: str, formula: str, variables: dict):
        self._message = f'\nThe compatible {substance_type} for formula "{formula}" is not found.'
        self.description = (f'\nThis exception means that you tried to use the Acids- or BasesTable to convert \n'
                            f'{substance_type} into another type of substance (three types available: acid, acid rest,\n'
                            f'and acidic oxide, OR base, metal and basic oxide) and that the substance of type\n'
                            f'{substance_type} for substance with formula "{formula}" was not found.\n'
                            f'NOTE 1: The exception is the same regardless of what of the three particles the program \n'
                            f'failed to find.\n'
                            f'NOTE 2: Please note, that there are acidic oxides not for all acids!')
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables

class AcidNotFound(SubstanceNotFound):
    def __init__(self,  formula: str, variables: dict):
        super().__init__('acid', formula, variables)



class BaseNotFound(SubstanceNotFound):
    def __init__(self,  formula: str, variables: dict):
        super().__init__('base', formula, variables)


class AcidicOxideNotFound(SubstanceNotFound):
    def __init__(self, formula: str, variables: dict):
        super().__init__('acidic oxide', formula, variables)


class WrongTextFileData(CompatibilityTableException):
    def __init__(self, data: str, file_name: str, variables: dict):
        self._message = f'\nThe piece of data "{data}" in the file called "{file_name}" has a wrong form.'
        self.description = (f'\nThere usually is a certain convention on what kind of text data should be written in a\n'
                            f'certain text file. This exception means that the conventions were not followed and\n'
                            f'the parser that tried to read the file has got an error.')
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables


# ===================================================================================== METAL ACTIVITY SERIES EXCEPTIONS
class ElementIsNotMetal(CompatibilityTableException):
    def __init__(self, element: str, variables: dict):
        self._message = f'\nThe element with a symbol "{element}" is not a metal.'
        self.description = (f'\nMore precisely, this element is not in a list of metals defined in ptable.py. You can \n'
                            f'always see this list by printing ptable.METALS.')
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables


class UnknownActivityMetal(CompatibilityTableException):
    def __init__(self, element: str, variables: dict):
        self._message = f'\nThe element {element} has an unknown activity.'
        self.description = (f'\nUsually this error occurs when you tried to use activity of a metal in some\n'
                            f'algorithm, for example function estimate() for metal activity series. This algorithm\n'
                            f'(most probably) requires the metal to have a known activity.')
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables

