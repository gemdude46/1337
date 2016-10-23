from htmlentitydefs import name2codepoint
import sys, time
for c in u'\n'.join([u'%s: %s' % (i, unichr(name2codepoint[i])) for i in name2codepoint.keys()]):
 sys.stdout.write(c)
 time.sleep(0.03)
