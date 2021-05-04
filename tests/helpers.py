import contextlib
import sys
from unittest.mock import patch

import dashdash


@contextlib.contextmanager
def test_app_context(context_file, args=None):
    try:
        stashed_registry = dashdash.magic._registry
        dashdash.magic._registry = set()

        stashed_argv = sys.argv
        sys.argv = [context_file]
        if args is not None:
            sys.argv.append(*args)

        with patch.object(sys.modules['__main__'], "__file__", context_file):
            yield
    finally:
        dashdash.magic._registry = stashed_registry
        sys.argv = stashed_argv
