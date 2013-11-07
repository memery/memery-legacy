import subprocess, common
from re import sub

# `run_cmarkov` gathers some randomly generated sentences and
# returns them in a list.
def run_cmarkov(myname, settings, corpus):
    # Tries to get sentences thrice if no qualified sentences appear
    for _ in range(0,3):
        try:
            output = subprocess.check_output([settings['markov']['executable'],
                                              str(settings['markov']['quantity']),
                                              str(settings['markov']['pickiness']),
                                              corpus])
        except (OSError, subprocess.CalledProcessError) as e:
            common.log('Gick inte att köra markov! Anledning: {}'.format(str(e)), 'error')
            return None

        sentences = output.decode('UTF-8').split('\n')

        # Strip out any accidental nudges and don't use lines directed to me
        qualified = [sub(r'^[^ ]+[:,] ', '', s) for s in sentences if myname not in s]
        if qualified:
            return qualified
    else:
        raise ValueError('Hittade inga kvalificerade meningar i {}'.format(corpus))

