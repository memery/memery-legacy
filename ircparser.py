
from time import time
import interpretor, common

class In_Message:
    def from_raw(self, line):
        sender, msgtype, rest = line[1:].split(' ', 2)
        self.sender, self.senderident = sender.split('!', 1)
        self.recipient, self.message = rest.split(' :', 1)
        return self

    def log(self):
        common.log('<{}!{}> {}'.format(self.sender, self.senderident, self.message), self.recipient)

    def __init__(self):
        pass

class In_Join:
    def from_raw(self, line):
        sender, msgtype, rest = line[1:].split(' ', 2)
        self.sender, self.senderident = sender.split('!', 1)
        self.channel = rest
        return self

    def log(self):
        common.log('-- {} ({}) has joined {}'.format(self.sender, self.senderident, self.channel), self.channel)

    def __init__(self):
        pass

class In_Part:
    def from_raw(self, line):
        sender, msgtype, rest = line[1:].split(' ', 2)
        self.sender, self.senderident = sender.split('!', 1)
        if ' :' in rest: self.channel, self.message = rest.split(' :', 1)
        else: self.channel, self.message = rest, ''
        return self

    def log(self):
        common.log('-- {} ({}) has left {} ({})'.format(self.sender, self.senderident, self.channel, self.message), self.channel)

    def __init__(self):
        pass

class In_Kick:
    def from_raw(self, line):
        sender, msgtype, rest = line[1:].split(' ', 2)
        self.sender, self.senderident = sender.split('!', 1)
        self.channel, self.kickee, reason = rest.split(' ', 2)
        self.reason = reason[1:]
        return self

    def log(self):
        common.log('-- {}!{} has kicked {} from {} ({})'.format(self.sender, self.senderident, self.kickee, self.channel, self.reason), self.channel)

    def __init__(self):
        pass

class In_Quit:
    def from_raw(self, line):
        sender, msgtype, rest = line[1:].split(' ', 2)
        self.sender, self.senderident = sender.split('!', 1)
        self.channel, self.message = ("irc", rest[1:])
        return self

    def log(self):
        common.log('-- {} ({}) has quit {} ({})'.format(self.sender, self.senderident, self.channel, self.message), self.channel)

    def __init__(self):
        pass

class In_Mode:
    def from_raw(self, line):
        sender, msgtype, rest = line[1:].split(' ', 2)
        self.sender, self.senderident = sender.split('!', 1)
        self.channel, self.modes, nicks = rest.split(' ', 2)
        self.nicks = nicks.split()
        return self

    def log(self):
        common.log('-- Mode {} [{} {}] by {}'.format(self.channel, self.modes, ' '.join(self.nicks), self.sender), self.channel)

    def __init__(self):
        pass

class Out_Messages:
    def to_raw(self):
        messages = self.messages

        if len(messages) > 5:
            messages = ['fler än fem rader i ett meddelande ({} st rader), kickad för flooding är inte ok'.format(len(responses))]\
                       + messages[:4]

        return '\n'.join('PRIVMSG {} :{}'.format(self.recipient, msg) for msg in messages)

    def log(self):
        for msg in self.messages:
            common.log('<{}> {}'.format(self.sender, msg), self.recipient)

    def __init__(self, sender, recipient, messages):
        self.sender = sender
        self.recipient = recipient
        if type(messages) != type([]):
            self.messages = [messages]
        else:
            self.messages = messages

class Out_Mode:
    def to_raw(self):
        return 'MODE {} {} {}'.format(self.channel, self.mode*len(self.names), ' '.join(self.names))

    def log(self):
        common.log('-- Mode {} [{} {}] by {}'.format(self.channel, self.mode, ' '.join(self.names), self.sender), self.channel)

    def __init__(self, sender, channel, mode, names):
        self.sender = sender
        self.channel = channel
        self.mode = mode
        self.names = names


def irc_to_data(line):
    """ Convert an irc line to data that interpretor.py can understand """
    msgtype = line.split()[1]

    if msgtype == 'PRIVMSG':
        return In_Message().from_raw(line)
    elif msgtype == 'JOIN':
        return In_Join().from_raw(line)
    elif msgtype == 'PART':
        return In_Part().from_raw(line)
    elif msgtype == 'KICK':
        return In_Kick().from_raw(line)
    elif msgtype == 'QUIT':
        return In_Quit().from_raw(line)
    elif msgtype == 'MODE' and line.split()[2][0] == '#': # channel modes
        return In_Mode().from_raw(line)
    else:
        raise NotImplementedError

def data_to_irc(data):
    try:
        return data.to_raw()
    except AttributeError:
        raise NotImplementedError('type {} not implemented'.format(type(data)))


def parse(raw_line, state, settings):
    # 1. Convert a raw irc message to interpretor-compatible data
    try:
        indata = irc_to_data(raw_line)
    except NotImplementedError:
        common.log('>> ' + raw_line)
        return None

    # 2. Try to log the incoming message well-formatted
    #    Exceptions are okay at this stage, irc.py will catch
    #    them and log the line properly anyway!
    indata.log()

    # 3. Parse the data to a response
    if not state['quiet']:
        response = interpretor.main_parse(indata, state, state['nick'], settings)
        if not response:
            return None

        # 4. Try to log the outgoing response well-formatted
        #    Exceptions are okay at this stage, irc.py will catch
        #    them and log the line properly anyway!
        response.log()

        # (log this response in the anti-flood state log)
        floodident = '{}!{}'.format(indata.sender, indata.senderident)
        if floodident not in state['anti-flood']:
            state['anti-flood'][floodident] = []
        state['anti-flood'][floodident].append(time())

        # 5. Return the response in raw form to send it to irc
        return data_to_irc(response)



