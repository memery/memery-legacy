import os.path, re
import json
from urllib.parse import quote
from urllib.request import Request, urlopen

def url_request(url):
    req = Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 memery')
    return req

def read_file(fname):
    if not os.path.isfile(fname):
        with open(fname, mode='w', encoding='utf-8') as f:
            print('NEWFILE!!!!')
            f.write('')
        return []
    else:
        with open(fname, encoding='utf-8') as f:
            lines = [l for l in f.read().splitlines()
                     if l and not l.startswith('#')]
        return lines

def read_json(fname):
  if not os.path.isfile(fname):
    with open(fname, mode='w', encoding='utf-8') as f:
      print('NEWFILE!!!!')
      f.write('')
    return {}
  else:
    with open(fname, encoding='utf-8') as f:
      content = json.loads(f.read())
    return content

def _is_in_list(sendernick, senderident, fname):
    list_ = read_file(fname)
    for regex in list_:
        if re.match(regex, sendernick + '!' + senderident, re.IGNORECASE) != None:
            return True
    return False

def is_admin(nick, ident):
    return _is_in_list(nick, ident, 'adminlist')

def is_blacklisted(nick, ident):
    return _is_in_list(nick, ident, 'userblacklist')
