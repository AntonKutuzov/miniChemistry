"""
The QuantityCalculator is a class that allows to perform calculations on variables (Datum instances) keeping both
the magnitudes and the units. The whole functionality of the class works for a method called "solve()". The idea is to
write down the data, run the solve() method and get the result at the end. So, the class reads the equations from a
text file, allows to write the data in any form of SI units, and calculate the target variable. For example, since the
formulas are given for chemistry, let's find the number of moles of a substance with molar mass = 18 g/mole and a
certain mass.

The formulas used here is n=m/M (simple school chemistry), which is present in the "formulas.txt" file. The example
then looks like

>>> qc = QuantityCalculator()
>>> qc.write_value(Datum('M', 18, 'g/mole'))
>>> qc.write_value(Datum('mps', 0.713, qc.ureg.gram))

>>> s = qc.solve(solve_for='n', round_to=3, answer_units=qc.ureg.millimole)
>>> print(*s)
n = 39.611 millimole

Here we defined a variable (not to call it quantity, which can be confused with pint.Quantity. Variable also has a
special symbol, like "mps" for "mass pure solid") with a value of 0.713 grams. We also defined another variable with
molar mass ("M") equal to 18 grams/mole. In the solve() method we specify what kind of answer we want: the variable with
a symbol "n" (moles), rounded to 3 digits after the comma, and in the units of millimoles. In all cases the units
can be specified as both strings and pint.Unit.

The class uses sympy to solve equations, which means it substitutes the written values by the numbers and solves
for the target variable's symbol. To clear the equations (get them back to purely symbolical form), use the clear()
method. To erase value (magnitude and units) of one or more variables use the erase_value() method. If the clear()
method is used, only the variables with a default value will be kept. The default values are given in the text files.

TEXT FILES\n
"formulas.txt"\n
The formulas are stored in a separate text file, split by a new line sign. The formulas are written in a form that they
can be directly converted in sympy.Expr object, i.e. without an equal sign, but with a negative sign. For example, a
formulas n=V/V0 will look like n-V/V0. In the first case the sympy.parse_expr() constructor will raise an exception.\n

"units_and_names.txt"\n
Each variable from the formulas.txt file must be written into the "units_and_names.txt" file in the following form:\n
<variable symbol>:<variable name>:<variable units>\n
The name can include spaces. For the units, they must be within the SI system, but do not necessarily need to be in
the base SI units. For example, they can be "grams", "mole/L" or something similar.
"""


import sympy as sp
import pint
from typing import List, Dict, Tuple, Union

from miniChemistry.Computations.ComputationExceptions.DatumException import IncompatibleUnits
from miniChemistry.Utilities.File import File
from miniChemistry.Computations.Datum import Datum
from miniChemistry.Utilities.Checks import type_check_decorator
from miniChemistry.Computations.ComputationExceptions.QuantityCalculatorException import (
    UnknownVariableException,
    VariableHasValue,
    ValueNotFoundException,
    SolutionNotFound
)


class QuantityCalculator:
    """
    The QuantityCalculator has the following methods:\n
    VARIABLE CONTROL\n
    - write_value(d: Datum) -> None\n
    - read_value(d: Datum|str, units: pint.Unit|str = 'default') -> Datum\n
    - erase_value(var: str) -> None\n
    - clear() -> None\n
    - solve(solve_for: str|Datum, answer_units: str|pint.Unit, round_to: int|None = 2) -> List[Datum]\n

    TESTS\n
    - has_value(name: str) -> bool

    (PRIVATE) READING DATA\n
    - _read_formula() -> List[sympy.Expr]\n
    - _read_units_and_symbols() -> Tuple[Dict[str, pint.Unit], Dict[str, str]]\n
    - _read_default_values() -> List[Datum]\n

    (PRIVATE) MANAGING EQUATIONS\n
    - _push() -> None # substitutes all the variables into the equations
    - _solve_from_strings(solve_for: str) -> List[Datum]\n
    - _solve_from_datum(d: Datum) -> List[Datum]

    PROPERTIES\n
    - equations() -> List[sympy.Expr]\n
    - default_units() -> Dict[str, pint.Unit]\n
    - var_symbols() -> Tuple[str, ...]\n
    - values() -> List[Datum]\n
    - constants() -> List[Datum]\n
    - ureg() -> pint.UnitRegistry\n
    """

    def __init__(self):
        self._formulas_file = File(__file__).caller.parent / 'CalculatorFiles/formulas.txt'
        self._units_names_file = File(__file__).caller.parent / 'CalculatorFiles/units_and_names.txt'

        self._ureg = pint.UnitRegistry(system='SI')

        self._formulas_list = self._read_formulas()
        self._tfl = self._formulas_list.copy()  # "temporary formula list" (the one that will get updated each time)

        self._default_units, self._symbols = self._read_units_and_symbols()
        self._values = self._read_default_values()
        self._constants = self._values.copy()

    # ================================================================================================== PRIVATE METHODS
    def _read_formulas(self) -> List[sp.Expr]:
        formula_list = list()
        with open(self._formulas_file, 'r') as file:
            for line in file:
                eq = sp.parse_expr(line.strip('\n'))
                formula_list.append(eq)
        return formula_list

    def _read_units_and_symbols(self) -> Tuple[Dict[str, pint.Unit], Dict[str, str]]:
        """Check how the "units_and_names.txt" file is organized."""

        unit_dict = dict()
        symbol_dict = dict()
        with open(self._units_names_file, 'r') as file:
            for line in file:
                symbol, name, units, default_value = line.strip('\n').split(':')
                # the line below returns the default SI units regardless of what is given in the .txt file
                units = self._ureg.parse_expression(units).to_base_units().units
                unit_dict[symbol] = units
                symbol_dict[name] = symbol
        return unit_dict, symbol_dict

    def _read_default_values(self) -> List[Datum]:
        value_list = list()
        with open(self._units_names_file, 'r') as file:
            for line in file:
                symbol, name, units, default_value = line.strip('\n').split(':')
                if default_value == 'None':
                    continue
                else:
                    d = Datum(symbol, float(default_value), units)
                    value_list.append(d)
        return value_list

    def _push(self) -> None:
        for var in self.values:
            for index, expr in enumerate(self._tfl):
                q = var.quantity.to_base_units()
                self._tfl[index] = expr.subs(var.variable, q.magnitude)

    def _solve_from_strings(self, solve_for: str) -> List[Datum]:
        """
        The method solves each equation for the target variable and checks if the solution(s) obtained is a numerical
        value. If it is, then the method returns the respective Datum as a list. The units of the Datum in this
        method will always be default SI units for the given variable.\n

        IMPORTANT: the method takes the first solution found. I.e. if two formulas could give the same (or different,
        although in this case it's already a mistake) solution, only the one obtained from the first formula will be
        returned.

        :param solve_for: the symbol of the variable for which the result is to be obtained
        :return: A list of Datum instances which are solutions to the suitable equations
        """

        target = sp.Symbol(solve_for)
        self._push()
        for eq in self._tfl:
            solutions = sp.solve(eq, target)
            if len(solutions) > 0 and all([answer.is_number for answer in solutions]):
                answers = list()
                for solution in solutions:
                    units = self._default_units[solve_for]
                    answers.append(Datum(solve_for, float(solution), units))
                self._tfl = self._formulas_list.copy()
                return answers

    def _solve_from_datum(self, d: Datum) -> List[Datum]:
        symbol = d.variable
        return self._solve_from_strings(symbol)

    # ================================================================================================== PRIVATE METHODS
    @type_check_decorator
    def has_value(self, name: str) -> bool:
        names = [var.variable for var in self.values]
        return name in names

    @type_check_decorator
    def write_value(self, d: Datum) -> None:
        """
        Before the Datum can be written to the variables of the QuantityCalculator, two checks must be made:\n
        - If the variable with this symbol is present in the formulas (more precisely – in the "units_and_names.txt" file\n
        - If there's no Datum with the same variable (has_value() method)

        :param d: Datum to be written in as a value for a given variable
        :return: None
        """

        name, value, units = d  # unpacking the list from Datum.__iter__ method
        if name not in self.var_symbols:
            raise UnknownVariableException(name, variables=locals())
        elif self.has_value(name):
            raise VariableHasValue(d.variable, variables=locals())
        elif not units.is_compatible_with(self._default_units[name]):
            raise IncompatibleUnits(initial_units=str(units), final_units=self._default_units[name], variables=locals())
        else:
            self._values.append(d)

    def read_value(self, d: Datum|str, units: pint.Unit|str = 'default') -> Datum:
        """


        :param d:
        :param units:
        :return:
        """

        name = d.variable if isinstance(d, Datum) else d

        for i, dat in enumerate(self.values):
            if dat.variable == name and self.has_value(dat.variable):
                return self.values[i] if units == 'default' else self.values[i].convert(units)
        else:
            raise ValueNotFoundException(name, variables=locals())

    @type_check_decorator
    def erase_value(self, var: str) -> None:
        if self.has_value(var):
            names = [var.variable for var in self.values]
            i = names.index(var)
            self.values.pop(i)
        else:
            raise ValueNotFoundException(var, variables=locals())

    def clear(self) -> None:
        """Copies the formulas from the self._formula_list into the self._tfl list, which stands for "temporary
        formula list", and which is used to solve equations for the target variable. The original formula list is
        never changed."""

        self._values = self._read_default_values()
        self._tfl = self._formulas_list.copy()

    def solve(self,
              solve_for: Union[str, Datum],
              answer_units: Union[str, pint.Unit] = 'default',
              round_to: int|None = 2) -> List[Datum]:
        """
        The method uses _solve_from_datum or _solve_from_strings private methods to get the solution of the current
        set of equations (current = with all the given variables), and then sets up the answer. First it checks that
        there is at least one solution (that the "solutions" list is not empty), then converts it to the required
        units and round up to a given number of digits.

        :param solve_for: the target variable given in as a Datum or as a string
        :param answer_units: THe string or pint.Unit instance indicating the units for the answer
        :param round_to: the number of digits after the comma that the answer must have
        :return: a list of Datum instances obtained from self._solve_from_string() method
        """

        if isinstance(solve_for, Datum):
            solutions = self._solve_from_datum(solve_for)
        elif isinstance(solve_for, str):
            solutions = self._solve_from_strings(solve_for)
        else:
            raise TypeError('Wrong "solve_for" argument type in a function "QuantityCalculator/solve()".')

        if not solutions:
            target = solve_for.variable if isinstance(solve_for, Datum) else solve_for
            raise SolutionNotFound(target, variables=locals())

        for i, solution in enumerate(solutions):
            if not answer_units == 'default':
                final_units = answer_units if isinstance(answer_units, pint.Unit) else pint.Unit(answer_units)
                solution = solution.convert(final_units)

            if round_to is not None:
                solution.rewrite(value=round(solution.magnitude, round_to), units=solution.units)
            else:
                solution.rewrite(value=solution.magnitude, units=solution.units)
            solutions[i] = solution

        return solutions

    # ======================================================================================================= PROPERTIES
    @property
    def equations(self) -> List[sp.Expr]:
        return self._formulas_list

    @property
    def default_units(self) -> Dict[str, pint.Unit]:
        return self._default_units

    @property
    def var_symbols(self) -> Tuple[str, ...]:
        return tuple(self._symbols.values())

    @property
    def values(self) -> List[Datum]:
        return self._values

    @property
    def constants(self) -> List[Datum]:
        return self._constants

    @property
    def ureg(self) -> pint.UnitRegistry:
        return self._ureg

"""
qc = QuantityCalculator()
qc.write_value(Datum('M', 18, 'g/mole'))
qc.write_value(Datum('mps', 0.713, qc.ureg.gram))

s = qc.solve(solve_for='n', round_to=3, answer_units=qc.ureg.millimole)
print(*s)
"""