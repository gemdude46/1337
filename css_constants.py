import json

tcolors = {
    (0,0,0) : 'black',
    (176,0,0) : 'red',
    (0,176,0) : 'green',
    (0,0,176) : 'blue',
    (0,176,176) : 'cyan',
    (176,176,0) : 'yellow',
    (176,0,176) : 'magenta',
    (230,230,230) : 'white'
}

csscolorsf = open('colors.json', 'r')
csscolors = json.loads(csscolorsf.read())
csscolorsf.close()

cursors = {
    'all-scroll': 'm',
    'cell': '+',
    'crosshair': '+',
    'default': '^',
    'grab': 'W',
    'grabbing': 'm',
    'help': '?',
    'move': 'm',
    'not-allowed': '0',
    'pointer': 'h',
    'text': 'I',
    'wait': unichr(0x2573),
    'zoom-in': 'Q',
    'zoom-out': 'q',
}

charsize = (8,12)
