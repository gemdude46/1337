import string
from css_constants import *

scrsize = (80, 24)

def memodict(f):
    """ Memoization decorator for a function taking a single argument """
    class memodict(dict):
        def __missing__(self, key):
            ret = self[key] = f(key)
            return ret 
    return memodict().__getitem__

def setscrsize(ns):
    global scrsize
    scrsize = ns

def parse(css):
    css = css.strip()
    ss = []
    while css:
        q = ''
        while css and css[0] != '{':
            q += css[0]
            css = css[1:]
        css = css[1:]
        
        r = ''
        while css and css[0] != '}':
            r += css[0]
            css = css[1:]
        css = css[1:]
        
        ss.append((
            q.strip(),
            [ [ ri.strip() for ri in rp.split(':') ] for rp in r.split(';') if rp.strip() ]
        ))
    
    return ss

def color(css, df='black'):
    
    if type(css) is tuple:
        cd = 999
        for c in tcolors.keys():
            d = abs(c[0] - css[0]) + abs(c[1] - css[1]) + abs(c[2] - css[2])
            if d < cd:
                cd = d
                clr = tcolors[c]
                
        return clr
    
    css = css.lower()
    
    if css.startswith('#'):
        if len(css) == 4:
            return color('#{0[1]}{0[1]}{0[2]}{0[2]}{0[3]}{0[3]}'.format(css))
        elif len(css) == 7:
            return color((int(css[1:3], 16),int(css[3:5], 16),int(css[5:], 16)))
    
    if (css.startswith('rgb(') or css.startswith('rgba(')) and css.endswith(')'):
        return color(tuple([int(i) for i in css[1+css.index('('):-1].split(',') if '.' not in i][:3]))
    
    if css in csscolors.keys():
        return color(csscolors[css])
    
    return df
    
def evalsize(css, parent=0, d='v', auto=None):
    css = css.strip()
    if css == '0': return 0
    if css == 'auto': return parent if auto is None else auto
    
    try:
        numeric = '0123456789-.'
        for i,c in enumerate(css):
            if c not in numeric:
                break
        
        n = float(css[:i])
        u = css[i:]
        
        if u == 'em' or u == 'ch' or u == 'pc': return n
        if u == 'px' or u == 'pt': return n / charsize[d == 'v']
        if u == 'ex': return n / 2.0
        if u == '%': return n * parent / 100.0
        if u == 'vh': return n * scrsize[1] / 100.0
    except: pass
    return 0

def CRPrule(t):
    n = CRPsubrule(t)
    if t:
        if t.pop(0) != ',':
            raise TypeError
        return ('or', n, CRPrule(t))
    return n

def CRPsubrule(t):
    n = CRPchain(t)
    if t and t[0] == '>':
        t.pop(0)
        return ('parent', n, CRPsubrule(t))
    return n

def CRPchain(t):
    n = ('all',)
    while t and (t[0][0] == 'i' or t[0] in ('.','#','*')):
        s = t.pop(0)
        if s == '.':
            n = ('and', n, ('class', t.pop(0)[1:]))
        if s == '#':
            n = ('and', n, ('id', t.pop(0)[1:]))
        if s[0] == 'i':
            n = ('and', n, ('tag', s[1:]))
    return n

@memodict
def parserule(rule):
    rule = rule.lower()
    ci = 0
    idch = string.ascii_lowercase + string.digits + '-_'
    tks = []
    while ci < len(rule):
        if rule[ci] in string.whitespace:
            ci += 1
            continue
        if rule[ci] in idch:
            s = 'i'
            while ci < len(rule) and rule[ci] in idch:
                s += rule[ci]
                ci += 1
            tks.append(s)
            continue
        tks.append(rule[ci])
        ci += 1
    
    try: return CRPrule(tks)
    except KeyboardInterrupt: raise
    except: return ('tag', '~~fail~~')
