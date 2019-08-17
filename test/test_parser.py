import sys

from prettyparse.prettyparse import Usage

sys.path += ['.']  # noqa

import pytest
from argparse import ArgumentParser, ArgumentError
from prettyparse import create_parser, add_to_parser


class TestParser:
    def test_description(self):
        usage = 'This is the description'
        assert create_parser(usage).description == usage

    def test_newline(self):
        usage = '''
<line one>
<line two>
'''
        assert create_parser(usage).description == '<line one> <line two>'

    def test_indent(self):
        usage = '''
        <line one>
        <line two>
        '''
        assert create_parser(usage).description == '<line one> <line two>'

    def test_optional(self):
        usage = '''
        :-a --alpha str def_a
        :-b --beta int 6
        '''
        parser = create_parser(usage)
        args = parser.parse_args([])
        assert args.alpha == 'def_a'
        assert args.beta == 6
        args = parser.parse_args(['-a', 'arg_a', '-b', '12'])
        assert args.alpha == 'arg_a'
        assert args.beta == 12

    def test_boolean(self):
        usage = '''
        :-a --alpha
        '''
        parser = create_parser(usage)
        assert parser.parse_args([]).alpha == False
        assert parser.parse_args(['-a']).alpha == True

    def test_required(self):
        usage = '''
        :alpha str
        :beta int
        '''
        parser = create_parser(usage)
        args = parser.parse_args(['hello', '14'])
        assert args.alpha == 'hello'
        assert args.beta == 14

    def test_all(self):
        """Best we can do is verify no parsing exception is thrown"""
        usage = '''
        <description line 1>
        <description line 2>
        
        :alpha int
            <alpha help line 1>
            <alpha help line 2>
        :-b --beta str beta_default
            <beta desc>
        :-g --gamma
            <gamma desc>
        '''
        usage = Usage(usage)
        assert len(usage.arguments) == 3
        assert usage.desc == '<description line 1> <description line 2>'
        assert usage.arguments == {
            'alpha': dict(_0='alpha', type=int, help='<alpha help line 1> <alpha help line 2>'),
            'beta': dict(_0='-b', _1='--beta', type=str, help='<beta desc>. Default: beta_default', default='beta_default'),
            'gamma': dict(_0='-g', _1='--gamma', help='<gamma desc>', action='store_true')
        }

    def test_add_to_parser(self):
        parser = ArgumentParser(description='desc')
        parser.add_argument('alpha')

        add_to_parser(parser, ':beta int')

        args = parser.parse_args(['<alpha>', '32'])
        assert args.alpha == '<alpha>'
        assert args.beta == 32

    def test_extra(self):
        usage = '''
        <desc>
        ...
        '''
        assert create_parser(usage).description == '<desc>'

    def test_parser_error(self):
        with pytest.raises(ValueError):
            create_parser(':without_type')

        with pytest.raises(ValueError):
            create_parser(':pos str with_default_val')

        with pytest.raises(ValueError):
            create_parser(':arg invalid_type')

        with pytest.raises(ValueError):
            create_parser(':too int many args')

    def test_overlap(self):
        parser = create_parser('''
            description
            :-a --alpha
            :-b --beta
        ''')
        usage = Usage('''
                description
                :-a --alpha
                    desc 1
                :-a --alpha
                    desc 2
            ''')
        assert len(usage.arguments) == 1
        assert usage.arguments['alpha']['help'] == 'desc 2'
        with pytest.raises(ArgumentError):
            add_to_parser(parser, ':-a --alpha')
        add_to_parser(parser, 'new_desc\n:-a --alpha', True)
        assert parser.description == 'description'
        add_to_parser(parser, ':-g --gamma')

    def test_fuzzy_indent(self):
        Usage('''
          description
              :-a --alpha
            this is alpha
                description
            :-b --beta
        ''')

    def test_or(self):
        usage = Usage('''
            desc 1
            :-a --alpha
                alpha 1
            :-b --beta
        ''') | Usage('''
            desc 2
            :-a --alpha
                alpha 2
            :-g --gamma
        ''')
        assert set(usage.arguments) == {'alpha', 'beta', 'gamma'}
        assert usage.desc == 'desc 1'
        assert usage.arguments['alpha']['help'] == 'alpha 1'
