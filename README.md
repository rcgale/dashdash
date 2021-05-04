# `dashdash`

I love using Python's [`argparse`](https://docs.python.org/3/library/argparse.html), but sometimes when I write a simple app, I find myself copy-pasting argument names and documentation. Using `dashdash`, you just write a function, and with a couple lines of additional code, the `argparse` work is done for you.

## Installation

```bash
pip install dashdash
```

## Basic Example

Here is a toy app we'll name `example.py`:
```python
import dashdash


@dashdash.register
def my_app(message, *, prefix="IMPORTANT MESSAGE: "):
    """
    This is an example of the basic usage of dashdash.
    :param message: A message to print.
    :param prefix: What to say before the message.
    :return:
    """
    print("{} {}".format(prefix, message))


if __name__ == '__main__':
    dashdash.run()
```

<br/>

The first parameter `message` is a positional argument, as it is in Python.
<pre style="font-weight: bold;">&gt; python example.py "Look behind you!"</pre>

```
IMPORTANT MESSAGE:  Look behind you!
```

<br/>

Since it came after a `*` in the function signature, the parameter `--prefix` is a named argument in both Python and `argparse`.

<pre style="font-weight: bold;">&gt; python example.py "Listen!" --prefix "Hey!"</pre>

```
Hey! Listen!
```

<br/>

Since `message` didn't have a default value in the function signature, it's required.

<pre style="font-weight: bold;">&gt; python example.py --prefix "Hey!"</pre>

```
usage: example.py [-h] [--prefix PREFIX] message
example.py: error: the following arguments are required: message
```

<br/>

The help menu uses the docstring (if available) to fill in descriptions.

<pre style="font-weight: bold;">&gt; python example.py --help</pre>
```
usage: example.py [-h] [--prefix PREFIX] message

This is an example of the basic usage of dashdash.

positional arguments:
  message          A positional argument, which is registered by
                   ArgumentParser as positional.

optional arguments:
  -h, --help       show this help message and exit
  --prefix PREFIX  Since the function signature has this arg after the *, it's
                   bound to `--prefix` (default: IMPORTANT MESSAGE: )

```

<br/>

## More Examples

### Specifying types

If you put a type annotation on your arguments, `dashdash` will provide those types to `argparse`.

```python
from typing import Tuple

import dashdash


@dashdash.register
def my_app(*numbers_to_sum: Tuple[int, ...], scale: float = 1.0):
    result = scale * sum(numbers_to_sum)
    print("Hmm, let's see... {}?".format(result))


if __name__ == '__main__':
    dashdash.run()

```

Then the incoming arguments for `numbers_to_sum` and `--scale` are cast as a tuple of `int` and a `float`, respectively.

<pre style="font-weight: bold;">&gt; python example.py 1 2 3 4 5 --scale 2</pre>

```
Hmm, let's see... 30.0?
```

<br/>


### Variable length positional arguments

If one of the positional arguments is marked as a packed tuple with the `*` operator, it's registered with `argparse` as `nargs='*'`.

```python
import dashdash


@dashdash.register
def my_app(*messages, prefix="IMPORTANT MESSAGE: "):
    for message in messages:
        print("{} {}".format(prefix, message))
    if len(messages) == 0:
        print("{} I've got nothing to say.".format(prefix))


if __name__ == '__main__':
    dashdash.run()

```

Run it with one argument

<pre style="font-weight: bold;">&gt; python example.py "Ho! Let's go!" --prefix "Hey!"</pre>

```
Hey! Ho! Let's go!
```

<br/>

Run it with two arguments

<pre style="font-weight: bold;">&gt;  python example.py "Now" "Now, Don't believe it's over." --prefix "Hey!"</pre>

```
Hey! Now
Hey! Now, Don't believe it's over.
```

<br/>


Run it with no arguments

<pre style="font-weight: bold;">&gt; python example.py --prefix "Hey!"</pre>

```
Hey! I've got nothing to say.
```

### *Required* variable length positional arguments

There's a generic type annotation called `Required`

```python
from typing import Tuple

import dashdash
from dashdash import Required


@dashdash.register
def my_app(*messages: Required[Tuple[str, ...]], prefix: Required):
    for message in messages:
        print("{} {}".format(prefix, message))
    if len(messages) == 0:
        print("{} I've got nothing to say.".format(prefix))


if __name__ == '__main__':
    dashdash.run()

```

Run it with no arguments and face the consequences 

<pre style="font-weight: bold;">&gt; python example.py</pre>

```
usage: example.py [-h] --prefix PREFIX messages [messages ...]
example.py: error: the following arguments are required: messages, --prefix
```

## Todo

- I figure if more than one function is registered in a given `.py` file, [subcommands](https://docs.python.org/3/library/argparse.html#sub-commands) would be a natural result. Haven't done it yet though.
- The variable length arguments could be `nargs={integer}` if the type annotation was a finite length, e.g. `Tuple[int, int, int]`. Not sure somebody would use that, but the current handling of `Tuple[int, ...]` casting is making some very narrow assumptions.
- PRs welcome!

## Dependencies

Only [`docstring-parser`](https://pypi.org/project/docstring-parser/), which has no dependencies of its own. Very nice package, thanks [Marcin Kurczewski](https://github.com/rr-)!