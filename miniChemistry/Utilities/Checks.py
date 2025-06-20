from typing import Union, Dict, Any
from miniChemistry.Core.CoreExceptions.SubstanceExceptions import MultipleElementCation, ChargeError
from miniChemistry.Utilities.UtilityExceptions import *


def type_check(parameters: list, types: list, strict_order: bool = False, raise_exception: bool = False) -> bool:
    """
    To be used in any case when the decorator cannot be used. For example, if a function accepts *args and **kwargs,
    you cannot set the types, so you have to check them manually.

    :param parameters: list of parameters of a function.
    :param types: list of types that each parameter can be.
    :param strict_order: if True, then each parameter in "parameters" is matched to a type in "types" according to their
    position in a list (i.e. type_check([a, b, c, d], [str, int, str, int], strict_order=True) means that we check for
    type(a) == str, type(b) == int, type(c) == str, and type(d) == int. If strict_order=False, we check for
    isinstance(a, (str, int)), same for all other parameters.
    :param raise_exception: True if exception is to be raised if the test failed.
    :return: Boolean or exception indicating if the type check is passed.
    """

    if not strict_order:
        for p in parameters:
            if not isinstance(p, tuple(types)):
                if raise_exception:
                    raise TypeError(f'Parameter with value "{p}" has wrong type. Expected one of the '
                                    f'{types}, got {type(p)}.')
                else:
                    return False
        else:
            return True
    elif strict_order:
        for p, t in zip(parameters, types):
            if not isinstance(p, t):
                if raise_exception:
                    raise TypeError(f'Parameter with value "{p}" has wrong type. Expected one of the '
                                    f'{types}, got {type(p)}.')
                else:
                    return False
        else:
            return True


def keywords_check(keywords: Union[list, tuple], allowed_keywords: Union[list, tuple], function_name: str, variables: dict,
                   raise_exception: bool = True) -> bool:
    """
    Checks if the keywords passed to a function are within the allowed keywords.

    :param keywords: keywords to check. Usually **kwargs.
    :param allowed_keywords: A list or tuple of allowed keywords.
    :param function_name: Name of a function that called the keywords_check(). Used in exception calls.
    :param variables: locals() from the function that called the keywords_check().
    :param raise_exception: True if exception is to be raised if the test failed.
    :return:
    """

    keyword_difference = set(keywords).difference(set(allowed_keywords))

    if keyword_difference:  # if it is not empty
        if raise_exception:
            kna = KeywordNotAllowed(*keyword_difference, variables=variables, func_name=function_name)
            raise kna
        else:
            return False
    else:
        return True


def single_element_cation_check(composition: Dict[Any, int], charge: int, raise_exception: bool = False) -> bool:
    """
    Checks if a cation passed to a function contains one element. The function is used in Particle class to check ALL
    substances. Hence, we have if charge > 0: else: return True. This line ensures that if a particle checked is NOT
    a cation at all, the test is passed.

    :param composition: composition of a cation. Can be obtained from ion.composition.
    :param charge: charge of a cation.
    :param raise_exception: True if exception is to be raised if test failed.
    :return: boolean or exception on whether a particle passed is a single-element cation.
    """
    if charge > 0:
        if len(composition) > 1:
            if raise_exception:
                raise MultipleElementCation(composition, charge, variables=locals())
            else:
                return False
        else:
            return True
    else:
        return True



def charge_check(charge: Union[list, tuple], neutrality: bool, raise_exception: bool = True) -> bool:
    """
    Checks if the total charge passed to a function is (not) zero.

    :param charge: a list or tuple of integers that indicate charges.
    :param neutrality: True if charge must be equal to zero and False if not.
    :param raise_exception: True if exception is to be raised if the test is failed.
    :return: Boolean of exception describing if the charge is according to expectations ("neutrality" parameter).
    """

    if neutrality and sum(charge) == 0:
        return True
    elif not neutrality and not sum(charge) == 0:
        return True
    elif not raise_exception:
        return False
    else:
        raise ChargeError(sum(charge), neutrality)
