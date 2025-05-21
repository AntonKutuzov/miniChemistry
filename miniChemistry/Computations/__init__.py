from QCalculator.database import FORMULA_LIST, UNIT_REGISTRY, DEFAULTS, add_formula, add_variable
from QCalculator import Formula
from miniChemistry.Utilities.File import File


formulas_file = File(__file__)
formulas_file.bind('CalculatorFiles/formulas.txt')

for line in formulas_file.read_all():
    add_formula(line.strip('\n'), add_vars=False)

units_file = File(__file__)
units_file.bind('CalculatorFiles/units_and_names.txt')

for line in units_file.read_all():
    symbol, name, unit, default = line.split(':')

    if not default == 'None':
        default = float(default)
    else:
        default = None

    add_variable(symbol, unit, default = default)
