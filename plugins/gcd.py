
# author: ~kqr

def help():
  return {'authors':     ['kqr'],
          'years':       ['2012'],
          'version':     '1.0',
          'description': 'Calculates the greatest common divisor of two natural numbers.',
          'argument':    '<natural number> <natural number>'}

def run(nick, args):
  return "{0}: {1}".format(nick, gcd(args))

def gcd(args):
  try:
    a, b = [int(n) for n in args.split()]
  except ValueError:
    return "Specify two integers, space separated."

  return "GCD({0}, {1}) = {2}".format(a, b, euclids(a, b))

def euclids(a, b):
  rest = -1
  while rest != 0:
    rest = a - a/b * b
    a = b
    b = rest
  return a


