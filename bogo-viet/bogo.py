"""Bộ gõ tiếng Việt toàn hệ thống cho Windows (portable, không cần cài).
Chạy: python bogo.py   |   Đóng gói: build.bat
Ctrl+Shift: bật/tắt. Cấu hình lưu trong bogo.json cạnh file chạy."""
import ctypes, ctypes.wintypes as wt, json, os, sys, threading
import tkinter as tk
from tkinter import ttk, messagebox
import unicodedata as ud, re
from bogo_engine import ime
from docso import docso as _docso, convert_text
try:
    import pystray
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    pystray = None

BASE = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
CFG = os.path.join(BASE, 'bogo.json')
DEF_ABBR = {'ko': 'không', 'dc': 'được', 'đc': 'được', 'vn': 'Việt Nam', 'tphcm': 'TP. Hồ Chí Minh',
            'ngta': 'người ta', 'bt': 'bình thường', 'trc': 'trước', 'sg': 'Sài Gòn', 'hn': 'Hà Nội'}


class S:  # trạng thái dùng chung
    enabled = True; mode = 'telex'; nw = False; ab = True
    abbr = dict(DEF_ABBR); buf = ''; last = None; hwnd = 0; pending = False; hook_ok = None; hook_err = 0; want_conv = False; conv_busy = False; show = False
    num = {'vn': 'vn', 'linh': 'linh', 'ng': 'nghìn', 'ty': 'tỷ', 'cap': 'f', 'suffix': ''}


def load():
    try:
        d = json.load(open(CFG, encoding='utf-8'))
        S.mode = d.get('mode', 'telex'); S.nw = d.get('nw', False); S.ab = d.get('ab', True)
        S.abbr = d.get('abbr', S.abbr); S.enabled = d.get('enabled', True); S.num.update(d.get('num', {}))
        if S.mode == 'off':
            S.mode = 'telex'; S.enabled = False
    except Exception:
        pass


def save():
    try:
        json.dump({'mode': S.mode, 'nw': S.nw, 'ab': S.ab, 'abbr': S.abbr, 'enabled': S.enabled, 'num': S.num},
                  open(CFG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    except Exception:
        pass


# ---------- Windows API ----------
u32 = ctypes.WinDLL('user32', use_last_error=True)
k32 = ctypes.WinDLL('kernel32', use_last_error=True)
k32.GetModuleHandleW.restype = wt.HMODULE
k32.GetModuleHandleW.argtypes = [wt.LPCWSTR]
ULP = ctypes.c_size_t
class KBD(ctypes.Structure):
    _fields_ = [('vk', wt.DWORD), ('scan', wt.DWORD), ('flags', wt.DWORD), ('time', wt.DWORD), ('extra', ULP)]
class KI(ctypes.Structure):
    _fields_ = [('vk', wt.WORD), ('scan', wt.WORD), ('flags', wt.DWORD), ('time', wt.DWORD), ('extra', ULP)]
class MI(ctypes.Structure):
    _fields_ = [('dx', wt.LONG), ('dy', wt.LONG), ('data', wt.DWORD), ('flags', wt.DWORD), ('time', wt.DWORD), ('extra', ULP)]
class HI(ctypes.Structure):
    _fields_ = [('msg', wt.DWORD), ('lo', wt.WORD), ('hi', wt.WORD)]
class IU(ctypes.Union):
    _fields_ = [('ki', KI), ('mi', MI), ('hi', HI)]
class INP(ctypes.Structure):
    _fields_ = [('type', wt.DWORD), ('u', IU)]
HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_int, wt.WPARAM, wt.LPARAM)
u32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wt.HINSTANCE, wt.DWORD]
u32.SetWindowsHookExW.restype = wt.HHOOK
u32.GetForegroundWindow.restype = wt.HWND
u32.GetMessageW.argtypes = [ctypes.POINTER(wt.MSG), wt.HWND, wt.UINT, wt.UINT]
u32.CallNextHookEx.argtypes = [wt.HHOOK, ctypes.c_int, wt.WPARAM, wt.LPARAM]
u32.CallNextHookEx.restype = ctypes.c_ssize_t
u32.SendInput.argtypes = [wt.UINT, ctypes.POINTER(INP), ctypes.c_int]
u32.GetAsyncKeyState.restype = ctypes.c_short


def send(bs, text):
    """Xóa bs ký tự rồi gõ text (Unicode). '\\n' gửi phím Enter."""
    ev = []
    def key(vk=0, scan=0, fl=0):
        i = INP(); i.type = 1; i.u.ki = KI(vk, scan, fl, 0, 0); ev.append(i)
    for _ in range(bs):
        key(0x08); key(0x08, 0, 2)
    for ch in text:
        if ch == '\n':
            key(0x0D); key(0x0D, 0, 2)
        else:
            key(0, ord(ch), 4); key(0, ord(ch), 4 | 2)
    if ev:
        arr = (INP * len(ev))(*ev)
        u32.SendInput(len(ev), arr, ctypes.sizeof(INP))


down = lambda vk: bool(u32.GetAsyncKeyState(vk) & 0x8000)
reset = lambda: (setattr(S, 'buf', ''), setattr(S, 'last', None))


def on_key(n, wp, lp):
    nxt = lambda: u32.CallNextHookEx(None, n, wp, lp)
    try:
        if n < 0:
            return nxt()
        k = ctypes.cast(lp, ctypes.POINTER(KBD)).contents
        if k.flags & 0x10:  # phím do chính mình gửi
            return nxt()
        vk, dn = k.vk, wp in (0x100, 0x104)
        ctrl, shift = vk in (0x11, 0xA2, 0xA3), vk in (0x10, 0xA0, 0xA1)
        if ctrl or shift:  # Ctrl+Shift để bật/tắt
            if dn:
                if (down(0x11) and down(0x10)) and not S.pending and not any(
                        down(c) for c in (0x12, 0x5B, 0x5C)):
                    S.pending = True
            elif S.pending:
                S.pending = False; S.enabled = not S.enabled; save(); reset()
            return nxt()
        if dn:
            S.pending = False
            if vk == 0x44 and down(0x11) and down(0x12):
                S.want_conv = True; return 1
        if not dn or not S.enabled or S.mode == 'off' and not S.ab:
            return nxt()
        h = u32.GetForegroundWindow()
        if h != S.hwnd:
            S.hwnd = h; reset()
        if down(0x11) or down(0x12) or down(0x5B) or down(0x5C):
            reset(); return nxt()
        if vk == 0x14:
            return nxt()
        up = down(0x10) != bool(u32.GetKeyState(0x14) & 1)
        ch = None
        if 0x41 <= vk <= 0x5A:
            ch = chr(vk) if up else chr(vk).lower()
        elif 0x30 <= vk <= 0x39 and not down(0x10):
            ch = chr(vk)
        if ch is not None:
            S.last = None
            if S.mode != 'off' and ch.isalpha() or (S.mode == 'vni' and ch.isdigit()):
                if S.buf:
                    r = ime(S.buf, ch, S.mode, S.nw) if S.mode != 'off' else None
                    if r is not None:
                        send(len(S.buf), r); S.buf = r; return 1
                if ch.isalpha():
                    S.buf += ch
                else:
                    S.buf = ''
            elif ch.isalpha():
                S.buf += ch
            else:
                S.buf = ''
            return nxt()
        if vk == 0x08:
            if S.last:
                o, x = S.last; S.last = None
                send(len(x), o); S.buf = o; return 1
            S.buf = S.buf[:-1]; return nxt()
        if vk in (0x20, 0x0D):
            w = S.buf
            x = S.ab and w and S.abbr.get(w.lower())
            reset()
            if x:
                if len(w) > 1 and w == w.upper(): x = x.upper()
                elif w[0] != w[0].lower(): x = x[0].upper() + x[1:]
                sep = ' ' if vk == 0x20 else '\n'
                send(len(w), x + sep); S.last = (w, x + sep); return 1
            return nxt()
        if vk in (0x10, 0xA0, 0xA1, 0x12, 0xA4, 0xA5):
            return nxt()
        reset()
    except Exception:
        pass
    return nxt()


def on_mouse(n, wp, lp):
    if n >= 0 and wp in (0x201, 0x204, 0x207):
        reset()
    return u32.CallNextHookEx(None, n, wp, lp)


def hook_thread():
    global kcb, mcb
    kcb, mcb = HOOKPROC(on_key), HOOKPROC(on_mouse)
    hm = k32.GetModuleHandleW(None)
    h1 = u32.SetWindowsHookExW(13, kcb, hm, 0)
    if not h1:
        h1 = u32.SetWindowsHookExW(13, kcb, None, 0)
    S.hook_err = 0 if h1 else ctypes.get_last_error()
    S.hook_ok = bool(h1)
    u32.SetWindowsHookExW(14, mcb, hm, 0) or u32.SetWindowsHookExW(14, mcb, None, 0)
    msg = wt.MSG()
    while u32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        u32.TranslateMessage(ctypes.byref(msg)); u32.DispatchMessageW(ctypes.byref(msg))


def make_icon(on):
    im = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((2, 2, 62, 62), 12, fill=(14, 106, 90, 255) if on else (138, 45, 45, 255))
    ch = 'V' if on else 'E'
    try:
        d.text((32, 34), ch, font=ImageFont.truetype('arialbd.ttf', 44), fill='white', anchor='mm')
    except Exception:
        d.text((24, 22), ch, fill='white')
    return im


def chord(vk):
    ev = []
    for v, fl in ((0x11, 0), (vk, 0), (vk, 2), (0x11, 2)):
        i = INP(); i.type = 1; i.u.ki = KI(v, 0, fl, 0, 0); ev.append(i)
    u32.SendInput(len(ev), (INP * len(ev))(*ev), ctypes.sizeof(INP))


def numopts():
    n = S.num
    return dict(vn=n['vn'] == 'vn', linh=n['linh'], ng=n['ng'], ty=n['ty'])


def num_line(line, with_suffix=True):
    o = numopts()
    r = _docso(line, cap=S.num['cap'], suffix=S.num['suffix'] if with_suffix else '', **o)
    return r if r is not None else convert_text(line, **o)


CV = {'Unicode dựng sẵn': lambda s: ud.normalize('NFC', s), 'Unicode tổ hợp': lambda s: ud.normalize('NFD', s),
      'Bỏ dấu': lambda s: re.sub('[\u0300-\u036f]', '', ud.normalize('NFD', s)).replace('đ', 'd').replace('Đ', 'D'),
      'VIẾT HOA': str.upper, 'viết thường': str.lower,
      'Viết Hoa Từng Chữ': lambda s: re.sub(r'(^|[\s\-(])(\w)', lambda m: m.group(1) + m.group(2).upper(), s.lower())}


# ---------- Giao diện ----------
def main():
    load()
    threading.Thread(target=hook_thread, daemon=True).start()
    r = tk.Tk(); r.title('Bộ gõ Việt'); r.minsize(560, 460)
    top = tk.Frame(r); top.pack(fill='x', padx=8, pady=6)
    st = tk.Label(top, font=('Segoe UI', 26, 'bold'), width=3); st.pack(side='left')
    inf = tk.Frame(top); inf.pack(side='left', padx=10)
    hk = tk.Label(inf, text='Đang kiểm tra bộ bắt phím...', fg='gray'); hk.pack(anchor='w')
    tk.Label(inf, text='Bấm vào chữ V/E (hoặc icon ở khay, hoặc Ctrl+Shift) để chuyển Việt/Anh', fg='gray').pack(anchor='w')
    tk.Label(inf, text='Ctrl+Alt+D: đổi số đang bôi đen thành chữ', fg='gray').pack(anchor='w')
    tray = None
    def toggle(*_):
        S.enabled = not S.enabled; save(); reset()
    st.config(cursor='hand2'); st.bind('<Button-1>', toggle)
    def quit_app(*_):
        save(); os._exit(0)
    if pystray:
        try:
            menu = pystray.Menu(pystray.MenuItem('Bật/tắt gõ tiếng Việt (V/E)', toggle, default=True),
                                pystray.MenuItem('Mở cửa sổ', lambda *_: setattr(S, 'show', True)),
                                pystray.MenuItem('Thoát', quit_app))
            tray = pystray.Icon('bogo', make_icon(True), 'Bộ gõ Việt', menu); tray.run_detached()
        except Exception:
            tray = None
    def hide_win():
        r.withdraw() if tray else r.iconify()
    nb = ttk.Notebook(r); nb.pack(fill='both', expand=True, padx=8, pady=(0, 6))

    # --- Tab gõ phím ---
    t1 = ttk.Frame(nb); nb.add(t1, text='Gõ phím')
    mode = tk.StringVar(value=S.mode); nw = tk.BooleanVar(value=S.nw); ab = tk.BooleanVar(value=S.ab)
    def apply(*_):
        S.mode, S.nw, S.ab = mode.get(), nw.get(), ab.get(); reset(); save()
    row = ttk.Frame(t1); row.pack(anchor='w', padx=8, pady=8)
    ttk.Label(row, text='Kiểu gõ').pack(side='left')
    cb = ttk.Combobox(row, textvariable=mode, values=['telex', 'vni'], state='readonly', width=8)
    cb.pack(side='left', padx=6); cb.bind('<<ComboboxSelected>>', apply)
    tk.Checkbutton(t1, text='Đặt dấu kiểu mới (hoà, thuỷ)', variable=nw, command=apply).pack(anchor='w', padx=8)
    tk.Checkbutton(t1, text='Bung gõ tắt khi nhấn Space hoặc Enter', variable=ab, command=apply).pack(anchor='w', padx=8)
    ttk.Label(t1, text='Gõ thử (ví dụ Vieejt Nam, toio, ddoio):').pack(anchor='w', padx=8, pady=(10, 0))
    te = tk.Entry(t1, font=('Segoe UI', 13)); te.pack(fill='x', padx=8, pady=4)
    ttk.Label(t1, text='Gõ lại đúng phím dấu (hoặc nhấn z trong Telex) để bỏ dấu, ở bất kỳ vị trí nào trong từ.', foreground='gray').pack(anchor='w', padx=8)

    # --- Tab số thành chữ ---
    t2 = ttk.Frame(nb); nb.add(t2, text='Số thành chữ')
    op = ttk.Frame(t2); op.pack(fill='x', padx=6, pady=6)
    def addopt(label, key, choices):
        ttk.Label(op, text=label).pack(side='left')
        cur = next((d for d, c in choices if c == S.num[key]), choices[0][0]); v = tk.StringVar(value=cur)
        c = ttk.Combobox(op, textvariable=v, values=[d for d, _ in choices], state='readonly', width=9)
        c.pack(side='left', padx=(2, 8))
        def ch(*_):
            S.num[key] = dict(choices)[v.get()]; save(); runnum()
        c.bind('<<ComboboxSelected>>', ch)
    addopt('Kiểu số', 'vn', [('1.234,5', 'vn'), ('1,234.5', 'en')])
    addopt('Số lẻ', 'linh', [('linh', 'linh'), ('lẻ', 'lẻ')])
    addopt('1000', 'ng', [('nghìn', 'nghìn'), ('ngàn', 'ngàn')])
    addopt('10⁹', 'ty', [('tỷ', 'tỷ'), ('tỉ', 'tỉ')])
    addopt('Hoa', 'cap', [('chữ đầu', 'f'), ('TOÀN BỘ', 'u'), ('không', 'n')])
    op2 = ttk.Frame(t2); op2.pack(fill='x', padx=6)
    ttk.Label(op2, text='Hậu tố (ví dụ " đồng")').pack(side='left')
    sv = tk.StringVar(value=S.num['suffix']); se = ttk.Entry(op2, textvariable=sv, width=18); se.pack(side='left', padx=6)
    def suf(*_):
        S.num['suffix'] = sv.get(); save(); runnum()
    sv.trace_add('write', suf)
    ttk.Label(t2, text='Mỗi dòng một số, hoặc dán cả đoạn văn có chứa số:').pack(anchor='w', padx=6, pady=(8, 0))
    tin = tk.Text(t2, height=5, wrap='word', font=('Segoe UI', 11)); tin.pack(fill='both', expand=True, padx=6, pady=3)
    tout = tk.Text(t2, height=5, wrap='word', font=('Segoe UI', 11)); tout.pack(fill='both', expand=True, padx=6, pady=3)
    def runnum(*_):
        res = '\n'.join(num_line(l) if l.strip() else '' for l in tin.get('1.0', 'end-1c').split('\n'))
        tout.delete('1.0', 'end'); tout.insert('1.0', res)
    tin.bind('<KeyRelease>', runnum)
    def clip(w):
        r.clipboard_clear(); r.clipboard_append(w.get('1.0', 'end-1c')); r.update()
    ttk.Button(t2, text='Sao chép kết quả', command=lambda: clip(tout)).pack(pady=4)

    # --- Tab đổi chữ ---
    t3 = ttk.Frame(nb); nb.add(t3, text='Đổi chữ')
    kind = tk.StringVar(value='Unicode dựng sẵn')
    rw = ttk.Frame(t3); rw.pack(anchor='w', padx=6, pady=6)
    ttk.Label(rw, text='Chuyển sang').pack(side='left')
    kc = ttk.Combobox(rw, textvariable=kind, values=list(CV), state='readonly', width=22); kc.pack(side='left', padx=6)
    cin = tk.Text(t3, height=6, wrap='word', font=('Segoe UI', 11)); cin.pack(fill='both', expand=True, padx=6, pady=3)
    cout = tk.Text(t3, height=6, wrap='word', font=('Segoe UI', 11)); cout.pack(fill='both', expand=True, padx=6, pady=3)
    def runcv(*_):
        cout.delete('1.0', 'end'); cout.insert('1.0', CV[kind.get()](cin.get('1.0', 'end-1c')))
    cin.bind('<KeyRelease>', runcv); kc.bind('<<ComboboxSelected>>', runcv)
    ttk.Button(t3, text='Sao chép kết quả', command=lambda: clip(cout)).pack(pady=4)

    # --- Tab gõ tắt ---
    t4 = ttk.Frame(nb); nb.add(t4, text='Gõ tắt')
    ttk.Label(t4, text='Mỗi dòng: tắt=bung   (ví dụ ko=không)').pack(anchor='w', padx=6, pady=6)
    at = tk.Text(t4, height=12, font=('Segoe UI', 11)); at.pack(fill='both', expand=True, padx=6)
    at.insert('1.0', '\n'.join(f'{k}={v}' for k, v in sorted(S.abbr.items())))
    def saveab():
        d = {}
        for l in at.get('1.0', 'end').splitlines():
            if '=' in l:
                a, b = l.split('=', 1)
                if a.strip() and b.strip(): d[a.strip().lower()] = b.strip()
        S.abbr = d; save(); messagebox.showinfo('Gõ tắt', f'Đã lưu {len(d)} mục.')
    ttk.Button(t4, text='Lưu', command=saveab).pack(pady=6)

    # --- Chân cửa sổ ---
    def web():
        for p in (os.path.join(BASE, 'Cong-cu-tieng-Viet.html'), os.path.join(BASE, '..', 'docs', 'index.html'),
                  os.path.join(BASE, 'docs', 'index.html')):
            if os.path.exists(p):
                os.startfile(p); return
        messagebox.showinfo('Công cụ web', 'Không tìm thấy file Cong-cu-tieng-Viet.html')
    f = tk.Frame(r); f.pack(pady=(0, 8))
    ttk.Button(f, text='Công cụ web (font...)', command=web).pack(side='left', padx=4)
    ttk.Button(f, text='Ẩn xuống khay' if tray else 'Thu nhỏ', command=hide_win).pack(side='left', padx=4)
    ttk.Button(f, text='Thoát', command=quit_app).pack(side='left', padx=4)

    # --- Đổi số đang bôi đen ở mọi phần mềm (Ctrl+Alt+D) ---
    def conv2():
        try: tx = r.clipboard_get()
        except Exception: tx = ''
        if tx.strip() and tx != '\x01':
            r.clipboard_clear(); r.clipboard_append(num_line(tx.strip())); r.update()
            chord(0x56)
            r.after(400, lambda: setattr(S, 'conv_busy', False))
        else:
            S.conv_busy = False
    def do_conv():
        S.conv_busy = True
        try:
            r.clipboard_clear(); r.clipboard_append('\x01'); r.update()
        except Exception: pass
        chord(0x43); r.after(300, conv2)

    def tick():
        on = S.enabled and S.mode != 'off'
        st.config(text='V' if on else 'E', fg='white', bg='#0e6a5a' if on else '#8a2d2d')
        r.title('Bộ gõ Việt: ' + ('V' if on else 'E'))
        if S.hook_ok is True: hk.config(text='V: gõ tiếng Việt    E: gõ không dấu (tiếng Anh)', fg='#0e6a5a')
        elif S.hook_ok is False: hk.config(text=f'LỖI bộ bắt phím (mã {S.hook_err})', fg='#a02020')
        if tray:
            if S.show:
                S.show = False; r.deiconify(); r.lift(); r.focus_force()
            if getattr(tick, 'last', None) != on:
                tick.last = on; tray.icon = make_icon(on); tray.title = 'Bộ gõ Việt: ' + ('V' if on else 'E')
        if S.want_conv and not S.conv_busy and not any(down(k) for k in (0x10, 0x11, 0x12, 0x5B, 0x5C, 0x44)):
            S.want_conv = False; do_conv()
        r.after(150, tick)
    r.protocol('WM_DELETE_WINDOW', hide_win)
    if tray:
        r.bind('<Unmap>', lambda e: e.widget is r and r.state() == 'iconic' and r.after(10, r.withdraw))
        if '--tray' in sys.argv:
            r.withdraw()
    tick(); r.mainloop()


if __name__ == '__main__':
    main()
