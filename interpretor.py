import imp, os, os.path, random, re
from urllib.parse import quote_plus, quote
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from html.parser import HTMLParser
import ircparser, common


# Plugins

def get_plugins():
    plugins = [x[:-3] for x in os.listdir('plugins') if x.endswith('.py')]
    return plugins

def load_plugin(pluginname):
    fp, pathname, description = imp.find_module(pluginname, ['plugins'])
    plugin = imp.load_module(pluginname, fp, pathname, description)
    return plugin

def run_plugin(sendernick, msg, pluginname):
    # Get the argument(s)
    msgparts = re.match(r'\S+(\s+(?P<nudgenick>@\S+)?\s*(?P<args>.+)*)?', msg)
    if msgparts.group('nudgenick'):
        sendernick = msgparts.group('nudgenick')[1:]
    if msgparts.group('args'):
        args = msgparts.group('args')
    else:
        args = ''
    
    # Load the plugin
    plugin = load_plugin(pluginname)

    # Run the plugin
    try:
        response = plugin.run(sendernick, args)
    except NotImplementedError:
        return None
    else:
        return response

def get_command_help(msg, sendernick, myname, command_prefix, plugins):
    msgparts = re.match(r'[{}]help(\s+(?P<nudgenick>@\S+)?\s*(?P<args>.+)*)?'.format(command_prefix), msg)
    if msgparts.group('args') == None:
        return ['{}: Hej Och Välkommen Till {}, En Vänlig Och Hjälpsam IRC (InterNet Relay Chat) "Bot"!'.format(sendernick, myname.title()),
                '{0}: Skriv \'{1}list commands\' eller \'{1}list plugins\' för en lista på kommandon/plugins'.format(sendernick, command_prefix),
                '{}: Skriv \'{}help <kommando>\' för hjälp med <kommando>.'.format(sendernick, command_prefix)]
    pluginname = msgparts.group('args')
    if msgparts.group('nudgenick'):
        nudgenick = msgparts.group('nudgenick')[1:]
    else:
        nudgenick = sendernick

    if pluginname in plugins:
        plugin = load_plugin(pluginname)
        try:
            info = plugin.help()
            return ['{}: {}: {}'.format(nudgenick, pluginname, info['description']),
                    '{}: Användning: {}{} {}'.format(nudgenick, command_prefix, pluginname, 
                                                info['argument'])]
        except NotImplementedError:
            return 'nån idiot har glömt att lägga in hjälptext i {}{}'.format(command_prefix, 
                                    pluginname)
    else:
        helpsplit_re = re.compile(r'\s+\?>\s+?')
        lines = common.read_lineconf(common.read_file('commands'))
        helplines = [x for x in lines if helpsplit_re.search(x) != None]
        for h in helplines:
            try:
                cmd, args, desc = helpsplit_re.split(h)
            except ValueError:
                continue
            else:
                if pluginname == cmd.format(c=''):
                    return ['{}: {}: {}'.format(nudgenick, pluginname, desc.format(myname=myname)),
                            '{}: Användning: {} {}'.format(nudgenick, cmd.format(c=command_prefix), 
                                                      args).strip()]

        return '{}: finns inget sånt kommando'.format(sendernick)


# Main functions

def giveop(msg, channel, sendernick):
    names = set(msg.split()[1:])
    # Don't bother opping in query
    if channel.startswith('#'):
        if not names:
            names = [sendernick]
        return ircparser.Out_Mode(channel, '+o', names)
    return None


def nudge_response(sendernick, msg):
    if random.randint(0,6) > 0:
        return None
    l = ['{}: MEN DU ÄR JU DUM I HUVUDET',
         '{}: det kanske är du som gör fel?',
         '{}: aa fast nej',
         '{}: troru det själv eller']
    return random.choice(l).format(sendernick)

def get_command_imports(lines):
    """
    Extract all module names from the lines, import them,
    and then return the imported modules in a dict.
    """
    names = []
    for line in lines:
        names.extend(re.split(r'\s*,\s*', line))

    out = {}
    for name in names:
        fp, pathname, description = imp.find_module(name)
        try:
            out[name] = imp.load_module(name, fp, pathname, description)
        except AttributeError:
            # No module of that name, suck it up!
            continue
        finally:
            # Since we may exit via an exception, close fp explicitly.
            if fp:
                fp.close()
    return out

def get_output(msg='', myname='', sender='', channel='', command_prefix='.'):
    msg = msg.strip()

    cmdsplit_re = re.compile(r'\s+->\s+')
    importline_re = re.compile(r'(\w|\.)+?(,\s+(\w|\.)+?)*\s*$')
    # helpsplit_re = re.compile(r'\s+\?>\s+')

    lines = common.read_lineconf(common.read_file('commands'))

    cmdlines = [x for x in lines if cmdsplit_re.search(x) != None]
    importlines = [x for x in lines if importline_re.match(x) != None]

    imports = get_command_imports(importlines)

    format_answer = lambda t, arg: t.format(message=msg, myname=myname,
                     channel=channel, sender=sender, arg=arg, qarg=quote(arg),
                     c='['+command_prefix+']')
    exec_answer = lambda code, arg: eval(code, imports, 
                    {'arg':arg, 'qarg':quote(arg), 'message':msg,
                     'sender':sender, 'channel':channel, 'myname':myname})

    # Fancy regexmagic!
    format_cmd = lambda t: format_answer(t, r'(?P<arg>.+?)') + '$'

    for line in cmdlines:
        try:
            rawcmd, rawanswer = cmdsplit_re.split(line)
        except ValueError:
            # TODO: some good error handling here
            continue
        cmd = format_cmd(rawcmd)
        cmd_match = re.match(cmd, msg) # ugly poc name but w/e :/
        if cmd_match:
            if 'arg' in cmd_match.groupdict():
                arg = cmd_match.group('arg')
            else:
                arg = ''
            if rawanswer.startswith('#py:'):
                answer = exec_answer(rawanswer[4:], arg)
            else:
                answer = format_answer(rawanswer, arg)
            return answer.split('[\\n]')
            
    return None

def markov_talk(channel, frequency, pickiness):
    if pickiness < 1 or type(pickiness) != type(2):
        return 'Error i configen. Ogiltigt värde för markov_pickiness! (Ska vara heltal större än 0.)'
    if frequency < 0 or type(frequency) != type(2):
        return 'Error i configen. Ogiltigt värde för markov_frequency! (Ska vara positivt heltal eller noll.)'

    if random.randint(0, frequency) > 0:
        return None
    try:
        with open('markovdata/{}.txt'.format(channel), 'r') as f:
            corpus = f.read()
    except:
        return None

    sentence = random.choice(corpus.splitlines()).split()[:pickiness]

    while True:
        ms = re.findall(r'\b{} (.+?$)'.format(re.escape(' '.join(sentence[-pickiness:]))), corpus, re.MULTILINE)
        if not ms:
            break
        nextword = random.choice(ms).split()[:1]
        if not nextword:
            break
        sentence += nextword

    return ' '.join(sentence)


# Entry point

def main_parse(data, myname, settings):
    """ 
    >> Main entry function! <<
    The returned values from this function should be valid
    irc message, minus the trailing \r\n.

    NO IT SHOULD NOT
    """

    msg = data.message
    channel = data.recipient
    sendernick = data.sender
    senderident = data.senderident

    command_prefix = settings['behaviour']['command_prefix']

    is_admin = common.is_admin(sendernick, senderident)

    if common.is_blacklisted(sendernick, senderident):
        return None

    startswith_cp = lambda msg, cmd: re.match(r'[{}]{}(\s|$)'.format(command_prefix, cmd), msg)
    url_re = re.compile(r'https?://\S+') #(www[.]\S+?[.]\S+)
    spotify_url_re = re.compile(r'spotify(:\S+)+?')
    plugins = get_plugins()

    # .giveop
    if startswith_cp(msg, 'giveop') and is_admin:
        return giveop(msg, channel, sendernick)

    # memery:
    elif re.match('{}.? '.format(myname), msg):
        return ircparser.Out_Messages(channel, nudge_response(sendernick, msg))

    # .help
    elif startswith_cp(msg, 'help'):
        return ircparser.Out_Messages(channel, get_command_help(msg, sendernick, myname,
                                                               command_prefix, plugins))

    # plugins:
    elif msg.startswith(command_prefix) and msg.split()[0][1:] in plugins:
        return ircparser.Out_Messages(channel, run_plugin(sendernick, msg, msg.split()[0][1:]))

    # Title
    elif url_re.search(msg):
        out = []
        titles = set()
        for url in set(url_re.findall(msg)):
            title = common.get_title(url)
            if title:
                titles.add(title)
        return ircparser.Out_Messages(channel, list(titles))

    # spotify title
    elif spotify_url_re.search(msg):
        out = []
        titles = set()
        for m in set(spotify_url_re.findall(msg)):
            title = common.get_title('http://open.spotify.com' + m.replace(':', '/'))
            if title:
                titles.add(re.sub(r'(.+?) by (.+?) on Spotify', r'Spotify: \1 (\2)', title))
        return ircparser.Out_Messages(channel, list(titles))

    # Rest of the commands
    else:
        output = get_output(msg, myname, sendernick, channel, command_prefix)
        if output:
            return ircparser.Out_Messages(channel, output)
        # markov chain-style talking
        else:
            try: os.makedirs('markovdata')
            except: pass
            with open('markovdata/{}.txt'.format(channel), 'a') as f:
                f.write('{}\n'.format(msg))
            remarks = markov_talk(channel, settings['behaviour']['markov_frequency'], settings['behaviour']['markov_pickiness'])
            if remarks:
                return ircparser.Out_Messages(channel, remarks)


