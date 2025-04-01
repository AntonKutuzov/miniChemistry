"""
"Datum" is a singular from "data", which more often is replaced by "a piece of data". Datum class is needed to represent
physical quantities in a convenient way for the QuantityCalculator class and, after this, for IterativeCalculator and
ReactionCalculator classes. Datum behaves like a normal physical quantity, although it allows for restrictions
and modifications. It also serves as a parent class for SSDatum which stands for "Substance-Specific Datum". So, the
Datum class is some king of wrapping for pint.Quantity class, as it preserves all main functionality. It is also
possible to get the quantity (pint.Quantity) from the Datum instance by using ".quantity" property.\n

(stc. – static method, ppt. – property, stt. – setter)\n

Besides typical arithmetical operations and some other magical methods, the class supports several "Constructors"
(quotation marks are here because in fact two of them are just methods)\n
- __init__(variable: str, value: float, units: str|pint.Unit = 'dimensionless') -> None\n
- from_quantity(name: str, q: Quantity) -> Datum\n
- from_string(string: str) -> Datum\n

Each method creates a Datum instance according to its name – from_quantity method accepts pint.Quantity, and
from_string method accepts a string (in strict form of <variable name> = <float|int> <units as strings>. Spaces
matter!\n

The class also supports the following methods for work with units\n
- use_units(units: str|pint.Unit = 'dimensionless') -> None\n
- to_base_units() -> None\n
- convert(units: str|pint.Unit = 'dimensionless') -> Datum\n
- convertable(units: str|pint.Unit = 'dimensionless') -> bool\n
- ppt. units() -> pint.Unit\n
- ppt. str_units() -> str\n

The following methods are used to work with physical quantities (pint.Quantity)\n
- rewrite(value: int|float, units: str|pint.Unit = 'dimensionless') -> None\n
- ppt. magnitude() -> float\n
- ppt. quantity() -> pint.Quantity\n

And the rest of the methods have the following functionality\n
- ppt. variable() -> str | returns the name of the Datum instance, e.g. "mps", "Vpg", etc.\n
- ppt. ALLOW_NEGATIVES() -> bool | getter of the "allow negatives" property\n
- stt. ALLOW_NEGATIVES(value: bool) -> None | setter of the "allow negatives" property\n
- ppt. num_decimals() -> int | returns the number of digits after the comma of the magnitude of the quantity

MAGIC METHODS\n
__add__ – allows for addition of two Datum instances with interconvertable units (for example, you can add to each other
Data with units of m/s and km/h, but you cannot add m/s to m**3.\n
__mul__ – allows multiplication of Datum by either Datum or float|int. In both cases the pint.Quantity datum is returned,
not the Datum instance. This is done, because, in fact any units can be multiplied by each other, and there are no symbols
and names for all possible units. (If you "subtract" variable's name from Datum, you get pint.Quantity, and this is indeed
what the function returns.\n
__truediv__ – Same as for multiplication, but with division by Datum or float|int\n
__sub__ – Same as for addition, but with negative sign\n
__eq__ – The method compares the two Datum instances, and returns True if their variable names, values and units coincide.
For variable names a simple equality check is used, for the value the math.isclose() method is used with a
zero_tolerance_exponent variable. For the units the method checks if they are compatible.\n
__str__ – Describes the Datum instance according to the following structure: <name> = <value> <units>\n
__getitem__ – Returns a value from the following list: [name of the datum, magnitude, units as pint.unit, units as str]\n
__iter__ – Returns the __iter__ object of the following list: [name of the datum, magnitude, units as pint.Unit]\n

\nPRIVATE METHODS\n
- _ZTE_test() -> bool\n
- stc. _get_decimals(value: float) -> int\n
- _negative_value_test(operation: str, value: int|float, raise_exception: bool = True) -> bool\n
"""


# import pint
from pint import Quantity, Unit
from typing import Union
import re
from miniChemistry.Utilities.Checks import type_check_decorator
from miniChemistry.Computations.ComputationExceptions.DatumException import (WrongMultiplicationFactor, WrongDivisionFactor,
                                                                             NegativesNotAllowed, IncompatibleUnits,
                                                                             WrongStringFormat, WrongZeroToleranceExponentValue)


class Datum:
    """
    The Datum class works and operates with three main variables:

    1) "variable" of type string, which shows the name of the Datum. The meaning and all possible names are given in the
    "units_and_names.txt" file or in documentation.\n

    2) "value" of type float which is the magnitude of the physical quantity stored in the Datum class.\n

    3) "units" of type pint.Unit (constructor accepts both pint.Unit and string) which stores units of the physical
    quantity used in Datum.\n

    The class also has two supporting variables, which act like settings variables for the class\n
    - ALLOW NEGATIVES, False by default, indicates whether a physical quantity can have a negative value\n
    - ZERO_TOLERANCE_EXPONENT, 3 by default. The variable is used for isclose() method as a power for 10 in rel_tol argument.\n
    """

    @type_check_decorator
    def __init__(self, variable: str, value: float, units: Union[str, Unit] = 'dimensionless') -> None:
        self._variable = variable
        self._value = value
        self._units = Unit(units) if isinstance(units, str) else units

        self._ALLOW_NEGATIVES = False
        self._ZERO_TOLERANCE_EXPONENT = 3

    def __eq__(self, other):
        """
        The two Datum instances are considered to be equal if the three conditions are met\n
        - They have the same name (mps, Vpg, etc.)\n
        - They have close enough magnitudes ("close enough" is determined by the ZERO_TOLERANCE_EXPONENT)\n
        - The base units of both Datum instances are the same\n

        :param other: another instance of Datum
        :return: boolean indicating whether the Datum instances are equal (in this case "equal" means interchangeable)
        """

        from math import isclose

        if not self._ZTE_test():
            raise WrongZeroToleranceExponentValue(str(self._ZERO_TOLERANCE_EXPONENT), variables=locals())

        conditions = (
                self.variable == other.variable,
                isclose(self.magnitude, other.magnitude, rel_tol=eval(f'10E{self._ZERO_TOLERANCE_EXPONENT}')),
                self.quantity.to_base_units() == other.quantity.to_base_units()
        )

        return all(conditions)

    def __getitem__(self, item):
        item_list = [self.variable, self.magnitude, self.units, self.str_units]
        return item_list[item]

    def __iter__(self):
        return [self.variable, self.magnitude, self.units].__iter__()

    def __str__(self):
        return f"{self.variable} = {self.magnitude} {self.str_units}"

    @type_check_decorator
    def __mul__(self, other: Union['Datum', float, int]) -> Quantity:
        """
        The Datum instance can be multiplied by either another Datum, or a number (float or int). In both cases (for
        consistency) the method returns a pint.Quantity, meaning that the name of the variable is lost. If you want
        to change the value of current Datum, use the rewrite() or scale() method (they both preserve the name).

        :param other: an instance of Datum or a number
        :return: pint.Quantity with new magnitude and same/new units
        """

        if isinstance(other, Datum):
            new_quantity = self.quantity * other.quantity
        elif isinstance(other, (float, int)):
            new_value = self.magnitude * other
            new_quantity = new_value * self.units
        else:
            raise WrongMultiplicationFactor(factor=str(other), factor_type=str(type(other)), variables=locals())

        self._negative_value_test(operation='multiplication', value=new_quantity.magnitude)
        return new_quantity.to_base_units()  # not to get something like kg*g, but kg**2 instead

    @type_check_decorator
    def __truediv__(self, other: Union['Datum', float, int]) -> Quantity:
        """
        The Datum instance can be divided by either another Datum, or a number (float or int). In both cases (for
        consistency) the method returns a pint.Quantity, meaning that the name of the variable is lost. If you want
        to change the value of current Datum, use the rewrite() or scale() method (they both preserve the name).

        :param other: an instance of Datum or a number
        :return: pint.Quantity with new magnitude and same/new units
        """

        if isinstance(other, Datum):
            new_quantity = self.quantity / other.quantity
        elif isinstance(other, (float, int)):
            new_value = self.magnitude / other
            new_quantity = new_value * self.units
        else:
            raise WrongDivisionFactor(factor=str(other), factor_type=str(type(other)), variables=locals())

        self._negative_value_test(operation='division', value=new_quantity.magnitude)
        return new_quantity.to_base_units()  # not to get something like kg*g, but kg**2 instead

    def __sub__(self, other):
        """
        As well as in __add__ method, the subtraction operation is possible only if the units of both Datum instances
        are compatible. That means, you cannot subtract meters from kilograms (as well as in reality, by the way), but
        you can subtract Datum of m/s from km/h, because the code will automatically convert them for you.

        :param other: An instance of Datum with units compatible with the units of the current Datum
        :return: a pint.Quantity with new magnitude and the units of the current Datum
        """

        if other.convertable(self.units):
            result = self.quantity - other.quantity
            self._negative_value_test(operation='substitution', value=result.magnitude)
            return result
        else:
            raise IncompatibleUnits(initial_units=other.str_units, final_units=self.str_units, variables=locals())

    def __add__(self, other):
        """
        As well as in __sub__ method, the subtraction operation is possible only if the units of both Datum instances
        are compatible. That means, you cannot add meters to kilograms (as well as in reality, by the way), but
        you can add Datum of m/s to km/h, because the code will automatically convert them for you.

        :param other: An instance of Datum with units compatible with the units of the current Datum
        :return: a pint.Quantity with new magnitude and the units of the current Datum
        """

        if other.convertable(self.units):
            result = self.quantity + other.quantity
            self._negative_value_test(operation='addition', value=result.magnitude)
            return result
        else:
            raise IncompatibleUnits(initial_units=other.str_units, final_units=self.str_units, variables=locals())

    def _ZTE_test(self) -> bool:
        """Is needed because the ZTE is used with the eval() function."""
        zte = self._ZERO_TOLERANCE_EXPONENT

        if isinstance(zte, int) and 0 < zte < 100:
            return True
        else:
            return False

    @staticmethod
    def _get_decimals(value: float) -> int:
        """
        Is used to determine the number of digits after the comma in the magnitude of the Datum instance. Be careful
        not to pass a value of zero to this function as it will always return 1 (0.0 and 0.0000 are the same things).
        The correct way to use the function is to pass 0.1 or 0.0001, then the first case returns 1, and the second
        returns 4.

        :param value: magnitude of the Datum instance, type float
        :return: the number of digits after the comma, int
        """

        if isinstance(value, float) and value == 0.0:
            raise ValueError('Cannot determine decimals with a value of zero. Give a non-zero value for the last digit.')
        v = str(float(value))
        decimals = v.split('.')[1]
        return len(decimals)

    @type_check_decorator
    def _negative_value_test(self, operation: str, value: Union[int, float], raise_exception: bool = True) -> bool:
        if value < 0 and not self.ALLOW_NEGATIVES:
            if raise_exception:
                raise NegativesNotAllowed(operation=operation, result=str(value), variables=locals())
            else:
                return False
        else:
            return True

    @type_check_decorator
    def from_quantity(self, name: str, q: Quantity) -> 'Datum':
        self._negative_value_test(operation='Quantity to Datum convertion', value=q.magnitude)
        m = q.magnitude
        u = q.units
        return Datum(name, m, u)

    @type_check_decorator
    def from_string(self, string: str) -> 'Datum':
        pattern = '^[a-z]+ = \d+(\.\d+)? [a-z]+$'
        if re.fullmatch(pattern, string):
            name, rest = string.split(' = ')
            value, units = rest.split(' ')
            self._negative_value_test(operation='string to Datum convertion', value=float(value))
            return Datum(name, float(value), units)
        else:
            raise WrongStringFormat(string=string, variables=locals())

    @type_check_decorator
    def use_units(self, units: Union[str, Unit] = 'dimensionless') -> None:
        """
        Sets the default units of the Datum instance to be the ones indicated in the "units" parameter. Also
        converts the magnitude since change in units often induce change in the numerical value.

        :param units: string or pint.Unit to be set as default one. 'Dimensionless' by default.
        :return: None
        """

        u = Unit(units) if isinstance(units, str) else units
        if u.is_compatible_with(self.units):
            new_datum = self.convert(u)
            self._value = new_datum.magnitude
            self._units = new_datum.units
        else:
            raise IncompatibleUnits(initial_units=self.str_units, final_units=str(units), variables=locals())

    def to_base_units(self) -> None:
        """Sets the base units of the Datum instance as its default units"""

        q = self.quantity.to_base_units()
        self.use_units(q.units)

    @type_check_decorator
    def convert(self, units: Union[str, Unit] = 'dimensionless') -> 'Datum':
        """
        Converts the Datum instance into a new Datum with the new units. DOES NOT rewrite the original Datum instance,
        but just returns the new one.

        :param units: string or pint.Unit
        :return: an instance of Datum
        """

        q = self.quantity.to(Unit(units) if isinstance(units, str) else units)
        m = q.magnitude
        u = q.units
        return Datum(self.variable, m, u)

    @type_check_decorator
    def convertable(self, units: Union[str, Unit] = 'dimensionless') -> bool:
        """
        Checks if the quantity of the Datum instance can be converted to the indicated units.

        :param units: string or pint.Unit to be compared with
        :return: boolean, True if the units are convertable, otherwise False
        """
        return self.quantity.is_compatible_with(Unit(units) if isinstance(units, str) else units)

    @type_check_decorator
    def rewrite(self, value: Union[int, float], units: Union[str, Unit] = 'dimensionless') -> None:
        """
        Sets up a new value and units for the current Datum instance. The new units do not need to be compatible with
        the old ones, thus this function completely overwrites the previous data.

        :param value: new magnitude of the Datum instance, int or float
        :param units: new units of the Datum instance, str or pint.Unit
        :return: None
        """

        if self.convertable(units):
            new_datum = Datum(self.variable, value, units)
            new_datum = new_datum.convert(self.units)
            self._value = new_datum.magnitude
        else:
            raise IncompatibleUnits(initial_units=str(units), final_units=self.str_units, variables=locals())

    def scale(self, factor: int|float) -> None:
        """
        Changes the magnitude of the Datum by a factor of "factor" parameter, preserving the units.

        :param factor: int or float. The magnitude of the Datum will be multiplied by this number
        :return: None
        """

        magnitude = self.magnitude * factor
        units = self.units
        self.rewrite(magnitude, units)

    @property
    def units(self) -> Unit:
        return self._units

    @property
    def str_units(self) -> str:
        return str(self._units)

    @property
    def magnitude(self) -> float:
        return self._value

    @property
    def variable(self) -> str:
        return self._variable

    @property
    def quantity(self) -> Quantity:
        return self.magnitude * self.units

    @property
    def ALLOW_NEGATIVES(self) -> bool:
        return self._ALLOW_NEGATIVES

    @type_check_decorator
    @ALLOW_NEGATIVES.setter
    def ALLOW_NEGATIVES(self, value: bool) -> None:
        self._ALLOW_NEGATIVES = value

    @property
    def num_decimals(self) -> int:
        return self._get_decimals(self.magnitude)
