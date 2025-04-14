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


from typing import Union, Tuple, List
from miniChemistry.Core.Substances import Molecule, Simple
from miniChemistry.Utilities.Checks import type_check
from miniChemistry.Core.Tools.parser import parse
from miniChemistry.Core.Tools.predict import predict
from miniChemistry.Core.Tools.Equalizer import Equalizer
from miniChemistry.Core.CoreExceptions.ReactionExceptions import WrongReactionConstructorParameters, WrongNumberOfReagents
from miniChemistry.MiniChemistryException import NotSupposedToHappen


class Reaction:
    
    def __init__(self, *args: Union[Simple, Molecule],
                 reagents: Union[List[Union[Simple, Molecule]], None] = None,
                 products: Union[List[Union[Simple, Molecule]], None] = None) -> None:
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

        self.NO_RESTRICTIONS = False

        self._reagents = list()
        self._products = list()

        if reagents is products is None and args:
            if 1 <= len(args) <= 2:
                self._reagents = list(args)
                self._products = list(predict(*args, ignore_restrictions=self.NO_RESTRICTIONS))
            else:
                raise WrongNumberOfReagents(reagents=[arg.formula() for arg in args], variables=locals())
        elif reagents and products and not args:
            self._reagents = reagents
            self._products = products
        else:
            raise WrongReactionConstructorParameters(variables=locals())

    def __iter__(self):
        self.substances.__iter__()

    def __getitem__(self, item):
        return self.substances[item]

    def __eq__(self, other):
        return self.scheme == other.scheme

    def __hash__(self):
        return hash(self.scheme)

    def _get_scheme(self) -> str:
        """
        The method composes a scheme of a reaction based on formulas of the reagents and products.
        :return: string, representing a reaction scheme
        """

        scheme = ' + '.join([r.formula() for r in self._reagents])
        scheme += ' -> '
        scheme += ' + '.join([p.formula() for p in self._products])
        return scheme

    def _get_equation(self) -> str:
        """
        The method composes reaction equation (scheme, but with coefficients) based on formulas and coefficients
        obtained from Equalizer (used in self.coefficients property)
        :return: string, representing a reaction equation
        """

        equation = ''

        for reagent in self._reagents:
            coef = str(self.coefficients[reagent])
            equation += coef if not coef == '1' else ''
            equation += reagent.formula() + ' + '
        equation = equation.strip(' + ')

        equation += ' = '

        for product in self._products:
            coef = str(self.coefficients[product])
            equation += coef if not coef == '1' else ''
            equation += product.formula() + ' + '
        equation = equation.strip(' + ')

        return equation

    def _get_type(self) -> str:
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

        if len(self._reagents) > 1 and len(self._products) == 1:
            return 'addition'
        elif len(self._reagents) == 1 and len(self._products) > 1:
            return 'decomposition'
        elif type_check([*self._reagents], [Molecule], raise_exception=False):
            return 'exchange'
        elif type_check([*self._reagents], [Simple, Molecule], raise_exception=False):
            return 'substitution'
        else:
            nsth = NotSupposedToHappen(variables=locals())
            nsth.description += f'\nThe reaction "{self.scheme}" has an unknown type.'
            raise nsth

    @staticmethod
    def split_reaction_string(reaction: str) -> Tuple[List[Union[Molecule, Simple]], List[Union[Molecule, Simple]]]:
        """
        Method is used as a part of .from_string() method, also implemented for Reaction class. It takes in a full
        chemical reaction (scheme, so no coefficients) and returns two lists of substances.

        :param reaction: reaction scheme, NOT equation!
        :return: Two lists of Simple and/or Molecule instances, representing respectively, reagents and products.
        """

        reaction = reaction.replace(' ', '')
        reaction = reaction.replace('=', '->')  # does nothing if there is no '='
        reagent_str, product_str = reaction.split("->")

        reagents_str_split = reagent_str.split('+')
        products_str_split = product_str.split('+')

        reagents = [parse(r) for r in reagents_str_split]
        products = [parse(p) for p in products_str_split]

        return reagents, products

    @staticmethod
    def split_RHS_or_LHS(substances: str) -> List[Union[Molecule, Simple]]:
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
    def from_string(reaction: str) -> 'Reaction':
        """
        The .from_string() method takes in reaction's scheme and returns a Reaction instance.

        :param reaction: reaction's scheme as a string (NOT equation, NO coefficients!)
        :return: an instance of Reaction with respective reagents and products
        """

        if '->' in reaction or '=' in reaction:
            reagents, products = Reaction.split_reaction_string(reaction)
            return Reaction(reagents=reagents, products=products)
        else:
            reagents = Reaction.split_RHS_or_LHS(reaction)
            return Reaction(*reagents)

    @property
    def scheme(self) -> str:
        return self._get_scheme()

    @property
    def equation(self) -> str:
        return self._get_equation()

    @property
    def reagents(self):
        return self._reagents

    @property
    def products(self):
        return self._products

    @property
    def substances(self):
        return self._reagents + (self._products if self._products is not None else [])

    @property
    def coefficients(self):
        return Equalizer(reagents=self._reagents, products=self._products).coefficients

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
        return self._get_type()
