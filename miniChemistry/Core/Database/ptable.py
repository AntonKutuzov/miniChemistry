"""
BACKGROUND IN CHEMISTRY
Periodic table is one of the most important data sets in chemistry. Mathematically we can treat it as a matrix with
some cells filled with elements and some being empty. Position of an element in a periodic table gives us a lot of very
useful information when it comes to interactions between different elements and their compositions (molecules).

A chemical element, speaking formally, is a set of atoms with a given number of protons. But for us, in the scope of
this Python module, elements can be treated as classes. Their instances then are atoms that possess all the properties
of a given element. Atoms can bind to each other according to some chemical rules and form molecules. Hence, a molecule
is just a set of atoms (but same atoms can appear several times).

The periodic table looks like this

    I   II  III IV  V   VI  VII     VIII    I   II  III IV  V   VI  VII VIII
    A   A   B   B   B   B   B        B      B   B   A   A   A   A   A   A
––|–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
1 | H                                                                    He
2 | Li  Be                                           B   C   N   O   F   Ne
3 | Na  Mg                                           Al  Si  P   S   Cl  Ar
4 | K   Ca   Sc  Ti  V   Cr  Mn  Fe  Co  Ni  Cu  Zn  Ga  Ge  As  Se  Br  Kr
5 | Rb  Sr   Y   Zr  Nb  Mo  Tc  Ru  Rh  Pd  Ag  Cd  In  Sn  Sb  Te  I   Xe
6 | Cs  Ba  |La  Hf  Ta  W   Re  Os  Ir  Pt  Au  Hg  Tl  Pb  Bi  Po  At  Rn
7 | Fr  Ra  |Ac  Rf  Db  Sg  Bh  Hs  Mt  Ds  Rg  Cn  Nh  Fl  Mc  Lv  Ts  Og
            |
            |Ce  Pr  Nd  Pm  Sm  Eu  Gd  Tb  Dy  Ho  Er  Tm  Yb  Lu (Lanthanides)
            |Th  Pa  U   Np  Pu  Am  Cm  Bk  Cf  Es  Fm  Md  No  Lr (Actinides)

Since we can treat it as a matrix, the columns are called groups and are denoted by a number and a letter (A or B).
The rows are called periods and are also numbered. Even though in chemistry we usually say that the signature (in
kind of a programming sense) of an element is its number of protons, it is not a mistake to say that the signature
of an element is its position in the table. Lanthalides and actinides in this code both belong to III B group.

Position of an element in the table gives to us all its properties. However, there's a lot of chemistry needed to
explain them, so I will just list those that are required to know for this code.

PROPERTIES OF ELEMENTS USED
1) oxidation state, Tuple[int]. By oxidation state we usually mean the number of electrons that an atom gained or lost during a
a chemical reaction. However, since this code is not modelling electrons' movement, we can just treat as a set of numbers
that an atom can use to build a molecule with another atom. The only requirement would be that the weighed sum of these
numbers inside a molecule is equal to zero (for more see "Substance" file).

2) Symbol, str. In addition to group and period, each element has a unique name composed of one or two letters. You can
refer to every element in this code by using the symbols from periodic table. E.g.

    >>> import Core.Database.ptable as pt
    >>> pt.O.atomic_number  # symbol "O" refers to oxygen. Period 2, group VI A
    8

3) Atomic number, int (positive only). Atomic number is numerically equal to the number of protons inside an atom. So we
 can treat it as a serial number of an element. You can then see that since hydrogen (H) is the first in the table, its
 atomic number is 1. We count from left to right, from top to bottom. Skip the empty spaces, don't jump to the new period
 before the previous is completed. Lanthanides and actinides go after La and Ac respectively. (Believe me, there is clear
 logic in this if you look at it from the point of view of chemistry).

4) Molar mass, float (positive only). Since atoms are actually physical objects, they have a mass. Molar mass is just a
constant that shows mass of a certain number of atoms (namely 6.02**23 atoms, but this is not relevant for us). Molar
mass will be needed when making calculations over chemical reactions.

5) REN or Relative ElectroNegativity, float. REN is a property of an element that shows how strong it is at attracting
electrons. For us it may be important in the algorithms of building chemical bonds, predicting reactions and some other.
If you don't get it, you can think of it as of just another float number (both positive and negative).
Note: in chemistry electronegativity is only positive, but here also the value of -1 is used for the elements that do
not have this property in real world.

6) Radioactivity (boolean). Just included it here in case I would need it. I didn't. That's it.

STRUCTURE OF THE FILE
The file contains one class, Element, and 118 instances of it (all the elements from periodic table). The elements
(Element class' instances) are grouped into three large groups (namedtuples to keep the dot notation). These groups are

groups
periods
trivials

With "groups" and "periods" it is clear – you can access a group or a period separately. With "trivials", (almost) each
group in the table has also a trivial name. So, in case you want to address a group of elements (which is not always the
same as the group of periodic table) by their trivial name, use "trivials". This is done in the following way:

>>> pt.groups.FIRST_A
    (<Core.Database.ptable.Element object at 0x104f154f0>, <Core.Database.ptable.Element object at 0x104f160c0>,
    <Core.Database.ptable.Element object at 0x104f163c0>, <Core.Database.ptable.Element object at 0x104f168d0>,
    <Core.Database.ptable.Element object at 0x104f16d80>, <Core.Database.ptable.Element object at 0x104f17200>,
    <Core.Database.ptable.Element object at 0x104f178c0>)
>>> pt.trivials.ALKALI_METALS[0]
    <Core.Database.ptable.Element object at 0x104f160c0>

The names of the groups are written using capslock and with number in words, underscore, letter (A or B). Periods
are just numbers in words (FIRST, SECOND, ...). As for the trivials names, they are common in chemistry, written in
capslock. The following names are used: ALKALI_METALS, ALKALI_EARTH_METALS, HALOGENS, CHALCOGENS, LANTHANIDES,
ACTINIDES, NOBLE_GASES, NITROGEN_GROUP, CARBON_GROUP.

The elements are also grouped into the following tuples: TABLE, TABLE_STR, METALS and NONMETALS. The TABLE tuple just
contains all the elements of the periodic table in the order of their atomic numbers. TABLE_STR is the same thing,
but containing their symbols (strings).

METALS and NONMETALS is a common division of elements and contains the usual elements for these groups. Since
metalloids are not used in this package, all elements are fit into these two categories (the last sentence is just in
case a chemist comes to see the code).
"""


from collections import namedtuple
from typing import Union

from miniChemistry.MiniChemistryException import NotSupposedToHappen
from miniChemistry.Utilities.Checks import type_check_decorator
from miniChemistry.Core.CoreExceptions.ptableExceptions import ElementNotFound


class Element:
    """
    The Element class describes a chemical element template (basically, real elements then would be Element's instances).
    The class has the following attributes:

    class' private attributes
        _GROUP_A_OXIDATION_STATES
        _GROUP_B_OXIDATION_STATES
        Just to contain common oxidation states for each group.

    instance's private attributes
        _symbol (str)
        _name (str)
        _atomic_number (int)
        _period (int)
        _group (str)
        _molar_mass (float)
        _ren (float)
        _radioactivity (bool)
        These attributes should raise no question if the description above is read.

    All the methods are just properties to the these attributes. The only method, which is not a property is used
    to convert a symbol of an element into its instance. Namely, static method

    get_by_symbol(symbol: str) -> Element
    """

    _GROUP_A_OXIDATION_STATES = {
        '1A': (-1, 1),
        '2A': (2,),
        '3A': (-3, 1, 3),
        '4A': (-4, 2, 4),
        '5A': (-3, 3, 5),
        '6A': (-2, 2, 4, 6),
        '7A': (-1, 1, 3, 5, 7),
        '8A': (0,)
    }

    _GROUP_B_OXIDATION_STATES = {
        '1B': (1, 2),
        '2B': (2,),
        '3B': (3,),
        '4B': (2, 4),
        '5B': (3, 5),
        '6B': (2, 4, 6),
        '7B': (2, 3, 4, 6, 7),
        '8B': (2, 3, 6),
    }

    @type_check_decorator
    def __init__(self, symbol: str, name: str, atomic_number: int, period: int, group: str,
                 molar_mass: Union[float, int], ren: Union[float, int], radioactive: bool = False) -> None:
        self._symbol = symbol
        self._name = name
        self._atomic_number = atomic_number
        self._period = period
        self._group = group
        self._molar_mass = molar_mass
        self._ren = ren
        self._radioactivity = radioactive

    def __str__(self) -> str:
        return self.symbol

    # STATIC METHODS
    @staticmethod
    def get_by_symbol(symbol: str) -> 'Element':
        """
        Is useful when converting a formula of a molecule into an instance of the Molecule class. Or just when you need
        to convert a symbol of an element into the corresponding instance of Element class.

        The function searches for the symbol in the TABLE_STR and takes its index. Then it returns the element
        positioned at the same index in the TABLE list. The lists are created in such a way so that the symbols and
        Element's instances have the same indices.

        NOTE: the @check_type_decorator was not used here, because the typeguard module complains about string-form
        forward references (when return type is given in quotes).

        :param symbol: symbol of an element from the periodic table. Case matters.
        :return: the Element's instance corresponding to the given symbol
        """

        if not isinstance(symbol, str):
            raise TypeError(f'A parameter "symbol" of function "pt.Element.get_by_symbol" must have type string, got {type(symbol)}.')

        try:
            index = TABLE_STR.index(symbol)
            return TABLE[index]
        except ValueError:
            enf = ElementNotFound(symbol, locals())
            raise enf

    # PROPERTIES
    @property
    def oxidation_states(self) -> tuple:
        """
        The function just checks the group of an element (which is one of the attributes) and decides what oxidation
        states to return based on the following rules:

        - if the group is A => use dict for A groups
        - if the group is B => use the dict for B groups
        - if the element is a metal, keep only positive oxidation states (a rule comes from chemistry)

        :return: a tuple of integers
        """

        oxidation_states = tuple()
        if 'B' in self.group:
            oxidation_states = self._GROUP_B_OXIDATION_STATES[self.group]
        elif 'A' in self.group:
            oxidation_states = self._GROUP_A_OXIDATION_STATES[self.group]

        if self in METALS:
            return tuple([ost for ost in oxidation_states if ost >= 0])
        else:
            return oxidation_states

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def name(self) -> str:
        return self._name

    @property
    def atomic_number(self) -> int:
        return self._atomic_number

    @property
    def period(self) -> int:
        return self._period

    @property
    def group(self) -> str:
        return self._group

    @property
    def molar_mass(self) -> Union[float, int]:
        return self._molar_mass

    @property
    def ren(self) -> Union[float, int]:
        return self._ren

    @property
    def radioactive(self) -> bool:
        return self._radioactivity


# DEFINING ELEMENTS ================================================================================== DEFINING ELEMENTS
"""
The data presented here are taken from an actual periodic table. If you suspect a type or a mistake, then you can just
google a periodic table and check the values.
"""
# the first period
H = Element("H", "Hydrogen", 1, 1, '1A', 1.01, 2.10)
He = Element("He", "Helium", 2, 1, '8A', 4.0, -1)

# the second period
Li = Element("Li", "Lithium",  3, 2, '1A', 6.9, 0.98)
Be = Element("Be", "Beryllium",  4, 2, '2A', 9.0, 1.75)
B = Element("B", "Boron",  5, 2, '3A', 10.8, 2.04)
C = Element("C", "Carbon",  6, 2, '4A', 12.0, 2.55)
N = Element("N", "Nitrogen",  7, 2, '5A', 14.0, 3.04)
O = Element("O", "Oxygen",  8, 2, '6A', 16.0, 3.44)
F = Element("F", "Fluorine",  9, 2, '7A', 19.0, 3.98)
Ne = Element("Ne", "Neon",  10, 2, '8A', 20.2, -1)

# the third period
Na = Element("Na", "Sodium",  11, 3, '1A', 23.0, 0.93)
Mg = Element("Mg", "Magnesium",  12, 3, '2A', 24.3, 1.31)
Al = Element("Al", "Aluminium",  13, 3, '3A', 27.0, 1.61)
Si = Element("Si", "Silicon",  14, 3, '4A', 28.1, 1.90)
P = Element("P", "Phosphorus",  15, 3, '5A', 31.0, 2.19)
S = Element("S", "Sulfur",  16, 3, '6A', 32.1, 2.58)
Cl = Element("Cl", "Chlorine",  17, 3, '7A', 35.5, 3.16)
Ar = Element("Ar", "Argon",  18, 3, '8A', 39.9, -1.0)

# the fourth period
K = Element("K", "Potassium", 19, 4, '1A', 39.1, 0.82)
Ca = Element("Ca", "Calcium",  20, 4, '2A', 40.1, 1.00)
Sc = Element("Sc", "Scandium",  21, 4, '3B', 45.0, 1.36)
Ti = Element("Ti", "Titanium",  22, 4, '4B', 47.9, 1.54)
V = Element("V", "Vanadium",  23, 4, '5B', 50.9, 1.63)
Cr = Element("Cr", "Chromium",  24, 4, '6B', 52.0, 1.66)
Mn = Element("Mn", "Manganese",  25, 4, '7B', 54.9, 1.55)
Fe = Element("Fe", "Iron",  26, 4, '8B', 55.8, 1.83)
Co = Element("Co", "Cobalt",  27, 4, '8B', 58.9, 1.88)
Ni = Element("Ni", "Nickel",  28, 4, '8B', 58.7, 1.91)
Cu = Element("Cu", "Copper",  29, 4, '1B', 63.5, 1.90)
Zn = Element("Zn", "Zinc",  30, 4, '2B', 65.4, 1.65)
Ga = Element("Ga", "Gallium", 31, 4, '3A', 69.7, 1.81)
Ge = Element("Ge", "Germanium",  32, 4, '4A', 72.6, 2.01)
As = Element("As", "Arsenic",  33, 4, '5A', 74.9, 2.18)
Se = Element("Se", "Selenium",  34, 4, '6A', 79.0, 2.55)
Br = Element("Br", "Bromine",  35, 4, '7A', 79.9, 2.96)
Kr = Element("Kr", "Krypton",  36, 4, '8A', 83.8, 3.00)

# the fifth period
Rb = Element("Rb", "Rubidium",  37, 5, '1A', 85.5, 0.82)
Sr = Element("Sr", "Strontium",  38, 5, '2A', 87.6, 0.95)
Y = Element("Y", "Yttrium",  39, 5, '3B', 88.9, 1.22)
Zr = Element("Zr", "Zirconium",  40, 5, '4B', 91.2, 1.33)
Nb = Element("Nb", "Niobium", 41, 5, '5B', 92.9, 1.60)
Mo = Element("Mo", "Molybdenum",  42, 5, '6B', 95.9, 2.16)
Tc = Element("Tc", "Technetium",  43, 5, '7B', 98, 1.90, True)
Ru = Element("Ru", "Ruthenium", 44, 5, '8B', 101.1, 2.20)
Rh = Element("Rh", "Rhodium",  45, 5, '8B', 102.9, 2.28)
Pd = Element("Pd", "Palladium",  46, 5, '8B', 106.4, 2.20)
Ag = Element("Ag", "Silver",  47, 5, '1B', 107.9, 1.93)
Cd = Element("Cd", "Cadmium",  48, 5, '2B', 112.4, 1.69)
In = Element("In", "Indium",  49, 5, '3A', 114.8, 1.78)
Sn = Element("Sn", "Tin",  50, 5, '4A', 118.7, 1.96)
Sb = Element("Sb", "Antimony",  51, 5, '5A', 121.8, 2.05)
Te = Element("Te", "Tellurium",  52, 5, '6A', 127.6, 2.10)
I = Element("I", "Iodine",  53, 5, '7A', 126.9, 2.66)
Xe = Element("Xe", "Xenon",  54, 5, '8A', 131.3, 2.60)

# the sixth period
Cs = Element("Cs", "Caesium",  55, 6, '1A', 132.9, 0.79)
Ba = Element("Ba", "Barium",  56, 6, '2A', 137.3, 0.89)
La = Element("La", "Lanthanum",  57, 6, '3B', 138.9, 1.10)
Ce = Element("Ce", "Cerium",  58, 6, '3B', 140.1, 1.12)
Pr = Element("Pr", "Praseodymium",  59, 6, '3B', 140.9, 1.13)
Nd = Element("Nd", "Neodymium",  60, 6, '3B', 144.2, 1.14)
Pm = Element("Pm", "Promethium",  61, 6, '3B', 145.0, 1.13)
Sm = Element("Sm", "Samarium",  62, 6, '3B', 150.4, 1.17)
Eu = Element("Eu", "Europium",  63, 6, '3B', 152.0, 1.20)
Gd = Element("Gd", "Gadolinium",  64, 6, '3B', 157.3, 1.20)
Tb = Element("Tb", "Terbium",  65, 6, '3B', 158.9, 1.10)
Dy = Element("Dy", "Dysprosium",  66, 6, '3B', 162.5, 1.22)
Ho = Element("Ho", "Holmium",  67, 6, '3B', 164.9, 1.23)
Er = Element("Er", "Erbium",  68, 6, '3B', 167.3, 1.24)
Tm = Element("Tm", "Thulium",  69, 6, '3B', 168.9, 1.25)
Yb = Element("Yb", "Ytterbium",  70, 6, '3B', 173.0, 1.10)
Lu = Element("Lu", "Lutetium",  71, 6, '3B', 175.0, 1.27)
Hf = Element("Hf", "Hafnium",  72, 6, '4B', 178.5, 1.30)
Ta = Element("Ta", "Tantalum",  73, 6, '5B', 180.9, 1.50)
W = Element("W", "Tungsten",  74, 6, '6B', 183.8, 2.36)
Re = Element("Re", "Rhenium",  75, 6, '7B', 186.2, 1.90)
Os = Element("Os", "Osmium",  76, 6, '8B', 190.3, 2.20)
Ir = Element("Ir", "Iridium",  77, 6, '8B', 192.2, 2.20)
Pt = Element("Pt", "Platinum",  78, 6, '8B', 195.1, 2.28)
Au = Element("Au", "Gold",  79, 6, '1B', 197.0, 2.54)
Hg = Element("Hg", "Mercury",  80, 6, '2B', 200.6, 2.00)
Tl = Element("Tl", "Thallium", 81, 6, '3A', 204.4, 1.62)
Pb = Element("Pb", "Lead",  82, 6, '4A', 207.2, 2.33)
Bi = Element("Bi", "Bismuth",  83, 6, '5A', 209.0, 2.02)
Po = Element("Po", "Polonium",  84, 6, '6A', 209, 2.00, True)
At = Element("At", "Astatine",  85, 6, '7A', 210, 2.20, True)
Rn = Element("Rn", "Radon",  86, 6, '8A', 222, 2.20, True)

# the seventh period
Fr = Element("Fr", "Francium",  87, 7, '1A', 223, 0.79, True)
Ra = Element("Ra", "Radium",  88, 7, '2A', 226, 0.90, True)
Ac = Element("Ac", "Actinium",  89, 7, '3B', 227, 1.10, True)
Th = Element("Th", "Thorium",  90, 7, '3B', 232.0, 1.30, True)
Pa = Element("Pa", "Protactinium",  91, 7, '3B', 231, 1.50, True)
U = Element("U", "Uranium",  92, 7, '3B', 238.0, 1.38, True)
Np = Element("Np", "Neptunium", 93, 7, '3B', 237, 1.36, True)
Pu = Element("Pu", "Plutonium",  94, 7, '3B', 244, 1.28, True)
Am = Element("Am", "Americium",  95, 7, '3B', 243, 1.13, True)
Cm = Element("Cm", "Curium",  96, 7, '3B', 247, 1.28, True)
Bk = Element("Bk", "Berkelium",  97, 7, '3B', 247, 1.30, True)
Cf = Element("Cf", "Californium",  98, 7, '3B', 251, 1.30, True)
Es = Element("Es", "Einsteinium",  99, 7, '3B', 252, 1.30, True)
Fm = Element("Fm", "Fermium",  100, 7, '3B', 257, 1.30, True)
Md = Element("Md", "Mendelevium",  101, 7, '3B', 258, 1.30, True)
No = Element("No", "Nobelium", 102, 7, '3B', 259, 1.30, True)
Lr = Element("Lr", "Lawrencium", 103, 7, '3B', 262, 1.29, True)
Rf = Element("Rf", "Rutherfordium",  104, 7, '4B', 265, -1, True)
Db = Element("Db", "Dubnium", 105, 7, '5B', 268, -1, True)
Sg = Element("Sg", "Seaborgium",  106, 7, '6B', 271, -1, True)
Bh = Element("Bh", "Bohrium",  107, 7, '7B', 267, -1, True)
Hs = Element("Hs", "Hassium",  108, 7, '8B', 269, -1, True)
Mt = Element("Mt", "Meitnerium",  109, 7, '8B', 278, -1, True)
Ds = Element("Ds", "Darmstadtium",  110, 7, '8B', 281, -1, True)
Rg = Element("Rg", "Roentgenium",  111, 7, '1B', 281, -1, True)
Cn = Element("Cn", "Copernicium",  112, 7, '2B', 285, -1, True)
Nh = Element("Nh", "Nihonium",  113, 7, '3A', 284, -1, True)
Fl = Element("Fl", "Flerovium",  114, 7, '4A', 289, -1, True)
Mc = Element("Mc", "Moscovium",  115, 7, '5A', 288, -1, True)
Lv = Element("Lv", "Livermorium",  116, 7, '6A', 293, -1, True)
Ts = Element("Ts", "Tennessine",  117, 7, '7A', 294, -1, True)
Og = Element("Og", "Oganesson",  118, 7, '8A', 294, -1, True)



# GROUPING ==================================================================================================== GROUPING
"""
The elements can be classified according to the groups defined in chemistry. To keep the  convenient dot notation, 
namedtuples were used make access to the elements and their lists (tuples) easier.

The code given below suggests the following groups:
1) division by periodic table's groups. Named "groups"
2) division by periodic table's periods. Named "periods"
3) division by trivial names of several groups of elements. Named "trivials"

To access any of the tuples you can use the following code:
>>> pt.trivials.ALKALI_METALS
        (<Core.Database.ptable.Element object at 0x10ef3ad20>, <Core.Database.ptable.Element object at 0x1105faa20>, \
        <Core.Database.ptable.Element object at 0x1105fad20>, <Core.Database.ptable.Element object at 0x1105fb230>, \
        <Core.Database.ptable.Element object at 0x1105fb680>, <Core.Database.ptable.Element object at 0x1105fbec0>)
>>> [element.symbol for element in pt.trivials.ALKALI_METALS]
        ['Li', 'Na', 'K', 'Rb', 'Cs', 'Fr']
"""

groups = namedtuple('groups', 'FIRST_A, SECOND_A, THIRD_A, FOURTH_A, FIFTH_A, SIXTH_A, '
                              'SEVENTH_A, EIGHTH_A, FIRST_B, SECOND_B, THIRD_B, FOURTH_B, FIFTH_B,'
                              'SIXTH_B, SEVENTH_B, EIGHTH_B1, EIGHTH_B2, EIGHTH_B3')

periods = namedtuple('periods', 'FIRST, SECOND, THIRD, FOURTH, FIFTH, SIXTH, SEVENTH, EIGHTH')
trivials = namedtuple('trivials', 'ALKALI_METALS, ALKALI_EARTH_METALS, HALOGENS,'
                                  'CHALCOGENS, LANTHANIDES, ACTINIDES, NOBLE_GASES, NITROGEN_GROUP, CARBON_GROUP')

# DEFINING GROUPS OF ATOMS | TRIVIAL NAMES
trivials.ALKALI_METALS = (Li, Na, K, Rb, Cs, Fr)
trivials.ALKALI_EARTH_METALS = (Be, Mg, Ca, Sr, Ba, Ra)
trivials.HALOGENS = (F, Cl, Br, I)
trivials.CHALCOGENS = (O, S, Se, Te)
trivials.LANTHANIDES = (Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu)
trivials.ACTINIDES = (Th, Pa, U, Np, Pu, Am, Cm, Bk, Cf, Es, Fm, Md, No, Lr)
trivials.NOBLE_GASES = (He, Ne, Ar, Kr, Xe, Rn)
trivials.NITROGEN_GROUP = (N, P, As, Sb, Bi)
trivials.CARBON_GROUP = (C, Si, Ge, Sn, Pb)


# DEFINING GROUPS OF ATOMS | PERIODS
periods.FIRST = (H, He)
periods.SECOND = (Li, Be, B, C, N, O, F, Ne)
periods.THIRD = (Na, Mg, Al, Si, P, S, Cl, Ar)
periods.FOURTH = (K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr)
periods.FIFTH = (Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe)
periods.SIXTH = (Cs, Ba, La, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, W, Re,
                 Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn)
periods.SEVENTH = (Fr, Ra, Ac, Th, Pa, U, Np, Pu, Am, Cm, Bk, Cf, Es, Fm, Md, No, Lr, Rf, Db, Sg, Bh,
                   Hs, Mt, Ds, Rg, Cn, Nh, Fl, Mc, Lv, Ts, Og)
all_periods = (periods.FIFTH, periods.SECOND, periods.THIRD, periods.FOURTH, periods.FIFTH, periods.SIXTH,
               periods.SEVENTH, periods.EIGHTH)


# DEFINING GROUPS OF ATOMS | GROUPS
groups.FIRST_A = (H, Li, Na, K, Rb, Cs, Fr)
groups.SECOND_A = (Be, Mg, Ca, Sr, Ba, Ra)
groups.THIRD_A = (B, Al, Ga, In, Tl, Nh)
groups.FOURTH_A = (C, Si, Ge, Sn, Pb, Fl)
groups.FIFTH_A = (N, P, As, Sb, Bi, Mc)
groups.SIXTH_A = (O, S, Se, Te, Po, Lv)
groups.SEVENTH_A = (F, Cl, Br, I, At, Ts)
groups.EIGHTH_A = (He, Ne, Ar, Kr, Xe, Rn, Og)
all_A_groups = (groups.FIRST_A, groups.SECOND_A, groups.THIRD_A, groups.FOURTH_A, groups.FIFTH_A, groups.SECOND_A,
                groups.SEVENTH_A, groups.EIGHTH_A)

groups.FIRST_B = (Cu, Ag, Au, Rg)
groups.SECOND_B = (Zn, Cd, Hg, Cn)
groups.THIRD_B = (Sc, Y, La, Ac)
groups.FOURTH_B = (Ti, Zr, Hf, Rf)
groups.FIFTH_B = (V, Nb, Ta, Db)
groups.SIXTH_B = (Cr, Mo, W, Sg)
groups.SEVENTH_B = (Mn, Tc, Re, Bh)
groups.EIGHTH_B_1 = (Fe, Ru, Os, Hs)
groups.EIGHTH_B_2 = (Co, Rh, Ir, Mt)
groups.EIGHTH_B_3 = (Ni, Pd, Pt, Ds)
groups.EIGHTH_B = groups.EIGHTH_B_1 + groups.EIGHTH_B_2 + groups.EIGHTH_B_3
all_B_groups = (groups.FIRST_B, groups.SECOND_B, groups.THIRD_B, groups.FOURTH_B, groups.FIFTH_B, groups.SIXTH_B,
                groups.SEVENTH_B, groups.EIGHTH_B_1, groups.EIGHTH_B_2, groups.EIGHTH_B_3)
all_groups = all_A_groups + all_B_groups

# DEFINING ENTIRE PERIODIC TABLE
TABLE = periods.FIRST + periods.SECOND + periods.THIRD + periods.FOURTH + periods.FIFTH + \
        periods.SIXTH + periods.SEVENTH

TABLE_STR = tuple([element.symbol for element in TABLE])

# DEFINING METALS
METALS = (groups.FIRST_A[1:] + groups.SECOND_A + groups.FIRST_B + groups.SECOND_B + groups.THIRD_B + groups.FOURTH_B +
          groups.FIFTH_B + groups.SIXTH_B + groups.SEVENTH_B + groups.EIGHTH_B_1 + groups.EIGHTH_B_2 +
          groups.EIGHTH_B_3 + (Al, Ga, In, Tl, Sn, Pb, Sb, Bi) + trivials.LANTHANIDES + trivials.ACTINIDES +
          (Po, At, Nh, Fl, Mc, Lv, Ts, Og))


NONMETALS = ((H,) + trivials.HALOGENS + trivials.CHALCOGENS + trivials.NOBLE_GASES + (B, N, P, As) + (C, Si, Ge))


# ================================================================================================ SOME USEFUL FUNCTIONS
def next_element(element: Element) -> Element:
    """Returns element that is staying next (after) to the element passed as a parameter."""
    Z = element.atomic_number

    if Z < 118:
        return TABLE[Z]
    else:
        enf = ElementNotFound(symbol="<unknown>", variables=locals())
        enf.description += (f'\n\nIMPORTANT:\nRemember that in programming counting starts from zero, so when Z = 118, that\n'
                            f'actually means "an element with atomic number of 119"!')
        raise enf


def prev_element(element: Element) -> Element:
    """Returns element that is staying before the element passed as a parameter."""
    Z = element.atomic_number - 2

    if Z <= 0:
        raise ElementNotFound(symbol="<unknown>", variables=locals())
    else:
        return TABLE[Z]

# wtf is the return value?
def group_tuple(element: Element) -> tuple:
    """Returns the namedtuple of type "group" where the element passed as a parameter is present."""
    for group in all_groups:
        if element in group:
            return group
    else:
        nsth = NotSupposedToHappen(variables=locals())
        nsth.description += f'\nThe element "{element.symbol}" does not belong to any of the groups of the periodic table.'
        raise nsth


def above(element: Element) -> Element:
    """Returns the element that stays above the element passed as a parameter."""
    g = group_tuple(element)
    i = g.index(element)

    if i > 0:
        return g[i-1]
    else:
        enf = ElementNotFound(symbol="<unknown>", variables=locals())
        enf.description += (f'\n\nThe element you are trying to address is expected to stay ABOVE {element.symbol}, but\n'
                            f"there's nothing in the periodic table in this place.")
        raise enf


def below(element: Element) -> Element:
    """Returns the element that is below the one passed as a parameter."""
    g = group_tuple(element)
    i = g.index(element)

    if i < len(g)-1:
        return g[i+1]
    else:
        enf = ElementNotFound(symbol="<unknown>", variables=locals())
        enf.description += (f'\n\nThe element you are trying to address is expected to stay BELOW {element.symbol}, but\n'
                            f"there's nothing in the periodic table in this place.")
        raise enf
