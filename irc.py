from imp import reload
import os.path, re, socket, ssl, traceback
import common, ircparser, interpretor


def init_irc(settings):
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc.connect((settings['server'], settings['port']))
    irc = ssl.wrap_socket(irc)

    send(irc, 'NICK {}'.format(settings['nick']))
    send(irc, 'USER {0} {0} {0} :{0}'.format(settings['nick']))
    for channel in settings['channels']:
        send(irc, 'JOIN {}'.format(channel))
    return irc

def send(irc, text):
    irc.send(bytes(text + '\r\n', 'utf-8'))
    log_output(text)

def quit(irc):
    send(irc, 'QUIT :baiiiii')
    irc.close()

def log(text):
    try:
        common.log(text)
    except:
        print('[BACKUP] '+text.encode(errors='replace'))

def log_input(text):
    log('>> ' + text)

def log_output(text):
    log('<< ' + text)

# This should not be repurposed to send_to_channel or some shit like that!
# This should otoh get line numbers!
def send_error(irc, channel, desc, error):
    exception_re = re.compile(r'File "(.+?)", line (\d+), (.+?)(\n|$)')
    try:
        stacktrace = traceback.format_exc()
        chunks = exception_re.findall(stacktrace)
        errortype = stacktrace.split('\n')[-2]
    except:
        tb = '[bad/no stacktrace]'
        errortype = str(type(error))[8:-2]
    else:
        if chunks:
            # file.py:38 in lolfunction
            tb = '{}:{} {}'.format(os.path.basename(chunks[-1][0]),
                                   chunks[-1][1], chunks[-1][2])
    args = (desc, errortype, error, tb)
    if channel:
        send(irc, 'PRIVMSG {} :{}: [{}] {} - {}'.format(channel, *args))
    else:
        log('<No channel> {}: [{}] {} - {}'.format(*args))


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


# ==== Parsing functions ====

def exec_admin_cmd(irc, line, settings):
    chunks = line.split(' ', 3)
    if chunks[1] != 'PRIVMSG':
        return
    # Is someone talking to me?
    rawcmd = re.match(r':{}[,:]\s+?(.+)'.format(settings['nick']), chunks[3])
    if rawcmd == None:
        return
    # Make sure its an admin who's talking
    if not is_admin(chunks[0][1:]):
        return
    # Ignore the namenudge
    cmd = rawcmd.group(1)

    if cmd in ('quit', 'reconnect', 'restart'):
        return cmd
    elif cmd == 'reload':
        reloaded = []
        for m in (interpretor, ircparser, common):
            try:
                reload(m)
            except Exception as e:
                send_error(irc, chunks[2], m.__name__, e)
            else:
                reloaded.append(m.__name__)
        send(irc, 'PRIVMSG {} :reloaded: {}'.format(chunks[2], ', '.join(reloaded)))
        return 'continue'
    # elif cmd == 'stfu'
    # Not neccessary but spelled out for clarity
    else:
        return None


# ==== Entry point ====

def run(message, settings): # message is unused for now
    try:
        settings = common.read_json('config')
    except Exception as e:
        log('Invalid config: {}'.format(e))
        # TODO: this
        pass

    irc = init_irc(settings)

    if message:
        log('[STATEMESSAGE] ' + message)
        if settings['channels']:
            send(irc, 'PRIVMSG {} :{}: {}'.format(settings['channels'][0],
                                                  '[statemsg]', message))

    readbuffer = ''
    stack = []
    while True:
        readbuffer += irc.read(4096).decode('utf-8', 'replace')
        stack = readbuffer.split('\r\n')
        readbuffer = stack.pop()
        for line in stack:
            log_input(line)
            if line.startswith('PING'):
                send(irc, 'PONG ' + line.split()[1])
                continue

            channel = ircparser.get_channel(line)

            # == Admin ==
            try:
                admin_action = exec_admin_cmd(irc, line, settings)
            except Exception as e:
                send_error(irc, channel, 'admincmd', e)
            else:
                if admin_action == 'continue':
                    continue
                elif admin_action != None:
                    quit(irc)
                    return admin_action
            # == End admin ==

            
            # 1. Convert a raw irc message to interpretor-compatible data
            try:
                indata = ircparser.irc_to_data(line)
            except NotImplementedError:
                continue
            except Exception as e:
                send_error(irc, channel, 'irc->data', e)
                continue
            # 2. Parse the data to a list of responses
            try:
                responses = interpretor.main_parse(indata, settings['nick'],
                                                   settings['command_prefix'])
            except Exception as e:
                send_error(irc, channel, 'interpretor', e)
                continue
            # Nothing to do if there are no responses
            if not responses:
                continue
            # 3. Convert the list of responses to list of raw send()able irc messages
            for response in responses:
                try:
                    outmessage = ircparser.data_to_irc(response)
                except Exception as e:
                    send_error(irc, channel, 'data->irc', e)
                else:
                    send(irc, outmessage)
