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
    #return '\n<!doctype html>\n<html>\n<head>\n    <title>Example Domain</title>\n\n    <meta charset="utf-8" />\n    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />\n    <meta name="viewport" content="width=device-width, initial-scale=1" />\n    <style type="text/css">\n    body {\n        background-color: #f0f0f2;\n        margin: 0;\n        padding: 0;\n        font-family: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;\n        \n    }\n    div {\n        width: 600px;\n        margin: 5em auto;\n        padding: 50px;\n        background-color: #fff;\n        border-radius: 1em;\n    }\n    a:link, a:visited {\n        color: #38488f;\n        text-decoration: none;\n    }\n     </style>    \n</head>\n\n<body>\n<div>Lol</div> <div>\n    <h1>Example Domain</h1>\n    <p>This domain is established to be used for illustrative examples in documents. You may use this\n    domain in examples without prior coordination or asking for permission.</p>\n    <p><a href="http://www.iana.org/domains/example">More information...</a></p>\n</div>\n</body>\n</html>'
    if uri.startswith('file://'):
        f = open(uri[7:], 'r')
        c = f.read()
        f.close()
    if uri.startswith('http://') or uri.startswith('https://'):
        try: r = requests.get(uri)
        except KeyboardInterrupt: raise
        except: return '' if rmt else errpage.format(uri)
        if rmt and rmt != r.headers.get('content-type'):
            return ''
        c = r.text if r.headers.get('content-type','text/plain').startswith('text/') else r.content
    return c
