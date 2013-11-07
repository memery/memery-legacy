import subprocess, common
from re import sub

# `run_cmarkov` gathers some randomly generated sentences and
# returns them in a list.
def run_cmarkov(settings, corpus):
    try:
        output = subprocess.check_output([settings['markov']['executable'],
                                          str(settings['markov']['quantity']),
                                          str(settings['markov']['pickiness']),
                                          corpus])
    except subprocess.CalledProcessError:
        log('Gick inte att köra markov', file='error')
        return None

    return output.decode('UTF-8').split('\n')

def markov(myname, sentences):
    # Strip out any accidental nudges and don't use lines directed to me
    qualified = [sub(r'^[^ ]+[:,] ', '', s) for s in sentences if myname not in s]

    try:
        choice = sentences.pop(0)
    except IndexError:
        raise ValueError('Finns inga kvalificerade meningar')

    return choice, sentences
