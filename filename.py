from random import choice

print 'qa%s.html' % (''.join(choice('0123456789ABCDEF') for i in range(16)))
