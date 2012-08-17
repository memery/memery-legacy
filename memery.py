import common, os.path, re, socket, ssl
from imp import reload
import interpretor

def get_privmsg_info(text, nick):
    _info, msg = text[1:].strip().split(':', 1)
    _sender, _, channel = _info.split(None, 2)
    sendernick, senderident = _sender.split('!', 1)
    if channel.strip() == nick.strip():
        channel = sendernick
    return {'msg':msg.strip(), 'sendernick':sendernick.strip(), 
            'senderident':senderident.strip(), 'channel':channel.strip()}

def safeprint(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode(errors='replace'))


def run_irc(settings):
    # YOU SHOULD NEVER USE irc.send() ALONE, USE send() INSTEAD!
    def send(text):
        irc.send(bytes(text + '\r\n', 'utf-8'))
        safeprint('<< ' + text)

    def try_to_reload(*modules):
        reloaded = []
        for m in modules:
            print(m)
            try:
                reload(m)
            except Exception as e:
                send('PRIVMSG {} :{}: {}'.format(msgdata['channel'], m.__name__, e))
            else:
                reloaded.append(m.__name__)
        if reloaded:
            send('PRIVMSG {} :reloaded: {}'.format(msgdata['channel'], ', '.join(reloaded)))



    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc.connect((settings['irc']['server'], settings['irc']['port']))
    if settings['irc']['ssl']:
        irc = ssl.wrap_socket(irc)

    nick = settings['irc']['nick']
    send('NICK {}'.format(nick))
    send('USER {0} {0} {0} :{0}'.format(nick))
    for channel in settings['irc']['channels']:
        send('JOIN {}'.format(channel))

    command_prefix = d['behaviour']['command_prefix']
    quiet = False
    errorstack = []
    errorlimit = 2

    readbuffer = ''
    stack = []
    running = True
    while running:
        if settings['irc']['ssl']:
            readdata = irc.read(4096)
        else:
            readdata = irc.recv(4096)
        readbuffer += readdata.decode('utf-8', 'replace')
        stack = readbuffer.split('\n')
        readbuffer = stack.pop()
        for rawdata in stack:
            safeprint('>> ' + rawdata)

            if rawdata.startswith('PING'):
                send('PONG ' + rawdata.split()[1])
            elif rawdata.split()[1] == 'PRIVMSG':
                msgdata = get_privmsg_info(rawdata, nick)

                def cmd(text):
                    return re.match(nick + r'[:,]\s+' + text, msgdata['msg']) != None
                if common.is_admin(msgdata['sendernick'], msgdata['senderident']):
                    if cmd('quit'):
                        running = False
                        break
                    if cmd('reload'):
                        try_to_reload(interpretor, common)
                        continue
                    if cmd('stfu'):
                        if quiet:
                            msg = 'bax'
                            quiet = False
                        else:
                            msg = 'afk'
                            quiet = True
                        send('PRIVMSG {} :{}'.format(msgdata['channel'], msg))
                        continue
                    if cmd('sup?'):
                        if errorstack:
                            msg = 'crashing: {}'.format(errorstack[-1])
                        else:
                            msg = 'just fiiiiine baby'
                        send('PRIVMSG {} :{}'.format(msgdata['channel'], msg))
                        continue

                ## END DEBUG
                if quiet:
                    continue
                try:
                    responses = interpretor.main_parse(myname=nick, command_prefix=command_prefix, **msgdata)
                except Exception as e:
                    msg = 'PRIVMSG {} :{}'.format(msgdata['channel'], e)
                    safeprint(msg)
                    if len(errorstack) < errorlimit:
                        if not errorstack or errorstack[-1] == str(e):
                            errorstack.append(str(e))
                        send(msg)
                    elif errorstack[-1] != str(e):
                        send(msg)
                        errorstack = errorlimit * [str(e)]
                    else:
                        continue
                else:
                    if responses == None:
                        continue
                    if errorstack:
                        errorstack = []
                    for r in responses:
                        if type(r) == type('') and len(r) > 0:
                            send(r)

    send('QUIT :baiiiii')
    irc.close()

if __name__ == '__main__':
    # Let the whole damn thing crash if the config is crap!
    d = {}
    try:
      d = common.read_json(common.read_file('config'))
      run_irc(d)
    except Exception as e:
      print('Invalid config: {}'.format(e))

