from miniChemistry.MiniChemistryException import MiniChemistryException


class SolubilityTableException(MiniChemistryException):
    pass


class SolubilityTableNotInitiated(SolubilityTableException):
    def __init__(self, variables: dict):
        self._message = f'\nThe SolubilityTable instance you are trying to use is not initiated. Please call the .begin() method.'
        self.description = ''
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables


class SubstanceAlreadyPresent(SolubilityTableException):
    def __init__(self, substance_signature: list, variables: dict):
        self._message = (f'\nSubstance with the following signature is already present in the solubility table: '
                         f'{substance_signature}.')
        self.description = ('If you noted a mistake, you can erase the substance and rewrite it into the table.\n'
                            "In this case also don't forget to change the 'ModifySolubilityTable.py file.\n"
                            "Also, check for typos in the way you wrote the formula of a substance, and check\n"
                            "that the indicated charges are correct.")
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables


class SubstanceNotFound(SolubilityTableException):
    def __init__(self, substance_signature: list, variables: dict):
        self._message = (f'\nSubstance with the following signature is not found in the solubility table: '
                         f'{substance_signature}.')
        self.description = ''
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables


class IonNotFound(SolubilityTableException):
    """Raised when an ion that was expected by the user to be in the solubility table is not found there."""
    def __init__(self, ion_signature: list, variables: dict):
        self._message = (f'\nIon with the following signature is not found in the solubility table: '
                         f'{ion_signature}.')
        self.description = ''
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables


class OutOfOptions(SolubilityTableException):
    """Raised when iteration over the whole solubility table did not result in finding a required substance or ion."""
    def __init__(self, formula: str, function_name: str, variables: dict):
        self._message = (f'\nThe solubility table cannot validate existence of (part of) this molecule: '
                         f'{formula}.')
        self.description = (f'\nThis exception means that a function (namely, "{function_name}") was iterating over\n'
                            f'the whole solubility table to find a match for a molecule or ion passed to the\n'
                            f'function, but it did not succeed.')
        super().__init__(variables)

    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables
