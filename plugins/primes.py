
def help():
    return {'authors':     ['kqr'],
            'years':       ['2012'],
            'version':     '0.8',
            'description': 'Calculates prime factors.',
            'argument':    '<natural number n, where 2 < n < 100000>'} 

def run(nick, args):
    try:
        number = int(args)
        if number <= 2 or number > 99999:
            raise ValueError
    except ValueError:
        return "Argument must be an integer between 2 and not too high!"

    return "{}: {} = {}".format(nick, number, ' * '.join([str(f) for f in primes(number)]))

def primes(number):
    factors = []
    factor = 0

    while factor < number:
        factor = 2
        while number % factor != 0:
            factor += 1
        number /= factor
        yield factor


