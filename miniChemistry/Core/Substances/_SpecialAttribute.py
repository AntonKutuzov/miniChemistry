


class _SpecialSubstance:
    """
    Needed to avoid complex error messages when a special substance is used without their initiation. Say, we try to
    use

    em = Particle.empty

    but the attribute 'empty' is not yet defined (Particle.create_special_particles() is not called). The error message
    in this case is huge and complicated. To avoid it, Particle.empty and other special substances are instances
    of _SpecialSubstance class which redefines __get__ method.
    """

    def __init__(self, attr, name: str):
        self._attr = attr
        self._name = name

    def __get__(self, instance, owner):
        if instance is not None:
            raise Exception('Please address special substances via class attribute.')

        if self._attr is not None:
            return self._attr
        else:
            raise TypeError(f'"{self._name}" is a special attribute, and thus cannot be None. Create special attributes.')
