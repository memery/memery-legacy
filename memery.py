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


def run_irc(network, port, channels, nick):
    # YOU SHOULD NEVER USE irc.send() ALONE, USE send() INSTEAD!
    def send(text):
        irc.send(bytes(text + '\r\n', 'utf-8'))
        safeprint('<< ' + text)
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc.connect((network, port))
    irc = ssl.wrap_socket(irc)

    send('NICK {}'.format(nick))
    send('USER {0} {0} {0} :{0}'.format(nick))
    for channel in channels:
        send('JOIN {}'.format(channel))

    quiet = False
    errorstack = []
    errorlimit = 2

    readbuffer = ''
    stack = []
    running = True
    while running:
        readbuffer += irc.read(4096).decode('utf-8', 'replace')
        stack = readbuffer.split('\n')
        readbuffer = stack.pop()
        for rawdata in stack:
            safeprint('>> ' + rawdata)

            if rawdata.startswith('PING'):
                send('PONG ' + rawdata.split()[1])
            elif rawdata.split()[1] == 'PRIVMSG':
                msgdata = get_privmsg_info(rawdata, nick)
                if common.is_admin(msgdata['sendernick'], msgdata['senderident']):
                    if msgdata['msg'] == '{}: quit'.format(nick):
                        running = False
                        break
                    if msgdata['msg'] == '{}: reload'.format(nick):
                        try:
                            reload(interpretor)
                        except Exception as e:
                            send('PRIVMSG {} :{}'.format(msgdata['channel'], e))
                        else:
                            send('PRIVMSG {} :reloaded'.format(msgdata['channel']))
                        continue
                    if msgdata['msg'] == '{}: stfu'.format(nick):
                        if quiet:
                            send('PRIVMSG {} :bax'.format(msgdata['channel']))
                            quiet = False
                        else:
                            send('PRIVMSG {} :afk'.format(msgdata['channel']))
                            quiet = True

                ## END DEBUG
                if quiet:
                    continue
                try:
                    responses = interpretor.main_parse(myname=nick, **msgdata)
                except Exception as e:
                    msg = 'PRIVMSG {} :{}'.format(msgdata['channel'], e)
                    print(msg)
                    if len(errorstack) < errorlimit:
                        if not errorstack or errorstack[-1] == msg:
                            errorstack.append(msg)
                        send(msg)
                    elif errorstack[-1] != msg:
                        send(msg)
                        errorstack = errorlimit * [msg]
                    else:
                        continue
                else:
                    if errorstack:
                        errorstack = []
                    if responses == None:
                        continue
                    for r in responses:
                        if type(r) == type('') and len(r) > 0:
                            send(r)

    send('QUIT :baiiiii')
    irc.close()

if __name__ == '__main__':
    # Let the whole damn thing crash if the config is crap!
    d = {}
    with open('config', encoding='utf-8') as f:
        lines = [l.split(':', 1) for l in f.read().splitlines()
                 if l and not l.startswith('#')]
    for l in lines:
        if len(l) == 2:
            d[l[0]] = l[1]
    run_irc(d['server'], int(d['port']), d['channels'].split(','), d['nick'])