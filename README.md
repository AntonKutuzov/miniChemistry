# About miniChemistry Project
*miniChemistry Project* is a Python package designed to simulate basics of chemistry, and to perform typical stoichiometric calculations over chemical reactions.

## Features
The package consists of four main parts.

- **Periodic table, metal activity series and some other chemical data as well as simple description of molecule and ion**.
	- Each database is implemented in a form of .csv file
	- Molecule and ion (particles from chemistry) are simulated by using classes, inheriting from an abstract class Particle (see "Substances.py")

- **Reaction prediction tool**
	- A chemical reaction is described in a single class that can balance and predict reactions as well as converting strings to Reaction instance
	- "ReactionMechanisms" directory contains description of all functions used to convert reaction reagents to products
	- "predict.py" contains the code used to classify the reactions and chose the correct prediction mechanism

- **Stoichiometric calculator**
	- A class in "ReactionCalculator.py" implements all basic algorithms needed for stoichiometric calculators over chemical reactions
	- Uses QuantityCalculator to iterate over most used formulas in chemistry, conserving units of all quantities

- **Examples**
	- Several examples that demonstrate how the package can be used to solve or create exercises in chemistry

Together these parts provide a simple, but powerful enough framework for solving typical stoichiometric exercises in chemistry.

## Dependencies
- chemparse
- [QuantityCalculator](https://github.com/AntonKutuzov/QuantityCalculator)

# Applications
*miniChemistry project* has two main applications: *solving* many exercises of the same kind, and *creating* exercises of the same kind. Using Python loops and collections (lists and dicts mostly) allows to use a single solution mechanism for many exercises by changing reaction or input data. In the same way they allow to create exercises of the same type by changing numbers, quantities or reactions.

# Installation  
Git clone the repository and run `build.sh`

# Examples
The code contains several examples on how to solve exercises and how to create them. To run the examples, open the console, run the following code
```py
from miniChemistry import EXAMPLES
```
And follow the instructions.

**NOTE: prior knowledge of chemistry is required to understand the exercises.**

# Contributions Welcome
The project is mostly written by a single chemical engineering student. Hence, despite many checks and tests, the code can contain some mistakes and can sometimes result in errors. Contributions, improvements or issue reports are always welcomed.
