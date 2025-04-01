from miniChemistry.Computations.Datum import Datum
from miniChemistry.Core.Substances import Molecule, Simple
from miniChemistry.Utilities.Checks import type_check_decorator
from typing import Union
from pint import Unit


class SSDatum(Datum):
    """
    SSDatum stands for "Substance–Specific Datum". This class extends the Datum class by adding a substance as another
    data point. The constructor then takes in an additional parameter ("substance", which will always go the first one).
    """

    @type_check_decorator
    def __init__(self,
                 substance: Union[Molecule, Simple],
                 variable: str,
                 value: float,
                 units: Union[str, Unit] = 'dimensionless') -> None:

        self._substance = substance
        super().__init__(variable, value, units)

    def __eq__(self, other: 'SSDatum'):
        return self.datum == other.datum and self.substance == other.substance

    def __getitem__(self, item):
        item_list = [self.substance, *self.datum, self.datum.str_units]
        return item_list[item]

    def __iter__(self):
        iter_list = [self.substance, *self.datum]
        return iter_list.__iter__()

    def __str__(self):
        return_str = f'{self.variable}({self.substance.formula()}) = {self.magnitude} {self.units}'
        return return_str

    @property
    def datum(self) -> Datum:
        return Datum(self.variable, self.magnitude, self.units)

    @property
    def substance(self) -> Union[Molecule, Simple]:
        return self._substance

"""
ssd = SSDatum(Molecule.water, 'mps', 18, 'g')
print(ssd.datum)
"""