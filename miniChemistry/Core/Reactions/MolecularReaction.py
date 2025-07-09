"""
TWO WAYS TO LOOK AT CHEMICAL REACTION
A chemical reaction is an interaction between several (in some cases one) chemical substances, which results in
formation of a set of new chemical substances (in case of one substance, the "interaction" is decomposition).

We can look at a chemical process from two perspectives: "from inside" and "from outside".  The latter case can be
interpreted as a "black box" model of a reaction – we look only at what comes in and what comes out, but don't case
about the way the substances are converted from one to another.

The "from inside" view is described in this module in "ReactionMechanisms" folder by simple and complex reaction
mechanisms. The conclusion of the "from inside" view is given in predict.py, which contains a function that uses all
the mechanisms described in "ReactionMechanisms" and predicts the products of a reaction based on a set of provided
reagents.

This file, however, offers a "from outside" view. Now we can look at a chemical reaction as on a black box, i.e. we
don't case about how products are obtained from reagents, but rather care about their stoichiometric relations and
some other variables described here. The Reaction class is a basis for Computations/ReactionCalculator.py, which will
then be used to perform typical stoichiometric calculations over a chemical reaction.

IMPLEMENTATION
The Reaction class contains all the properties of a reaction that follow directly from its reagents and products. Those are
- reaction type (roughly indicates reaction mechanism)
- equation
- scheme (equation without coefficients)
- coefficients (a dict with substances as keys and their coefficients as values)
- substances (list of all substances)
- reagents
- products

The class also has some magic methods implemented for easier handling of the reactions. Those are
__hash__. Returns a hash of a reaction scheme, because a scheme (given that the module does not support isomers) is
reaction's unique signature
__eq__. Compares reaction's schemes (for the same reason)
__iter__. Iterates over reaction's substances
__getitem__. Returns a substance. The indices are provided in the same order as reagents, plus products if they are given
"""


from __future__ import annotations
from typing import Tuple, List, Callable, Optional
from miniChemistry.Core.Substances import Molecule, Simple
from miniChemistry.Utilities.Checks import type_check
from miniChemistry.Core.Tools.parser import parse
from miniChemistry.Core.Tools.ReactionPredictionTool.predict import RPT
from miniChemistry.Core.Tools.Equalizer import Equalizer
from miniChemistry.Core.CoreExceptions.ReactionExceptions import WrongReactionConstructorParameters, WrongNumberOfReagents
from miniChemistry.MiniChemistryException import NotSupposedToHappen
from miniChemistry.Core.Reactions.AbstractReaction import AbstractReaction


class MolecularReaction(AbstractReaction):
    ALLOWED_PARTICLES = Simple | Molecule
    _rpt = RPT(algorithm='molecular')

    def __init__(self, *args: Simple|Molecule,
                 reagents: Optional[ List[ALLOWED_PARTICLES] ] = None,
                 products: Optional[ List[ALLOWED_PARTICLES] ] = None,
                 ignore_restrictions: bool = False,
                 _RPT: Callable = _rpt.predict
                ) -> None:
        """
        The constructor can be called in two ways: first with both reagents and products given as lists in
        keyword arguments, or, second, as separate substances that will be interpreted as reagents. The constructor then
        uses predict.py to estimate reaction's products.
        NOTE: if the products are provided, then the code does not check is the reaction is correct.

        Since the code supports only 1 or 2 reagents, and 1 to 3 products, this is tested before the reaction can
        be considered valid. Wrong number of reagents causes an exception with the same name: WrongNumberOfReagents.
        NOTE: if it is impossible to predict products (if only reagents are given), the code will raise an exception.

        :param args: reagents, instances of Molecule or Simple
        :param reagents: list of Simple and/or Molecule
        :param products: list of Simple and/or Molecule
        """

        _reagents = list()
        _products = list()

        self._predict = _RPT

        if reagents is products is None and args:
            if 1 <= len(args) <= 2:
                _reagents = list(args)
                _products = list(self._predict(*args, ignore_restrictions=ignore_restrictions))
            else:
                raise WrongNumberOfReagents(reagents=[arg.formula() for arg in args], variables=locals())
        elif reagents and products and not args:
            _reagents = reagents
            _products = products
        else:
            raise WrongReactionConstructorParameters(variables=locals())

        super().__init__(reagents=_reagents, products=_products)


    @staticmethod
    def extract_substances(reaction: str) -> Tuple[ List[ALLOWED_PARTICLES], List[ALLOWED_PARTICLES] ]:
        """
        Method is used as a part of .from_string() method, also implemented for Reaction class. It takes in a full
        chemical reaction (scheme, so no coefficients) and returns two lists of substances.

        :param reaction: reaction scheme, NOT equation!
        :return: Two lists of Simple and/or Molecule instances, representing respectively, reagents and products.
        """

        reaction = reaction.replace(' ', '')
        reaction = reaction.replace('=', '->')  # does nothing if there is no '='
        reagent_str, product_str = reaction.split("->")

        reagents = MolecularReaction.parse_side(reagent_str)
        products = MolecularReaction.parse_side(product_str)

        return reagents, products

    @staticmethod
    def parse_side(substances: str) -> List[ALLOWED_PARTICLES]:
        """
        Used as a part of .from_string() method that is also implemented for Reaction class. This method splits
        (parses) one side of the scheme – either right-hand side, or left-hand side.

        :param substances: RHS or LHS of a chemical reaction's scheme
        :return: list of Simple and/or Molecule instances
        """

        substances = substances.replace(' ', '')
        substance_list = substances.split('+')
        resulting = [parse(s) for s in substance_list]
        return resulting


    @staticmethod
    def from_string(reaction: str) -> MolecularReaction:
        """
        The .from_string() method takes in reaction's scheme and returns a Reaction instance.

        :param reaction: reaction's scheme as a string (NOT equation, NO coefficients!)
        :return: an instance of Reaction with respective reagents and products
        """

        if '->' in reaction or '=' in reaction:
            reagents, products = MolecularReaction.extract_substances(reaction)
            return MolecularReaction(reagents=reagents, products=products)
        else:
            reagents = MolecularReaction.parse_side(reaction)
            return MolecularReaction(*reagents)

    @property
    def scheme(self) -> str:
        return super().scheme

    @property
    def equation(self) -> str:
        return super().equation

    @property
    def reagents(self):
        return super().reagents

    @property
    def products(self):
        return super().products

    @property
    def substances(self):
        return self.reagents + (self.products if self.products is not None else [])

    @property
    def coefficients(self):
        return Equalizer(reagents=self.reagents, products=self.products).coefficients

    @property
    def string_coefficients(self):
        """
        Is used if one needs a dict of coefficients where instead of instances of Simple and Molecule one has their
        respective formulas (str).

        :return:
        """

        string_dict = dict()

        for sub, coef in self.coefficients.items():
            formula = sub.formula()
            string_dict.update({formula : coef})

        return string_dict

    @property
    def reaction_type(self) -> str:
        """
        In school chemistry, we can divide reactions in four types, based on the number of reacting substances.
        Addition: two molecules add to one
        Decomposition: one molecules splits into two (sometimes three) simpler molecules
        Substitution: a Simple substance reacts with a Molecule to form another Simple and another Molecule
        Exchange: reaction of two Molecules to form two another Molecules
        NOTE: this classification is not the same as the one used in "ReactionMechanisms". The latter is a custom
        classification for this package, and it is based on the one provided here, but is not exactly the same. Also,
        this classification is real and is widely used in school chemistry.

        :return: string, one of the four: "addition", "decomposition", "exchange", "substitution"
        """

        if len(self.reagents) > 1 and len(self.products) == 1:
            return 'addition'
        elif len(self.reagents) == 1 and len(self.products) > 1:
            return 'decomposition'
        elif type_check([*self.reagents], [Molecule], raise_exception=False):
            return 'exchange'
        elif type_check([*self.reagents], [Simple, Molecule], raise_exception=False):
            return 'substitution'
        else:
            nsth = NotSupposedToHappen(variables=locals())
            nsth.description += f'\nThe reaction "{self.scheme}" has an unknown type.'
            raise nsth
