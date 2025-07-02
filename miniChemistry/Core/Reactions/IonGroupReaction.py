from miniChemistry.Core.Reactions.MolecularReaction import MolecularReaction
from miniChemistry.Core.Substances import Molecule, Ion, IonGroup
from miniChemistry.Core.Tools.ReactionPredictionTools.IonPredict import ion_predict
from typing import Optional, List
from functools import partial


class IonGroupReaction(MolecularReaction):
    def __init__(self, *args: Molecule|Ion|IonGroup,
                 reagents: Optional[List[Ion | IonGroup | Molecule]] = None,
                 products: Optional[List[Ion | IonGroup | Molecule]] = None,
                 complete_reaction: bool = False,
                 ignore_restrictions: bool = False
                 ) -> None:
        super().__init__(
            *args,
            reagents=reagents,
            products=products,
            ignore_restrictions=ignore_restrictions,
            _RPT=partial(ion_predict, complete_reaction=complete_reaction))
