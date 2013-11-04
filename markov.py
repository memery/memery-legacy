import subprocess, common

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
    qualified = list(filter(lambda x: myname not in x, sentences))
    if qualified:
        choice = qualified[0]
        sentences.remove(choice)
        return choice, sentences
    else:
        raise ValueError('Finns inga kvalificerade meningar')
