# miniChemistry Documentation

This guide provides a high level overview of the project, its core packages and a brief reference of the most visible classes and functions.

## Project Structure

`miniChemistry` is organised into two major cores:

* **Core** – contains modelling primitives for chemical substances and reactions.  It is responsible for reading chemical databases, predicting reaction products and representing molecules, ions and reactions.
* **Computations** – builds on top of `Core` and performs stoichiometric calculations using linear algebra utilities.  It wraps the reaction objects to compute moles, ratios and other values.

The repository also includes a small **Utilities** package with helper functions and classes, an `EXAMPLES` package with usage examples and a command line entry point `cli.py`.

### Core subpackages

```
Core/
├── Database/              # CSV databases (solubility tables, activity series)
├── ReactionMechanisms/    # Functions that produce reaction products
├── Tools/                 # Parser, reaction predictor and helpers
├── Substances.py          # Particle, Simple, Ion and Molecule classes
├── Reaction.py            # Reaction class describing reagents and products
└── CoreExceptions/        # Custom exceptions
```

### Computations subpackages

```
Computations/
├── ReactionCalculator.py        # Main class for stoichiometric calculations
├── SSDatum.py                   # Datum with linked substance information
├── ComputationExceptions/       # Exceptions for calculation modules
└── CalculatorFiles/             # Text files with formulas and units
```

Both cores rely on a small `Utilities` package that provides input validation helpers and a tiny `File` abstraction to work with text files.

## Relations between cores

The `Computations` core uses the `Reaction` class and the substance classes from the `Core` package.  A simplified relation diagram is shown below.

```
[ReactionCalculator] --uses--> [Reaction]
[Reaction] --has--> [Molecule] / [Simple] / [Ion]
[Molecule] and [Simple] inherit from [Particle]
```

## UML diagrams

### Core

```
class Particle <<abstract>>
    +composition: Dict[Element, int]
    +charge: int
    +from_string(...)
    +formula()
```

```
class Simple extends Particle
    +element: Element
    +index: int
```

```
class Ion extends Particle
    +is_cation
    +is_anion
```

```
class Molecule extends Particle
    +cation: Ion
    +anion: Ion
    +simple_class()
```

```
class Reaction
    +reagents: List[Particle]
    +products: List[Particle]
    +equation
    +coefficients
```

### Computations

```
class SSDatum(Datum)
    +substance: Molecule|Simple
```

```
class ReactionCalculator
    +reaction: Reaction
    +write(...)
    +compute_moles_of(...)
    +compute(...)
```

## API Reference with examples

### Creating substances

```python
from miniChemistry.Core.Substances import Simple, Ion, Molecule
import miniChemistry.Core.Database.ptable as pt

h2 = Simple(pt.H, 2)
na = Ion({pt.Na:1}, 1)
cl = Ion({pt.Cl:1}, -1)
NaCl = Molecule(na, cl)
print(NaCl.formula())  # NaCl
```

### Working with reactions

```python
from miniChemistry.Core.Reaction import Reaction
from miniChemistry.Core.Substances import Molecule, Simple

r = Reaction(Simple(pt.Na,1), Molecule.water)
print(r.equation)  # balanced equation
```

### Stoichiometric calculations

```python
from miniChemistry.Computations.ReactionCalculator import ReactionCalculator
from miniChemistry.Computations.SSDatum import SSDatum

rc = ReactionCalculator("Na + H2O -> NaOH + H2")
rc.write(SSDatum(rc.reaction.products[0], 'mps', 25, 'g'))
print(rc.compute_moles_of(rc.reaction.products[0]))
```

The examples under `miniChemistry/EXAMPLES` provide more extensive scripts demonstrating these classes in action.
