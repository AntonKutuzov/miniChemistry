from __future__ import annotations

from miniChemistry.Core.Tools.ReactionPredictionTool.predict import RPT
from miniChemistry.Core.Reactions import MolecularReaction, HalfReaction
from miniChemistry.Core.Reactions.AbstractReaction import AbstractReaction
from miniChemistry.Core.Tools.Equalizer import Equalizer

from typing import Optional, List, Tuple, Dict, Any


"""
OXRED REACTION IS NOT YET READY.
The prediction tool must take two half-reactions or only reagents and predict
the products.
"""

class RedoxReaction(AbstractReaction):
    ALLOWED_PARTICLES = MolecularReaction.ALLOWED_PARTICLES
    _rpt = RPT(algorithm='redox')

    def __init__(self,
                    *args: Optional[ ALLOWED_PARTICLES ],
                    half_reactions: Optional[ Tuple[HalfReaction, HalfReaction] ] = None,
                    reagents: Optional[ List[ALLOWED_PARTICLES] ] = None,
                    products: Optional[ List[ALLOWED_PARTICLES] ] = None
                 ):

        super().__init__(reagents, products)

    def _init_from_args(self, *args) -> RedoxReaction:
        pass

    def _init_from_halfreactions(self, *hrs: HalfReaction) -> RedoxReaction:
        pass
    
    def _init_from_substances(self, reagents: List[ALLOWED_PARTICLES], products: List[ALLOWED_PARTICLES]) -> RedoxReaction:
        pass

    def _select_halfreaction(self, *reagents) -> HalfReaction:
        pass

    @staticmethod
    def from_string(reaction: str) -> RedoxReaction:
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
