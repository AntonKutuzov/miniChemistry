from miniChemistry.MiniChemistryException import MiniChemistryException


class PeriodicTableException(MiniChemistryException):
    pass


class ElementNotFound(PeriodicTableException):
    def __init__(self, symbol: str, variables: dict):
        self._message = f'\nThe element with a symbol "{symbol}" is not found in the periodic table.'
        self.description = (f'Check for the typos and check for the case. The first letter of the symbol should be \n'
                             f'capital, which means "cu" will raise an exception, but "Cu" (stands for copper) will not.')
        super().__init__(variables)

    
