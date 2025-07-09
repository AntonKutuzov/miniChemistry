from __future__ import annotations

from miniChemistry.Core.Reactions import MolecularReaction, HalfReaction
from miniChemistry.Core.Reactions.AbstractReaction import AbstractReaction
from typing import Optional, List, Tuple, Dict, Any

from miniChemistry.Core.Tools.Equalizer import Equalizer


"""
OXRED REACTION IS NOT YET READY.
The prediction tool must take two half-reactions or only reagents and predict
the products.
"""

class OxredReaction(AbstractReaction):
    ALLOWED_PARTICLES = MolecularReaction.ALLOWED_PARTICLES

    def __init__(self,
                    half_reactions: Optional[ Tuple[HalfReaction, HalfReaction] ] = None,
                    reagents: Optional[ List[ALLOWED_PARTICLES] ] = None,
                    products: Optional[ List[ALLOWED_PARTICLES] ] = None
                 ):
        super().__init__(reagents, products)

    @staticmethod
    def from_string(reaction: str) -> OxredReaction:
        pass

    @property
    def scheme(self) -> str:
        return super().scheme

    @property
    def equation(self) -> str:
        return super().equation

    @property
    def reagents(self) -> List[ALLOWED_PARTICLES]:
        return super().reagents

    @property
    def products(self) -> List[ALLOWED_PARTICLES]:
        return super().products

    @property
    def substances(self) -> List[ALLOWED_PARTICLES]:
        return super().substances

    @property
    def coefficients(self) -> Dict[ALLOWED_PARTICLES, float|int]:
        return Equalizer(reagents=self.reagents, products=self.products).coefficients
