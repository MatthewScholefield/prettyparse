from argparse import ArgumentParser, ArgumentError
import re

types = {
    'str': str,
    'int': int,
    'float': float,
    'bool': bool
}


def create_parser(usage):
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
    Returns:
        ArgumentParser: parser object created from the described string
    """
    parser = ArgumentParser()
    Usage(usage).apply(parser)
    return parser


def add_to_parser(parser, usage, ignore_existing=False):
    """
    Add arguments described in the usage string to the
    parser. View more details at the <create_parser> docs

    Args:
        parser (ArgumentParser): parser to add arguments to
        usage (str): Usage string in the format described above
        ignore_existing (bool): Ignore any arguments that have already been defined
    """
    Usage(usage).apply(parser, ignore_existing)


class Usage(object):
    def __init__(self, usage_string=''):
        """
        Create and parse a usage string
        Args:
            usage_string (str): Usage string to parse
        """
        self.desc = ''
        self.arguments = {}
        self.ingest(usage_string)

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
                            arg['type'] = types[arg['type']]
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

    def apply(self, parser, ignore_existing=False):
        """
        Write the usage to a parser
        Args:
            parser (ArgumentParser): Parser object to add arguments to
            ignore_existing (bool): Whether to ignore arguments that already exist in the parser
        """
        parser.description = (parser.description or self.desc) if ignore_existing else (self.desc or parser.description)
        for argument in self.arguments.values():
            argument = dict(argument)
            positional = [argument.pop(k) for k in sorted(argument) if k.startswith('_')]
            try:
                parser.add_argument(*positional, **argument)
            except ArgumentError:
                if not ignore_existing:
                    raise

    def __or__(self, other):
        """
        Operator for (self | other), with the left arg taking precedence
        Args:
            other (Usage): Right hand operator
        Returns:
            Usage: Combination of both usages
        """
        usage = Usage()
        usage.desc = self.desc or other.desc
        for k, v in other.arguments.items():
            usage.arguments[k] = dict(v)
        for k, v in self.arguments.items():
            usage.arguments[k] = dict(v)
        return usage
