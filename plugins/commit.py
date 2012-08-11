
import common
import re

def help():
  return {'authors':     ['kqr'],
          'years':       ['2012'],
          'version':     '1.0',
          'description': 'Generates bad commit messages via http://whatthecommit.com/.',
          'argument':    ''}

def run(nick, args):
  return "Don't know what to write in your commit message? Why not: \"{0}\"".format(commit())

def commit():
  request = common.url_request("http://whatthecommit.com")
  with common.urlopen(request) as s:
    content = s.read().decode('utf-8', 'replace')

  print(content)
  message = re.search(r'<p>(.+?)\n', content).group(1)
  return message


