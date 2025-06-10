from miniChemistry.MiniChemistryException import MiniChemistryException


class ParsingException(MiniChemistryException):
    pass

class EqualizerException(MiniChemistryException):
    pass


class CannotSelectCoefficients(EqualizerException):
    """Raised by an equalizer tool when it is not possible to equate a chemical reaction."""
    def __init__(self, reagent_formulas: list, variables: dict):
        self._message = f'\nThe reaction of the given reagents cannot be equated: {', '.join(reagent_formulas)}.'
        self.description = f'\n'
        super().__init__(variables)

    


class InvalidFormula(ParsingException):
    """Raised when parsing of a string formula failed due to unexpected form or symbols."""
    def __init__(self, formula: str, variables: dict):
        self._message = f'\nParsing the formula "{formula}" failed due to unexpected form or symbol.'
        self.description = (f'\nThis error typically occurs if you tried to parse a formula of an ion or a molecule \n'
                            f'(also Simple), but the form of the string was wrong. For example, it is impossible to\n'
                            f'have such symbols as # or @ in chemical formulas. If they are met, this exception\n'
                            f'is raised.')
        super().__init__(variables)

    


class CannotEquateReaction(EqualizerException):
    """Raised in the case if a reaction cannot be equated."""
    def __init__(self, reagents: list, variables: dict):
        self._message = f'\nCould not equate the reaction with reagents {reagents}.'
        self.description = ''
        super().__init__(variables)

    
