def help():
    return {'authors': ['jocke-l'],
            'years': ['2014'],
            'version': '1.2',
            'description': 'Minutes-to-hours converter',
            'argument': '<minutes>'}

def run(nick, args):
    try:
        return '{}: {}'.format(nick, m2h(args))
    except ValueError:
        return '{}: invalid argument'.format(nick)

def m2h(m):
    def pluralise(amount, unit):
        return ('{} {}'.format(amount, unit + ('s' if amount > 1 else ''))
                if amount else '')

    if not isinstance(m, int):
        m = int(m)

    hours, minutes = divmod(m, 60)

    return ' and '.join(filter(bool, (pluralise(hours, 'hour'),
                                      pluralise(minutes, 'minute')))) or '^'
