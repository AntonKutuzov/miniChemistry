from __future__ import annotations

from miniChemistry.Core.Reactions import MolecularReaction
from miniChemistry.Core.Reactions.MathReaction import MathReaction
from miniChemistry.Core.Reactions.AbstractReaction import AbstractReaction
from miniChemistry.Core.Substances import Ion, IonGroup
from miniChemistry.Core.ElementaryParticle import *
from miniChemistry.Core.Tools.Equalizer import Equalizer
from miniChemistry.Core.Tools.parser import parse, parse_ion

from typing import List, Dict, Tuple


class HalfReaction(AbstractReaction):
    PARTICLE_SUBCLASSES = Ion | IonGroup | MolecularReaction.ALLOWED_PARTICLES
    ALLOWED_PARTICLES = PARTICLE_SUBCLASSES | ElementaryParticle

    def __init__(self,
                 reagents: List[ALLOWED_PARTICLES],
                 products: List[ALLOWED_PARTICLES]
                 ) -> None:

        super().__init__(reagents, products)

    def __len__(self):
        return self.substances.__len__()

    @staticmethod
    def _particle_type(particle: str) -> Literal['Neutral', 'Ion', 'ElementaryParticle']:
        from re import fullmatch

        if fullmatch(r'[epn]\([+-]?\d\)', particle):
            return 'ElementaryParticle'
        elif fullmatch(r'[epn]\([+-]?\d+\)', particle):
            raise Exception('Elementary Particles cannot have charge with two digits.')
        elif fullmatch(r'(?![epn]\()[A-Za-z0-9()]+\([+-]?\d+\)', particle):
            return 'Ion'
        elif fullmatch(r'[A-Za-z0-9()]+', particle):
            return 'Neutral'
        else:
            raise ValueError(f'The particle does not match any of the patterns: {particle}.')

    @staticmethod
    def charge_sum(coefficients: Dict[PARTICLE_SUBCLASSES, int|float]) -> int:
        """Sums up all the charges in a gives set of particle subclasses. Includes coefficients."""
        return sum( [s.charge * cf for s, cf in coefficients.items()] )

    @staticmethod
    def parse_particle(p: str) -> ALLOWED_PARTICLES:
        p_type = HalfReaction._particle_type(p)
        if p_type == 'ElementaryParticle':
            if 'e' in p:
                return Electron
            elif 'p' in p:
                return Proton
            elif 'n' in p:
                return Neutron

        elif p_type == 'Neutral':
            return parse(p)

        elif p_type == 'Ion':
            f, ch = parse_ion(p)
            return Ion.from_string(f, ch)
        else:
            raise Exception(f'What type is it?: {p}.')

    @staticmethod
    def parse_side(side: str) -> List[ALLOWED_PARTICLES]:
        while ' ' in side:
            side = side.replace(' ', '')
        substance_str = side.split('+')
        substances = [HalfReaction.parse_particle(p) for p in substance_str]
        return substances

    @staticmethod
    def extract_substances(reaction: str) -> Tuple[ List[ALLOWED_PARTICLES], List[ALLOWED_PARTICLES] ]:
        reaction = reaction.replace('=', '->')
        reagent_str, product_str = reaction.split('->')
        reagents = HalfReaction.parse_side(reagent_str)
        products = HalfReaction.parse_side(product_str)

        return reagents, products

    @staticmethod
    def from_string(reaction: str) -> HalfReaction:
        if '->' in reaction or '=' in reaction:
            reagents, products = HalfReaction.extract_substances(reaction)
            return HalfReaction(reagents=reagents, products=products)

    def reversed(self) -> HalfReaction:
        mr = MathReaction(self)
        mr.reverse()
        new_hr = HalfReaction(mr.reagents, mr.products)
        return new_hr

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
    def scheme(self) -> str:
        return super().scheme

    @property
    def coefficients(self) -> Dict[ALLOWED_PARTICLES, float]:
        return Equalizer(reagents=self.reagents, products=self.products).coefficients
