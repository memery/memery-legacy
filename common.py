import json, os.path, re, traceback
from urllib.parse import quote
from urllib.request import Request, urlopen
from html.parser import HTMLParser

def safeprint(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode(errors='replace'))

def log(text):
    # TODO: not this
    safeprint(text)

def error_info(desc, error):
    """ 
    Return a useful string containing info about the current exception.
    This should always be used when handling the exception yourself instead
    of letting irc.py do it. Without this, no line numbers!

    desc is a short description of what it was that just crashed
    error is the exception that was catched
    """
    exception_re = re.compile(r'File "(.+?)", line (\d+), (.+?)(\n|$)')
    try:
        stacktrace = traceback.format_exc()
        chunks = exception_re.findall(stacktrace)
        # This does not seem to work
        # errortype = stacktrace.split('\n')[-2]
    except:
        tb = '[bad/no stacktrace]'
    else:
        if chunks:
            # [example]:   file.py:38 in lolfunction
            tb = '{}:{} {}'.format(os.path.basename(chunks[-1][0]),
                                   chunks[-1][1], chunks[-1][2])
    errortype = str(type(error))[8:-2]
    args = (desc, errortype, error, tb)
    return '{}: [{}] {} - {}'.format(*args)

def url_request(url):
    req = Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 memery')
    return req

def read_url(url, args='', quote_=True, content_whitelist=[]):
    """
    Return the data (presumably text) from a url and decode it to utf-8 using
    the page's preferred encoding (if found).

    args -- a suffix argument that will be appended to the url
    quote_ -- if True, will mean that args will be appended as quote(args)
    content_whitelist -- a list of MIME types which the page's type has to be
                         one of (empty list means no restriction)
    """

    # Handy thing to append stuff to the url with a valid format
    if args:
        if quote_:
            args = quote(args)
        url += str(args)

    # Read the page and try to find the encoding in the headers
    encoding = None
    with urlopen(url_request(url)) as s:
        if content_whitelist and s.info().get_content_type() not in content_whitelist:
            return None
        # This may return None
        encoding = s.info().get_content_charset()
        page = s.read()

    # Get the encoding of the page manually if there's no header
    if not encoding:
        metatag_encoding = re.search(b'<meta.+?charset="?(.+?)["; ].*?>', page)
        if metatag_encoding:
            encoding = metatag_encoding.group(1).decode()

    if encoding:
        content = page.decode(encoding, 'replace')
    # Fallback, in case there is no known encoding
    else:
        try:
            content = page.decode('utf-8')
        except:
            content = page.decode('latin-1', 'replace')

    return content

def get_title(url):
    """ 
    Return the title from the page the url points to.

    Return None if isn't an (x)html page or if it simply has no <title>-tag.
    No other exceptions/errors are handled.
    """
    content = read_url(url, content_whitelist=['text/html'])
    if not content:
        return None

    title_re = re.compile('<title.*?>(.+?)</title>', re.IGNORECASE | re.DOTALL)
    rawtitle = title_re.search(content)
    if rawtitle:
        title = HTMLParser().unescape(rawtitle.group(1).strip())
        # Get rid of unnecessary whitespace
        return re.sub(r'\s+', ' ', title)
    else:
        return None

def read_file(fname):
    """ Read a file and return the raw data. Create a new file if necessary. """
    if not os.path.isfile(fname):
        with open(fname, mode='w', encoding='utf-8') as f:
            #TODO: Um. Something more professional perhaps
            print('NEWFILE!!!!')
            f.write('')
        return ''
    else:
        with open(fname, encoding='utf-8') as f:
            return f.read()

def read_lineconf(str):
    """ 
    Return the argument parsed as a memery-specific line-parsed file, 
    where empty lines and lines starting with # are ignored.

    Examples: adminlist, userblacklist, commands
    """
    return [l for l in str.splitlines()
            if l and not l.startswith('#')]

def read_json(str):
    return json.loads(str)

def truncate(str, size):
    if len(str) > size:
        return str[:size - 1] + '…'
    else:
        return str

def _is_in_list(sendernick, senderident, fname):
    list_ = read_lineconf(read_file(fname))
    for regex in list_:
        if re.match(regex, sendernick + '!' + senderident, re.IGNORECASE) != None:
            return True
    return False

def is_admin(nick, ident):
    return _is_in_list(nick, ident, 'adminlist')

def is_blacklisted(nick, ident):
    return _is_in_list(nick, ident, 'userblacklist')
