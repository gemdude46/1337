from HTMLParser import HTMLParser
import DOM
from html_constants import *

cur = None

class parser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        global cur
        a = {}
        for attr in attrs:
            a[attr[0]] = attr[1]
        cur = DOM.Element(cur, tag, a)
        if tag in self_closing_tags:
            cur.parent.write(cur)
            cur = cur.parent
    
    def handle_endtag(self, tag):
        global cur
        oc = cur
        try:
            while cur.tag != tag:
                cur = cur.parent
            cur = cur.parent
            if cur is None: raise AttributeError("cur is None")
        except AttributeError:
            cur = oc
            return
        cur.write(oc)
    
    def handle_data(self, data):
        global cur
        cur.write(data)

def parse(html):
    global cur
    cur = DOM.Element(None, 'document')
    parser().feed(html)
    while cur.tag != 'document':
        cur.parent.write(cur)
        cur = cur.parent
    if not cur.getElementsByTagName('body'):
        return parse('<html><body>%s</body></html>' % html)
    return cur
