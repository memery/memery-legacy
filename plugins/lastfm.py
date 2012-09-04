
import common
from urllib.error import HTTPError
import xml.dom.minidom
import re

def help():
  return {'authors':     ['kqr'],
          'years':       ['2012'],
          'version':     '1.0',
          'description': 'Hämta det senaste spåret från någons last.fm-profil. Kräver en last.fm API-nyckel (placeras i lastfm-api-key i arbetskatalogen för boten.)',
          'argument':    '<last.fm-användarnamn>'}

def run(nick, args):
  return "{}: {}".format(nick, lastfm(args))

def lastfm(args):
  try:
    key = common.read_lineconf(common.read_file("lastfm-api-key"))[0]
    if not (len(key) == 32 and re.search(r'^[0-9a-f]+$', key)):
      raise IOError
  except (IOError, IndexError):
      raise IOError('Ingen nyckel för last.fm-API:et kunde hittas. Skapa filen lastfm-api-key med enbart nyckeln i sig i botens arbetskatalog.')

  try:
    content = common.read_url("http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&limit=1&api_key={0}&user={1}".format(key, common.quote(args)))
  except HTTPError:
    return "Kunde inte hitta en last.fm-användare med namnet {}.".format(args)


  dom = xml.dom.minidom.parseString(content)
  latesttrack = dom.getElementsByTagName('track')[0]
  artist = latesttrack.getElementsByTagName('artist')[0].childNodes[0].data
  title = latesttrack.getElementsByTagName('name')[0].childNodes[0].data

  returnstr = "{0}".format(args)
  if (latesttrack.hasAttribute("nowplaying")):
    playstatus = "spelar just nu"
  else:
    playstatus = "spelade senast"

  return "{0} {1} {2} ({3}) -- History: http://www.last.fm/user/{0}/tracks".format(args, playstatus, title, artist)



