"""Đọc số thành chữ tiếng Việt (cùng thuật toán với bản JS/VBA)."""
import re
U = ['không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín']


def _r3(n, full, linh):
    h, t, u = n // 100, n % 100 // 10, n % 10
    p = []
    if h or full:
        p.append(U[h] + ' trăm')
    if t > 1:
        p.append(U[t] + ' mươi')
        p.append('mốt' if u == 1 else 'lăm' if u == 5 else U[u] if u else '')
    elif t == 1:
        p.append('mười')
        p.append('lăm' if u == 5 else U[u] if u else '')
    elif u:
        if h or full:
            p.append(linh)
        p.append(U[u])
    return ' '.join(x for x in p if x)


def _gn(i, ng, ty):
    return '' if i == 0 else ng if i == 1 else 'triệu' if i == 2 else ty if i == 3 else _gn(i - 3, ng, ty) + ' ' + ty


def _int2w(s, linh, ng, ty):
    s = s.lstrip('0') or '0'
    if s == '0':
        return U[0]
    g = []
    e = len(s)
    while e > 0:
        g.append(int(s[max(0, e - 3):e])); e -= 3
    out, st = [], False
    for i in range(len(g) - 1, -1, -1):
        if g[i]:
            out.append((_r3(g[i], st, linh) + ' ' + _gn(i, ng, ty)).strip()); st = True
    return ' '.join(out)


def _parse(s, vn):
    s = re.sub(r'\s', '', str(s)); neg = bool(re.match(r'^[-−–]', s)); s = re.sub(r'^[-+−–]', '', s)
    th, de = ('.', ',') if vn else (',', '.')
    p = s.split(de)
    if len(p) > 2:
        return None
    i, f = p[0].replace(th, ''), (p[1] if len(p) > 1 else '')
    if not re.fullmatch(r'\d+', i) or (f and not re.fullmatch(r'\d+', f)):
        return None
    return neg, i, f


def docso(v, vn=True, linh='linh', ng='nghìn', ty='tỷ', cap='f', suffix=''):
    n = _parse(v, vn)
    if not n:
        return None
    neg, i, f = n
    r = ('âm ' if neg else '') + _int2w(i, linh, ng, ty) + (' phẩy ' + ' '.join(U[int(d)] for d in f) if f else '') + suffix
    return r.upper() if cap == 'u' else r[0].upper() + r[1:] if cap == 'f' else r


def convert_text(text, vn=True, linh='linh', ng='nghìn', ty='tỷ'):
    def f(m):
        r = docso(m.group(0), vn, linh, ng, ty, 'n')
        return m.group(0) if r is None else r
    return re.sub(r'\d[\d.,]*\d|\d', f, text)
