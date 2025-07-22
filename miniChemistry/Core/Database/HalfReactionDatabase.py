from miniChemistry.Core.Reactions.HalfReaction import HalfReaction
from miniChemistry.Utilities.File import File
import pandas as pd
from typing import Tuple, List, Literal


class HalfReactionDatabase:
    def __init__(self):
        self._file = File(caller=__file__)
        self._file.bind('HalfReactionDatabase.csv')
        self._df = self._read_dataframe()

    def _read_dataframe(self) -> pd.DataFrame:
        csv = pd.read_csv(str(self._file.path))
        df = pd.DataFrame(columns=['scheme', 'potential', 'reagents', 'products'])

        for i in range(len(csv)):
            hr = HalfReaction.from_string( csv.loc[i, 'scheme'] )
            df.loc[i] = {
                'scheme': hr.scheme,
                'potential': csv.loc[i, 'potential'],
                'reagents': hr.reagents,
                'products': hr.products
            }

        return df

    def _erase_database(self) -> None:
        self._file.erase_all()

    def save_dataframe(self) -> None:
        self._df.drop_duplicates(inplace=True, subset='scheme')

        self._file.write('scheme,potential')

        for row in self._df.iterrows():
            self._file.append(row[1]['scheme'] + ',', add_splitter=False)
            self._file.append(str(row[1]['potential']))

    @staticmethod
    def _parse_reaction(df: pd.DataFrame) -> Tuple[str, float, List, List]:
        df.reset_index(inplace=True)

        scheme = df['scheme'][0]
        potential = float( df['potential'][0] )
        reagents = list( df['reagents'][0] )
        products = list( df['products'][0] )

        return scheme, potential, reagents, products

    def compare_potentials(self,
            *hrs: HalfReaction,
            condition: Literal['min', 'max']
        ) -> HalfReaction:

        min_pot = 0
        min_hr = None
        max_pot = 0
        max_hr = None

        for hr in hrs:
            row = self._df[ self._df['scheme'] == hr.scheme ]

            if len(row) > 1:
                raise Exception(f'Got more than 1 rows for the same scheme: {hr.scheme}.')

            scheme, potential, reagents, products = HalfReactionDatabase._parse_reaction(row)

            if potential < min_pot:
                min_hr = hr
                min_pot = potential
            elif potential > max_pot:
                max_hr = hr
                max_pot =potential

        if condition == 'min':
            return min_hr
        elif condition == 'max':
            return  max_hr
        else:
            raise Exception()


    def halfreaction_present(self, hr: HalfReaction) -> bool:
        return not self._df[self._df['scheme'] == hr.scheme].empty

    def add_halfreaction(self, hr: HalfReaction, potential: float) -> None:
        self._df.loc[len(self._df)] = {
            'scheme': hr.scheme,
            'potential': potential,
            'reagents': tuple( hr.reagents ),
            'products': tuple( hr.products )
        }

        self._df.drop_duplicates(inplace=True, subset='scheme')
        self.save_dataframe()

    def rewrite_halfreaction(self, hr: HalfReaction, potential: float) -> None:
        if self.halfreaction_present(hr):
            self.remove_halfreaction(hr)
            self.add_halfreaction(hr, potential)
        else:
            raise Exception(f'Half-reaction {hr.scheme} is not found in the database.')

    def remove_halfreaction(self, hr: HalfReaction) -> None:
        self._df = self._df[ self._df['scheme'] != hr.scheme ]
        self._df.reset_index(inplace=True)

    def halfreaction_list(self) -> List[HalfReaction]:
        hr_list = list()

        for i in range(len(self._df)):
            rs = list( self._df.loc[i, 'reagents'] )
            ps = list( self._df.loc[i, 'products'] )

            hr = HalfReaction(reagents=rs, products=ps)
            hr_list.append(hr)

        return hr_list

    def match(self,
              substance: HalfReaction.ALLOWED_PARTICLES,
              place: Literal['reagents', 'products', 'all'] = 'all'
              ) -> List[HalfReaction]:

        if place == 'all':
            return self.match(substance, 'reagents') + self.match(substance, 'products')

        elif place in {'reagents', 'products'}:
            reactions = list()
            df = self._df[ self._df[place].apply(lambda x: substance in x) ]

            for row in df.iterrows():
                reagents = list( row[1]['reagents'] )
                products = list( row[1]['products'] )
                reactions.append( HalfReaction(reagents=reagents, products=products) )
            return reactions

        else:
            raise Exception(f'Invalid search place: "{place}". Expected "all", "reagents" or "products".')

    def print_df(self):
        for row in self._df.iterrows():
            scheme = row[1]['scheme']
            potential = row[1]['potential']
            reagents = [r.formula() for r in row[1]['reagents']]
            products = [p.formula() for p in row[1]['products']]

            print(scheme, '\t', potential, '\t', reagents, products)
