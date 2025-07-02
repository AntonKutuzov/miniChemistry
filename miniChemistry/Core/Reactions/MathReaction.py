from __future__ import annotations

from miniChemistry.Core.Reactions import MolecularReaction
from miniChemistry.Core.Reactions.AbstractReaction import AbstractReaction
from miniChemistry.Core.Substances import Molecule, Simple, Ion
from miniChemistry.Core.Tools.Equalizer import Equalizer

from typing import Optional, List, Callable, Literal
import pandas as pd


class MathReaction(AbstractReaction):
    def __init__(self,
                     reaction: Optional[AbstractReaction] = None,
                     *,
                     reagents: Optional[ List[Molecule|Simple|Ion] ] = None,
                     products: Optional[ List[Molecule|Simple|Ion] ] = None,
                     equalizer: Callable = Equalizer
                 ) -> None:

        self._math_data = pd.DataFrame(columns=['substance', 'side', 'sign', 'coefficient'])

        if reaction is not None:
            reagents = reaction.reagents
            products = reaction.products

        self._orig_substances = reagents + products  # note that property "substances" does not return this attribute!
        self._orig_reagents = reagents
        self._orig_products = products
        self._equalizer = equalizer

        self._fill_math_data()
        super().__init__(reagents, products)

    def __mul__(self, other: float|int) -> None:
        for s in self.substances:
            coef = self.get(s, 'coefficient')
            self.alter(s, 'coefficient', other * coef)
        # return self

    def __truediv__(self, other: float|int) -> None:
        for s in self.substances:
            coef = self.get(s, 'coefficient')
            self.alter(s, 'coefficient', coef / other)
        # return self

    def __add__(self, other: MathReaction) -> None:
        for sub in other.substances:
            other_sign = other.get(sub, 'sign')
            other_coef = other.get(sub, 'coefficient')
            other_side = other.get(sub, 'side')

            if sub in self.substances:
                coef = self.get(sub, 'coefficient')
                multip = 1 if self.get(sub, 'side') == other_side else -1

                self.alter( sub, 'coefficient', coef + multip * other_sign * other_coef )

            elif sub not in self.substances:
                self._add_row(sub, other_side, other_sign, other_coef)

            else:
                raise Exception('How is this possible?')

    def __sub__(self, other: MathReaction) -> None:
        for sub in other.substances:
            other.alter(sub, 'sign', -other.get(sub, 'sign'))

        self + other

    @staticmethod
    def from_string(reaction: str) -> AbstractReaction:
        r = MolecularReaction.from_string(reaction)
        return MathReaction(r)

    def _add_row(self,
                 s: Molecule|Simple|Ion,
                 side: Literal['RHS', 'LHS'],
                 sign: int,
                 coef: float|int
                ) -> None:
        self.math_data.loc[len(self.math_data)] = [s, side, sign, coef]

    def _del_row(self,
                 s: Molecule|Simple|Ion
                 ) -> None:
        self.math_data.drop(self._subs_index(s), inplace=True)

    def _fill_math_data(self) -> None:
        for substance in self._orig_substances:
            coefficients = self._equalizer(reagents=self._orig_reagents, products=self._orig_products).coefficients
            # types are indicated to avoid warnings about type mismatch
            side: Literal['RHS', 'LHS'] = 'LHS' if substance in self._orig_reagents else 'RHS'
            sign: Literal[-1, 1] = 1  # 'plus' (-1 for minus)
            coef: float|int = float(coefficients[substance])

            self._add_row(substance, side, sign, coef)

    def _subs_row(self, s: Molecule|Simple|Ion) -> pd.DataFrame:
        return self.math_data[ self.math_data['substance'] == s ]

    def _subs_index(self, s: Molecule|Simple|Ion) -> int:
        return self.math_data[ self.math_data['substance'] == s ].index[0]

    def _sub_present(self, s: Molecule|Simple|Ion) -> bool:
        return s in self.math_data['substance'].values

    def _check(self,
               check: Literal['positive sign', 'int coefficient'],
               condition: Literal['all', 'any']
               ) -> bool:

        positive = lambda x: x > 0
        integer = lambda x: int(x) == x

        condition_dict = {
            ('positive sign', 'all'): self.math_data['sign'].apply(positive).all(),
            ('positive sign', 'any'): self.math_data['sign'].apply(positive).any(),
            ('int coefficient', 'all'): self.math_data['coefficient'].apply(integer).all(),
            ('int coefficient', 'any'): self.math_data['coefficient'].apply(integer).any()
        }

        result = condition_dict[ (check, condition) ]
        return bool(result)

    def flip_sign(self) -> None:
        for s in self:  # look at AbstractReaction.__iter__() if typechecker gives you a warning
            sign = self.get(s, 'sign')
            self.alter(s, 'sign', self._opposite_sign(sign))

    @staticmethod
    def _opposite_side(side: Literal['LHS', 'RHS']) -> str:
        if side == 'RHS':
            return 'LHS'
        elif side == 'LHS':
            return 'RHS'
        else:
            raise ValueError(f'Expected either "LHS" or "RHS", got {side}.')

    @staticmethod
    def _opposite_sign(sign: Literal[1, -1]) -> int:
        if sign == 1:
            return -1
        elif sign == -1:
            return 1
        else:
            raise ValueError(f'Expected 1 or -1, got {sign}.')

    def get(self,
            s: Molecule|Simple|Ion,
            data: Literal['substance', 'side', 'sign', 'coefficient'],
            index: int = 0
            ): # indicating possible return types will raise a lot of type mismatch warnings
        return self._subs_row(s)[data].iloc[index]

    def alter(self,
              s: Molecule|Simple|Ion,
              data: Literal['substance', 'side', 'sign', 'coefficient'],
              new_value: str|int|float
              ) -> None:
        self.math_data.loc[self._subs_index(s), data] = new_value

    def reverse(self) -> None:
        for s in self.substances:
            self.flip(s)
            self.alter(s, 'sign', self._opposite_sign(self.get(s, 'sign')))

    def flip(self, s: Molecule|Simple|Ion) -> None:
        side = self.get(s, 'side')
        sign = self.get(s, 'sign')

        self.alter(s, 'side', self._opposite_side(side))  # due to generality of .get method
        self.alter(s, 'sign', self._opposite_sign(sign))

    def solve_for(self, s: Molecule|Simple|Ion) -> None:
        side = self.get(s, 'side')

        if side == 'RHS':
            self.flip(s)
            side = self._opposite_side(side)

        for substance in self.substances:
            if not substance == s and self.get(substance, 'side') == side:
                self.flip(substance)

        if self.get(s, 'sign') == -1:
            self.flip_sign()

    def side(self,
             side: Literal['LHS', 'RHS'],
             ignore_coef: bool = False
             ) -> str:
        string = ''

        for s in self.substances:
            sign = ' + ' if self.get(s, 'sign') == 1 else ' - '
            coef = self.get(s, 'coefficient') if not ignore_coef else 1.0
            coef = '' if coef == 1.0 else coef

            if self.get(s, 'side') == side:
                string += f"{sign}{coef} {s.formula()}"

        return string.strip(' + ')  # do not cut minus sign, because it is always needed

    def remove_zero_coef(self) -> None:
        for s in self:
            if self.get(s, 'coefficient') == 0:
                self._del_row(s)

    def substitute(self, mr: MathReaction, s: Molecule|Simple|Ion) -> None:
        if s not in self:
            raise Exception(f'Substance {s.formula()} is not found in a reaction {self.equation}.')
        elif s not in mr:
            raise Exception(f'Substance {s.formula()} is not found in a reaction {mr.equation}.')
        else:
            pass

        insert_side = self.get(s, 'side')
        mr.solve_for(s)

        mr_coef = mr.get(s, 'coefficient')
        self_coef = self.get(s, 'coefficient')
        mr / mr_coef  # __truediv__ does not require assignment
        mr * self_coef

        self._del_row(s)
        mr._del_row(s)

        for s in mr:
            sign = mr.get(s, 'sign')
            coef = mr.get(s, 'coefficient')

            if s not in self:
                self._add_row(s, insert_side, sign, coef)
            else:
                old_side = self.get(s, 'side')
                old_coef = self.get(s, 'coefficient')
                multip = 1 if insert_side == old_side else -1

                self.alter(s, 'coefficient', old_coef + multip * sign * coef)

        self.remove_zero_coef()

        # remove substances with coefficient of zero
        self._math_data = self.math_data[~(self.math_data['coefficient'] == 0)].reset_index(drop=True)

    def standard_form(self) -> None:
        for s in self:
            if self.get(s, 'sign') == -1:
                self.flip(s)

    @property
    def equation(self) -> str:
        return self.side('LHS') + ' == ' + self.side('RHS')

    @property
    def scheme(self) -> str:
        return self.side('LHS', ignore_coef=True) + ' == ' + self.side('RHS', ignore_coef=True)

    @property
    def math_data(self) -> pd.DataFrame:
        return self._math_data

    @property
    def substances(self) -> List[Molecule|Simple|Ion]:
        return list( self.math_data['substance'] )

    @property
    def reagents(self) -> List[Molecule|Simple|Ion]:
        return list( self.math_data[self.math_data['side'] == 'LHS']['substance'] )

    @property
    def products(self) -> List[Molecule|Simple|Ion]:
        return list( self.math_data[self.math_data['side'] == 'RHS']['substance'] )

    @property
    def coefficients(self):
        return Equalizer(reagents=self.reagents, products=self.products).coefficients
