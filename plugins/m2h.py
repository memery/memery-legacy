from math import floor
from decimal import Decimal

def help():
    return {'authors': ['jocke-l'],
            'years': ['2014'],
            'version': '1.1',
            'description': 'Minutes-to-hours converter',
            'argument': '<minutes>'}

def run(nick, args):
    try:
        return '{}: {}'.format(nick, m2h(args[0]))
    except IndexError:
        return '{}: too few arguments'

def m2h(m):
    def pluralise(amount, unit):
        return ('{} {}'.format(amount, unit + ('s' if amount > 1 else ''))
                if amount else '')

    def either(a, b):
        return a if a else b

    if not isinstance(m, Decimal):
        m = Decimal(m)

    hours, minutes = m // 60, m % 60

    return either(' and '.join(filter(bool, (pluralise(hours, 'hour'),
                                             pluralise(minutes, 'minute')))),
                  '^')
