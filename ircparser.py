
import interpretor

class In_Message:
    def from_raw(self, line):
        sender, msgtype, rest = line[1:].split(' ', 2)
        self.sender, self.senderident = sender.split('!', 1)
        self.recipient, self.message = rest.split(' :', 1)
        return self

    def __init__(self):
        pass

class Out_Messages:
    def to_raw(self):
        messages = self.messages

        if len(messages) > 5:
            messages = ['fler än fem rader i ett meddelande ({} st rader), kickad för flooding är inte ok'.format(len(responses))]\
                       + messages[:4]

        return '\n'.join('PRIVMSG {} :{}'.format(self.recipient, msg) for msg in messages)

    def __init__(self, recipient, messages):
        self.recipient = recipient
        if type(messages) != type([]):
            self.messages = [messages]
        else:
            self.messages = messages

class Out_Mode:
    def to_raw(self):
        return 'MODE {} {} {}'.format(self.channel, self.mode*len(self.names), ' '.join(self.names))

    def __init__(self, channel, mode, names):
        self.channel = channel
        self.mode = mode
        self.names = names


def irc_to_data(line):
    """ Convert an irc line to data that interpretor.py can understand """
    msgtype = line[1:].split(' ', 2)[1]

    if msgtype == 'PRIVMSG':
        return In_Message().from_raw(line)
    else:
        raise NotImplementedError

def data_to_irc(data):
    if data:
        try:
            return data.to_raw()
        except AttributeError:
            raise NotImplementedError('type {} not implemented'.format(type(data)))


def parse(raw_line, state, settings):
    # 1. Convert a raw irc message to interpretor-compatible data
    try:
        indata = irc_to_data(raw_line)
    except NotImplementedError:
        return None

    # 2. Parse the data to a response
    response = interpretor.main_parse(indata, state['nick'], settings)

    # 3. Return the response in raw form to send it to irc
    return data_to_irc(response)



