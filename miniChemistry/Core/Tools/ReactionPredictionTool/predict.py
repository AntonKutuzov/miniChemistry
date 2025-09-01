from miniChemistry.Core.CoreExceptions.MechanismExceptions import CannotPredictProducts
from miniChemistry.Core.ElementaryParticle import ElementaryParticle
from miniChemistry.Core.Substances.Particle import Particle

from miniChemistry.Core.Tools.ReactionPredictionTool.MolecularPredict import mechanism_dict as molecular_mechanism_dict
from miniChemistry.Core.Tools.ReactionPredictionTool.MolecularPredict import restriction_dict as molecular_restriction_dict
from miniChemistry.Core.Tools.ReactionPredictionTool.MolecularPredict import effective_class as molecular_effective_class
from miniChemistry.Core.Tools.ReactionPredictionTool.MolecularPredict import file as molecular_file

from miniChemistry.Core.Tools.ReactionPredictionTool.IonPredict import mechanism_dict as ionic_mechanism_dict
from miniChemistry.Core.Tools.ReactionPredictionTool.IonPredict import restriction_dict as ionic_restriction_dict
from miniChemistry.Core.Tools.ReactionPredictionTool.IonPredict import effective_class as ionic_effective_class
from miniChemistry.Core.Tools.ReactionPredictionTool.IonPredict import file as ionic_file


from typing import List, Dict, Any, Tuple, Literal, Callable
import csv



class RPT:
    MECHANISMS: Dict[str, Dict[str, Callable]] = {
        'molecular': molecular_mechanism_dict,
        'ionic': ionic_mechanism_dict
    }

    RESTRICTIONS: Dict[str, Dict[str, Callable]] = {
        'molecular': molecular_restriction_dict,
        'ionic': ionic_restriction_dict
    }

    CLASS_FUNCTIONS: Dict[str, Callable] = {
        'molecular': molecular_effective_class,
        'ionic': ionic_effective_class
    }


    def __init__(self,
                 algorithm: Literal['molecular', 'ionic']
                 ) -> None:

        match algorithm:
            case 'molecular':
                self._mr_file = str(molecular_file.path)
            case 'ionic':
                self._mr_file = str(ionic_file.path)
            case _:
                raise Exception(f'Wrong reaction prediction algorithm: {algorithm}.')

        self._mechanisms = RPT.MECHANISMS[algorithm]
        self._restrictions = RPT.RESTRICTIONS[algorithm]
        self._class_function = RPT.CLASS_FUNCTIONS[algorithm]

        self._list = self._read_file()
        self._decision_dict = self._get_decision_dict()


    def _read_file(self) -> List[str]:
        file = open(self._mr_file, 'r')
        reader = csv.reader(file)
        next(reader)
        l = list()

        for line in reader:
            l.append(line[0])

        return l


    def _get_decision_dict(self) -> Dict[Tuple[str, ...], Dict[str, Callable[..., Any]]]:
        dd = dict()

        for line in self._list:
            *classes, mechanism, restriction = line.split(';')

            signature = tuple( sorted( map(str.lower, classes) ) )
            mechanism_function = self._mechanisms[mechanism]
            restriction_function = self._restrictions[restriction]

            mr_dict = {
                'mechanism': mechanism_function,
                'restriction': restriction_function
            }

            dd.update({ signature : mr_dict })

        return dd


    def predict(self,
                *reagents: Particle | ElementaryParticle,
                ignore_restrictions: bool = False
                ):

        signature = list()

        for reagent in reagents:
            reagent_class = self._class_function(reagent)
            signature.append( reagent_class.lower() )

        signature = tuple( sorted(signature) )

        try:
            mechanism = self.decision_dict[signature]['mechanism']
            restriction = self.decision_dict[signature]['restriction']
        except KeyError:
            raise CannotPredictProducts(
                reagents=[r.formula() for r in reagents],
                function_name="RPT.predict",
                variables=locals()
            )

        products = mechanism(*reagents)
        no_proceed = restriction(*products, raise_exception=not ignore_restrictions)

        return products

    @property
    def decision_dict(self) -> Dict[Tuple[str, ...], Dict[str, Callable[..., Any]]]:
        return self._decision_dict
