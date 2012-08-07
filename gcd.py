

def help():
  raise NotImplementedError

def run(nick, args):
  return "{0}: {1}".format(nick, gcd(args))

def gcd(args):
  try:
    [a, b] = [int(n) for n in args.split()]
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


