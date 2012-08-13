def get_channel(line):
    chunks = line.split()
    try:        
        if chunks[1] in ('PRIVMSG', 'KICK', 'TOPIC', 'JOIN', 'MODE'):
            return chunks[2]
    except IndexError:
        return None
    return None


def irc_to_data(line):
    """ Convert an irc line to data that interpretor.py can understand """
    out = {}
    out['sender'], msgtype, rest = line[1:].split(' ', 2)
    if msgtype == 'PRIVMSG':
        out['type'] = 'message'
        out['channel'], out['message'] = rest.split(' :', 1)
        # TODO: Should this be in?
        out['sendernick'], out['senderident'] = out['sender'].split('!', 1)
    # elif msgtype == ''
    else:
        raise NotImplementedError
    return out


def data_to_irc(data):
    if data['type'] == 'message':
        return 'PRIVMSG {0[channel]} :{0[message]}'.format(data)
    else:
        raise NotImplementedError('type {} not implemented'.format(data['type']))