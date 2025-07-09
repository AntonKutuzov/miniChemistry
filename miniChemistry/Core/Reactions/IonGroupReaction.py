from __future__ import annotations

from miniChemistry.Core.Reactions.MolecularReaction import MolecularReaction
from miniChemistry.Core.Substances import Molecule, Ion, IonGroup
from miniChemistry.Core.Tools.ReactionPredictionTool.predict import RPT
from typing import Optional, List


class IonGroupReaction(MolecularReaction):
    def __init__(self, *args: Molecule|Ion|IonGroup,
                 reagents: Optional[List[Ion | IonGroup | Molecule]] = None,
                 products: Optional[List[Ion | IonGroup | Molecule]] = None,
                 ignore_restrictions: bool = False
                 ) -> None:

        rpt = RPT(algorithm='ionic')

        super().__init__(
            *args,
            reagents=reagents,
            products=products,
            ignore_restrictions=ignore_restrictions,
            _RPT=rpt.predict)

    @staticmethod
    def from_string(reaction: str) -> IonGroupReaction:
        pass
