from sys import stdin

current_file = ''
for line in stdin:
    p = line.strip().split(':')
    if p[0] != current_file:
        print
        print p[0]
        current_file = p[0]
    print '%02d: %s' % (int(p[1]), p[2])
