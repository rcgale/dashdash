from typing import Tuple

import dashdash
from dashdash import Required


@dashdash.register
def my_app(*numbers_to_sum: Required[Tuple[int]], scale: float = 1.0):
    result = scale * sum(numbers_to_sum)
    print("Hmm, let's see... {}?".format(result))


if __name__ == '__main__':
    dashdash.run()