"""
In chemistry, there're pairs of substances based on their chemical behaviour. Thus, in chemistry we have bases bound to
basic oxides and respective cations, and acids bound to their acid rests and acidic oxides.

BASES
A base in school is a substance that possesses a hydroxide ion and can easily give it away in chemical reactions. As well
as with acids (the logic is similar), in this module we call a base any instance of Molecule that has as its anion
a hydroxide ion. That means, we neglect the fact that the real base also has to easily give away this group.
NOTE: miniChemistry limits itself to the bases formed by metal ions. That means, all non-metal cations here do not have
bases. The most important exception for this is ammonia [NH4(+)]. Moreover, it's a good moment to remind that miniChemistry
supports only cations consisting of one element (which also excludes ammonia).

Each base, then, has a form of <metal cation>(OH)x with x being cation charge's absolute value. There're two items
corresponding to every base – its cation (metal) and basic oxide. Again, as with acids, the main most important (at
least here) property of a basic oxide is that when reacting with water is forms the corresponding base.

EXAMPLES
name                      base        metal/ion           basic oxide
–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
sodium hydroxide        NaOH            Na/Na(1)            Na2O
zinc hydroxide          Zn(OH)2         Zn/Zn(2)            ZnO
copper hydroxide        Cu(OH)2         Cu/Cu(2)            CuO

This module provides only cations, because it is very easy to convert them to the respective instance of Simple (just
use either simple() from Substances.py or ion.elements[0] to get a pt.Element instance.

It is important to note that the bases, cations, and basic oxides are located at the same position in their lists. I.e.
if sodium hydroxide is the first one (index = 0), then the first basic oxide would be Na2O and the first cation would
be Na(1). This property is used to select respective substances in the methods base(), basic_oxide() and cation().

Since all the metals and their cations are present in the solubility table (stable.py), there's no point in storing them
in a text file, because there are no ion to be added.

NOTE: in case you need to add an ion that is not present in the BasesTable, just add it to the SolubilityTable and it
should appear in the BasesTable as well.

ACIDS
For similar information on acids, look at AcidsTable.py.
"""



from miniChemistry.Core.Database.stable import SolubilityTable
import miniChemistry.Core.Database.ptable as pt
from miniChemistry.Core.Substances import Molecule, Ion
from miniChemistry.Core.CoreExceptions.CompatibilityTableExceptions import BaseNotFound
from typing import Tuple


class BasesTable:
    def __init__(self):
        self._cations, self._bases, self._basic_oxides = self._create_lists()

    @staticmethod
    def _create_lists() -> Tuple[Tuple[Ion, ...], Tuple[Molecule, ...], Tuple[Molecule, ...]]:
        """
        Creates all three lists used in this class, starting from SolubilityTable database. The method iterates over a
        database and with each substance does the following:

        1) checks if it is a metal and if it has already been used
        2) (if the tests are passed), passes the formula and charge of the substance to the Ion.from_string() to get
        an instance of Ion. The ion is then passed to the Molecule.base() and Molecule.oxide() methods to obtain
        respective substances.

        At the end the tuples with
        1) cations
        2) bases
        3) basic oxides
        are returned.

        :return: returns a tuple of tuples. The inner tuples contain cations, bases and basic oxides respectively.
        """

        st = SolubilityTable()
        st.begin()

        metals = [m.symbol for m in pt.METALS]
        used_cations = list()
        ions, bases, oxides = list(), list(), list()

        for substance in st:
            if substance.cation in metals and substance.cation not in used_cations:
                i = Ion.from_string(substance.cation, substance.cation_charge)
                b = Molecule.base(i)
                o = Molecule.oxide(i)

                ions.append(i)
                bases.append(b)
                oxides.append(o)
                used_cations.append(substance.cation)
        st.end()

        return tuple(ions), tuple(bases), tuple(oxides)

    
    def base(self, substance: (Ion, Molecule)) -> Molecule:
        """
        Takes in cation or basic oxide and returns a corresponding base. To select the base the index of the parameter's
        substance is used.

        :param substance: an instance of Molecule or Ion which represents either basic oxide or cation respectively.
        :return: an instance of Molecule (namely, a base)
        """

        if substance in self._cations:
            index = self._cations.index(substance)
        elif substance in self._basic_oxides:
            index = self._basic_oxides.index(substance)
        else:
            raise BaseNotFound(formula=substance.formula(), variables=locals())

        return self._bases[index]

    
    def basic_oxide(self, substance: (Ion, Molecule)) -> Molecule:
        """
        Takes in a base or a cation, and returns a basic oxide. To select the oxide the index of the parameter's
        substance is used.

        :param substance: an instance of Molecule or Ion which represents either base or cation respectively.
        :return: an instance of Molecule (namely, basic oxide)
        """
        # type_check([substance], [Ion, Molecule], raise_exception=True)

        if substance in self._cations:
            index = self._cations.index(substance)
        elif substance in self._bases:
            index = self._bases.index(substance)
        else:
            raise BaseNotFound(formula=substance.formula(), variables=locals())

        return self._basic_oxides[index]

    
    def cation(self, substance: Molecule) -> Ion:
        """
        Takes in a base or a basic oxide and returns a respective cation. To select the cation the index of the parameter's
        substance is used.

        :param substance: an instance of Molecule representing either base or basic oxide
        :return: an instance of Ion (namely, respective cation)
        """
        # type_check([substance], [Molecule], raise_exception=True)

        if substance in self._bases:
            index = self._cations.index(substance)
        elif substance in self._basic_oxides:
            index = self._basic_oxides.index(substance)
        else:
            raise BaseNotFound(formula=substance.formula(), variables=locals())

        return self._cations[index]

    @property
    def cations(self):
        return self._cations

    @property
    def bases(self):
        return self._bases

    @property
    def basic_oxides(self):
        return self._basic_oxides
