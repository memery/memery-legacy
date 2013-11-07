import common
import re

def help():
    return {'authors':     ['kqr', 'jocke-l'],
            'years':       ['2012', '2013'],
            'version':     '1.3',
            'description': 'Interface till Google via något slags ajax json API.',
            'argument':    '<googlesökning>'}

def run(nick, args):
    return "{0}: {1}".format(nick, search(args))

def search(args):
    hits = common.read_json(common.read_url("http://ajax.googleapis.com/ajax/services/search/web?v=1.0&safe=off&q=", args))['responseData']['results']

    if hits:
        striphtml = lambda s: re.sub(r'<.+?>', '', re.sub(r'(  +|\n)', '', s))
        url = striphtml(hits[0]['unescapedUrl'])
        title = striphtml(hits[0]['titleNoFormatting'])
        content = striphtml(hits[0]['content'])
        result = "{1}: {2} -- {0}".format(url, title, content)
    else:
        result = "No hits."

    return result


