
import common
import re

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
  str = re.sub(r'\\x3csup\\x3e(\d+)\\x3c/sup\\x3e\\x26#8260;\\x3csub\\x3e(\d+)\\x3c/sub\\x3e', r' och \1/\2', str)
  str = re.sub(r'\xa0', r' ', str)
  str = re.sub(r'\x3d', r'=', str)
  str = re.sub(r'\\x26#215;', r'×', str)
  str = re.sub(r'\\x3csup\\x3e', r'^(', str)
  str = re.sub(r'\\x3c/sup\\x3e', r')', str)
  return str

