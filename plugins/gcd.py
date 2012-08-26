
def help():
    return {'authors':     ['kqr'],
            'years':       ['2012'],
            'version':     '1.0',
            'description': 'Calculates the greatest common divisor of two natural numbers.',
            'argument':    '<natural number> <natural number>'}

def run(nick, args):
    try:
        a, b = [int(n) for n in args.split()]
    except ValueError:
        return "Specify two integers, space separated."

    return "{}: GCD({}, {}) = {}".format(nick, a, b, gcd(a, b))

def gcd(a, b):
    rest = -1
    while rest != 0:
        rest = a - int(a/b) * b
        a = b
        b = rest
    return a


