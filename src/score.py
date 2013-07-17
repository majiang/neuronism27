import datetime
table = range(4)

def get_players(dat):
    ret = [int(e) for e in dat]
    if len(ret) - 4:
        raise ValueError('invalid number of players')
    for i in table:
        if ret[i] <= 0:
            ret[i] = 0
            continue
        for j in range(i + 1, 4):
            if ret[i] == ret[j]:
                raise ValueError('duplicate player: %d,%d,%d,%d' % (ret[0], ret[1], ret[2], ret[3]))
    return ret

def get_points(dat):
    ret = [int(float(e)+0.5) for e in dat]
    if len(ret) - 4:
        raise ValueError('invalid number of points')
    s = sum(ret)
    if s <= 910:
        raise ValueError('too small: %d = sum (%d,%d,%d,%d)' % (s, ret[0], ret[1], ret[2], ret[3]))
    if 1090 <= s:
        raise ValueError('too large: %d = sum (%d,%d,%d,%d)' % (s, ret[0], ret[1], ret[2], ret[3]))
    if not (ret[0] >= ret[1] >= ret[2] >= ret[3]):
        raise ValueError ('points confict with rank: (%d, %d, %d, %d)' % (ret[0], ret[1], ret[2], ret[3]))
    return ret

def get_date(dat):
    digits = '0123456789'
    s = ['', '', '']
    p = 0
    while dat[p] not in digits:
        p += 1
    for i in range(3):
        try:
            while dat[p] in digits:
                s[i] += dat[p]
                p += 1
            while dat[p] not in digits:
                p += 1
        except:
            try:
                s = [int(e) for e in s]
            except:
                raise ValueError('not a date: %d', dat)
            return datetime.date(int(s[0]), int(s[1]), int(s[2]))
    raise ValueError('not a date: %d', dat)

def valid(line):
    dat = line.strip().split(',')
    if len(dat) < 9:
        raise ValueError('less than 9 column: %s' % line.strip())
    get_players(dat[0:4])
    get_points(dat[4:8])
    return get_date(dat[8])
