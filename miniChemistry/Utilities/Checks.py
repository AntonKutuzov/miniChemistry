import inspect
from functools import wraps
from typing import Union, Dict, Any, Callable

from miniChemistry.Core.CoreExceptions.SubstanceExceptions import MultipleElementCation, ChargeError
from miniChemistry.Utilities.UtilityExceptions import *
from typeguard import check_type as tg_check_type
from typeguard import TypeCheckError
from miniChemistry.Utilities.UtilityExceptions import DecoratedTypeCheckError, TypeHintNotFound


TURN_OFF = False

def _count_arguments(func: Callable) -> Dict[str, inspect.Parameter.kind]:
    signature = inspect.signature(func)
    parameters = dict(signature.parameters)

    if 'self' in signature.parameters:
        parameters.pop('self')

    number_of_arguments = {
        'positional only': 0,
        'positional or keyword': 0,
        'variable positional': 0,
        'keyword only': 0,
        'variable keyword': 0
    }

    for parameter in parameters.values():
        if parameter.kind == parameter.POSITIONAL_ONLY:
            number_of_arguments['positional only'] += 1
        elif parameter.kind == parameter.POSITIONAL_OR_KEYWORD:
            number_of_arguments['positional or keyword'] += 1
        elif parameter.kind == parameter.VAR_POSITIONAL:
            number_of_arguments['variable positional'] += 1
        elif parameter.kind == parameter.KEYWORD_ONLY:
            number_of_arguments['keyword only'] += 1
        elif parameter.kind == parameter.VAR_KEYWORD:
            number_of_arguments['variable keyword'] += 1
        else:
            raise Exception('How did it even happen? Did you find the sixth argument type?')

    return  number_of_arguments


def _match_typing(func, *args, **kwargs):
    annotations = func.__annotations__.copy()
    number_of_arguments = _count_arguments(func)
    number_of_args = (number_of_arguments['positional only'] + number_of_arguments['positional or keyword'] +
                      number_of_arguments['variable positional'])
    try:
        annotations.pop('return')
    except KeyError:
        raise TypeHintNotFound(func_name=func.__name__, hint_type='return', variables=locals())

    arg_list = list()  # this basically replaces a dictionary for us
    type_list = list()

    arg_counter = 0
    for arg, i, name, annotation in zip(args, range(number_of_args), annotations.keys(), annotations.values()):
        arg_list.append(arg)
        type_list.append(annotation)
        arg_counter += 1

    if arg_counter != len(args):
        last_type = type_list[-1]
        for arg in args[arg_counter:]:
            arg_list.append(arg)
            type_list.append(last_type)

    default_kwarg_type = annotations.get('kwargs')
    if default_kwarg_type is None and 'kwargs' in func.__annotations__:
        raise TypeHintNotFound(func_name=func.__name__, hint_type='parameter', variables=locals())
    else:
        default_kwarg_type = Any

    for kwarg in kwargs:
        ann_type = annotations.get(kwarg)
        if ann_type is not None:
            arg_list.append(kwarg)
            type_list.append(ann_type)
        else:
            arg_list.append(kwarg)
            type_list.append(default_kwarg_type)

    return arg_list, type_list


def type_check_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if TURN_OFF:
            return func(*args, **kwargs)

        signature = inspect.signature(func)

        # getting rid of 'self' if it is present
        new_args = list(args).copy()
        if 'self' in signature.parameters:
            index = list(signature.parameters.keys()).index('self')
            new_args.pop(index)

        # matching each argument to parameter's type
        arguments, correct_types = _match_typing(func, *new_args, **kwargs)
        # print('correct types', correct_types)

        # print(func, correct_types, new_args, kwargs)
        # checking each argument. Look for what _match_typing returns. Positional arguments are returned by their value, keyword arguments by key
        for argument, annotation in zip(arguments, correct_types):
            if argument in new_args:
                try:
                    tg_check_type(argument, annotation)
                except TypeCheckError:
                    raise DecoratedTypeCheckError(function_name=func.__name__,
                                                  parameter_type='positional',
                                                  parameter_name_or_value=f'{argument}',
                                                  expected_type=annotation,
                                                  received_type=type(argument),
                                                  variables=locals())
            elif argument in kwargs:
                try:
                    tg_check_type(kwargs[argument], annotation)
                except TypeCheckError:
                    raise DecoratedTypeCheckError(function_name=func.__name__,
                                                  parameter_type='keyword',
                                                  parameter_name_or_value=argument,
                                                  expected_type=annotation,
                                                  received_type=type(kwargs[argument]),
                                                  variables=locals())
            else:
                raise Exception(f'How did you get here? {argument, annotation}')

        result = func(*args, **kwargs)

        try:
            return_type = func.__annotations__['return']
            tg_check_type(result, return_type)
        except TypeCheckError:
            raise DecoratedTypeCheckError(function_name=func.__name__,
                                          parameter_type='return',
                                          parameter_name_or_value='return',
                                          expected_type=signature.return_annotation,
                                          received_type=type(result),
                                          variables=locals())

        return result
    return wrapper


@type_check_decorator
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

@type_check_decorator
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

@type_check_decorator
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
                raise MultipleElementCation(f'Only single-element cations are supported in the current version.',
                                            variables=locals())
            else:
                return False
        else:
            return True
    else:
        return True


@type_check_decorator
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
