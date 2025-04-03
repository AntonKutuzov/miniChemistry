from miniChemistry.MiniChemistryException import MiniChemistryException


class SubstanceException(MiniChemistryException):
    pass


class MultipleElementCation(SubstanceException):
    """Raised when a cation containing more than one element is met. These cations are not supported by miniChemistry
    module."""
    def __init__(self, cation, variables: dict):
        self._message = f'\nCurrent version of miniChemistry module supports only cations with one chemical element.'
        self.description = (f'\nThe cation {cation.composition} you entered consists of more than one chemical element.\n'
                            f'Currently, miniChemistry does not support this kind of ions.')
        super().__init__(variables)

    


class ElementNotFound(SubstanceException):
    """Raised when an element with a certain symbol is not found in a periodic table, BUT the call of the exception
    happened from the Substance.py or related classes or methods."""
    def __init__(self, element, variables: dict):
        self._message = f'\nThe element with symbol {element} is not found in the periodic table.'
        self.description = (f'\nCheck for typos and if everything is correct, refer to the real periodic table to see'
                            f' if the element you are trying to use really exists.')
        super().__init__(variables)

    


class SubstanceConvertionError(SubstanceException):
    """Raised when the code failed to convert one substance type to another."""
    def __init__(self, substance_to, substance_from, function_name: str, variables: dict):
        self._message = f'\nCould not convert {type(substance_from)} to {type(substance_to)}.'
        self.description = (f'\nThe function "{function_name}" does not support convertion of {type(substance_from)} \n'
                            f'data type to {type(substance_to)} data type. One of the two or both is wrong. Typically,\n'
                            f'the function is used to convert one Particle subclass into another (including Particle\n'
                            f'itself). The data types the function can take can always be found in documentation.')
        super().__init__(variables)

    


class UnsupportedSubstanceSize(SubstanceException):
    """Raised when the size of a substance (number of chemical elements) is not as expected."""
    def __init__(self, substance_composition, function_name: str, variables: dict):
        self._message = (f'\nAn operation you are trying to do does not support substance of this size: '
                         f'{len(substance_composition)}.')
        self.description = (f'\nThis error means that an operation that you tried to do (function "{function_name}")\n'
                            f'is not valid for a substance with this size ({len(substance_composition)}). Most \n'
                            f'commonly, it is the situation when you are trying to convert multiple-element particle \n'
                            f'into a Simple, which can only consist of one element.')
        super().__init__(variables)

    


class ChargeError(SubstanceException):
    """Used to indicate that the charge is not as expected."""
    def __init__(self, charge: int, neutrality: bool):
        self._message = f'\nThe substance is {('not ' if neutrality else '')} electrically neutral.'
        self.description = (f'\nThe substance you are trying to create (or check) does not meet the set requirement\n'
                            f' for charge: being {('not ' if neutrality else '')} electrically neutral.\n'
                            f'The charge set is "{charge}".')
