import argparse
import functools
import inspect
import logging
import sys
import typing
from typing import Callable

import docstring_parser

_registry = set()


def register(function=None, *args, **kwargs):
    def wrapper(f):
        @functools.wraps(f)
        def decorator(*args, dashdash_args=None, **kwargs):
            if len(args) or len(kwargs):
                return f(*args, **kwargs)
            else:
                args, kwargs = parse_args_for_function(f, args=dashdash_args)
                return f(*args, **kwargs)

        if f.__globals__['__file__'] == sys.modules['__main__'].__file__:
            _registry.add(decorator)

        return decorator

    if function is not None and isinstance(function, Callable):
        # Optional parens on the decorator, in case we want to have options down the road
        return wrapper(function)
    else:
        return wrapper


def run(args=None):
    if len(_registry) == 1:
        main = _registry.pop()
        return main(dashdash_args=args)
    elif len(_registry) > 1:
        raise NotImplementedError("dashdash doesn't currently support multiple main functions")
    elif len(_registry) == 0:
        logging.warning("No functions registered as main.")


def parse_args_for_function(func, args=None):
    signature = inspect.signature(func)
    docstring = docstring_parser.parse(getattr(func, "__doc__", ""))
    param_docs = {p.arg_name: p for p in getattr(docstring, "params", [])}

    parser = argparse.ArgumentParser(
        description=getattr(docstring, "short_description"),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    positional_keys = []
    for key, parameter in signature.parameters.items():
        parameter_args, parameter_kwargs = build_parameter_args(key, parameter, param_docs)
        parser.add_argument(*parameter_args, **parameter_kwargs)

    parsed = parser.parse_args(args)

    args = []
    kwargs = {}
    for key, parameter in signature.parameters.items():
        if parameter.kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD
        ):
            args.append(getattr(parsed, key))
        elif parameter.kind in (inspect.Parameter.VAR_POSITIONAL, ):
            args.extend(getattr(parsed, key))
        else:
            kwargs[key] = getattr(parsed, key)

    return tuple(args), kwargs


def build_parameter_args(key, parameter, param_docs):
    parameter_args = []
    parameter_kwargs = {}

    if parameter.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.VAR_POSITIONAL,
    ):
        parameter_args.append(key)

    elif parameter.kind in (
            inspect.Parameter.KEYWORD_ONLY,
            inspect.Parameter.VAR_KEYWORD,
            # inspect.Parameter.POSITIONAL_OR_KEYWORD
    ):
        parameter_args.append("--{}".format(key.replace("_", "-")))

    if parameter.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
    ):
        if is_required(parameter):
            parameter_kwargs["nargs"] = "+"
        else:
            parameter_kwargs["nargs"] = "*"
    elif is_required(parameter):
        parameter_kwargs["required"] = True

    if parameter_is_optional(parameter):
        # e.g. `Optional[str]`
        parameter_kwargs["nargs"] = "?"

    if parameter.default is not inspect._empty:
        parameter_kwargs["default"] = parameter.default

    if parameter.annotation and parameter.annotation is not inspect._empty:
        cast_type = parameter.annotation
        if is_required(cast_type):
            required_args = getattr(parameter.annotation, "__args__", [])
            if required_args and len(required_args):
                cast_type = required_args[0]
            else:
                cast_type = None

        if cast_type:
            if parameter.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                cast_type_args = getattr(cast_type, "__args__", [])
                if len(cast_type_args) == 1 or len(cast_type_args) == 2 and Ellipsis in cast_type_args:
                    parameter_kwargs["type"] = cast_type_args[0]
            else:
                parameter_kwargs["type"] = cast_type


    parameter_kwargs["help"] = ""
    if key in param_docs and param_docs.get(key).description:
        param_doc: docstring_parser.DocstringParam = param_docs.get(key)
        parameter_kwargs["help"] = param_doc.description

    return tuple(parameter_args), parameter_kwargs


def parameter_is_optional(parameter):
    return type(None) in (getattr(parameter.annotation, "__args__", []) or [])


def is_required(t):
    t = getattr(t, "annotation", t)
    if getattr(t, "__qualname__", None) == "Required":
        return True
    elif getattr(t, "__origin__", None) == Required:
        return True
    return False


T = typing.TypeVar('T')


class Required(typing.Generic[T]):
    """
    Indicates to dashdash.register that a parameter is required, e.g.

    @dashdash.register
    def my_func(*variable_positional: Required[List[str]]):
        ...

    """
