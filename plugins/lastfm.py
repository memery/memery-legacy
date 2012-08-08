
import common
import xml.dom.minidom
import re

def help():
  return {'authors':     ['kqr'],
          'years':       ['2012'],
          'version':     '1.0',
          'description': 'Get the last track from someones last.fm. Requires a last.fm API key! (Place key in lastfm-api-key in the working directory of the bot.)',
          'argument':    '<last.fm user name>'}

def run(nick, args):
  return "{0}".format(lastfm(args))

def lastfm(args):
  try:
    key = common.read_file("lastfm-api-key")[0]
    if not (len(key) == 32 and re.search(r'^[0-9a-f]+$', key)):
      raise IOError
  except IOError:
    raise IOError('No key for last.fm API found. Create file lastfm-api-key with only the key in it in the working directory of the bot.')

  request = common.url_request("http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&limit=1&api_key={1}&user={0}".format(common.quote(args), key))
  with common.urlopen(request) as s:
    content = s.read().decode('utf-8', 'replace')

  dom = xml.dom.minidom.parseString(content)
  latesttrack = dom.getElementsByTagName('track')[0]
  artist = latesttrack.getElementsByTagName('artist')[0].childNodes[0].data
  title = latesttrack.getElementsByTagName('name')[0].childNodes[0].data

  returnstr = "{0}".format(args)
  if (latesttrack.hasAttribute("nowplaying")):
    playstatus = "is now playing"
  else:
    playstatus = "last played"

  return "{0} {1} {2} ({3}) -- http://www.last.fm/user/{0}/tracks".format(args, playstatus, title, artist)



