from miniChemistry.MiniChemistryException import MiniChemistryException
from typing import List


class MechanismException(MiniChemistryException):
    pass

"""
class SimpleMechanismException(MechanismException):
    pass

class ComplexMechanismException(MechanismException):
    pass

class ExceptionalMechanismException(MechanismException):
    pass
"""

class CannotPredictProducts(MechanismException):
    """Raised when a function failed to predict reaction products based on reaction reagents."""
    def __init__(self, reagents: List[str], function_name: str, variables: dict):
        self._message = f'\nFailed to predict reaction products for the given reagents: {', '.join(reagents)}. Function used is "{function_name}".'
        self.description = ''
        super().__init__(variables)

    


class WrongSimpleClass(MechanismException):
    """Raised when a mechanism method received a substance with a wrong simple class (NOT simple SUBclass)"""
    def __init__(self, formula: str, simple_class: str, expected_class: str, variables: dict):
        self._message = (f'\nA reaction prediction mechanism expected a substance {formula} to have a simple class of \n'
                         f'"{expected_class}", but obtained "{simple_class}".')
        self.description = ''
        super().__init__(variables)

    


class WrongSimpleSubclass(MechanismException):
    """Raised when a mechanism method received a substance with a wrong simple subclass (NOT simple CLASS)"""
    def __init__(self, formula: str, simple_subclass: str, expected_subclass: str, variables: dict):
        self._message = (f'\nA reaction prediction mechanism expected a substance {formula} to have a simple subclass \n'
                         f'of "{expected_subclass}", but obtained "{simple_subclass}".')
        self.description = ''
        super().__init__(variables)

    


class WrongIon(MechanismException):
    """Raised when an ion expected by the mechanism is not as expected. (Used in nitrate_decomposition mechanism)"""
    def __init__(self, formula: str, ion: str, expected_ion: str, variables: dict):
        self._message = f'\nA substance with formula {formula} must have the following ion: {expected_ion}, but has {ion}.'
        self.description = ''
        super().__init__(variables)

    

# =================================================================================================== RESTRICTION ERRORS
class WeakElectrolyteNotFound(MechanismException):
    """Raised if a weak electrolyte is not found among the reaction products."""
    def __init__(self, products: List[str], variables: dict):
        self._message = f'\nA weak electrolyte was not found among the products: {products}.'
        self.description = ''
        super().__init__(variables)

    


class LessActiveMetalReagent(MechanismException):
    """Raised by metal activity restriction if the metal to be replaced in the salt or acid is more active."""
    def __init__(self, metal: str, molecule: str, variables: dict):
        self._message = (f'\nThe metal in the molecule "{molecule}" is more active that "{metal}" and thus cannot replace\n'
                         f'the one in the molecule.')
        self.description = ''
        super().__init__(variables)

    


class WrongMetalActivity(MechanismException):
    """Raised when activity (from metal activity series) of a given metal is not as expected."""
    def __init__(self, metal: str, activity: str, expected_activity: str, variables: dict):
        self._message = f'\nThe metal "{metal}" has wrong activity. Expected "{expected_activity}", got "{activity}".'
        self.description = ''
        super().__init__(variables)

    
