import pytest
from argparse import ArgumentParser, ArgumentError

from prettyparse import parse_args, Usage


class TestParser:
    def test_description(self):
        usage = 'This is the description'
        assert Usage(usage).desc == usage

    def test_newline(self):
        usage = '''
<line one>
<line two>
'''
        assert Usage(usage).desc == '<line one> <line two>'

    def test_indent(self):
        usage = '''
        <line one>
        <line two>
        '''
        assert Usage(usage).desc == '<line one> <line two>'

    def test_optional(self):
        usage = '''
        :-a --alpha str def_a
        :-b --beta int 6
        '''
        args = parse_args(usage, [])
        assert args.alpha == 'def_a'
        assert args.beta == 6
        args = parse_args(usage, ['-a', 'arg_a', '-b', '12'])
        assert args.alpha == 'arg_a'
        assert args.beta == 12

    def test_boolean(self):
        usage = '''
        :-a --alpha
        '''
        assert parse_args(usage, []).alpha is False
        assert parse_args(usage, ['-a']).alpha is True

    def test_required(self):
        usage = '''
        :alpha str
        :beta int
        '''
        args = parse_args(usage, ['hello', '14'])
        assert args.alpha == 'hello'
        assert args.beta == 14

    def test_all(self):
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
            'beta': dict(_0='-b', _1='--beta', type=str, help='<beta desc>. Default: beta_default',
                         default='beta_default'),
            'gamma': dict(_0='-g', _1='--gamma', help='<gamma desc>', action='store_true')
        }

    def test_add_to_parser(self):
        parser = ArgumentParser(description='desc')
        parser.add_argument('alpha')

        Usage(':beta int').apply(parser)

        args = parser.parse_args(['<alpha>', '32'])
        assert args.alpha == '<alpha>'
        assert args.beta == 32

    def test_extra(self):
        usage = '''
        <desc>
        ...
        '''
        assert Usage(usage).desc == '<desc>'

    def test_parser_error(self):
        with pytest.raises(ValueError):
            Usage(':without_type')

        with pytest.raises(ValueError):
            Usage(':pos str with_default_val')

        with pytest.raises(ValueError):
            Usage(':arg invalid_type')

        with pytest.raises(ValueError):
            Usage(':too int many args')

    def test_overlap(self):
        parser = ArgumentParser()
        Usage('''
            description
            :-a --alpha
            :-b --beta
        ''').apply(parser)
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
            Usage(':-a --alpha').apply(parser)
        Usage(':-g --gamma').apply(parser)

    def test_fuzzy_indent(self):
        Usage('''
          description
              :-a --alpha
            this is alpha
                description
            :-b --beta
        ''')

    def test_customizer(self):
        def modify_usage(parser):
            parser.usage = (parser.usage or '') + 'hello'

        parser = ArgumentParser()
        assert parser.usage is None
        usage = Usage()
        usage.add_customizer(modify_usage)
        usage.apply(parser)
        assert parser.usage == 'hello'

        def modify_usage_2(parser):
            parser.usage = (parser.usage or '') + ' hi'

        usage_2 = Usage()
        usage_2.add_customizer(modify_usage_2)
        usage |= usage_2
        parser = ArgumentParser()
        usage.apply(parser)
        assert parser.usage == 'hello hi'

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

    def test_renderers(self):
        usage = Usage('''
            desc 1
            :alpha str
            :beta str
        ''', alpha_beta=lambda args: args.alpha + args.beta)
        a = usage.parse(['aval', 'bval'])
        assert a.alpha == 'aval'
        assert a.beta == 'bval'
        assert a.alpha_beta == 'avalbval'
        usage |= Usage(betabeta=lambda args: args.beta * 2)
        assert usage.parse(['aval', 'bval']).betabeta == 'bvalbval'
