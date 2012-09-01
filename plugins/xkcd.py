from urllib.error import HTTPError
import common
import re

def help():
    return {'authors':     ['nycz'],
            'years':       ['2012'],
            'version':     '1.0',
            'description': 'Skriver ut info om en viss xkcd-comic.',
            'argument':    '<nr> eller <sökord> eller <url>'}

def run(nick, args):
    number_re = re.compile(r'\s*(\d+)\s*')
    url_re = re.compile(r'\s*(http://xkcd\.com/\d+/)\s*')

    if not args.strip():
        return '{}: skriv ett nummer, sökord eller en url'.format(nick)
    elif number_re.match(args):
        return xkcd_info('http://xkcd.com/{}/'.format(number_re.match(args).group(1)), nick)
    elif url_re.match(args):
        return xkcd_info(url_re.match(args).group(1), nick)
    else:
        url = xkcd_search(args)
        if url and url_re.match(url):
            return xkcd_info(url, nick)
        else:
            return '{}: hittar ingen xkcd som passar din sökning!'.format(nick)

def xkcd_search(args):
    """
    Search google for an xkcd page matching the args.
    Return the url.
    """
    searchterms = '{} site:xkcd.com'.format(args)
    hits = common.read_json(common.read_url("http://ajax.googleapis.com/ajax/services/search/web?v=1.0&safe=off&q=", searchterms))['responseData']['results']
    
    if not hits:
        return None

    striphtml = lambda s: re.sub(r'<.+?>', '', re.sub(r'  +', '', s))
    return striphtml(hits[0]['url'])

def xkcd_info(url, nick):
    """ Return the transcript and title of an xkcd page. """
    try:
        data = common.read_url(url)
    except HTTPError:
        return '{}: kunde inte ladda sidan: {}'.format(nick, url)

    title_re = re.compile(r'<title>xkcd: (.+?)</div>')
    titlebackup_re = re.compile(r'<div id="ctitle">(.+?)</div>')
    transcript_re = re.compile(r'<div id="transcript" .+?>(?P<transcript>.*?)(\{\{(?P<alt>.+?)\}\})?</div>', re.DOTALL)
    
    # Transcript
    result = transcript_re.search(data)
    transcript = [line.strip() for line in result.group('transcript').splitlines() 
                  if line.strip()]

    if not transcript:
        transcript = ['Ingen beskrivning än!']

    # Unused for now - also borken if no transcript is available
    # alttext = result.group('alt').strip()

    # Title
    title = title_re.search(data)
    if not title:
        title = titlebackup_re.search(data)

    firstline = '{} – {}'.format(title.group(1), url)

    return [common.truncate(common.unescape_html(x), 400) for x in [firstline] + transcript[:3]]