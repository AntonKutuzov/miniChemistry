class MiniChemistryException(Exception):
    """
    The exception hierarchy here is quite simple. Every (almost) package has its own Exceptions file so that we can
    easily track from where did the exception come from. All exceptions start from this one – MiniChemistryException,
    because this one contains an important parameter self._relevant_variables. It is printed by any exception so that
    we can immediately see without debugging what values the variables had.
    """
    def __init__(self, variables: dict):
        if not hasattr(self, '_message') or not hasattr(self, 'description'):
            raise AttributeError('Each subclass of the MiniChemistryException must have both "_message" and "description" variables.')

        # this if–statement will never be called, but if you delete it, Python will complain, because it won't
        # see any "_message" and "description" variables
        if not hasattr(self, '_message') or not hasattr(self, 'description'):
            self._message = 'this is a message of the miniChemistry base exception.'
            self.description = 'this is a description of the miniChemistry base exception.'
                
        self._relevant_variables = f'\n\n {''.join([str(item) + "\n" for item in variables.items()])}'
        super().__init__()
    
    def __str__(self):
        return self._message + '\n\n' + self.description + '\n\n' + self._relevant_variables


class NotSupposedToHappen(MiniChemistryException):
    def __init__(self, variables: dict):
        self._message = f"\nIf you see this error, there's a bug in the code that you use."
        self.description = (f'\nThe "NotSupposedToHappen" errors are raised in the case if an if–else statement or\n'
                             f'a similar piece of code goes to the last possible (impossible in normal case) option\n'
                             f'of raising this exception. For example, if an element of pt.Element does not belong\n'
                             f'to neither METALS, not NONMETALS, which is not supposed to happen.')
        self._relevant_variables = f'\n\n {''.join([str(item) + "\n" for item in variables.items()])}'
        super().__init__(variables)


class NoArgumentForFunction(MiniChemistryException):
    def __init__(self, function_name: str, variables: dict):
        self._message = f'\nA function "{function_name}" expected to get some arguments, but it did not.'
        self.description = ''
        self._relevant_variables = f'\n\n {''.join([str(item) + "\n" for item in variables.items()])}'
        super().__init__(variables)
