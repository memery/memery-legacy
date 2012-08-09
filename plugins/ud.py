
import common
import re

def help():
  return {'authors':     ['kqr'],
          'years':       ['2012'],
          'version':     '1.0',
          'description': 'Interface to UrbanDictionary.com via their main site. (APIs are for wussies.)',
          'argument':    '<term>'}

def run(nick, args):
  return "{0}: {1}".format(nick, search(args))

def search(args):
  url = "http://www.urbandictionary.com/define.php?term=" + common.quote(args)
  request = common.url_request(url)
  with common.urlopen(request) as s:
    content = s.read().decode('utf-8', 'replace')

  try:
    match = re.search(r'<div class="definition">(.+?)</div>.*?<div class="example">(.+?)</div>', content)
    definition = common.truncate(match.group(1), 200)
    example = common.truncate(match.group(2), 200)
    result = '{0} ("{1}") -- {2}'.format(definition, example, url)
  except AttributeError:
    result = "No hits. ({0})".format(url)

  return result


