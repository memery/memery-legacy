
import common
import re

def help():
    return {'authors':     ['kqr'],
            'years':       ['2012'],
            'version':     '1.2',
            'description': 'Interface to Google via some kind of ajax json API.',
            'argument':    '<google query>'}

def run(nick, args):
    return "{0}: {1}".format(nick, search(args))

def search(args):
    hits = common.read_json(common.read_url("http://ajax.googleapis.com/ajax/services/search/web?v=1.0&safe=off&q=", args))['responseData']['results']

    if hits:
        striphtml = lambda s: re.sub(r'<.+?>', '', re.sub(r'  +', '', s))
        url = striphtml(hits[0]['url'])
        title = striphtml(hits[0]['title'])
        content = striphtml(hits[0]['content'])
        result = "{1}: {2} -- {0}".format(url, title, content)
    else:
        result = "No hits."

    return result


