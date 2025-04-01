"""
In chemistry, there're pairs of substances based on their chemical behaviour. Thus, in chemistry we have acids bound to
acidic oxides and acid rests, and bases bound to their cations and basic oxides.

ACIDS
An acid in school chemistry is a molecule that possesses a proton (H(+) ion) and can easily give it away in chemical
reactions. In miniChemistry then, an acid as any molecule that has H(+) as its cation. This is not entirely correct,
as we can also define, say, ammonia as an acid then, but for majority of school chemistry molecules it works.
NOTE FOR CHEMISTS: just in case it wasn't clear. In this package the property of easily detaching a proton is omitted,
so only possession is enough to call a molecule an acid.

Each acid consists of a cation (proton) and anion (they are different). The anion is called an "acid rest", because this
is what is left when an acid looses a proton. Moreover, if an element forming an acid is taken (sulfur for sulfuric acid,
phosphorus for phosphoric acid, etc.), and an oxide is formed with the same oxidation state as the element has in the
acid (see examples below), the formed oxide is called an acidic oxide. One of its important (also to this package)
properties is that when reacting with water, it forms a corresponding acid.

EXAMPLES
name        acid        acid forming element        acid rest           acidic oxide
––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
sulfuric    H2SO4           S   (sulfur)            SO4(-2)                 SO3
phosphoric  H3PO4           P   (phosphorus)        PO4(-3)                 P2O5
carbonic    H2CO3           C   (carbon)            CO3(-2)                 CO2

If you look at the oxidation state of the acid-forming element in both acid and the corresponding oxide, you will
see that it is the same.
NOTE: we don't discuss here how to calculate oxidation states of elements in molecules, because this is a basic knowledge
obtained from school chemistry. And this text is primarily documentation of the Python code, not chemistry textbook.

BASES
For similar information on bases, look at BasesTable.py.
"""


from typing import Tuple, List
from chemparse import parse_formula
from miniChemistry.Core.Tools.parser import parse_ion
from miniChemistry.Utilities.File import File
from miniChemistry.Core.Substances import Molecule, Ion, _string_to_elementary_composition
from miniChemistry.Core.CoreExceptions.CompatibilityTableExceptions import AcidNotFound, AcidicOxideNotFound, WrongTextFileData
from miniChemistry.Core.CoreExceptions.ToolExceptions import InvalidFormula
from miniChemistry.Utilities.Checks import type_check_decorator


class AcidsTable:
    """
    Given the information above, the class stores three types of substances – acids, acid rests (ions), and
    acidic oxides. The data are read from a text file and converted into instances of Molecule and Ion. This is done
    so that it is easy to add new acids to the file without working with the actual code.

    The class has three respective methods:
    acid() -> Molecule
    acid_rest() -> Ion
    acidic_oxide() -> Molecule

    Each takes in a Molecule or Ion instance and returns corresponding acid/acid rest/acidic oxide. There are also
    methods used to create these substances from their formulas. These methods are private.

    To add a new acid to the file, do the following
    1) Take a look at the method used to convert the acid rest formula to the instance of Ion (_convert_acid_rests).
    The acid should not cause any exceptions there (in case of doubt, this can always be checked experimentally)
    2) Open the AcidCompatibilityTable.txt and add there the following text, replacing the brackets by respective
    molecules/ion: <acid rest in the conventional form>:<acid-forming element as an ion in the conventional form>.
    The conventional form of writing ions in this module is writing their formula and placing their charge in
    parentheses, e.g. O(-2) or H(1). Note that there's no plus sign!
    3) In case if the acid does not have an acidic oxide, e.g. HF, write "None" (exactly like here)
    4) Close the file and test if the code works
    NOTE: no spaces are needed between the ions or colon. Leave an empty line at the end of the file.
    """

    def __init__(self):
        # find and bind to the file
        self._file_name = 'AcidCompatibilityTable'
        self._file = File(__file__)
        self._file.bind(self._file_name)

        # read the data from file
        self._acid_rests_str, self._elements = self._read_file()

        # convert the strings to the Molecule and Ion instances
        self._acidic_oxides = self._create_oxides()
        self._acid_rests = self._convert_acid_rests()
        self._acids = self._create_acids()

    # ================================================================================================== PRIVATE METHODS
    def _read_file(self) -> Tuple[List[str], List[str]]:
        """
        The method reads the data from AcidCompatibility and fills in the self._acid_rests_str and self._elements
        lists.

        The method reads the file line by line and parses it according to the conventions mentioned above. For example,
        the line SO4(-2):S(6) will be first split by colon into the acid rest and the element strings, i.e. into
        "SO4(-2)" and "S(6)". If the colon is not present, the WrongTextFileData exception will be raised.

        Next, the strings will be appended to the corresponding lists and returned.

        :return: Two lists of strings. The first list contains the acid rests (as strings), the second contains the acid-forming elements (as strings).
        """

        acid_rests, elements = list(), list()

        for line in self._file:
            try:
                acid_rest, element = line.split(':')
            except ValueError:
                raise WrongTextFileData(data=line, file_name=self._file.name, variables=locals())

            if element != 'None':
                acid_rests.append(acid_rest)
                elements.append(element)
            else:
                acid_rests.append(acid_rest)
                elements.append(None)

        return acid_rests, elements

    def _create_oxides(self) -> List[Molecule]:
        """
        Converts the strings from self._elements [they are for example S(6), P(5), N(5), etc.] into corresponding
        acidic oxides.

        This is done by iterating over a list and trying to convert the string into separately formula and charge [e.g.
        S(6) will be split into "S" and 6]. These two variables are passed straight to the Ion.from_string() method
        that returns an instance of Ion (or raises exception).

        In the case of exception, it is caught and the description is completed to mention that the error most likely
        occurred due to wrong form of string in AcidCompatibilityTable.txt.

        The ion is then passed to the Molecule.oxide() method that returns an oxide of the passed ion. THe oxide is
        appended to the oxides list and the list is returned.

        NOTE: since not all elements can have acidic oxides [say, Cl(-1) cannot], sometimes the value of None is appended
        to the list. This is then handled by the AcidicOxideNotFound exception in self.acidic_oxide() method.

        :return: a list of Molecule instances (namely, acidic oxides)

        NOTE 2: The order of acids, acidic oxides and acid rests in the final lists are the same (i.e. if sulfuric acid
        is the first, then SO3 and SO4(-2) will also be first in their lists). This is crucial property, because the
        substances are selected based on their indices in the respective lists (see methods self.acid(), self.acid_rest()
        and self.acidic_oxide()).
        """

        oxides = list()

        for element in self._elements:
            if element is not None:
                try:
                    i = Ion.from_string(*parse_ion(element))
                except InvalidFormula as ife:
                    ife.description += ('\n\nIMPORTANT:\nThis exception occurred while parsing the data from AcidCompatibilityTable.txt\n'
                                              'file. Please check that the data you wrote in are correct.')
                    raise ife

                oxide = Molecule.oxide(i)
                oxides.append(oxide)
            else:
                oxides.append(None)

        return oxides

    def _create_acids(self) -> List[Molecule]:
        """
        Converts the acid rests from the self._acid_rests list (those are not strings, those are instances of Ion) into
        acids (instances of Molecule) by using Molecule.acid() method.

        :return: a list of Molecule instances (namely, list of acids)
        """

        acids = list()

        for rest in self._acid_rests:
            acid = Molecule.acid(rest)
            acids.append(acid)

        return acids

    def _convert_acid_rests(self) -> List[Ion]:
        """
        Converts string acid rests into instances of Ion (real acid rests). Does this by iterating over
        self._acid_rests_str and parsing the ion into string-ion and charge [e.g. SO4(-2) becomes "SO4" and -2 separately].
        The string-ion is then converted into string composition (by using chemparse.parse_formula()) and finally into
        elementary composition by using _string_to_elementary_composition() from Substances.py.

        The final (elementary) composition and charge are then passed to the constructor of Ion, and the obtained
        instance is appended to the list. After iterating is done, the list is returned.

        :return: a list of Ion instances (namely, acid rests)
        """

        rests = list()

        for rest in self._acid_rests_str:
            try:
                ion, charge = parse_ion(rest)
            except InvalidFormula as ife:
                ife.description += (
                    '\n\nIMPORTANT:\nThis exception occurred while parsing the data from AcidCompatibilityTable.txt\n'
                    'file. Please check that the data you wrote in are correct.')
                raise ife
            composition = _string_to_elementary_composition(parse_formula(ion))
            i = Ion(composition, int(charge))
            rests.append(i)

        return rests


    # =================================================================================================== PUBLIC METHODS
    @type_check_decorator
    def acid(self, substance: (Ion, Molecule)) -> Molecule:
        """
        Takes in either acid rest or acidic oxide, and returns the corresponding acid. Selection of acid is based on
        the index of the parameter's substance in its own list.

        :param substance: either acid rest or acidic oxide (instance of either Ion or Molecule)
        :return: an instance of Molecule (respective acid)
        """

        if substance in self._acid_rests:
            index = self._acid_rests.index(substance)
        elif substance in self._acidic_oxides:
            index = self._acidic_oxides.index(substance)
        else:
            raise AcidNotFound(formula=substance.formula(), variables=locals())

        return self._acids[index]

    @type_check_decorator
    def acid_rest(self, substance: Molecule) -> Ion:
        """
        Takes in an acid or an acidic oxide and returns the corresponding acid rest. Selection of acid rest is based
        on the index of the parameter's substance in its own list.

        :param substance: either acid or acidic oxide (instance of Molecule)
        :return: an instance of Ion (respective acid rest)
        """

        if substance in self._acids:
            index = self._acids.index(substance)
        elif substance in self._acidic_oxides:
            index = self._acidic_oxides.index(substance)
        else:
            raise AcidNotFound(formula=substance.formula(), variables=locals())

        return self._acid_rests[index]

    @type_check_decorator
    def acidic_oxide(self, substance: (Ion, Molecule)) -> Molecule:
        """
        Takes in either acid or acid rest, and returns corresponding acidic oxide. Selection of acidic oxide is based
        on the index of the parameter's substance in its own list.

        :param substance: either acid or acid rest (instance of either Molecule or Ion)
        :return: an instance of Molecule (respective acidic oxide)
        """

        if substance in self._acids:
            index = self._acids.index(substance)
        elif substance in self._acid_rests:
            index = self._acid_rests.index(substance)
        else:
            raise AcidNotFound(formula=substance.formula(), variables=locals())

        oxide = self._acidic_oxides[index]

        if oxide is None:
            raise AcidicOxideNotFound(substance.formula(), variables=locals())
        else:
            return oxide

    # ======================================================================================================= PROPERTIES
    @property
    def acids(self) -> Tuple[Molecule, ...]:
        return tuple(self._acids)

    @property
    def acid_rests(self) -> Tuple[Ion, ...]:
        return tuple(self._acid_rests)

    @property
    def acidic_oxides(self) -> Tuple[Molecule, ...]:
        return tuple(self._acidic_oxides)
