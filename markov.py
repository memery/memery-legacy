# `run_cmarkov` gathers some randomly generated sentences and
# returns them in a list.
def run_cmarkov(settings, pickiness, corpus):
    try:
        output = subprocess.check_output([settings['markov']['executable'], str(settings['markov']['pickiness'])])
    except CalledProcessError:
        print('Error: cmarkov kunde inte köras')
        return None

    return output.split('\n')


def markov(myname, sentences):
    qualified = filter(lambda x: myname not in x, sentences)
    if qualified:
        choice = qualifieds[0]
        sentences.remove(choice)
        return choice, sentences
    else:
        raise ValueError('Det finns ingen mening som inte innehåller `myname`')

