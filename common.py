import os.path, re
import json
from urllib.parse import quote
from urllib.request import Request, urlopen

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
