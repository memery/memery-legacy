import common
import re

def help():
  return {'authors':     ['kqr'],
          'years':       ['2012'],
          'version':     '1.0',
          'description': 'Interface to UrbanDictionary.com via their main site. (APIs are for wussies.)',
          'argument':    '<term>'}

def run(nick, args):
  return "{0}: {1}".format(nick, search(args, nick))

def search(args, nick):
  url = "http://www.urbandictionary.com/define.php?term=" + common.quote(args)
  content = common.read_url(url)

  match = re.search(r'<div class="definition">(.+?)</div>.*?<div class="example">(.+?)</div>', content)
  try:
    definition = match.group(1)
    example = match.group(2)
  except AttributeError:
    result = "No hits. ({0})".format(url)
  else:
    def fixhtml(str):
      str = re.sub(r'&amp;', r'&', str)
      str = re.sub(r'&quot;', r'"', str)
      str = re.sub(r'(<br ?/>)+', r' ', str)
      str = re.sub('\n', r' ', str)
      str = re.sub('\r', r' ', str)
      return re.sub(r'(<.+?>)+', r'', str)

    # magic constants used when calculating space_left:
    #   * 450 -- the smallest length of an irc message (hopefully; depends on server.)
    #   * 20  -- the longest channel name including # (hopefully; i have no idea)
    #   * 16  -- the length of the static crap in the result string (definitely)
    space_left = (450 - len('PRIVMSG  :') - 20 - len(nick + ': ') - len(url) - 16)

    definition = common.truncate(fixhtml(definition), int(space_left/2))
    example = common.truncate(fixhtml(example), int(space_left/2))
    result = '{0} (Example: {1}) -- {2}'.format(definition, example, url)

  return result


