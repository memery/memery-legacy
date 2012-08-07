
import common
import re

# author: ~kqr and slaeshjag

def help():
  raise NotImplementedError

def run(nick, args):
  return "{0}: {1}".format(nick, calc(args))

def calc(args):
  request = common.url_request("http://www.google.com/ig/calculator?h=en&q=" + common.quote(args))
  with common.urlopen(request) as s:
    content = s.read().decode('utf-8', 'replace')

  lhs = sanitise(re.search(r'lhs: "(.*?)"', content).group(1))
  rhs = sanitise(re.search(r'rhs: "(.*?)"', content).group(1))
  err = sanitise(re.search(r'error: "(.*?)"', content).group(1))

  if err != "":
    return "Invalid expression by Google standards! ({0})".format(err)
  else:
    return "{0} = {1}".format(lhs, rhs)


def sanitise(str):
  str = re.sub(r'\xa0', r' ', str)
  str = re.sub(r'\\x3csup\\x3e(\d+)\\x3c/sup\\x3e\\x26#8260;\\x3csub\\x3e(\d+)\\x3c/sub\\x3e', r' and \1/\2', str)
  str = re.sub(r'\\x26#215;', r'×', str)
  str = re.sub(r'\\x3csup\\x3e', r'^(', str)
  str = re.sub(r'\\x3c/sup\\x3e', r')', str)
  return str

