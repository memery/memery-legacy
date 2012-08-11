
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
  content = common.read_url("http://www.google.com/pda/?q=", args)

  try:
    match = re.search(r'<div class="jd"><a class="p" href="(.+?)".*?>(.+?)</a>', content)
    link = match.group(1)
    title = re.sub(r'<.+?>', '', match.group(2))
    if link[:4] != "http":
      link = re.search(r'q=(http.+?)&amp;', link).group(1)
    result = "{0} -- {1}".format(title, link)
  except AttributeError:
    result = "No hits."

  return result


