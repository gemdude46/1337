import requests

errpage = '''
<!DOCTYPE html>
<html>
    <head>
        <title> 1337 - ERROR </title>
    </head>
    <body>
        <h1 style="color: red;" > Uh-Oh, an error occurred! </h1>
        At requests.get(uri)<br><br>
        <a href="{}">Reload</a>
    </body>
</html>
'''

def GET(uri, rmt=None):
    if uri.startswith('file://'):
        f = open(uri[7:], 'r')
        c = f.read()
        f.close()
    if uri.startswith('http://') or uri.startswith('https://'):
        try: r = requests.get(uri, headers={'User-Agent': '1337/DEV'})
        except KeyboardInterrupt: raise
        except: return '' if rmt else errpage.format(uri)
        if rmt and rmt != r.headers.get('content-type'):
            return ''
        c = r.text if r.headers.get('content-type','text/plain').startswith('text/') else r.content
    return c
