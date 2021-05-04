import inspect
import sys
import unittest
from io import StringIO
from typing import Tuple

import dashdash
from dashdash import Required
from tests.helpers import test_app_context


class TestParser(unittest.TestCase):
    def test_no_args(self):
        with test_app_context(__file__):
            @dashdash.register
            def my_app():
                return True

            args, kwargs = dashdash.magic.parse_args_for_function(my_app, args=[])
            self.assertEqual(0, len(args))
            self.assertEqual(0, len(kwargs))

    def test_positional_arg_is_provided(self):
        with test_app_context(__file__):
            @dashdash.register
            def my_app(my_positional_arg):
                return "Got: {}".format(my_positional_arg)

            args, kwargs = dashdash.magic.parse_args_for_function(my_app, args=["positional value"])
            self.assertEqual(0, len(kwargs))
            self.assertEqual(args, ("positional value", ))

    def test_positional_arg_is_not_provided(self):
        with test_app_context(__file__):
            @dashdash.register
            def my_app(my_positional_arg):
                return "Got: {}".format(my_positional_arg)

            try:
                stash_stderr = sys.stderr
                temp_stderr = StringIO()
                sys.stderr = temp_stderr

                with self.assertRaises(SystemExit) as e:
                    args, kwargs = dashdash.magic.parse_args_for_function(my_app, args=[])

                output = temp_stderr.getvalue().strip()
                print(output)
                self.assertIn("the following arguments are required: my_positional_arg", output)
            finally:
                sys.stderr = stash_stderr

    def test_positional_arg_with_nargs_star(self):
        with test_app_context(__file__):
            @dashdash.register
            def my_app_1(first_arg, *multiarg, last_arg, keyword_arg_with_default="SOME_DEFAULT"):
                pass

            test_cases = [
                # POSITIONAL_OR_KEYWORD
                (my_app_1, "first_arg",
                 ("first_arg", {"help": ""})),

                # VAR_POSITIONAL
                (my_app_1, "multiarg",
                 ("multiarg", {"nargs": "*", "help": ""})),

                # KEYWORD_ONLY
                (my_app_1, "last_arg",
                 ("--last-arg", {"help": ""})),

                # KEYWORD_ONLY, WITH DEFAULT
                (my_app_1, "keyword_arg_with_default",
                 ("--keyword-arg-with-default", {"default": "SOME_DEFAULT", "help": ""})),
            ]

            for function, key, (*expect_args, expect_kwargs) in test_cases:
                with self.subTest((key, expect_args, expect_kwargs)):
                    signature = inspect.signature(function)
                    parameter = signature.parameters[key]
                    actual_args, actual_kwargs = dashdash.magic.build_parameter_args(key, parameter, param_docs={})
                    self.assertEqual(tuple(expect_args), tuple(actual_args))
                    self.assertEqual(expect_kwargs, actual_kwargs)

    def test_positional_arg_with_nargs_plus(self):
        with test_app_context(__file__):
            @dashdash.register
            def my_app_1(first_arg, *multiarg: Required[Tuple[str, ...]], last_arg, keyword_arg_with_default="SOME_DEFAULT"):
                pass

            test_cases = [
                # POSITIONAL_OR_KEYWORD
                (my_app_1, "first_arg",
                 ("first_arg", {"help": ""})),

                # VAR_POSITIONAL
                (my_app_1, "multiarg",
                 ("multiarg", {"nargs": "+", "help": "", "type": str})),

                # KEYWORD_ONLY
                (my_app_1, "last_arg",
                 ("--last-arg", {"help": ""})),

                # KEYWORD_ONLY, WITH DEFAULT
                (my_app_1, "keyword_arg_with_default",
                 ("--keyword-arg-with-default", {"default": "SOME_DEFAULT", "help": ""})),
            ]

            for function, key, (*expect_args, expect_kwargs) in test_cases:
                with self.subTest((key, expect_args, expect_kwargs)):
                    signature = inspect.signature(function)
                    parameter = signature.parameters[key]
                    actual_args, actual_kwargs = dashdash.magic.build_parameter_args(key, parameter, param_docs={})
                    self.assertEqual(tuple(expect_args), tuple(actual_args))
                    self.assertEqual(expect_kwargs, actual_kwargs)


    def test_multiargs_required(self):
        with test_app_context(__file__):
            @dashdash.register
            def my_app(*multiarg: Required[Tuple[str, ...]]):
                pass

            in_args = ("a", "b", "c")
            args, kwargs = dashdash.magic.parse_args_for_function(my_app, args=in_args)

            self.assertEqual(in_args, args)


    def test_build_parameter_args_with_required(self):
        with test_app_context(__file__):
            @dashdash.register
            def my_app_1(*var_length_required: Required[Tuple[str, ...]], named_required: Required):
                pass

            test_cases = [
                (my_app_1, "var_length_required",
                 ("var_length_required", {'nargs': '+', 'help': '', "type": str})),

                (my_app_1, "named_required",
                 ("--named-required", {"help": "", "required": True})),
            ]

            for function, key, (*expect_args, expect_kwargs) in test_cases:
                with self.subTest((key, expect_args, expect_kwargs)):
                    signature = inspect.signature(function)
                    parameter = signature.parameters[key]
                    actual_args, actual_kwargs = dashdash.magic.build_parameter_args(key, parameter, param_docs={})
                    self.assertEqual(tuple(expect_args), tuple(actual_args))
                    self.assertEqual(expect_kwargs, actual_kwargs)


    def test_named_required(self):
        with test_app_context(__file__):
            @dashdash.register
            def my_app(*, named_arg: Required):
                pass

            try:
                stash_stderr = sys.stderr
                temp_stderr = StringIO()
                sys.stderr = temp_stderr

                with self.assertRaises(SystemExit) as e:
                    args, kwargs = dashdash.magic.parse_args_for_function(my_app, args=[])

                output = temp_stderr.getvalue().strip()
                print(output)
                self.assertIn("the following arguments are required: --named-arg", output)
            finally:
                sys.stderr = stash_stderr


