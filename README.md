# Prettyparse

[![PyPI version](https://img.shields.io/pypi/v/prettyparse.svg)](https://pypi.org/project/prettyparse/)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/cc0574a2e4c64f60bece2a6b1caa2b0f)](https://www.codacy.com/app/MatthewScholefield/prettyparse?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=MatthewScholefield/prettyparse&amp;utm_campaign=Badge_Grade)
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/matthewscholefield/prettyparse.svg)](https://github.com/MatthewScholefield/prettyparse/archive/master.zip)
[![License](https://img.shields.io/github/license/matthewscholefield/prettyparse.svg)](https://github.com/MatthewScholefield/prettyparse/blob/master/LICENSE)

*A clean, simple way to create Python argument parsers*

This module creates a Python [ArgumentParser][argparse] from a simple Python
usage string. The benefit of this is a much cleaner looking source code
that acts as a docstring at the top of the file. You can compare argparse
and prettyparse side by side [here][comparison].

[argparse]: https://docs.python.org/3.6/library/argparse.html
[comparison]: https://gist.github.com/MatthewScholefield/12839868f307f409118f1e6a554df973

### Example

script.py:

```Python
#!/usr/bin/env python3
from prettyparse import create_parser

usage = '''
    My program description
    
    :first_arg int
        This is the help message
        which can span multiple lines
    
    :-a --alpha str default_val
        This is an optional, positional argument
    
    :-n --number int 3
        This is a number. Any Python basic type is allowed
    
    :-b --beta-arg
        This creates a boolean option that is
        set to False by default
'''

args = create_parser(usage).parse_args()
print('First:', args.first_arg)
print('Alpha:', args.alpha)
print('Number:', args.number)
print('Beta:', args.beta_arg)

```

```bash
$ ./script.py 8 -b -n 32
First: 8
Alpha: default_val
Number: 32
Beta: True
```

## More Complex Arguments

If you need to use any of the other features of `ArgumentParser`,
you can create the parser with `create_parser` and then extra arguments
like you normally would.

### Example

```Python
from prettyparse import create_parser

usage = '''
    My program
    
    :file str
        Filename to use
    :-q --quiet
        Run program in quiet mode
    ...
'''

parser = create_parser(usage)
parser.add_argument('-v', '--version', action='version', version='0.1.0')
args = parser.parse_args()

```
The `...` is ignored by prettyparse and can optionally be used to indicate
there are more options than those listed in the usage string.
