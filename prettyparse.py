from itertools import chain

import re
from argparse import ArgumentParser
from argparse import Namespace
from collections import OrderedDict
from copy import deepcopy


def parse_args(usage, args=None, **renderers):
    """
    Creates an argument parser from a condensed usage string in the format of:

    This is the program description

    :pos_arg_name int
        This is the help message
        which can span multiple lines
    :-o --optional_arg str default_value
        The type can be any valid python type
    :-eo --extra-option
        This adds args.extra_option as a bool
        which is False by default

    Args:
        usage (str): Usage string in the format described above
        args (list): Optional list of arguments to send to parser. If not defined, taken from stdin
        renderers (dict): Functions of the form myval=lambda args: 'my_new_val'
    Returns:
        Namespace: args parsed from usage
    """
    return Usage(usage, **renderers).parse(args)


class Usage(object):
    types = {
        'str': str,
        'int': int,
        'float': float,
        'bool': bool
    }

    def __init__(self, usage_string='', **renderers):
        """
        Create and parse a usage string
        Args:
            usage_string (str): Usage string to parse
        """
        self.desc = ''
        self.arguments = OrderedDict()
        self.renderers = renderers
        self.customizers = []
        self.ingest(usage_string)

    def add_argument(self, _0, _1=None, **kwargs):
        """Add a custom argument that will be forwarded to ArgumentParser.add_argument"""
        arg = dict(kwargs, _0=_0)
        if _1 is not None:
            arg['_1'] = _1
        key = arg.get('_1', arg['_0']).replace('-', '_').strip('_')
        self.arguments[key] = arg

    def add_customizer(self, customizer):
        """
        Adds a function that receives the parser for modification
        Args:
            customizer (Callable): Function that receives an ArgumentParser
        """
        self.customizers.append(customizer)

    def ingest(self, usage_string):
        """
        Parse a usage string and apply it to the current usage object
        Args:
            usage_string (str): Usage string to parse
        """
        usage = usage_string
        usage = re.sub(r'^\s*...\s*$', '', usage, flags=re.MULTILINE)
        first_arg = last_arg = {}

        while usage:
            try:
                if usage.startswith('...'):
                    _, usage = (usage + '\n').split('\n', 1)
                    continue
                if usage.startswith(':'):
                    options, usage = (usage[1:] + '\n').split('\n', 1)
                    if options.count(' ') == 1:
                        if options[0] == '-':
                            short, long = options.split(' ')
                            arg = dict(_0=short, _1=long, action='store_true')
                        else:
                            short, typ = options.split(' ')
                            arg = dict(_0=short, type=typ)
                    else:
                        short, long, typ, default = options.split(' ')
                        default = '' if default == '-' else default
                        arg = dict(_0=short, _1=long, type=typ, default=default)

                    if 'type' in arg:
                        try:
                            arg['type'] = self.types[arg['type']]
                        except KeyError:
                            raise ValueError('No such type: {}'.format(arg['type']))
                    key = arg.get('_1', arg['_0']).replace('-', '_').strip('_')
                    self.arguments[key] = last_arg = arg
                else:
                    next_marker = usage.find(':') if ':' in usage else len(usage)
                    help = ' '.join([i for i in map(str.strip, usage[:next_marker].split('\n')) if i])
                    if 'default' in last_arg:
                        help += '. Default: ' + last_arg['default']
                    last_arg.update(help=help)
                    usage = usage[next_marker:].strip()
            except Exception as e:
                print(e.__class__.__name__ + ': ' + str(e))
                lines = usage_string.split('\n')
                line_id = 0
                chars_left = len(usage)
                for line_id in range(len(lines) - 1, -1, -1):
                    chars_left -= len(lines[line_id]) + 1
                    if chars_left < 0:
                        break
                print('While parsing line {}: {}'.format(line_id, lines[line_id]))
                print('From usage:\n{}'.format(usage_string))
                raise ValueError('Failed to create parser from usage string')

        self.desc = first_arg.get('help', self.desc)

    def apply(self, parser):
        parser.description = self.desc or parser.description
        for argument in self.arguments.values():
            argument = dict(argument)
            positional = [argument.pop(k) for k in sorted(argument) if k.startswith('_')]
            parser.add_argument(*positional, **argument)
        for i in self.customizers:
            i(parser)

    def render_args(self, args):
        args = deepcopy(args)
        for attribute, renderer in self.renderers.items():
            setattr(args, attribute, renderer(args))
        return args

    def parse(self, args=None):
        """
        Parse arguments from the usage
        """
        parser = ArgumentParser()
        self.apply(parser)
        return self.render_args(parser.parse_args(args))

    @staticmethod
    def _merge_args(a, b):
        merged = dict(b or a)
        if 'help' in b or 'help' in a:
            merged['help'] = b.get('help') or a.get('help')
        return merged

    def __or__(self, other):
        """
        Operator for (self | other),  with the left arg taking precedence
        Args:
            other (Usage): Right hand operator
        Returns:
            Usage: Combination of both usages
        """
        usage = Usage()
        usage.desc = self.desc or other.desc
        for k in chain(self.arguments, other.arguments):
            if k not in usage.arguments:
                usage.arguments[k] = self._merge_args(other.arguments.get(k, {}), self.arguments.get(k, {}))
        usage.renderers.update(other.renderers)
        usage.renderers.update(self.renderers)
        usage.customizers.extend(self.customizers)
        usage.customizers.extend(other.customizers)
        return usage
