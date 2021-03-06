import common
import json, re

def help():
  return {'authors':     ['nycz', 'jocke-l'],
          'years':       ['2012'],
          'version':     '1.0',
          'description': 'Exekverar Haskellkod.',
          'argument':    '<giltig Haskellkod>'}

def run(nick, args):
  return re.sub('\s+', ' ', haskell(args))

def haskell(args):
  data = common.read_url("http://tryhaskell.org/haskell.json?method=eval&expr=", args)

  jsondata = json.JSONDecoder(strict=False).decode(data)

  if 'result' in jsondata and jsondata['result'] and 'type' in jsondata:
    return '{result} :: {type}'.format(**jsondata)
  elif 'type' in jsondata:
    return jsondata['type']
  elif 'result' in jsondata:
    return jsondata['result']
  elif 'error' in jsondata:
    return jsondata['error'].replace(' +',' ')
  elif 'exception' in jsondata:
    return jsondata['exception']
