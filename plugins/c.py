import codecs, re
import common

def help():
    return {'authors':     ['kqr', 'slaeshjag'],
            'years':       ['2012'],
            'version':     '1.0',
            'description': 'Interface till Google calc-API:et.',
            'argument':    '<uttryck>'}

def run(nick, args):
    return "{0}: {1}".format(nick, calc(args))

def calc(args):
    content = common.read_url("http://www.google.com/ig/calculator?h=en&q=", args)

    lhs = sanitise(re.search(r'lhs: "(.*?)"', content).group(1))
    rhs = sanitise(re.search(r'rhs: "(.*?)"', content).group(1))
    err = sanitise(re.search(r'error: "(.*?)"', content).group(1))

    if err:
        return "Ogiltigt uttryck enligt Google! (Felkod: {0})".format(err)
    else:
        return "{0} = {1}".format(lhs, rhs)


def sanitise(str):
    str = common.unescape_html(codecs.getdecoder('unicode_escape')(str)[0])
    # Note the special ⁄-char (not a regular slash) between </sup> and <sub>
    str = re.sub(r'<sup>(\d+)</sup>⁄<sub>(\d+)</sub>', r'and \1/\2', str)
    return str.replace('<sup>', '^(').replace('</sup>',')')

