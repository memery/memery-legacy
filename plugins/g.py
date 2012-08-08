
import common
import re

def help():
  return {'authors':     ['kqr'],
          'years':       ['2012'],
          'version':     '1.0',
          'description': 'Interface to Google via /pda search page and regexes. (APIs are for wussies.)',
          'argument':    '<google query>'}

def run(nick, args):
  return "{0}: {1}".format(nick, search(args))

def search(args):
  request = common.url_request("http://www.google.com/pda/?q=" + common.quote(args))
  with common.urlopen(request) as s:
    content = s.read().decode('utf-8', 'replace')

  result = re.search(r'<div class="jd"><a class="p" href="(.+?)"', content).group(1)

  return result


