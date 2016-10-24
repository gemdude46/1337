import cssparse, math, random
from gpw import *
from urlparse import urljoin

master_css_file = open('master.css', 'r')
master_css_raw = master_css_file.read()
master_css_file.close()
master_css = cssparse.parse(master_css_raw)

class Element:
    def __init__(self, parent, tag, attrs={}):
        self.age = 0
        self.parent = parent
        self.I_did_an_errorz = False
        self.root = parent.root if parent else self 
        self.tag = tag.lower()
        self.attrs = attrs
        self.content = []
        self.match_cache = {}
        self.csr_start_render = (0,0)
        self.css = {'display':'block'} if tag == 'document' else self.CSS()
        self.css_cache = {} if tag == 'document' else None
        self.GET_cache = {} if tag == 'document' else None
        self.rdleft = self.rdright = self.rdtop = self.rdbottom = 0
        self.margin = [0,0,0,0]
        
    
    def GET(self, uri, rmt=None):
        if uri in self.GET_cache:
            return self.GET_cache[uri]
        c = GET(uri, rmt)
        self.GET_cache[uri] = c
        return c
    
    def write(self, con):
        if self.content and type(con) in (str, unicode) and type(self.content[-1]) in (str, unicode): self.content[-1] += con
        else: self.content.append(con)
    
    def string(self, indents):
        i = 0
        s = u''
        while i < len(self.content):
            s += unichr(0x2502) * indents
            s += unichr(0x251c)
            if type(self.content[i]) in (str, unicode): s += u' '.join(self.content[i].split())
            else: s += u'<{} {}>\n{}'.format(self.content[i].tag,
                                            u' '.join([u'{}="{}"'.format(a, self.content[i].attrs[a]) for a in self.content[i].attrs.keys()]),
                                            self.content[i].string(indents+1))
            s += '\n'
            i += 1
        return s.strip()
    
    def __str__(self):
        return u'<{}>\n{}'.format(self.tag, self.string(0)).encode('UTF-8')
    
    def children(self):
        return [i for i in self.content if isinstance(i, Element)]
    
    def getElementById(self, id_):
        if self.attrs.get('id') == id_: return self
        for kid in self.children():
            res = kid.getElementById(id_)
            if res: return res
    
    def getElementsByTagName(self, tag):
        if self.tag == tag: return [self]
        arr = []
        for kid in self.children():
            arr.extend(kid.getElementsByTagName(tag))
        return arr
    
    def positionalparent(self):
        return self.parent if self.parent.positioned() else self.parent.positionalparent()
    
    def getTitle(self):
        try: return self.getElementsByTagName('title')[0].content[0]
        except IndexError: return ''
    
    def getAllCSS(self):
        if 'all css' in self.__dict__:
            return self.__dict__['all css']
        css = []
        for sheet in ([i.content for i in self.getElementsByTagName('style')] + 
                        [(self.GET(urljoin(self.uri, l.attrs['href']), 'text/css'),) for l in self.getElementsByTagName('link') 
                        if l.attrs.get('rel') == 'stylesheet' and 'href' in l.attrs]):
            if sheet:
                cache = self.css_cache.get(sheet[0])
                if not cache:
                    cache = self.css_cache[sheet[0]] = cssparse.parse(sheet[0])
                css.extend(cache)
        self.__dict__['all css'] = css
        return css
    
    def tick(self, rsp):
        self.age += 1
        if True:
            self.css = self.CSS()
        if self.tag == 'document':
            del self.__dict__['all css']
            cssparse.setscrsize((self.cssize[1], self.cssize[0]))
        for kid in self.children():
            kid.tick(rsp)
        
    def click(self, rsp):
        if self.tag == 'a' and 'href' in self.attrs and not self.attrs['href'].startswith('#'):
            rsp.append('goto(%r)' % urljoin(self.root.uri, self.attrs['href']))
        if self.parent: self.parent.click(rsp)
    
    def matches(self, rule):
        if type(rule) is tuple:
            c = rule[0]
            if c == 'all':
                return True
                
            if c == 'and':
                return self.matches(rule[1]) and self.matches(rule[2])
            if c == 'or':
                return self.matches(rule[1]) or  self.matches(rule[2])
            
            if c == 'tag':
                return self.tag == rule[1]
            if c == 'id':
                return self.attrs.get('id', '').lower() == rule[1]
            if c == 'class':
                return rule[1] in self.attrs.get('class', '').lower().split()
            return False
        else:
            if rule in self.match_cache:
                return self.match_cache[rule]
            else:
                res = self.matches(cssparse.parserule(rule))
                self.match_cache[rule] = res
                return res
        
    
    def CSS(self):
        if self.tag[0] == '/': return {}
        CSS = self.parent.css.copy() if self.parent else {}
        for rule in master_css + self.root.getAllCSS() + cssparse.parse('*{%s}' %  self.attrs.get('style','')):
            
            if self.matches(rule[0]):
                for p in rule[1]:
                    if len(p) != 2: continue
                    if p[1] != 'inherit':
                        CSS[p[0]] = p[1]
        return CSS
    
    def block(self):
        return self.css.get('display') in ('block', 'list-item')
    
    def ablock(self):
        return self.block() or self.css.get('display') == 'inline-block'
    
    def positioned(self):
        return self.css.get('position') not in ('static', 'initial')
    
    def width(self):
        pw = self.parent.width() if self.parent else self.root.cssize[1]
        return cssparse.evalsize(self.css.get('width', 'auto' if self.block() or not self.ablock() else ('%rem' % (self.rdright - self.rdleft))),
            pw, 'h', (pw - self.margin[1] - self.margin[3]))
    
    def iwidth(self):
        return int(math.ceil(self.width()))
    
    def height(self):
        h = cssparse.evalsize(self.css.get('height', '%rem' % self.lnheight()),
            self.parent.lheight() if self.parent else self.root.cssize[0], 'v', 0)
        self.__dict__['l h'] = h
        return h
    
    def iheight(self):
        return int(math.ceil(self.height()))
    
    def lheight(self):
        return self.__dict__.get('l h', 1.0)
    
    def lnheight(self, est = -1):
        if self.css.get('display') == 'none': return 0
        h = 1
        est += 1
        while est < len(self.content):
            if isinstance(self.content[est], Element):
                if self.content[est].block() or self.content[est].tag == 'br':
                    break
                h = max(h, self.content[est].iheight() if self.content[est].ablock() else self.content[est].lnheight())
            est += 1
        return h
    
    def takenl(self, csr):
        if self.positioned(): return csr
        if not self.parent.ablock():
            return self.parent.takenl(csr)
        try: obji = self.parent.content.index(self)
        except ValueError: obji = 0
        lh = self.parent.lnheight(obji)
        csr[0] = self.parent.csr_start_render[0]
        csr[1] += lh
        return csr
    
    def render(self, setpx, csr):
        
        if self.tag == '/start': return csr
        
        margin = [0,0,0,0]
        
        rdleft = rdright = csr[0]
        rdtop = rdbottom = csr[1]
        
        oric = csr[:]
        
        try:
            if self.css.get('display') == 'none': return csr
            
            if self.block() and csr[0] != self.parent.csr_start_render[0]: self.takenl(csr)
            
            if self.css.get('position') == 'absolute':
                pp = self.positionalparent()
                csr = [
                    int(pp.rdleft + cssparse.evalsize(self.css.get('left', '0'), pp.width(), 'h')),
                    int(pp.rdtop  + cssparse.evalsize(self.css.get('top', '0'), pp.height(), 'v'))
                ]
                rdleft = rdright = csr[0]
                rdtop = rdbottom = csr[1]
            
            margin = self.css.get('margin').split()
            if len(margin) == 1:
                margin *= 4
            elif len(margin) == 2:
                margin *= 2
            elif len(margin) == 3:
                margin = [margin[0], margin[1], margin[2], margin[1]]
            elif len(margin) != 4:
                margin = [0,0,0,0]
            
            if 'margin-top'    in self.css: margin[0] = self.css['margin-top']
            if 'margin-right'  in self.css: margin[1] = self.css['margin-right']
            if 'margin-bottom' in self.css: margin[2] = self.css['margin-bottom']
            if 'margin-left'   in self.css: margin[3] = self.css['margin-left']
            
            
            margin = [
                int(math.ceil(cssparse.evalsize(margin[0], self.parent.height(), 'v', (self.parent.height()/2 - self.height()/2
                    if self.css.get('position') == 'absolute' else 0)))),
                int(math.ceil(cssparse.evalsize(margin[1], self.parent.width(), 'h', 0))),
                int(math.ceil(cssparse.evalsize(margin[2], self.parent.height(), 'v', 0))),
                int(math.ceil(cssparse.evalsize(margin[3], self.parent.width(), 'h', (self.parent.width()/2 - self.width()/2))))
            ]
            
            csr[0] += margin[3]
            csr[1] += margin[0]
            
            self.csr_start_render = csr[:] if self.ablock() else self.parent.csr_start_render
            
            if not self.block() and self.ablock(): csr[1] -= self.iheight() - 1
            
            if self.tag == 'br': return self.takenl(csr)
            
            bgc = cssparse.color(self.css.get('background-color'), False)
            
            if bgc and self.ablock():
                top = csr[1]
                left = csr[0]
                width = self.iwidth()
                height = self.iheight()
                for i in range(width):
                    for j in range(height):
                        setpx((left+i, top+j), ' ', 'cp(0,%s)' % bgc, self)
                if self.tag == 'body': self.root.bgc = bgc
                
            self.content.insert(0, Element(self, '/start'))
            
            lastel = self.content[0]
            
            for obj in self.content:
                if isinstance(obj, Element):
                    if not obj.positioned(): lastel = obj
                    csr = obj.render(setpx, csr)
                    
                    if csr[0] > rdright: rdright = csr[0]
                    if csr[0] < rdleft: rdleft = csr[0]
                    if csr[1] > rdbottom: rdbottom = csr[1]
                    if csr[1] < rdtop: rdtop = csr[1]
                else:
                    fa = ['cp({},{})'.format(cssparse.color(self.css['color']), '{bg}' if self.ablock() else (bgc or '{bg}'))]
                    
                    if self.css.get('font-weight') == 'bold':
                        fa.append('curses.A_BOLD')
                    if self.css.get('text-decoration'):
                        for i in self.css['text-decoration'].split():
                            if i == 'underline':
                                fa.append('curses.A_UNDERLINE')
                    
                    f = '|'.join(fa)
                    for c in u' '.join(obj.split()):
                        setpx(csr, c, f, self)
                        csr[0] += 1
                        
                        if csr[0] > rdright: rdright = csr[0]
                        if csr[0] >= self.width() + self.rdleft:
                            lastel.takenl(csr)
            
            if self.block(): self.takenl(csr)
            elif self.ablock(): csr[:] = [self.csr_start_render[0] + self.iwidth(), self.csr_start_render[1]]
            return csr
        
        except:
            self.I_did_an_errorz = True
            raise
        finally:
            if not self.I_did_an_errorz:
                self.rdleft = rdleft
                self.rdright = rdright
                self.rdtop = rdtop
                self.rdbottom = rdbottom
                
                csr[0] += margin[1]
                csr[1] += margin[2]
                
                self.margin = margin
                
                if self.content and isinstance(self.content[0], Element) and self.content[0].tag == '/start':
                    del self.content[0]
                
                if self.css.get('position') in ('absolute', 'fixed'): return oric
