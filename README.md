from os.path import join# Prettyparse

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
from prettyparse import parse_args

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

args = parse_args(usage)
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
from argparse import ArgumentParser
from prettyparse import Usage

usage = '''
    My program
    
    :file str
        Filename to use
    :-q --quiet
        Run program in quiet mode
    ...
'''

parser = ArgumentParser()
parser.add_argument('-v', '--version', action='version', version='0.1.0')
Usage(usage).apply(parser)
args = parser.parse_args()

```
The `...` is ignored by prettyparse and can optionally be used to indicate
there are more options than those listed in the usage string.

## Argument Merging

Suppose that you have two similar scripts. You can share a set of base arguments
as follows:

```python
from prettyparse import Usage
decoder_usage = Usage('''
    A script to decode foo data
    
    :foo_file str
        Input .foo file to decode
    :-q --quiet
        Don't output progress
''')
reencoder_usage = Usage('''
    A script to re-encode foo data
    
    :foo_file str
    :output_file str
        Ourput .foo file to write re-encoded data
    :-r --reencode-level float 0.1
        Level to reencode foo at
''') | decoder_usage
args = reencoder_usage.parse()
print(args.quiet, args.foo_file, args.output_file, args.reencode_level)
```

## Argument Renderers

Suppose you had an argument that you wanted to modify after it's been parsed.
You can do this like so:

```python
from prettyparse import Usage
from os.path import join

usage = Usage('''
    My program
    
    :root str
        Filename of root path
    :-s --src-subfolder
        Subfolder with source data
''', src_folder=lambda args: join(args.root, args.src_subfolder))

args = usage.parse()
print('Full path of source:', args.src_folder)
```

## Customizers

Suppose you wanted to do something very specific with the parser object
like modify the usage string. You could do this by adding a customizer which
is a function that receives and modifies the parser object. This happens after
arguments have been added but before any arguments are parsed:

```python
from prettyparse import Usage

def custom_usage(parser):
    """Adds '< input_data.txt' to a parser usage string"""
    parser.usage = parser.format_usage().strip().replace('usage: ', '') + ' < input_data.txt'

usage = Usage('My program that reads from stdin')
usage.add_customizer(custom_usage)
args = usage.parse()
```
