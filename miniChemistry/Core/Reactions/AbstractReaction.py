from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any, final


class AbstractReaction(ABC):
    def __init__(self,
                 reagents: List,
                 products: List,
                 ) -> None:

        self._reagents = reagents
        self._products = products

        self._reagents.sort(key=lambda s: s.formula())  # needed for consistent __eq__ and __hash__ work
        self._products.sort(key=lambda s: s.formula())  # to make them insensitive to order of reagents


    @final
    def __iter__(self):
        return self.substances.__iter__()

    @final
    def __eq__(self, other: AbstractReaction):
        return self.scheme == other.scheme

    @final
    def __hash__(self):
        return hash(self.scheme)

    @staticmethod
    @abstractmethod
    def from_string(reaction: str) -> AbstractReaction:
        ...

    @property
    @abstractmethod
    def scheme(self) -> str:
        scheme = ' + '.join([r.formula() for r in self.reagents])
        scheme += ' -> '
        scheme += ' + '.join([p.formula() for p in self.products])
        return scheme

    @property
    @abstractmethod
    def equation(self) -> str:
        equation = ''

        for reagent in self.reagents:
            coef = str(self.coefficients[reagent])
            equation += coef if not coef == '1' else ''
            equation += reagent.formula() + ' + '
        equation = equation.strip(' + ')

        equation += ' = '

        for product in self.products:
            coef = str(self.coefficients[product])
            equation += coef if not coef == '1' else ''
            equation += product.formula() + ' + '
        equation = equation.strip(' + ')

        return equation

    @property
    @abstractmethod
    def reagents(self) -> List:
        return self._reagents

    @property
    @abstractmethod
    def products(self) -> List:
        return self._products

    @property
    @abstractmethod
    def substances(self) -> List:
        return self.reagents + self.products

    @property
    @abstractmethod
    def coefficients(self) -> Dict[Any, float|int]:
        ...
