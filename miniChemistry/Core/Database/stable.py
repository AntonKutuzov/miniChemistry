from __future__ import annotations

from pandas.errors import EmptyDataError

import miniChemistry.Core.Database.ptable as pt
from miniChemistry.Utilities.Checks import type_check, keywords_check
from miniChemistry.Utilities.File import File

import pandas as pd
from typing import Iterable, List, Literal
from collections import namedtuple


class SolubilityTable:
    Ion = namedtuple(
        'Ion',
        'composition, charge'
    )

    Substance = namedtuple(
        'Substance',
        'cation, cation_charge, anion, anion_charge, solubility'
    )

    SOLUBILITY_OPTIONS = Literal['SL', 'SS', 'NS', 'RW', 'ND']
    AUTO_COMMIT: bool = True

    def __init__(self) -> None:
        self._file = File(caller=__file__)
        self._file.bind('SolubilityTable.csv')

        try:
            self._data = pd.read_csv(str(self._file.path))
        except EmptyDataError:
            self._data = pd.DataFrame(columns=['cation', 'cation_charge', 'anion', 'anion_charge', 'solubility'])

    def commit(self) -> None:
        if self.size > 0:
            self._data.sort_values(
                by='cation',
                key= lambda series: pd.Series( map(lambda cation: pt.Element.get_by_symbol(cation).atomic_number, series) ), # this trick only works while we don't deal with multiple-element cations!
                inplace=True
            )
        self._data.to_csv(str(self._file.path), index=False)

    def __iter__(self) -> Iterable:
        # for them to return True in isinstance(t, SolubilityTable.Substance)
        return [SolubilityTable.Substance(*t) for t in self._data.itertuples(index=False)].__iter__()

    def write(self,
                  cation: str,
                  cation_charge: int,
                  anion: str,
                  anion_charge: int,
                  solubility: SOLUBILITY_OPTIONS
              ) -> None:

        self._data.loc[self.size] = {
            'cation': cation,
            'cation_charge': cation_charge,
            'anion': anion,
            'anion_charge': anion_charge,
            'solubility': solubility
        }

        self._data.drop_duplicates(inplace=True)

        if SolubilityTable.AUTO_COMMIT:
            self.commit()

    def drop(self,
              cation: str,
              cation_charge: int,
              anion: str,
              anion_charge: int,
              solubility: SOLUBILITY_OPTIONS
              ) -> None:

        index = self._data[
            (self._data['cation'] == cation) &
            (self._data['cation_charge'] == cation_charge) &
            (self._data['anion'] == anion) &
            (self._data['anion_charge'] == anion_charge) &
            (self._data['solubility'] == solubility)
        ].index

        self._data.drop(index=index, inplace=True)

        if SolubilityTable.AUTO_COMMIT:
            self.commit()

    def select_ion(self, *args, **kwargs) -> List[SolubilityTable.Ion]:
        type_check(
            [*args, *kwargs.values()],
            [str, int],
            raise_exception=True
        )
        keywords_check(
            [*kwargs.keys()],
            ['cation', 'anion', 'charge'],
            function_name='SolubilityTable.select_ion',
            variables=locals(),
            raise_exception=True
        )

        # Join all the arguments, each of which is a `constraint`
        constraints = set(args).union(set(kwargs.values()))

        ions = set()
        isMatch = lambda substance: constraints.issubset(set(substance))
        matchingSubstances = filter(isMatch, self.__iter__())  # __iter__ added so that type checkers are satisfied

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


    def select_substance(self, *args, **kwargs) -> List[SolubilityTable.Substance]:
        keywords_check(
            [*kwargs.values()],
            ['cation', 'cation_charge', 'anion', 'anion_charge', 'solubility'],
            variables=locals(),
            function_name="SolubilityTable.select_substance",
            raise_exception=True
        )
        type_check(
            [*args, *kwargs.values()],
            [str, int],
            raise_exception=True
        )

        def isMatch(substance):
            # only match the substances mentioned in args
            condition1 = set(args).issubset(substance)
            # count properties which do not match
            discrepancies = sum([eval(f"{substance}.{constraint}") != kwargs[constraint]
                                 for constraint in kwargs])
            condition2 = not discrepancies  # no discrepancies = match
            return condition1 and condition2

        return list(filter(isMatch, self.__iter__()))

    def _erase_all(self, no_confirm: bool = False) -> bool:
        if not no_confirm:
            confirmation = input(
                '! Are you sure you want to delete the whole solubility table (type "confirm" to proceed)? – ')
        else:
            confirmation = 'confirm'

        if confirmation == 'confirm':
            self._data = pd.DataFrame(columns=['cation', 'cation_charge', 'anion', 'anion_charge', 'solubility'])
            self.commit()
            return True
        else:
            print("The solubility table was NOT erased.")
            return False

    @property
    def size(self) -> int:
        return len(self._data)

"""
st = SolubilityTable()
for s in st:
    print(s)
"""