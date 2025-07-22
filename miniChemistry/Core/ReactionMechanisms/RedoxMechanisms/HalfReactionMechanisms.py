from miniChemistry.Core.ReactionMechanisms.RedoxMechanisms.RedoxElementarySteps import redox_medium
from miniChemistry.Core.Reactions import HalfReaction, MolecularReaction, MathReaction, IonGroupReaction
from miniChemistry.Core.Tools.sorting import reduction_and_oxidation, sort_particles

from typing import List


def hr_addition(hr1: HalfReaction, hr2: HalfReaction) -> List[MolecularReaction.ALLOWED_PARTICLES]:
    reduction, oxidation = reduction_and_oxidation(hr1, hr2)
    oxidation = oxidation.reversed()

    red_mr = MathReaction(reduction)
    ox_mr = MathReaction(oxidation)

    red_mr + ox_mr

    match redox_medium(red_mr):
        case 'acidic' | 'basic' | 'neutral':
            return red_mr.products

        case 'unknown':
            ions = sort_particles(*red_mr.products, get='ions')

            if len(ions) == 2:
                igr = IonGroupReaction(*ions, ignore_restrictions=True)
                products = igr.products + red_mr.products

                for i in ions:
                    products.remove(i)

                return products
            else:
                return red_mr.products
