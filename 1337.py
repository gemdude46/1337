#!/usr/bi/env python

import htmlparse, curses, urllib, css_constants
from gpw import *

import locale
locale.setlocale(locale.LC_ALL, '')
encoding = locale.getpreferredencoding()
del locale

browser_name = '1337'

def cp(fg, bg):
    return curses.color_pair(fg + bg * 8)

black = 0
red = 1
green = 2
yellow = 3
blue = 4
magenta = 5
cyan = 6
white = 7

URI = None
document = None

def goto(uri):
    global URI, document
    URI = uri
    document = htmlparse.parse(GET(uri))
    document.uri = uri

mouse = [50, 1]

scrmap = None
osz = (0,0)

def app(stdscr):
    global scrmap, osz, URI
    
    focus = 'mouse'
    
    goto('http://neelu.co')
    
    stdscr.nodelay(True)
    
    eval_cache = {}
    
    if curses.has_colors() and curses.COLORS >= 8 and curses.COLOR_PAIRS >= 64:
        for i in range(8):
            for j in range(8):
                if i + j:
                    curses.init_pair(i + j * 8, i, j)
    
    while stdscr.getch() > -1: pass
    while True:
        ender = False
        document.cssize = size = stdscr.getmaxyx()
        
        if tuple(size) != osz:
            osz = tuple(size)
            scrmap = [[{} for _ in xrange(size[0]-4)] for _ in xrange(size[1])]
        
        kin = -2
        while kin != -1:
            if kin == 27:
                focus = 'mouse'
            if focus == 'mouse':
                curses.curs_set(False)
                if kin == curses.KEY_UP:
                    mouse[1] -= 1
                if kin == curses.KEY_DOWN:
                    mouse[1] += 1
                if kin == curses.KEY_LEFT:
                    mouse[0] -= 1
                if kin == curses.KEY_RIGHT:
                    mouse[0] += 1
                if kin in (curses.KEY_ENTER, 10, 13) and mouse[1] == 1 and mouse[0] > 10 and mouse[0] < size[1] - 10:
                    focus = 'uri'
            elif focus == 'uri':
                curses.curs_set(True)
                mouse[1] = 1
                if mouse[0] > len(URI) + 11:
                    mouse[0] = len(URI) + 11
                cpos = mouse[0] - 11
                if kin == curses.KEY_LEFT:
                    mouse[0] -= 1
                elif kin == curses.KEY_RIGHT:
                    mouse[0] += 1
                elif kin == curses.KEY_BACKSPACE:
                    mouse[0] -= 1
                    URI = URI[:cpos-1] + URI[cpos:]
                elif kin in (curses.KEY_ENTER, 10, 13):
                    ender = True
                    focus = 'mouse'
                elif kin > 0:
                    p = curses.unctrl(kin)
                    if len(p) == 1:
                        URI = URI[:cpos] + p + URI[cpos:]
                        mouse[0] += 1
            kin = stdscr.getch()
        
        if   mouse[0] < 0          : mouse[0] = 0
        elif mouse[0] > size[1] - 1: mouse[0] = size[1] - 1
        if   mouse[1] < 1          : mouse[1] = 1
        elif mouse[1] > size[0] - 1: mouse[1] = size[0] - 1
        
        document.tick()
        
        stdscr.addstr(0, 0, ('{:^%i}' % size[1]).format(browser_name), curses.A_BOLD | cp(white, blue))
        stdscr.addstr(1, 0, (' [<=] [>] [{:<%i}|reload] ' % (size[1] - 20)).format(URI), curses.A_BOLD | cp(black, white))
        stdscr.addstr(2, 0, ('{:^%i}' % size[1]).format(document.getTitle()), curses.A_UNDERLINE | cp(black, white))
        
        try: stdscr.addstr(size[0]-1, 0, ' ' * size[1], cp(black, white))
        except curses.error: pass
        
        def setpxcb(xy, c, f, e):
            if xy[0] >= 0 and xy[1] >= 0 and xy[0] < size[1] and xy[1] < size[0] - 4:
                scrmap[xy[0]][xy[1]]['e'] = e
                cpn = curses.pair_number(scrmap[xy[0]][xy[1]].get('a', 0))
                f = f.format(fg = cpn % 8, bg = cpn // 8)
                if f in eval_cache:
                    fp = eval_cache[f]
                else:
                    eval_cache[f] = eval(f)
                    fp = eval_cache[f]
                scrmap[xy[0]][xy[1]]['a'] = fp
                stdscr.addstr(xy[1]+3, xy[0], c.encode(encoding), fp)
        
        
        for x in range(size[1]):
            for y in range(size[0]):
                setpxcb((x,y), ' ', 'cp(0,%s)'%document.__dict__.get('bgc', 'white'), document)
        
        document.getElementsByTagName('body')[0].render(setpxcb, [0,0])
        
        if focus == 'mouse':
            try:
                mp = (
                    css_constants.cursors.get(scrmap[mouse[0]][mouse[1]-3]['e'].CSS().get('cursor'), css_constants.cursors['default']) 
                        if mouse[1] > 2 and mouse[1] < size[0] - 1 else 
                            css_constants.cursors['default']
                     )
                
                stdscr.addstr(mouse[1], mouse[0], mp, cp(black, white))
            except curses.error: pass
        else:
            stdscr.move(mouse[1], mouse[0])
        
        if ender: goto(URI)
        stdscr.refresh()

if __name__ == '__main__': curses.wrapper(app)
