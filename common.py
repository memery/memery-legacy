from urllib.parse import quote
from urllib.request import Request, urlopen

def url_request(url):
    req = Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 memery')
    return req
