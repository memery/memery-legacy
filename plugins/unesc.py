import html.parser
import urllib.parse

def help():
    return { 'authors':     ['jocke-l'],
             'years':       ['2013'],
             'version':     '1.0',
             'description': 'Utility to unescape escaped characters.',
             'argument':    '<escaped> | <type>' }

def run(nick, args):
    return '{}: {}'.format(nick, unescape(args))

def unescape(args):
    try: escaped, escape_type = args.split(' | ')
    except ValueError:
        return 'Syntax Error'

    try:
        return {'html': html.parser.HTMLParser().unescape(escaped),
                'url':  urllib.parse.unquote(escaped, encoding='utf-8')}[escape_type]
    except KeyError:
        return 'Type: {} is not supported'.format(escape_type)
