"""Lõi gõ tiếng Việt (Telex/VNI). Không phụ thuộc Windows nên kiểm thử được ở mọi nơi."""
import re
import unicodedata as ud

FIN = re.compile(r'^[aeiouyăâêôơư]*(c|ch|m|n|ng|nh|p|t)?$')

TONE = {'s': '\u0301', 'f': '\u0300', 'r': '\u0309', 'x': '\u0303', 'j': '\u0323'}
VT = {'1': 's', '2': 'f', '3': 'r', '4': 'x', '5': 'j'}
TONES = set(TONE.values())
CIRC = {'a': 'â', 'e': 'ê', 'o': 'ô'}
INV = {'â': 'a', 'ê': 'e', 'ô': 'o', 'ă': 'a', 'ơ': 'o', 'ư': 'u'}
VOW = 'aeiouyăâêôơư'


def split(w):
    t = None
    out = []
    for c in ud.normalize('NFD', w):
        if c in TONES:
            t = c
        else:
            out.append(c)
    return ud.normalize('NFC', ''.join(out)), t


def compose(b, t, nw):
    if not t:
        return b
    L = b.lower()
    s = 0
    if L[:2] == 'qu' and len(L) > 2:
        s = 2
    elif L[:2] == 'gi' and len(L) > 2 and L[2] in VOW:
        s = 2
    i = s
    while i < len(L) and L[i] not in VOW:
        i += 1
    j = i
    while j < len(L) and L[j] in VOW:
        j += 1
    g = j - i
    if not g:
        return b
    mod = [k for k in range(i, j) if L[k] in 'ăâêôơư']
    if mod:
        p = mod[-1]
    elif g == 1:
        p = i
    elif j < len(L):
        p = i + 1
    elif g == 2:
        p = (i + 1 if nw else i) if L[i:i + 2] in ('oa', 'oe', 'uy') else i
    else:
        p = i + 1
    a = list(b)
    a[p] = ud.normalize('NFC', a[p] + t)
    return ''.join(a)


def ime(w, k, mode, nw=False):
    """Trả về từ mới nếu phím k biến đổi từ w, ngược lại None (phím được gõ nguyên)."""
    b, t = split(w)
    lk = k.lower()

    def last_v():
        for i in range(len(b) - 1, -1, -1):
            if b[i].lower() in VOW:
                return i
        return -1

    def last_of(s):
        for i in range(len(b) - 1, -1, -1):
            if b[i].lower() in s:
                return i
        return -1

    def rep(i, c):
        nonlocal b
        up = b[i] != b[i].lower()
        b = b[:i] + (c.upper() if up else c) + b[i + 1:]

    tk = op = None
    if mode == 'telex':
        if lk in TONE:
            tk = lk
        elif lk == 'z':
            tk = 'z'
        elif lk in ('a', 'e', 'o'):
            op = 'c'
        elif lk == 'w':
            op = 'w'
        elif lk == 'd':
            op = 'd'
    else:
        if k in '012345' and len(k) == 1:
            tk = 'z' if k == '0' else VT[k]
        else:
            op = {'6': 'c', '7': 'h', '8': 'b', '9': 'd'}.get(k)
    if tk:
        if last_v() < 0:
            return None
        if tk == 'z':
            return compose(b, None, nw) if t else None
        if t == TONE[tk]:
            return compose(b, None, nw) + k
        return compose(b, TONE[tk], nw)
    if not op:
        return None
    if op == 'd':
        c = b[:1].lower()
        if c == 'd':
            rep(0, 'đ'); return compose(b, t, nw)
        if c == 'đ':
            rep(0, 'd'); return compose(b, t, nw) + k
        return None
    if op == 'c':
        fam = (lk, CIRC[lk]) if mode == 'telex' else ('a', 'e', 'o', 'â', 'ê', 'ô')
        for i in range(len(b) - 1, -1, -1):
            c = b[i].lower()
            if c in fam and FIN.match(b[i + 1:].lower()):
                if c in CIRC:
                    rep(i, CIRC[c]); return compose(b, t, nw)
                rep(i, INV[c]); return compose(b, t, nw) + k
        return None
    s = 'aouăơư' if mode == 'telex' else ('ouơư' if op == 'h' else 'aă')
    i = last_of(s)
    if i < 0:
        return None
    c = b[i].lower()
    if c in 'aou':
        if c == 'a':
            rep(i, 'ă')
        else:
            rep(i, 'ơ' if c == 'o' else 'ư')
            if c == 'o' and i > 0 and b[i - 1].lower() == 'u':
                rep(i - 1, 'ư')
        return compose(b, t, nw)
    rep(i, INV[c])
    if c == 'ơ' and i > 0 and b[i - 1].lower() == 'ư':
        rep(i - 1, 'u')
    return compose(b, t, nw) + k
