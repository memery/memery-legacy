
import common
import re

def help():
  return {'authors':     ['kqr'],
          'years':       ['2012'],
          'version':     '1.0',
          'description': 'Interface to Wikipedia via mr3ds PHP.',
          'argument':    '<article name>'}

def run(nick, args):
  return "{0}".format(wikipedia(args)[3:])

def wikipedia(args):
  request = common.url_request("http://h4xxel.org/failboat/wikipedia.php?nick=n&args=" + common.quote(args))
  with common.urlopen(request) as s:
    content = s.read().decode('utf-8', 'replace')

  return content


