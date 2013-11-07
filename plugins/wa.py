import xml.etree.ElementTree as ET
import common, re

def help():
    return { 'authors':     ['jocke-l'],
             'years':       ['2013'],
             'version':     '1.0',
             'description': 'Interface to the WolframAlpha™ API.',
             'argument':    '<query> [| <approx|exact>]' }

def run(nick, args):
    return '{0}: {1}'.format(nick, query(args))


def query(args):
    try:
        appid = common.read_lineconf(common.read_file('wolframalpha-api-key'))[0]
    except (IOError, IndexError):
        raise IOError('No appid to WolframAlpha™ was found.')

    m = re.search(r'^(.*?)( \| (.*?))?$', args)

    expr = m.group(1)
    xml = common.read_url('http://api.wolframalpha.com/v2/query?appid={0}&input='.format(appid), expr)

    output_type = 'approx' if not m.group(3) else m.group(3)

    root = ET.fromstring(xml)

    didyoumeans = root.find('didyoumeans')
    if didyoumeans:
        return 'Did you mean: \'{0}\'?'.format(didyoumeans.find('didyoumean').text)

    title = {'approx': 'Decimal approximation',
             'exact':  'Exact result'}

    for pod in root:
        if pod.tag == 'pod':
            if pod.attrib['title'] == 'Result' or pod.attrib['title'] == 'Value' or pod.attrib['title'] == title[output_type]:
                return pod.find('subpod').find('plaintext').text

    return 'WolframAlpha™ doesn\'t have the answer.'
