from math import lcm
from sympy import Matrix, Rational
from typing import List, Dict

import miniChemistry.Core.Database.ptable as pt
from miniChemistry.Core.ElementaryParticle import ElementaryParticle
from miniChemistry.Core.Substances import Particle, Ion, IonGroup, Simple, Molecule
from miniChemistry.Core.CoreExceptions.ToolExceptions import CannotEquateReaction


class Equalizer:
    PARTICLE_SUBCLASSES = Ion | IonGroup | Simple | Molecule
    ALLOWED_PARTICLES = PARTICLE_SUBCLASSES | ElementaryParticle

    LAMBDA_SEARCH_THRESHOLD: int = 4

    def __init__(self,
                    reagents: List[ALLOWED_PARTICLES],
                    products: List[ALLOWED_PARTICLES]
                 ) -> None:
        self._reagents = reagents
        self._products = products

    @staticmethod
    def _make_ints(m: Matrix) -> Matrix:
        m = m.applyfunc(Rational)
        denominators = [term.q for term in m]
        lcm_for_d = lcm(*denominators)
        m = m.applyfunc(lambda x: lcm_for_d * x)
        return m

    @staticmethod
    def _no_electrons(substances: List[ALLOWED_PARTICLES]) -> List[PARTICLE_SUBCLASSES]:
        """Returns a list by removing ElementaryParticle instances from there"""
        return list(filter(lambda x: not isinstance(x, ElementaryParticle), substances))

    def matrix(self,
               charge_balance: bool = True
               ) -> Matrix:
        matrix = []

        # mass balance part
        for el_index, element in enumerate(self.elements):
            matrix.append([])
            for sb_index, substance in enumerate(self.substances):
                if isinstance(substance, ElementaryParticle):
                    index = 0
                else:
                    index = substance.composition.get(element)

                multiple = -1 if substance in self.products else 1
                matrix[el_index].append(multiple * (index if index is not None else 0))

        # charge balance part
        if charge_balance:
            length = len(matrix)
            matrix.append([])
            for sb_index, substance in enumerate(self.substances):
                multiple = -1 if substance in self.products else 1
                charge = substance.charge
                matrix[length].append(multiple * charge)

        return Matrix(matrix)

    @staticmethod
    def _generate_lambdas(
                    ms: List[Matrix],
                    threshold: int = LAMBDA_SEARCH_THRESHOLD
                       ) -> List[int]:
        length = len(ms)
        lambdas = int( length * '1' )
        max_lambdas = int( length * str(threshold) )

        def to_list(n: int) -> List[int]:
            lst = len(str(n)) * [1]
            for i, l in enumerate(str(n)):
                lst[i] = int(l)
            return lst

        while lambdas <= max_lambdas:
            yield to_list(lambdas)
            lambdas += 1

    @staticmethod
    def _test(m: Matrix) -> bool:
        l = m.tolist()
        l = [ll[0] for ll in l]

        all_ints = all( [x%1==0 for x in l] )
        all_positive = all( [x > 0 for x in l]  )

        return all( [all_ints, all_positive] )

    def _guess(self, ms: List[Matrix]) -> Matrix:
        for lambdas in self._generate_lambdas(ms):
            matrix = Matrix( len(ms[0]) * [0] )
            for i, l in enumerate(lambdas):  # lambdas here is a list
                matrix += l * ms[i]

            if Equalizer._test(matrix):
                return matrix
            else:
                continue
        else:
            cer = CannotEquateReaction(reagents=[r.formula() for r in self.reagents], variables=locals())
            cer.description += 'Could not find valid values of lambdas to generate coefficients. Try to increase the threshold.'
            raise cer

    def solve(self) -> Matrix:
        solutions = self.matrix().nullspace()

        if len(solutions) == 0:
            cer = CannotEquateReaction(reagents=[r.formula() for r in self.reagents], variables=locals())
            cer.description += '\nNo valid combination of coefficients was found.'
            raise cer

        elif len(solutions) == 1:
            solution = self._make_ints(solutions[0])
            return solution

        else: # elif len(solutions) > 1
            solution = self._guess(solutions)
            return solution


    @property
    def coefficients(self) -> Dict[Particle, int]:
        answer_dict = dict()
        answer = self.solve()

        for item, substance in zip(answer.tolist(), self.substances):
            answer_dict.update(
                {substance: int(item[0])})  # since answer is a vector (matrix with one column), we just use [0]

        return answer_dict

    @property
    def reagents(self) -> List[ALLOWED_PARTICLES]:
        return self._reagents

    @property
    def products(self) -> List[ALLOWED_PARTICLES]:
        return self._products

    @property
    def substances(self) -> List[ALLOWED_PARTICLES]:
        return self.reagents + self.products

    @property
    def elements(self) -> List[pt.Element]:
        elements = set()

        for s in self.substances:
            if isinstance(s, ElementaryParticle):
                continue
            elements = elements.union( set(s.elements) )

        return list(elements)
