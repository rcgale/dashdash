import typing
import unittest

import dashdash
from dashdash import Required
from tests.helpers import test_app_context


class TestRunIfMain(unittest.TestCase):

    def test_run_if_main_basic(self):
        with test_app_context(__file__):
            message = "Success!"

            @dashdash.register
            def my_app():
                return message

            return_message = dashdash.run()

            self.assertEqual(message, return_message)

    def test_run_if_main_optional_parens(self):
        with test_app_context(__file__):
            message = "Success!"

            @dashdash.register()
            def my_app():
                return message

            return_message = dashdash.run()

            self.assertEqual(message, return_message)

    def test_run_if_main_multiple_not_implemented(self):
        with test_app_context(__file__):
            message = "Success!"

            @dashdash.register
            def my_app():
                return message

            @dashdash.register
            def my_app_ii():
                return message

            with self.assertRaises(NotImplementedError):
                dashdash.run()

    def test_casting(self):
        with test_app_context(__file__):
            @dashdash.register
            def sum_app(*numbers_to_sum: typing.Tuple[int, ...]):
                """
                This is an example of the basic usage of dashdash.
                :param message: A message to print.
                :param prefix: What to say before the message.
                :return:
                """
                return sum(numbers_to_sum)

            total = dashdash.run(["1", "2", "3"])
            self.assertEqual(total, 6)

    def test_casting_required(self):
        with test_app_context(__file__):
            @dashdash.register
            def sum_app(*numbers_to_sum: Required[typing.Tuple[int, ...]]):
                """
                This is an example of the basic usage of dashdash.
                :param message: A message to print.
                :param prefix: What to say before the message.
                :return:
                """
                return sum(numbers_to_sum)

            total = dashdash.run(["1", "2", "3"])
            self.assertEqual(total, 6)
