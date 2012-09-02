from imp import reload
import os.path, re, socket, ssl, traceback
import common, ircparser, interpretor
from time import time, sleep
import random, string


def log(text, type='general'):
    try:
        common.log(text, type)
    except:
        # TODO: Gör backuploggning mer felsäker för konstiga terminaler 
        print(repr('[BACKUP][{}] {}'.format(type.upper(), text)))

def log_error(text):
    log(text, type='error')


def init_irc(settings):
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc.settimeout(settings['irc']['grace_period']/10)

    while True:
        try: irc.connect((settings['irc']['server'], settings['irc']['port']))
        except:
            try: irc.send(bytes('', 'utf-8'))
            except:
                log_error('Uppkoppling till {}:{} misslyckades, försöker igen om {} sekunder...'.format(
                            settings['irc']['server'],
                            settings['irc']['port'],
                            settings['irc']['reconnect_delay']))
                sleep(settings['irc']['reconnect_delay'])
            else: break
        else: break

    if settings['irc']['ssl']:
        irc = ssl.wrap_socket(irc)

    send(irc, 'NICK {}'.format(settings['irc']['nick']))
    send(irc, 'USER {0} 0 * :IRC bot {0}'.format(settings['irc']['nick']))
    return irc

def quit(irc):
    send(irc, 'QUIT :baiiiii')
    irc.close()

def new_nick(nick):
    nick = nick[:min(len(nick), 6)] # determine how much to shave off to make room for random chars
    return '{}_{}'.format(nick, ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(2)))


def send(irc, text, logged=False):
    # Sanitize the text
    if text.count('\n') + text.count('\r') > 5:
        log_error('[ROGUE NEWLINES: (this was not sent)] {}'.format(repr(text)))
    else:
        irc.send(bytes(text + '\n', 'utf-8'))
        if not logged:
            log('<< ' + text)

def send_privmsg(irc, channel, msg):
    if msg.count('\n') + msg.count('\r') > 5:
        msg = '[rogue newlines:] {}'.format(repr(msg))
    send(irc, 'PRIVMSG {} :{}'.format(channel, msg))

def send_error(irc, channel, state, desc, error):
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
            # file.py:38 in lolfunction
            tb = '{}:{} {}'.format(os.path.basename(chunks[-1][0]),
                                   chunks[-1][1], chunks[-1][2])
    errortype = str(type(error))[8:-2]
    ircmsg = '{}: [{}] {} - {}'.format(desc, errortype, error, tb)

    autostfu = True

    # Autostfu in case of errorspam
    if state['error_repetitions'] < state['error_printcap']:
        if state['error_latest'] in ('', ircmsg):
            state['error_repetitions'] += 1
        else:
            state['error_repetitions'] = 1
        state['error_latest'] = ircmsg
        autostfu = False
    elif state['error_latest'] != ircmsg:
        state['error_latest'] = ircmsg
        state['error_repetitions'] = state['error_printcap']
        autostfu = False        

    log_error('[ERROR] {}'.format(ircmsg))
    if irc and channel and not autostfu:
        send_privmsg(irc, channel, ircmsg)


def is_admin(sender):
    # This taken from read_file in common, should be kept up to date!
    fname = 'adminlist'
    if not os.path.isfile(fname):
        with open(fname, mode='w', encoding='utf-8') as f:
            f.write('')
        raise EOFError('no adminlist file!')
    else:
        with open(fname, encoding='utf-8') as f:
            lines = [l for l in f.read().splitlines()
                     if l and not l.startswith('#')]
        if not lines:
            raise EOFError('empty adminlist file!')
        for regex in lines:
            if re.match(regex, sender, re.IGNORECASE) != None:
                return True
        return False

def get_channel(line, settings, state):
    chunks = line.split()
    try:        
        if chunks[1] in ('KICK', 'TOPIC', 'JOIN', 'MODE', 'PART'):
            return chunks[2][1:] if chunks[2][0] == ':' else chunks[2]
        elif chunks[1] == 'PRIVMSG':
            if chunks[2] == state['nick']:
                return chunks[0][1:]
            else:
                return chunks[2]
        elif chunks[1] == '403':
            return chunks[3]
    except IndexError:
        print('get_channel index error!') #TODO: remove this
        return None
    return None


# ==== Parsing functions ====

def exec_admin_cmd(irc, line, channel, settings, state):
    chunks = line.split(' ', 3)
    if chunks[1] != 'PRIVMSG' or not channel:
        return
    # Is someone talking to me?
    rawcmd = re.match(r':{}[,:]\s+?(.+)'.format(state['nick']), chunks[3])
    if rawcmd == None:
        return
    # Make sure its an admin who's talking
    if not is_admin(chunks[0][1:]):
        return
    # Ignore the namenudge
    cmd = rawcmd.group(1)

    if cmd in ('quit', 'reconnect', 'restart'):
        return cmd

    elif cmd in ('hjälp', 'help', 'commands', 'admin'):
        send_privmsg(irc, channel, 'adminkommandon: quit, reload (inte irc.py), reconnect (onödigt), restart (allt), update config, stfu, test')
        return 'continue'

    elif cmd == 'update config':
        try:
            newsettings = common.read_config('config')
        except Exception as e:
            send_error(None, None, state, 'update config', e)
        else:
            ns, os = newsettings, settings
            if ns['irc']['server'] != os['irc']['server']\
                or ns['irc']['port'] != os['irc']['port']\
                or ns['irc']['ssl'] != os['irc']['ssl']:
                return 'reconnect'
            elif ns['irc']['nick'] != os['irc']['nick']:
                send(irc, 'NICK {}'.format(ns['irc']['nick']))
                state['nick'] = ns['irc']['nick']
            elif ns['irc']['channels'] != os['irc']['channels']:
                pass # handled elsewhere
            elif ns == os:
                send_privmsg(irc, channel, 'configen har inte ändrats')
            # This should change the reference itself, not just this variable
            settings.clear()
            settings.update(newsettings)
        return 'continue'

    elif cmd == 'reload':
        reloaded = []
        for m in (interpretor, ircparser, common):
            try:
                reload(m)
            except Exception as e:
                send_error(irc, chunks[2], state, m.__name__, e)
            else:
                reloaded.append(m.__name__)
        send_privmsg(irc, channel, 'reloaded: {}'.format(', '.join(reloaded)))
        return 'continue'

    elif cmd == 'stfu':
        # Toggle state
        state['quiet'] = abs(state['quiet']-1)
        # TODO: toggle away
        if state['quiet']:
            send_privmsg(irc, channel, 'afk')
            send(irc, 'AWAY stfu\'d')
        elif not state['quiet']:
            send_privmsg(irc, channel, 'bax')
            send(irc, 'AWAY')
        return 'continue'

    elif cmd == 'test':
        send_privmsg(irc, channel, 'test')
        return 'continue'
    # Not neccessary but spelled out for clarity
    else:
        return None


# ==== Entry point ====

def run(message, settings): # message is unused for now
    try:
        settings = common.read_config('config')
    except Exception as e:
        log_error('Invalid config: {}'.format(e))
        # TODO: this
        pass

    state = {'quiet': False, 
             'error_latest': '', 
             'error_repetitions': 0, 
             'error_printcap': 2,
             'joined_channels': set(),
             'lastmsg': time(),
             'pinged': False,
             'nick': settings['irc']['nick']}

    def reset_errorstack():
        state['error_repetitions'] = 0
        state['error_latest'] = ''

    irc = init_irc(settings)

    if message:
        log_error('[STATEMESSAGE] ' + message)
        # TODO: Indexing channels causes a crash, some better way of reporting error is sought!
        # if settings['irc']['channels']:
        #     send(irc, 'PRIVMSG {} :{}: {}'.format(settings['irc']['channels'][0],
        #                                          '[statemsg]', message))

    readbuffer = b''
    stack = []
    while True:
        if time() - state['lastmsg'] > settings['irc']['grace_period'] and not state['pinged']:
            send(irc, 'PING :arst')
            state['pinged'] = True
        elif time() - state['lastmsg'] > settings['irc']['grace_period']*1.5:
            quit(irc)
            return 'reconnect'

        try:
            if settings['irc']['ssl']:
                readdata = irc.read(4096)
            else:
                readdata = irc.recv(4096)
        except socket.timeout:
            continue
        else:
            readbuffer += readdata
        
        stack = readbuffer.split(b'\r\n')
        readbuffer = stack.pop()
        for byteline in stack:
            def decode(text, encs):
                for enc in encs:
                    try:
                        text = text.decode(enc)
                    except:
                        continue
                    else:
                        return text, enc
                # Fallback is latin-1
                return text.decode('latin-1', 'replace')
            # Decode the line using likely encodings
            line, encoding = decode(byteline, ['utf-8', 'latin-1', 'cp1252'])

            state['lastmsg'] = time()
            state['pinged'] = False

            if line.startswith('PING'):
                log('>> ' + line)
                send(irc, 'PONG ' + line.split()[1])
                continue

            channel = get_channel(line, settings, state)

            # == State keeping ==
            if line.split()[1] == '403':
                log_error('[irc.py/state keeping] The channel {} does not exist!'.format(channel))
                settings['irc']['channels'].discard(channel)
                continue
            
            if line.split()[1] == '433':
                log_error('[irc.py/state keeping] Nick {} already in use, trying another one.'.format(state['nick']))
                state['nick'] = new_nick(settings['irc']['nick'])
                send(irc, 'NICK {}'.format(state['nick']))
                continue


            # == Admin ==
            try:
                admin_action = exec_admin_cmd(irc, line, channel, settings, state)
            except Exception as e:
                send_error(irc, channel, state, 'admincmd', e)
            else:
                if admin_action:
                    log('>> ' + line)
                    if admin_action == 'continue':
                        state['error_repetitions'] = 0
                        state['error_latest'] = ''
                        continue
                    else:
                        quit(irc)
                        return admin_action
            # == End admin ==


            try:
                outmessage = ircparser.parse(line, state, settings)
            except Exception as e:
                log('>> ' + line)
                send_error(irc, channel, state, 'ircparser', e)
            else:
                reset_errorstack()
                if outmessage:
                    send(irc, outmessage, logged=True)


        if state['joined_channels'] != settings['irc']['channels']:
            joins = settings['irc']['channels'] - state['joined_channels']
            parts = state['joined_channels'] - settings['irc']['channels']
            if joins:
                send(irc, 'JOIN {}'.format(','.join(joins)))
            if parts:
                send(irc, 'PART {}'.format(','.join(parts)))
            
