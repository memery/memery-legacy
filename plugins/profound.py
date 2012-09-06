from urllib.error import HTTPError
import common
import re

def help():
    return {'authors':     ['nycz'],
            'years':       ['2012'],
            'version':     '1.0',
            'description': 'Skriver ut info om en viss Profound Programmer-bild.',
            'argument':    '<sökord>'}

def run(nick, args):
    url_re = re.compile(r'http://theprofoundprogrammer.com/post/\d+')

    if not args.strip():
        return '{}: skriv ett eller flera sökord'.format(nick)
    else:
        url = pp_search(args, url_re)
        if url and url_re.match(url):
            return pp_info(url, nick)
        else:
            return '{}: hittar ingen profoundprogrammer som passar din sökning! {}'.format(nick, url)

def pp_search(args, url_re):
    """
    Search google for a Profound Programmer page matching the args.
    Return the url.
    """
    searchterms = '{} site:theprofoundprogrammer.com/post/'.format(args)
    hits = common.read_json(common.read_url("http://ajax.googleapis.com/ajax/services/search/web?v=1.0&safe=off&q=", searchterms))['responseData']['results']
    
    if not hits:
        return None

    striphtml = lambda s: re.sub(r'<.+?>', '', re.sub(r'  +', '', s))
    return striphtml(hits[0]['url'])

def pp_info(url, nick):
    """ Return the transcript and link to the image of a Profound Programmer page. """
    try:
        data = common.read_url(url)
    except HTTPError:
        return '{}: kunde inte ladda sidan: {}'.format(nick, url)

    main_re = re.compile(r"""
        <li\ class="post\ photo">
        \s*
        <img\ src="(?P<img>.+?)"
        .+?
        <div\ class="caption"><p>
            \[(?P<transcript>.+?)\]
        </p>
        \s*
        (<p><a\ href="(?P<hdimg>.+?)">\[HD\ Version\]</a>)?
        """, re.DOTALL | re.VERBOSE)

    transcript_re = re.compile(r'text: (“(?P<title1>.+?)”|‘(?P<title2>.+?)’)?(, )?(?P<transcript>.+)', re.DOTALL)
    
    result = main_re.search(data)
    if not result:
        print(url)
        raise AttributeError('.profound could not match the regex! Has theprofoundprogrammer.org change format?')

    rawtranscript = transcript_re.match(common.unescape_html(sanitize(result.group('transcript'))))

    title = None
    if rawtranscript:
        for t in ('title1', 'title2'):
            if rawtranscript.group(t):
                title = rawtranscript.group(t)
        transcript = rawtranscript.group('transcript')
    else:
        transcript = common.unescape_html(result.group('transcript'))

    if result.group('hdimg'):
        image = result.group('hdimg')
    else:
        image = result.group('img')

    out = ['[{}]'.format(transcript)] + [image]
    if title:
        out = ['"{}"'.format(title)] + out

    return [common.truncate(x, 400) for x in out]

def sanitize(text):
    """ Remove irrelevant html tags and FIX IT """
    tags = '|'.join(('strong', 'em'))
    text = re.sub('</?({})>'.format(tags), '', text)
    text = text.replace('<sup>TM</sup>', '™')
    return text
