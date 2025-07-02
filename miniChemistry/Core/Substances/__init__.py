"""
The Substances file describes the main substance's types used in this module. In fact, the code written here is based
on real (school) chemistry, however it is still somewhat simplified to make it possible to code. There are three main
substance types in miniChemistry, those are SIMPLE, MOLECULE, and ION. They all extend an abstract class (ABC) called
Particle which defines properties and methods common to all the substances.


TERMINOLOGY
In chemistry, we call by a particle any chemical object, an atom, a molecule, an ion, etc. A substance, in contrast, is
a macro world's object like water, sugar or salt. So, the class Particle is the most general one here, and it describes
the main attributes that every particle must have. Molecule, Simple and Ion just extend the class to make it more
specific and to fit the chemical description of each class of particles.


BACKGROUND FROM CHEMISTRY
The smallest unit of substance in chemistry is called an atom. That means, we can't chemically (i.e. by using
chemical reactions, chemical methods) divide an atom. There are 118 known atom types today which are called chemical
elements (see more in 'ptable.py' file). This code does not simulate individual atoms, so we don't have a class for them.
Instead, this code starts with molecules, which are groups of atoms bonded in a specific way. Molecules can differ
based on

1) the number of atoms
2) kind of atoms
3) arrangement of atoms

That means we can have molecules that consist of (1) two, three, four and much more atoms. We can also have molecules
with the same number of atoms, but different atom types (2) (different chemical elements). Finally, it is possible that
two molecules consist of the same atoms in the same quantities, but the arrangement of the atoms is different. In the
latter case the molecules are called isomers, and (!) they are not supported by this package. Hence, molecular formula,
i.e. composition of a molecule is its unique signature of a substance.

A special case of molecules is the ones that consists of only one type of atoms (one chemical element). Their substances
are called simple (in contrast to complex substance of molecules of more than one chemical element). The class Simple
describes such molecules as separate data type, because this will be important when we come to chemical reactions.

Finally, an ion is a charged set of atoms. This can be both single atom with a charge, or it can be a group of atoms
with some charge. There are rules in chemistry by which we decide what is the charge of a group of atoms based on their
properties, however in this package mostly the charges are set by the user (the exceptions are described separately).


IMPLEMENTATION
So, this file contains (and hence this package uses) three types of substances – Molecule which describes a group of
atoms of several chemical elements with zero charge; Simple which describes a group of atoms (one or more) of the same
chemical element with zero charge; Ion, which describes a group of atoms with charge not equal to zero.

In this code any molecule consists of two ions – cation and anion (positive and negative respectively). Hence, to
define a molecule it is enough to define both ions. There are special methods to create acids, bases and oxides faster
since their ions (one out of two) are known.

Finally, each class has some special substances which are defined as class' attributes. For example, water is a special
substance for Molecule class just because water is a very common molecule. Simple class has all substances with index 2
as special substances (those are H2, N2, O2, F2, Cl2, Br2, I2). The special substances can be addressed as class
attributes, however they are themselves instances of another class which defines their __get__ method. This is done
because (as they are instances of the class contained within that class) the substances have to be defined after the
constrictor of a class is run, otherwise we get a loop. So, there is an initiation method for these substances. To avoid
complex and unreadable error messages in the cases when a user tries to use undefined special substances, their __get__
method checks whether they are initiated and if not just gives a custom error message that directly asks to call
initiation method of a given class.


CONVERTION BETWEEN THE TYPES
It might be useful to convert between the types of substances and some other data types within the module. To do this
several functions named same as the classes are defined below. They take in data types that can (logically in real
chemistry) be converted into the required data type and perform some operations for this. For example, it is common
to convert between a chemical element (pt.Element) and a simple substance (Simple), because the simple substance contains
only this element. Hence, the function would be

element = simple(pt.Al)  # Returns Simple with formula 'Al'
element = simple(pt.O)  # Returns Simple with formula 'O2'

The following functions are defined:
ion() -> Ion
simple() -> Simple
molecule() -> Molecule

and

is_gas() which will be needed for prediction of chemical reaction outputs. It uses common patterns from school chemistry
to determine whether a substance passed to the function is a gas.
NOTE: the method does not really check if this is a gas. It just uses common rules that are not strict. So, the function
can make mistakes in complicated cases.
"""


from miniChemistry.Core.Substances.Ion import Ion
from miniChemistry.Core.Substances.Simple import Simple
from miniChemistry.Core.Substances.Molecule import Molecule
from miniChemistry.Core.Substances.IonGroup import IonGroup

from miniChemistry.Core.Substances.convert import *


Simple.create_special_simples()
Ion.create_special_ions()
Molecule.create_special_molecules()
