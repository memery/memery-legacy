import imp, os, os.path, random, re
from urllib.parse import quote_plus, quote
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from html.parser import HTMLParser
import common

# Helper/convenience functions
def make_privmsgs(texts, channel):
    if type(texts) != type([]):
        texts = [texts]
    out = []
    for t in texts:
        if t:
            if type(t) == type({}):
                out.append(t)
            else:
                out.append({'type': 'message', 'message': t, 'channel': channel})
    return out
    # return [{'type': 'message', 'message': t, 'channel': channel}
    #         for t in texts if t]


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
    try:
        plugin = load_plugin(pluginname)
    except Exception as e:
        return common.error_info('pluginen kunde inte laddas', e)

    # Run the plugin
    try:
        response = plugin.run(sendernick, args)
    except NotImplementedError:
        return None
    except Exception as e:
        return common.error_info('pluginen kraschade i runtime', e)
    else:
        return response

def get_command_help(msg, sendernick, myname, command_prefix, plugins):
    msgparts = re.match(r'[{}]help(\s+(?P<nudgenick>@\S+)?\s*(?P<args>.+)*)?'.format(command_prefix), msg)
    if msgparts.group('args') == None:
        return 'skriv {}help [kommando] för hjälp (lol du behöver hjälp!! ISSUE #49 KQR)'.format(command_prefix)
    pluginname = msgparts.group('args')
    if msgparts.group('nudgenick'):
        nudgenick = msgparts.group('nudgenick')[1:]
    else:
        nudgenick = sendernick

    if pluginname in plugins:
        try:
            plugin = load_plugin(pluginname)
        except Exception as e:
            return common.error_info('pluginen kunde inte laddas', e)
        else:
            try:
                info = plugin.help()
                return ['{}: {}: {}'.format(nudgenick, pluginname, info['description']),
                        '{}: Usage: {}{} {}'.format(nudgenick, command_prefix, pluginname, 
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
                            '{}: Usage: {} {}'.format(nudgenick, cmd.format(c=command_prefix), 
                                                      args).strip()]

        return '{}: finns inget sånt kommando'.format(sendernick)


# Main functions

def giveop(msg, channel, sendernick):
    names = set(msg.split()[1:])
    # Don't bother opping in query
    if channel.startswith('#'):
        if not names:
            names = [sendernick]
        return [{'type': 'mode', 
                 'mode': '+o', 
                 'names': names,
                 'channel': channel}]
    return None


def nudge_response(sendernick, msg):
    if random.randint(0,6) > 0:
        return None
    l = ['{}: MEN DU ÄR JU DUM I HUVUDET',
         '{}: det kanske är du som gör fel?',
         '{}: aa fast nej']
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
    format_cmd = lambda t: format_answer(t, '(.+?)') + '$'

    for line in cmdlines:
        try:
            rawcmd, rawanswer = cmdsplit_re.split(line)
        except ValueError:
            # TODO: some good error handling here
            continue
        cmd = format_cmd(rawcmd)
        cmd_match = re.match(cmd, msg) # ugly poc name but w/e :/
        if cmd_match:
            if len(cmd_match.groups()) > 0:
                arg = cmd_match.group(1)
            else:
                arg = ''
            if rawanswer.startswith('#py:'):
                answer = exec_answer(rawanswer[4:], arg)
            else:
                answer = format_answer(rawanswer, arg)
            return answer.split('[\\n]')
            
    return None

def random_talk(sendernick, msg):
    if random.randint(0,2300) > 0 or len(msg) > 40:
        return None
    choices = ['{msg} :)', '{msg}', '{msg}?',
               '...', 'uh', 'ok', 'va?',
               'precis', 'mm', 'exakt',
               'knappast', 'nej', 'du har fel',
               '{nick}: ?', '{nick}',
               'men', 'bah', 'pff', 'hm']
    return random.choice(choices).format(msg=msg, nick=sendernick)


# Entry point

def main_parse(data, myname, command_prefix):
# msg='', sendernick='', senderident='', channel='', myname='', command_prefix='.'):
    """ 
    >> Main entry function! <<
    The returned values from this function should be valid
    irc message, minus the trailing \r\n.

    NO IT SHOULD NOT
    """
    msg = data['message']
    channel = data['channel']
    sendernick = data['sendernick']
    senderident = data['senderident']

    is_admin = common.is_admin(sendernick, senderident)

    if common.is_blacklisted(sendernick, senderident):
        return None

    startswith_cp = lambda msg, cmd: re.match(r'[{}]{}(\s|$)'.format(command_prefix, cmd), msg)
    url_re = re.compile(r'https?://\S+') #(www[.]\S+?[.]\S+)
    spotify_url_re = re.compile(r'spotify:([a-z]+?):(\S+)')
    plugins = get_plugins()

    # .giveop
    if startswith_cp(msg, 'giveop') and is_admin:
        return giveop(msg, channel, sendernick)

    # memery:
    elif re.match('{}.? '.format(myname), msg):
        return make_privmsgs(nudge_response(sendernick, msg), channel)

    # .help
    elif startswith_cp(msg, 'help'):
        return make_privmsgs(get_command_help(msg, sendernick, myname, 
                                   command_prefix, plugins), channel)

    # plugins:
    elif msg.startswith(command_prefix) and msg.split()[0][1:] in plugins:
        return make_privmsgs(run_plugin(sendernick, msg, msg.split()[0][1:]), channel)

    # Title
    elif url_re.search(msg):
        out = []
        titles = set()
        errors = []
        for url in set(url_re.findall(msg)):
            try:
                title = common.get_title(url)
            except Exception as e:
                errors.append(common.error_info(url, e))
            else:
                if title:
                    titles.add(title)
        if titles:
            out.extend(titles)
        if errors:
            out.extend(errors)
        if out:
            return make_privmsgs(out, channel)

    # spotify title
    elif spotify_url_re.search(msg):
        matches = set(spotify_url_re.findall(msg))
        def titles(ms):
            for type_, id_ in ms:
                try:
                    title = get_title('http://open.spotify.com/{0}/{1}'.format(type_, id_))
                    formatted = re.sub(r'(.+?) by (.+?) on Spotify', r'Spotify: \1 (\2)', title)
                    yield formatted
                except Exception as e:
                    yield common.error_info('Spotify error', e)
        spotify_titles = [t for t in titles(matches)]    # coerce generator to list

        return make_privmsgs(spotify_titles, channel)

    # Rest of the commands
    else:
        output = get_output(msg, myname, sendernick, channel, command_prefix)
        if output:
            return make_privmsgs(output, channel)
        else:
            remarks = random_talk(sendernick, msg)
            if remarks:
                return make_privmsgs(remarks, channel)
