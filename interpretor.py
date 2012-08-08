import imp, os, os.path, random, re
from urllib.parse import quote_plus, quote
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from html.parser import HTMLParser
import common

o_blacklist_fname = 'o-blacklist'

# Helper/convenience functions
def make_privmsgs(texts, channel):
    if type(texts) != type([]):
        texts = [texts]
    return ['PRIVMSG {} :{}'.format(channel, t) 
            for t in texts if t]

# Not used

def expand_aliases(msg):
    lines = common.read_file('aliases.txt')
    for line in lines:
        try:
            alias, replc = re.split('\s+->\s+', line)
        except ValueError:
            # TODO: some good error handling here
            continue
        # Add a trailing space to prevent .choose -> .o choose because of .c
        if msg.startswith(alias + ' '):
            return replc + ' ' + msg[len(alias)+1:]
    return msg


# .o commands

def o_blacklist_commands(sendernick, msg):
    try:
        _, text = msg.split(None, 1)
    except ValueError:
        return None
    blacklist = common.read_file(o_blacklist_fname)

    try:
        cmd, args = text.split(None, 1)
    except ValueError:
        cmd = text
        args = None

    if cmd == 'list':
        if len(', '.join(blacklist)) > 450:
            return '{} svartlistade .o-kommandon'.format(len(blacklist))
        else:
            return 'svartlista: {}'.format(', '.join(blacklist))

    elif cmd == 'remove':
        if args == None:
            return 'inget att ta bort'
        elif args in blacklist:
            del blacklist[blacklist.index(args)]
            with open(o_blacklist_fname, mode='w', encoding='utf-8') as f:
                f.write('\n'.join(blacklist) + '\n')
            return '{} borttaget från svartlistan'.format(args)
        else:
            return '{} finns inte i svartlistan'.format(args)

    elif cmd == 'add':
        if args == None:
            return 'inget att lägga till'
        elif args not in blacklist:
            with open(o_blacklist_fname, mode='a', encoding='utf-8') as f:
                f.write(args + '\n')
            return '{} tillagt i svartlistan'.format(args)
        else:
            return '{} finns redan i svartlistan'.format(args)

    else:
        return 'möjliga blacklistkommandon: list, remove, add'

def o_blacklist_this(command):
    blacklist = common.read_file(o_blacklist_fname)
    if command not in blacklist:
        with open(o_blacklist_fname, 'a') as f:
            f.write(command + '\n')

def get_o_commands():
    with urlopen('http://h4xxel.org/failboat/services.html') as s:
        content = s.read().decode('utf-8', 'replace')

    commands = {}
    for line in re.findall('(?<=<li>).+?(?=</li>)', content):
        cmd, url = line.split(' ', 1)
        commands[cmd] = HTMLParser().unescape(url.replace('${','{'))
    
    # Woo specialfall för mr3d cant be bothered
    commands['haxell'] = 'http://adun.se/haskell.pl?{args}'
    commands['gcalc'] = 'http://w.rdw.se:81/gcalc.php?nonewline&args={args}'
    commands['404test'] = 'http://nothinghere.lol'
    return commands

def run_o_command(sendernick, msg, commands):
    # [.o] [cmd] [args] tex .o wik fisk
    msgchunks = msg.split(None, 2)
    cmd = msgchunks[1]
    if len(msgchunks) > 2:
        args = quote_plus(msgchunks[2])
    else:
        args = ''
    
    if cmd not in commands:
        return None

    blacklist = common.read_file(o_blacklist_fname)
    if cmd in blacklist:
        return random.choice(['svartlistat kommando', 
                'jag har bättre saker för mej',
                'nej', 'funkar inte'])

    req = common.url_request(commands[cmd].format(nick=sendernick, args=args))
    
    try:
        with urlopen(req) as s:
            response = s.readline().decode('utf-8', 'replace')
    except HTTPError as e:
        o_blacklist_this(cmd)
        return 'HTTPError: {}'.format(e.code)
    except URLError as e:
        o_blacklist_this(cmd)
        return 'URLError: {}'.format(e.reason)

    return response


# Plugins

def get_plugins():
    plugins = [x[:-3] for x in os.listdir('plugins') if x.endswith('.py')]
    return plugins

def run_plugin(sendernick, msg, pluginname):
    # Get the argument(s)
    msgchunks = msg.split(None, 1)
    if len(msgchunks) > 1:
        args = msgchunks[1]
    else:
        args = ''

    # Load the plugin
    try:
        fp, pathname, description = imp.find_module(pluginname, ['plugins'])
        plugin = imp.load_module(pluginname, fp, pathname, description)
    except Exception as e:
        return 'pluginen kunde inte laddas: {}'.format(e)

    # Run the plugin
    try:
        response = plugin.run(sendernick, args)
    except NotImplementedError:
        return None
    except Exception as e:
        return 'pluginen kraschade i runtime: {}'.format(e)
    else:
        return response


# Main functions

def giveop(msg, channel):
    names = msg.split()[1:]
    # Don't bother opping in query
    if names and channel.startswith('#'):
        return ['MODE {} +o {}'.format(channel, n)
                for n in names]
    elif not names and channel.startswith('#'):
        return ['MODE {} +o {}'.format(channel, n)
                for n in names]

    return None

def get_title(url):
    req = common.url_request(url)
    try:
        with urlopen(req) as s:
            page = s.read()
    except HTTPError as e:
        return 'HTTPError: {}'.format(e.code)
    except URLError as e:
        return 'URLError: {}'.format(e.reason)

    # Get the encoding of the page
    enc = re.search(b'<meta.+?charset="?(.+?)["; ].*?>', page)
    if enc:
        enc = enc.group(1).decode()
    else:
        enc = 'utf-8'
    
    # And then decode it to utf-8
    content = page.decode(enc, 'replace')

    title_re = re.compile('<title.*?>(.+?)</title>', re.IGNORECASE | re.DOTALL)
    rawtitle = title_re.search(content)
    if rawtitle:
        title = HTMLParser().unescape(rawtitle.group(1).strip())
        return ' '.join(title.split())
    else:
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

def get_output(msg='', myname='', sender='', channel=''):
    msg = msg.strip()

    cmdsplit_re = re.compile('\s+->\s+')

    lines = common.read_file('commands')

    importlines = [x for x in lines if cmdsplit_re.search(x) == None]
    cmdlines = [x for x in lines if x not in importlines]

    imports = get_command_imports(importlines)

    format_answer = lambda t, arg: t.format(message=msg, myname=myname,
                     channel=channel, sender=sender, arg=arg, qarg=quote(arg))
    exec_answer = lambda code, arg: eval(code, imports, 
                    {'arg':arg, 'qarg':quote(arg), 'message':msg,
                     'sender':sender, 'channel':channel, 'myname':myname})

    # Fancy regexmagic!
    format_cmd = lambda t: format_answer(t, '(.+?)') + '$'

    for line in cmdlines:
        try:
            rawcmd, rawanswer = re.split('\s+->\s+', line)
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

def main_parse(msg='', sendernick='', senderident='', channel='', myname=''):
    """ 
    >> Main entry function! <<
    The returned values from this function should be valid
    irc message, minus the trailing \r\n.
    """
    is_admin = common.is_admin(sendernick, senderident)

    if common.is_blacklisted(sendernick, senderident):
        return None

    url_re = re.compile(r'https?://\S+') #(www[.]\S+?[.]\S+)
    plugins = get_plugins()

    # .o
    if msg.startswith('.o '):
        commands = get_o_commands()
        return make_privmsgs(run_o_command(sendernick, msg, commands), channel)

    # .blacklist
    elif msg.startswith('.blacklist ') and is_admin:
        return make_privmsgs(o_blacklist_commands(sendernick, msg), channel)

    # .giveop
    elif msg.startswith('.giveop ') and is_admin:
        return giveop(msg, channel)

    # memery:
    elif msg.startswith('{}: '.format(myname)):
        return make_privmsgs(nudge_response(sendernick, msg), channel)
    # # .help
    # elif msg.startswith('.help '):

    # plugins:
    elif msg.split()[0][1:] in plugins:
        return make_privmsgs(run_plugin(sendernick, msg, msg.split()[0][1:]), channel)

    # Title
    elif url_re.search(msg):
        titles = list(set([get_title(u) for u in set(url_re.findall(msg))]))
        return make_privmsgs(titles, channel)


    # Rest of the commands
    else:
        output = get_output(msg, myname, sendernick, channel)
        if output:
            return make_privmsgs(output, channel)
        else:
            remarks = random_talk(sendernick, msg)
            if remarks:
                return make_privmsgs(remarks, channel)