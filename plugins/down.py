import codecs, re
import common

def help():
    return {'authors':     ['nycz'],
            'years':       ['2012'],
            'version':     '1.0',
            'description': 'Wrapper runt http://www.downforeveryoneorjustme.com/ för att se om en websida är nere för andra eller om det bara är ett problem med ens egen uppkoppling.',
            'argument':    '<url>'}

def run(nick, args):
    return "{0}: {1}".format(nick, isitdown(args))

def isitdown(args):
    if not args.strip():
        return "skriv in en url för att se om den är nere bara för dej"

    content = common.read_url("http://www.downforeveryoneorjustme.com/", common.quote(args))

    regex = re.search(r'<div id="container">\s*(.+?)\s*<p><a href="/">', content, re.DOTALL)

    # This will – and is supposed to – crash if the regex fails.
    text = regex.group(1).lower()
    
    if text.startswith("it's not just you"):
        return "sidan verkar vara nere!"
    elif text.startswith("it's just you"):
        return "sidan verkar inte vara nere"
    elif text.startswith('huh?'):
        return "du verkar inte ha skrivit in en url"
    else:
        raise AttributeError('error in .down plugin, major parse error')