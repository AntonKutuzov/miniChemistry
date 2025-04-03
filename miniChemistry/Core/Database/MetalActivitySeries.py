"""
BACKGROUND FROM CHEMISTRY
The metal activity series is a real series (i.e. it really is used in school chemistry) that shows metal activity
relative to hydrogen. It originates from the row of electric potentials, but that's not important right now. Instead,
there are some other empirical rules detected by the author of this package that are quite rough, but they are quite
enough for purposes of miniChemistry module.

The metal activity series looks literally like a series of metals (represented by their symbols), for example, a very
short version of the series will look like this

K Na Ca Al Zn Cr Fe Ni H Cu Ag Au
(in the order of decreasing activity, i.e. K is the most active, and Au is the least)

As you can see, there are two important things to mention. First, way not all metals are present in the series, and in
this package this is a problem as it does not restrict the user to several most well-known (in school) metals. Second,
in the METAL activity series, there is a hydrogen, which is not a metal (you can check it in 'ptable.py' if you want).

The answer/solution to these problems are the following:
1) The class MetalActivitySeries has a method called estimate() which estimates activity of a given metal by comparing
the metal passed as a parameter to the metals inside the series (although this seems like a loop, it is not. This
function uses the patterns found by the author. More on them in the function's description).
2) As you may know from school chemistry, (or as you could have guessed from the beginning of this text), hydrogen
is present in the series to see whether a metal is more active than hydrogen or less active. This becomes very
important when writing chemical reactions of metals and acids, as in these reactions metal always (tends to) replace
hydrogen inside an acid. Hence, if the metal is more active than hydrogen, it can replace it in the acid, if it is not,
then it can't. Moreover, more active metals will replace less active metals in salts. However, this is already basics of
school chemistry, so we won't go deep into them here.


IMPLEMENTATION
The MetalActivitySeries is implemented as a class, containing the series and providing some methods for work with it.
The most important application of the series, as you could have guessed, is comparing activity of different methods to
predict outcomes of chemical reactions. Thus, the class has a method called

compare(el1: pt.Element, el2: pt.Element, return_active: bool = True) -> pt.Element

It takes two elements (they must be metals) and returns either of them depending on the "return_active" parameter's
value. The other two methods are just a pre-set compare() method, namely

more_active(el1: pt.Element, el2: pt.Element) -> pt.Element     (return_active = True)
more_inert(el1: pt.Element, el2: pt.Element) -> pt.Element      (return_active = False)

Both return respective element.

The class also has a method that returns activity itself as a string, which is one of the four given below
1) active
2) middle active
3) inactive
4) unknown

activity(element: pt.Element) -> str

The class also has a method called estimate(element: pt.Element) -> pt.Element

which estimates activity of a metal that is not in the series by returning an element that IS present in the series
(may be needed if two metals are compared to each other, and one or both are not in the series). The details of the
decision-making mechanism is given in the description of the method.

All the other methods are explain in the class description.
"""


from miniChemistry.Core.CoreExceptions.CompatibilityTableExceptions import ElementIsNotMetal, UnknownActivityMetal
from miniChemistry.MiniChemistryException import NotSupposedToHappen

from typing import Tuple, Union, List
from miniChemistry.Core.Substances import Simple
from miniChemistry.Utilities.File import File
import miniChemistry.Core.Database.ptable as pt


class MetalActivitySeries:
    """
    MetalActivitySeries models a series of metals as explained above, and has the following methods

    PUBLIC METHODS
    estimate(element: pt.Element) -> pt.Element
    compare(el1: pt.Element, el2: pt.Element, return_active: bool = True) -> pt.Element
    more_active(el1: pt.Element, el2: pt.Element) -> pt.Element
    more_inert(el1: pt.Element, el2: pt.Element) -> pt.Element
    activity(element: pt.Element) -> str

    NOTE: all public methods use _is_metal() to check is the metal passed in a metallic element.

    PROPERTIES
    simples -> Tuple[Simple, ...]
    elements -> Tuple[pt.Element, ...]

    PRIVATE METHODS
    _convert_to_metals() -> List[Simple]
    _is_metal(element: pt.Element, raise_exception: bool = True) -> bool
    _index(element: Union[pt.Element, Simple] -> int
    _estimate_by_ren(element: pt.Element, among: Union[Tuple[pt.Element, ...], None] -> pt.Element
    """


    def __init__(self):
        """Loads the metal activity series from a txt file and converts strings to instances of Simple"""
        self._file = File(__file__)
        self._file.bind('MetalActivitySeries')
        self._metals = self._convert_to_metals()


    def __getitem__(self, item):
        return self.elements[item]

    def __iter__(self):
        return self.elements.__iter__()


    
    def _convert_to_metals(self) -> List[Simple]:
        """
        Takes in data obtained directly from the txt file ("MetalActivitySeries") and converts them into
        instances of Simple.

        :return: List of instances of Simple (representing metals in the order of decreasing activity)
        """

        simples = list()

        for metal in self._file.read_all():
            sub = Simple.from_string(metal)
            simples.append(sub)

        return simples


    @staticmethod
    
    def _is_metal(element: pt.Element, raise_exception: bool = True, include_hydrogen: bool = True) -> bool:
        """
        Is a test to check if an element is a metal. If yes, returns True, if no, either returns False or raises
        an exception.

        :param element: the element to be checked
        :param raise_exception: True if exception is to be raised if the element is not a metal
        :param include_hydrogen: True if hydrogen should not cause exception
        :return: (boolean) True if element in a metal, else False or exception raised
        """

        if element in pt.METALS:
            return True
        elif element == pt.H and include_hydrogen:
            return True
        elif raise_exception:
            raise ElementIsNotMetal(element=element.symbol, variables=locals())
        else:
            return False


    
    def _index(self, element: Union[pt.Element, Simple]) -> int:
        """
        Since metal activity series is short enough, it can easily be stored as a usual Python list. That means,
        since metals are ordered by their activity (by definition of the series), their index in the series can be
        used to estimate their activity (mainly for comparison). If we want to go scientific, we can call it
        "effective activity".

        This method returns the index of an element in the series.

        :param element: Instance of Simple or pt.Element
        :return: index of the element in the metal activity series (starting from zero for the most active one)
        """

        if isinstance(element, pt.Element):
            return self.elements.index(element)
        elif isinstance(element, Simple):
            return self.simples.index(element)
        else:
            nsth = NotSupposedToHappen(variables=locals())
            nsth.description += (f'\n\nIf you see this error, that means there is a problem with the type_check_decorator\n'
                                 f'as it should have prevented you from using wrong data type.')
            raise nsth


    
    def _estimate_by_ren(self, element: pt.Element, among: Union[Tuple[pt.Element, ...], None] = None) -> pt.Element:
        """
        The method is used in the estimate() method to estimate metal's activity based on its relative
        electronegativity (further – just "ren" or "REN", because typing this every time is too hard).

        MECHANISM
        The author of the package noted that from the most active metals up to (not including) the inactive ones,
        activity of a metal strongly correlates with its REN. Moreover, all the exceptions (not the inactive metals)
        can be easily explained. Thus, the method looks at the REN of the parameter's element and returns the element
        from the series that has the closest REN to it.

        NOTE: this method does not account for exceptions, this is done in the estimate() method.

        :param element: element whose alternative from the series has to be predicted based on its REN
        :param among: a group of metals in which the estimation must be searched for. The series is a default value.
        :return: an element from the series with the value of REN closest to the REN of the element.
        """

        if among is None:
            among = self.elements

        closest_element = among[0]

        for candidate in among:
            if abs(candidate.ren - element.ren) < abs(closest_element.ren - element.ren):
                closest_element = candidate

        return closest_element


    
    def estimate(self, element: pt.Element) -> pt.Element:
        """
        Estimates activity of an element by comparing its properties to the properties of the elements in the series.
        The logic for the choice is the following: the active metals generally obey the correlation between REN and
        activity, however there are two exceptions that fit well into an assumption that in this group of metals also
        the number of electrons (on the outer shell) plays significant role. Thus, to account for this, the analogies
        for passed metals are chosen only from the group the metals belongs to.

        For the middle active metals the rule with REN works without exceptions (or at least the author didn't see them),
        which is enough for this package. The only problems begin at the very end of middle active section, where
        inactive metals start.

        For inactive metals there's no one significant correlation between any property and activity, and thus (also
        knowing that inactive metals don't react much, which means we don't care about their activity so much) the
        algorithm is just returning the closest metal present in the table: for groups 1B and 2B the method returns
        silver (Ag), for group 8B – platinum (Pt), for anything else – tungsten (W).

        NOTE: to get more you can always print all the elements in the series together with their REN values.

        :param element: elements whose activity must be estimated
        :return: element whose activity is the closest to the parameter's element
        """


        self._is_metal(element, raise_exception=True, include_hydrogen=False)
        activity = self.activity(element)

        match activity:
            case 'active':
                if element.group == '1A':
                    els = set(self.elements).intersection(pt.groups.FIRST_A)
                elif element.group == '2A':
                    els = set(self.elements).intersection(pt.groups.SECOND_A)
                else:
                    raise NotSupposedToHappen(variables=locals())
                return self._estimate_by_ren(element, among=tuple(els))

            case 'middle active':
                return self._estimate_by_ren(element)

            case 'inactive':
                if element.group == '8B':
                    return pt.Pt
                elif element.group[0] in {'1', '2'}:
                    return pt.Ag
                else:
                    return pt.W

            case 'unknown':
                raise UnknownActivityMetal(element=element.symbol, variables=locals())


    
    def compare(self, el1: pt.Element, el2: pt.Element, return_active: bool = True) -> pt.Element:
        """

        :param el1:
        :param el2:
        :param return_active:
        :return:
        """

        self._is_metal(el1, raise_exception=True, include_hydrogen=True)  # because we can compare to it
        self._is_metal(el2, raise_exception=True, include_hydrogen=True)

        if el1 not in self:
            avatar1 = self.estimate(el1)
        else:
            avatar1 = el1

        if el2 not in self:
            avatar2 = self.estimate(el2)
        else:
            avatar2 = el2

        i1 = self._index(avatar1)
        i2 = self._index(avatar2)

        max_i = max([i1, i2])

        if return_active:
            return el1 if max_i == i1 else el2
        else:
            return el2 if max_i == i1 else el1


    def more_active(self, el1: pt.Element, el2: pt.Element) -> pt.Element:
        """Returns more active metal of the two."""
        return self.compare(el1, el2, return_active=True)


    def more_inert(self, el1: pt.Element, el2: pt.Element) -> pt.Element:
        """Returns less active (more inert) metal of the two."""
        return self.compare(el1, el2, return_active=False)


    
    def activity(self, element: pt.Element) -> str:
        """
        Returns activity of a metal as a string. Four possible values can be returned: "active", "middle active",
        "inactive" and in some cases "unknown" (mostly for too heavy elements).

        The following empirical rules (derived from the series) are imposed for the classification:
        ACTIVE METALS – the first two A groups
        MIDDLE ACTIVE METALS – Either metals of group B with REN < 1.90 (REN of copper, the least REN inactive metals, is 1.90)
        OR
        Metals of groups 3 to 8A (in fact, not 8, because there are no metals)
        OR
        Nickel, and hydrogen, which just do not fit in any rules
        INACTIVE METALS – metals of groups B with REN more than 1.90

        :param element: metals whose activity to be evaluated
        :return: string with activity one of the four: "active", "middle active", "inactive", "unknown"
        """

        self._is_metal(element, raise_exception=True, include_hydrogen=True)
        letter = element.group[1]
        period = element.period
        group = int(element.group[0])
        ren = element.ren

        active_if = [letter == 'A', group <= 2]
        middle_active_if = [(letter == 'B', ren < 1.90), (letter == 'A', group > 2), (element == pt.Ni, pt.H)]
        inactive_if = [letter == 'B', ren >= 1.90]

        if element.atomic_number >= 104:
            return 'unknown'
        elif all(active_if):
            return 'active'
        elif any([all(conditions) for conditions in middle_active_if]):
            return 'middle active'
        elif all(inactive_if):
            return 'inactive'
        else:
            NotSupposedToHappen(variables=locals())


    @property
    def simples(self) -> Tuple[Simple, ...]:
        return tuple(self._metals)


    @property
    def elements(self) -> Tuple[pt.Element, ...]:
        return tuple([metal.element for metal in self._metals])
