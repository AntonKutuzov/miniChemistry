"""
BACKGROUND IN CHEMISTRY
Solubility table (stable for short, read it as "s-table" same as "p-table" for "periodic table") is another very
important data set in chemistry. Basically, it shows whether a certain substance is soluble or not. However, especially
in school chemistry (what this module tries to simulate) the table is also used as an information source about different
ions. To explain this, let's discuss how solubility table works.

The solubility table can be also considered as a matrix consisting of two types of ions (see file called "Substances") –
negative and positive. Positive ions are usually located horizontally, i.e. they are the columns. Negative ions are
usually vertical, so rows. A typical solubility table looks like this (the amount of ions is very limited to keep it
small, but the main idea is still the same):

            Na(+)   Ca(+2)  Al(+3)  Mn(+2)  Cu(+2)
OH(-)       SL      SS      NS      NS      NS
Cl(-)       SL      SL      SL      SL      SL
SO4(-2)     SL      SS      SL      SL      SL
PO4(-3)     SL      NS      NS      NS      NS

The two letters (usually one, but here we need two, never mind, this is not so important) indicate the solubility of a
given substance. To determine solubility, you just select needed ions that compose a substance. For example, solubility
of table salt, NaCl will be SL (soluble), because it consists of two ions – Na(+) and Cl(-) and if you select the
respective row and column, you will see at the selected cell the value "SL".


VALUES OF SOLUBILITY
There are five different states of substance regarding its solubility in this code. Usually in a good solubility table
all five are given at the bottom of the table (you can again just google "solubility table").

SL – stands for "soluble". That means the solubility of this substance is more than 1 g per 100 g of water. In this code
soluble substance means that it does not produce a precipitate in chemical reactions.
SS – stands for "slightly soluble". That means the substance's solubility is between 0.1 and 1 g of substance per
100 g of water.
NS – stands for "not soluble". That means the solubility of the substance is less than 0.1 g per 100 g of water.

Both SS and NS in this code mean that the substance will produce precipitate. Technically, in this code NS and SS mean
the same thing, but to keep the solubility table reliable, both were included.

RW – stands for "reacts with water". That means, when a substance comes in contact with water, a chemical reaction
occurs, which means we can't determine the solubility of a substance.
ND – stands for "no data". That means a substance with the given formula is not yet known. However, this code also
should be included, because different ions form different substances and both ND and other codes can appear in the same
row. For example

            Na(+)   Ba(+2)  Mg(+2)  Al(+3)  Fe(+2)  Fe(+3)
SO3(-2)     SL      NS      SS      ND      NS      ND


IMPLEMENTATION IN PYTHON
The solubility table class uses sqlite3 to operate a real database. Basically, it wraps the SQL code so that the user
can use SolubilityTable's methods for the most common requests without appealing to SQL. The direct access to the
database, however, can also be gained.
Note: be careful not to delete the whole table. Use the direct access only if you know what you are doing.
Note 2: The table is not filled manually, however, so it can be easily restored.

You can use self.cursor and self.connect to operate the database directly.
"""

from typing import Iterable, List
from miniChemistry.Utilities.Checks import keywords_check, type_check
from miniChemistry.Core.CoreExceptions.stableExceptions import *
import os
import pandas as pd
from miniChemistry.Core.Database.ptable import * # needed for sorting by atom number when saving the file with self.end


class SolubilityTable:
    """
    The SolubilityTable class should store information about solubility of a substance and and the same time the
    ions that compose this substance. At the end we have a database that stores a single solubility in five variables:
    CATION: formula of the cation without charge
    CATION_CHARGE: charge of the cation
    ANION: formula of the anion
    ANION_CHARGE: charge of the anion
    SOLUBILITY: one of the five possible solubility values for the given substance
    The formulas and the solubility are TEXT, but the charges are INTEGER.

    To make it easier to return the result, two named tuples are used: Substance and Ion. You can see below that
    Substance consists of the first four items – cation, cation charge, anion and anion charge.
    An Ion consists of two other items – composition and charge (composition is just another name for formula).
    As a result, you can address the returned values of the SolubilityTable class as

    # >>> from Core.Database.stable import SolubilityTable as st
    # >>> ion = st.select_ion('Na')
    # >>> ion.composition
    'Na'
    """

    Ion = namedtuple(
        'Ion',
        'composition, charge'
    )

    Substance = namedtuple(
        'Substance',
        'cation, cation_charge, anion, anion_charge'
    )


    def __init__(self):

        # Filesystem path of the database.
        # Does not need to be on the class level scope,
        # however its more human-visible when put here,
        # if it ever needs to be changed.
        # Only used in `begin():self._connect`.
        _cwd = os.path.dirname(os.path.abspath(__file__))
        self._dbpath = os.path.join(_cwd, 'SolubilityTable.csv')
        self.data = pd.read_csv(self._dbpath,index_col=False)

    def commit(self):
        """Commit changes to the SolubilityTable csv database"""
        self.data.sort_values(
            by="cation",
            key=lambda series:pd.Series(map(lambda element:eval(element)._atomic_number,series)),
            inplace=True
        )
        self.data.to_csv(self._dbpath,index=False)

    def __iter__(self) -> Iterable:
        """
        Returns the solubility table as an iterable.
        :return:
        """
        return self.data.itertuples(name="Substance",index=False)

    def write(self, cation: str, cation_charge: int, anion: str, anion_charge: int, solubility: str) -> None:
        """
        Writes the following data into the database (into the Solubility Table)

        :param cation: str
        :param cation_charge: positive int
        :param anion: str
        :param anion_charge: negative int
        :param solubility: str (one of the five strings mentioned in the self._solubility_options)
        :return: None
        """

        # The five allowed solubility states.
        self._solubility_options = ('SL', 'SS', 'NS', 'RW', 'ND')
        # check that the solubility mentioned is actually one of the five allowed
        keywords_check([solubility], self._solubility_options, 'SolubilityTable.write', variables=locals())

        rowToAdd = (cation, cation_charge, anion, anion_charge, solubility)

        if rowToAdd in self.data.loc:
            # if got something, then raise an exception
            sap = SubstanceAlreadyPresent(substance_signature=[cation, cation_charge, anion, anion_charge], variables=locals())
            raise sap
        else:
            self.data.loc[len(self.data)] = rowToAdd
            self.data.drop_duplicates()

    def erase(self, cation: str, cation_charge: int, anion: str, anion_charge: int, solubility: str) -> None:
        pass

    def select_ion(self, *args, **kwargs) -> List['SolubilityTable.Ion']:
        """
        Filter the SolubilityTable by constraints and return the matching `Ion` instances.
        Each parameter is a constraint.
        Conditions can be properties such as formula and/or charge.
        This function accepts both positional and keyword arguments.

        POSITIONAL ARGUMENTS
        The function accepts positional arguments of types string and integer. String in this case means ion's formula
        and integer – ion's charge. The function will return a list of SolubilityTable.Ion instances where both
        conditions are met. If more than two positional arguments are given, the function will just return an empty list
        (because there's no ion with two formulas or two charges).

        KEYWORD ARGUMENTS
        The function accepts three keywords: cation, anion and charge. In this case you can specify the type of an
        ion (cation or anion) without indicating its charge. The function will return only positive (cation) or
        negative (anion) ions. If the charge is specified, then it is also included (also the sign).

        That means, the function with parameters select_ion(cation='Na', charge=-1) will return an empty list,
        because there are no cations with negative charge (by definition).

        IMPLEMENTATION
        The implementation is based on the set theory and iteration over the whole solubility table. Yes, it is more
        correct, fast and neat to compose a complicated command to the SQL database and not iterate over many items
        inside the database, but this code would be less readable and less adjustable. So, the author believes, your
        computer's power is large enough to compute these kind of things.

        Although, if you believe that this is not good to write code in this way, that means you know for sure how to
        write a proper code. Welcome, give it a try.

        The function first coverts the arguments to conditions that the ion should meet to be returned by the function.
        The conditions is just a set of strings and numbers (i.e. formulas and charges) which an ion must have to suit
        the requirements.

        Say, if we write st.select_ion('Na', 1) the conditions will be {'Na', 1}. For st.select_ion(anion='Na', charge=1)
        the conditions will also be {'Na', 1}. So, yes, the function first does not distinguish between cations and
        anions, it just collects the formulas and charges from the arguments.

        Then, the function iterated over the database (see __iter__ method and the line 'for substance in self' in this
        function) and checks whether the substance (not the ion!) meets the requirements. The check is done as follows:

        We have a set of conditions, for example {'Na', 1} and we have a substance, for example Na2SO4 with Na(+) and
        SO4(-2) ions, which is then converted into a set {'Na', 1, 'SO4', -2}. We accept the substance only in ALL the
        conditions were satisfied (if the condition set is a subset of the substance set).

        In this case we decompose the substance into its ions – cation and anion by using dot notation (remember that
        the substance is a namedtuple). We then check if conditions set is a subset of the ion sets (i.e. if the ions
        fulfill the conditions set).

        Finally, we eliminate all the negatively or positively charged ions depending on the keyword argument used. If
        the keyword 'cation' was used, the function must return only positive ions, if keyword 'anion' was used, then
        the function must return only negative ions.

        :param args: string and integer meaning ion's formula and charge
        :param kwargs: 'cation', 'anion' and 'charge' for customisation
        :return: list of SolubilityTable.Ion instances
        """
        type_check([*args, *kwargs.values()], [str, int], raise_exception=True)
        keywords_check([*kwargs.keys()], ['cation', 'anion', 'charge'],
                       function_name='SolubilityTable.select_ion', variables=locals(), raise_exception=True)

        # Join all the arguments, each of which is a `constraint`
        constraints = set(args).union( set(kwargs.values()) )

        # `ions` is the return value.
        # it is a set as to avoid duplicates.
        ions = set()

        # The substance is a match if its properties contain all of our constraints.
        isMatch = lambda substance : constraints.issubset(set(substance))
        matchingSubstances = filter(isMatch, self)

        for substance in matchingSubstances:
            cation = {substance.cation, substance.cation_charge}
            anion = {substance.anion, substance.anion_charge}

            if isMatch(cation):
                ions.add(
                    SolubilityTable.Ion(substance.cation, substance.cation_charge)
                )
            if isMatch(anion):
                ions.add(
                    SolubilityTable.Ion(substance.anion, substance.anion_charge)
                )

        if 'cation' in kwargs:
            return list(filter(lambda ion:ion.charge>0, ions))
        elif 'anion' in kwargs:
            return list(filter(lambda ion:ion.charge<0, ions))

        return list(ions)

    def select_substance(self, *args, **kwargs) -> List['SolubilityTable.Substance']:
        """
        The select_substance() method is used to select the substances from the solubility table that fulfill the set
        criteria. Here the positional arguments work in the same way as in .select_ion() method – the function just
        checks that all positional arguments are present in the set form of a substance. Say, if we have two positional
        arguments: 'Na' and 1 (as a set they are {'Na', 1}), the substance will be returned if it includes both sodium
        ion (has 'Na' in its formula) and this ion has a charge of +1. For example,

        Na2SO4 (in set form {'Na', 1, 'SO4', -2}) will be approved, but
        KCl (in set form {'K', 1, 'Cl', -1}) will be not.

        The keyword arguments are, however, checked in another way. This function supports five keyword arguments which
        copy the variables used to define a Substance namedtuple – cation, cation_charge, anion, anion_charge, solubility.
        For each keyword argument there is a condition set as a lambda function which works in the following way:
        (an example is given for a cation, but it works exactly in the same way for all the other keyword arguments
        as well.

        # remember that substance is a namedtuple defined at the beginning of the class
        def check_keyword_argument(substance):
            if 'cation' not in kwargs:
                return True
            elif 'cation' in kwargs and substance.cation == kwargs['cation']:
                return True
            else:
                return False

        Basically, if there's no keyword argument mentioned, the (lambda) function returns True, if the argument's value
        coincides with the corresponding quantity of the substance, it returns True, if the argument IS present in the
        kwargs, but the value does NOT coincide, then it returns False. In the form of a lambda function it looks like

        lambda s: True if 'cation' not in kwargs or s.cation == kwargs['cation'] else False

        With 's' meaning 'substance'.

        Basically, the function checks
        1) if all positional arguments are present in the substance when it is in the form of a set
        2) If each keyword argument's value is present in the substance when it is in the form of a set

        EXAMPLE
        Imagine we call
        st.select_substance('Na', 1, anion='SO4')
        The function then
        1) Selects all the substances where any ion (both cation and anion) has a formula 'Na', where there is a charge
        equal to +1 AND where anion is equal to 'SO4'.

        The difference with
        st.select_substance('Na', 1, 'SO4')
        is that in this case the function would return a substance (if it existed) with cation 'SO4' and anion 'Na', but
        in the first case we enforce the anion to be 'SO4'.


        IMPLEMENTATION
        To select the substances, the function creates a list of conditions that can be evaluated to True of False and
        feeds it into the all() function. The conditions are created separately for positional and keyword arguments.
        For positional arguments the condition is mere 'argument in substance' for each argument in positional arguments.
        In a but more Python way, it is

        for substance in self:
            for arg in args:
                if arg in substance:
                    return True
                else:
                    return False

        or to make it a list of evaluative conditions

        for substance in self:
            args_list = [arg in substance for arg in args]

        With the keyword arguments the conditions are created in the form of lambda functions. To evaluate them all
        for a certain substance we use

        for substance in self:
            kwargs_list = [c(substance) for c in conditions]

        where conditions is a list of lambda functions defined as described above.

        To combine all of this, we sum the two lists and pass the final list to the all() function to get

        for substance in self:
            if all([arg in substance for arg in args] + [c(substance) for c in conditions]):
                substances_to_return.append(substance)

        The function then just returns the 'substance_to_return' list.

        :param args: string or integer that indicate formula or charge of an ion respectively
        :param kwargs: cation, cation_charge, anion, anion_charge, solubility
        :return: List[SolubilityTable.Substance]
        """

        keywords_check([*kwargs.values()], ['cation', 'cation_charge', 'anion',
                                            'anion_charge', 'solubility'], variables=locals(),
                       function_name="SolubilityTable.select_substance", raise_exception=True)
        type_check([*args, *kwargs.values()], [str, int], raise_exception=True)

        def isMatch(substance):
            # only match the substances mentioned in args
            condition1 = set(args).issubset(substance)
            # count properties which do not match
            discrepancies = sum([   eval(f"{substance}.{constraint}") != kwargs[constraint]
                                    for constraint in kwargs ])
            condition2 = not discrepancies # no discrepancies = match
            return condition1 and condition2

        return list(filter(isMatch, self))

    def _erase_all(self, no_confirm: bool = False) -> bool:
        if not no_confirm:
            confirmation = input('! Are you sure you want to delete the whole solubility table (type "confirm" to proceed)? – ')
        else:
            confirmation = 'confirm'

        if confirmation == 'confirm':
            self._cursor.execute('DELETE FROM solubility_table')
            self._connect.commit()
            return True
        else:
            print("The solubility table was NOT erased.")
            return False
"""
    @property
    def cursor(self):
        return self._cursor

    @property
    def connect(self):
        return self._connect
"""


st = SolubilityTable()
length = len(st.select_substance())

if length == 0:
    print('WARNING: solubility table is empty. Run the following code:\n'
          '>>> from miniChemistry.Core.Database.ModifySolubilityTable import modify\n'
          '>>> modify(confirmation=False)\n'
          'The code will require confirmation to overwrite the solubility table file.\n'
          'After code execution the solubility table database should contain most common substances\n'
          'met in school chemistry.')
