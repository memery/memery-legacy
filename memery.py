from imp import reload
from time import time
import common, irc

def main():
    startuptime = time()
    # Crash like hell if the config is crap!
    settings = common.read_config('config')
    # Kind of like state
    message = ''
    while True:
        result = irc.run(message, settings, startuptime)
        message = ''
        if result == 'reconnect':
            continue
        elif result == 'restart':
            try:
                reload(irc)
            except Exception as e:
                message = str(e)
            continue
        else:
            break


if __name__ == '__main__':
    main()
