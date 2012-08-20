import json, os.path, re, traceback
from urllib.parse import quote
from urllib.request import Request, urlopen

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

def read_url(url, args='', quote_=True):
    if args:
        if quote_:
            args = quote(args)
        url += str(args)
    with urlopen(url_request(url)) as s:
        page = s.read()
    try:
        content = page.decode('utf-8')
    except:
        content = page.decode('latin-1', 'replace')
    return content

def read_file(fname):
    if not os.path.isfile(fname):
        with open(fname, mode='w', encoding='utf-8') as f:
            print('NEWFILE!!!!')
            f.write('')
        return []
    else:
        with open(fname, encoding='utf-8') as f:
            return f.read()

def read_lineconf(str):
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
