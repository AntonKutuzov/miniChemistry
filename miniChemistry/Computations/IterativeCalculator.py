"""
IterativeCalculator is an extension of the QuantityCalculator class. The main functionality in this class is to
solve each of the QuantityCalculator equations for each of its variables until (and this is important) no new
variables can be found. The algorithm is the following:\n
(With the variables set initially in QuantityCalculator)\n
- Solve all equations for all unknown variables\n
- Check each answer and select the ones that are numerical values (not expressions)\n
- Write them down to the QuantityCalculator\n
- If at least one new variable was found, go to step 1, else stop the algorithm\n
The algorithm is implemented in the solve() function (same name, but different functionality as in QuantityCalculator).
\n
The IterativeCalculator allows for more flexible settings of the physical conditions. Namely, it allows to read from a
text file (and immediately apply them) assumptions (described below). Mostly, apart from the main functionality, the
IterativeCalculator copies methods from QuantityCalculator to avoid using the calculator() property too often. Thus,
the class methods for writing, erasing, scaling, and increasing and decreasing the variables. Basically, all the
methods in this class can be categorized with one of the three purposes\n
- Solving iteratively all the equations (main functionality)\n
- Managing physical quantities (Datum instances)\n
- Properties\n
"""


from miniChemistry.Computations.ComputationExceptions.QuantityCalculatorException import ValueNotFoundException
from miniChemistry.Computations.QuantityCalculator import QuantityCalculator
from miniChemistry.Computations.ComputationExceptions.QuantityCalculatorException import UnknownVariableException
from miniChemistry.Computations.ComputationExceptions.IterativeCalculatorException import (
    IncorrectFileFormatting,
    AssumptionFailed,
    SolutionNotFound,
    NegativesNotAllowed)
from miniChemistry.Utilities.File import File
from miniChemistry.Computations.Datum import Datum
from typing import List, Generator, Tuple
import pint
from sympy import Expr


class Assumption:
    """
    An assumption in chemistry (and physics) is a statement that is accepted to be True (with some reasoning and
    limitations). The following theory is then built having this assumption in mind. Often assumptions allow to use
    some equations, and in our case an assumption would be a list of pre-set variables that are loaded at the very
    beginning and are used in calculations without necessity to explicitly set them up.\n

    For example, very common assumption, especially in school chemistry, is a "standard temperature and pressure
    conditions" assumption, often shortened as "STP". In our language it can be written as\n

    T = 273+25 K\n
    p = 101325 Pa\n

    Apart from constants (default values for the quantities), the assumptions can be "disables" and "enables", which means
    you decide which assumption to use. Comparing to the value of R which you will anyway use because it's always the
    (and hence it's a waste of time to set it up explicitly each time) same.\n

    This class described the three important parts of any assumption (from the coder's perspective):\n
    - The assumption itself, i.e. the pre-set values for some quantities\n
    - The values that can be calculated from these pre-set values and constants based on the given equations\n
    - The variables that we assume only for calculating the previous ones, and then erase\n

    ================ EXAMPLE ================\n
    For example,\n
    let's assume STP. The assumption itself looks like this\n
    >>> ic = IterativeCalculator()
    >>> ic.write(Datum('T', 273+25, 'K'))
    >>> ic.write(Datum('P', 101325, 'Pa'))\n
    This code writes the variables that are known UNDER THIS assumption. They are not universal constants as, for example,
    the universal (wow...) gas constant, R, which is always 8.31 J/(mol*K).\n

    However, after we set the new variables, the new formulas are "unlocked" and ready to use. And we can compute a
    condition-dependent constants, such as V0 (which is a constant at a given temperature and pressure).
    Knowing what is molar volume of a gas (refer to school chemistry), we see that to find it we need actually to assume
    that the number of moles is equal to 1, i.e.
    >>> ic.write(Datum('n', 1, 'mole'))  # only for the assumption

    Now, having all the needed variables for pV=nRT, we can express the volume, V = (nRT/p), and compute the V0 since
    at n = 1, V = V0 by definiton.

    >>> ic.target = Datum('V0', 0.01, 'L/mol')
    >>> result = ic.solve()
    >>> print(result)
    V0 = 24.44 liter / mole

    After we computed the variable, it is already automatically written in, and what is left is erasing the variable
    we assumed: n = 1, i.e.

    >>> ic.clear('n')

    ============== EXAMPLE (END) ==============\n

    The Assumption class provides three different lists for the three different variable types:\n
    - _to_compute list with variables that will be computes, like V0
    - _variables list with variables that will be the main assumption, like T and P
    - _to_assume list with variables that will be set temporarily for calculations, like n=1
    The respective setter methods are to_compute(), to_set() and to_assume(). The class also provides the save() method
    which writes the assumption to a text file in a correct manner. The class also has some properties.
    """

    def __init__(self, symbol: str, name: str) -> None:
        self._symbol = symbol
        self._name = name
        self._variables = list()
        self._to_compute = list()
        self._assume = list()

    def __str__(self):
        return (f'{self._symbol} (full name: "{self._name}"). Assumes {', '.join([str(datum) for datum in self._variables])}.'
                f' Computes {', '.join([str(var.variable) + ' in ' + str(var.units) for var in self._to_compute])}.'
                f' Temporarily assumes for calculations that {', '.join(str(var) for var in self._assume)}.')

    def to_compute(self, *vars: Datum) -> None:
        self._to_compute.extend(list(vars))

    def to_set(self, *data: Datum) -> None:
        self._variables.extend(data)

    def to_assume(self, *data: Datum) -> None:
        self._assume.extend(data)

    def save(self) -> None:
        file = File(__file__)
        file.bind('CalculatorFiles/Assumptions')

        file.append(f'!{self._symbol}: {self._name}')
        for var in self._variables:
            symbol, value, units = var
            file.append(f'variable {symbol}:{value}:{str(units)}')
        for var in self._to_compute:
            symbol, value, units = var
            file.append(f'compute {symbol}::{str(units)}')
        for var in self._assume:
            symbol, value, units = var
            file.append(f'assume {var}:{value}:{str(units)}')
        file.append('!')
        file.append('')

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def name(self) -> str:
        return self._name

    @property
    def variables(self) -> List[Datum]:
        return self._variables

    @property
    def compute(self) -> List[Datum]:
        return self._to_compute

    @property
    def assume(self) -> List[Datum]:
        return self._assume


class IterativeCalculator:
    """
    The structure of IterativeCalculator is similar to the one of QuantityCalculator. It also allows to write in all the
    data and then call the solve() method to obtain the result. The difference, however, is in the solving algorithm.
    This class iterates over the equations until the results it gets do not change. Most of other methods just copy
    the functionality of QuantityCalculator to avoid always using the calculator() property.
    """

    def __init__(self):
        self._calculator = QuantityCalculator()
        self._target = None


    # ================================================================================================== PRIVATE METHODS
    @staticmethod
    def _read_assumptions() -> Generator[Assumption, None, Assumption]:
        file = File(__file__)
        file.bind('CalculatorFiles/Assumptions')

        assumption = None

        for line in file.read_all():
            if line.startswith('#'):
                continue
            elif line == '!':
                if assumption is not None:
                    yield assumption
                else:
                    raise IncorrectFileFormatting(file_name=file.name, variables=locals())
                assumption = None
            elif line.startswith('!'):
                symbol, name = line.split(':')
                symbol = symbol.strip('!').strip(' ')
                name = name.strip(' ')
                assumption = Assumption(symbol, name)
            elif line.startswith('variable'):
                a, b = line.split(' ')
                symbol, value, unit = b.split(':')
                d = Datum(symbol, float(value), unit)
                assumption.to_set(d)
            elif line.startswith('compute'):
                a, b = line.split(' ')
                var, units = b.split('::')
                assumption.to_compute(Datum(var, 0, units))
            elif line.startswith('assume'):
                a, b = line.split(' ')
                var, value, units = b.split(':')
                assumption.to_assume(Datum(var, float(value), units))
            elif line.isalnum():
                raise IncorrectFileFormatting(file_name=file.name, variables=locals())

        if assumption is not None:
            return assumption

    def _apply_assumption(self, assumption: Assumption) -> None:
        keep_variables = list()

        for var in assumption.assume:
            self.write(var)

        for var in assumption.variables:
            keep_variables.append(var.variable)
            self.write(var)

        for var in assumption.compute:
            keep_variables.append(var.variable)
            self.target = var
            self.solve(stop_at_target=True)

            if not self.calculator.has_value(var.variable):
                raise AssumptionFailed(assumption_symbol=assumption.symbol, variables=locals())

        self.clear_all(but=keep_variables)

    #                                                                                                     solver methods
    def _compute_all_possible_vars(self) -> List[Datum]:
        """
        The method solves all equations for all variables and appends any obtained result to a list that is then
        returned.

        :return:
        """

        interres = list()
        for var in self.calculator.var_symbols:
            if not self.calculator.has_value(var):
                try:
                    res = self.calculator.solve(var, round_to=None)
                    interres.append(*res)
                except:
                    continue
        return interres

    def _iterate(self) -> List[Datum]:
        """
        The method initiates an infinite loop which computes all possible variables on this iteration, writes
        then down and either yields the obtained variables or returns them (returns an empty list).

        The idea is that while there are new variables obtained, there are new conditions set up for solving equations.
        New conditions can yield more variables. The algorithm is then ran until no new variables are obtained, i.e.
        no new conditions can be imposed. In this case there's no point to keep the loop running, and the loop is
        interrupted.

        :return: List of Datum
        """

        while True:
            interres = self._compute_all_possible_vars()  # "interres" = intermediate result

            for d in interres:
                self.write(d)

            if interres:
                yield interres
            else:
                return interres


    # =================================================================================================== PUBLIC METHODS
    def assume(self, *names: str) -> None:
        """
        First the method reads all the assumptions by using _read_assumptions() method, and then selects only the
        names of the assumptions. Then it checks if the name passed as a parameter is in the names of the assumptions
        read, and if yes,a applies the assumption.

        :param names:
        :return:
        """

        read_assumptions = [a for a in self._read_assumptions()]
        assumption_names = [a.symbol for a in read_assumptions]

        for i, name in enumerate(names):
            if name in assumption_names:
                self._apply_assumption(read_assumptions[i])

    #                                                                                                     solver methods
    def solve(self,
              stop_at_target: bool = False,
              alter_target: bool = True) -> Datum:
        """
        This trick with for–in: pass is done to preserve variables in the iterate() function. Basically, we need
        some static variables there, and since Python does not support then in the same way as Java or C, the
        generators are used.

        The method iterates over all newly obtained variables and checks if the target variable is among them. If yes
        AND if "stop_at_target" is set to True, the iterations stop. The result (target variable) is then read and
        rounded, and returned.

        If "alter_target" is set to True, the self.target property is changed to contain the obtained Datum instance.

        :param stop_at_target: True if the process can be stopped after the target variable is obtained
        :param alter_target: True if the target property has to be changed
        :return: an instance of Datum of the target variable
        """
        for data in self._iterate():
            if self.target.variable in [d.variable for d in data] and stop_at_target:
                break

        if self.calculator.has_value(self.target.variable):
            result = self.calculator.read_value(self.target, units=self.target.units)
        else:
            raise SolutionNotFound(self.target.variable, variables=locals())

        new_magnitude = round(result.magnitude, self.target.num_decimals)
        answer = Datum(result.variable, new_magnitude, result.units)

        if alter_target:
            self.target = answer
        return answer

    #                                                                                        variable management methods
    def write(self, *data: Datum) -> None:
        present = [d.variable in self.calculator.var_symbols for d in data]

        if all(present):
            self.calculator.write_value(*data)
        else:
            for i, p in enumerate(present):
                if not p:
                    uve = UnknownVariableException(data[i].variable, variables=locals())
                    uve.description += '\nThe exception was raised from an IterativeCalculator "write" method.'
                    raise uve

    def clear_all(self, *, but: List[str]) -> None:
        for var in self.calculator.var_symbols:
            if var not in but and self.calculator.has_value(var):
                self.clear(var)

    def clear(self, var: str) -> None:
        if self.calculator.has_value(var):
            self.calculator.erase_value(var)
        else:
            vnf = ValueNotFoundException(var, variables=locals())
            vnf.description += '\nThe exception was raised from an IterativeCalculator "write" method.'
            raise vnf

    def scale(self, var: str, factor: float|int) -> Datum:
        """Used to multiply the Datum instance by a certain number"""
        if var not in self.calculator.var_symbols:
            uve = UnknownVariableException(var, variables=locals())
            uve.description += '\nThe exception was raised from an IterativeCalculator "write" method.'
            raise uve

        q = self.calculator.read_value(var)
        d = Datum(q.variable, factor*q.magnitude, q.units)
        self.calculator.erase_value(var)
        self.calculator.write_value(d)
        return d

    def add(self, var: str, value: float|int, allow_negatives: bool = False) -> Datum:
        if var not in self.calculator.var_symbols:
            uve = UnknownVariableException(var, variables=locals())
            uve.description += '\nThe exception was raised from an IterativeCalculator "write" method.'
            raise uve

        q = self.calculator.read_value(var)
        d = Datum(q.variable, q.magnitude+value, q.units)

        if not allow_negatives and d.magnitude < 0:
            raise NegativesNotAllowed(var, value, variables=locals())
        else:
            self.calculator.erase_value(var)
            self.calculator.write_value(d)
            return d

    def sub(self, var: str, value: float|int, allow_negatives: bool = False) -> Datum:
        return self.add(var, -value, allow_negatives)

    def div(self, var: str, value: float|int) -> Datum:
        return self.scale(var, 1/value)

    def read(self, var: str, units: pint.Unit|str = 'default') -> Datum:
        return self.calculator.read_value(var, units)

    def has_value(self, var: str) -> bool:
        return self.calculator.has_value(var)

    def units(self, var: str) -> pint.Unit:
        q = self.calculator.read_value(var)
        return q.units

    def units_str(self, var: str) -> str:
        return str(self.units(var))

    # ======================================================================================================= PROPERTIES
    @property
    def calculator(self) -> QuantityCalculator:
        return self._calculator

    @property
    def target(self) -> Datum:
        return self._target

    @target.setter
    def target(self, value: Datum) -> None:
        if not isinstance(value, Datum):
            raise TypeError("The target variable must be a Datum instance.")
        self._target = value

    @property
    def variables(self) -> Tuple[str, ...]:
        return self.calculator.var_symbols

    @property
    def equations(self) -> List[Expr]:
        return self.calculator.equations


"""
ic = IterativeCalculator()
print('Assuming STP...')
ic.assume('STP')
print(*ic.calculator.values)
print('Writing down given data...')
# ic.write(Datum('V0', 0.224, 'm**3/mol'))
ic.write(Datum('Vpg', 25, 'L'))
ic.div('Vpg', 2)
print(ic.read('Vpg', 'L'))
ic.target = Datum('n', 0.001, 'mol')

print('Solving...')
print(ic.solve(stop_at_target=False))
print(ic.target)
"""