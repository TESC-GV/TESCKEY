/* Lõi đọc số thành chữ tiếng Việt. Dùng chung cho trang web, add-in Office, Google Sheets. */
(function (g) {
  'use strict';
  var U = ['không', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín'];
  function r3(n, full, o) {
    var h = Math.floor(n / 100), t = Math.floor(n % 100 / 10), u = n % 10, p = [];
    if (h || full) p.push(U[h] + ' trăm');
    if (t > 1) { p.push(U[t] + ' mươi'); if (u == 1) p.push('mốt'); else if (u == 5) p.push('lăm'); else if (u) p.push(U[u]); }
    else if (t == 1) { p.push('mười'); if (u == 5) p.push('lăm'); else if (u) p.push(U[u]); }
    else if (u) { if (h || full) p.push(o.linh); p.push(U[u]); }
    return p.join(' ');
  }
  function gn(i, o) { return i == 0 ? '' : i == 1 ? o.ng : i == 2 ? 'triệu' : i == 3 ? o.ty : gn(i - 3, o) + ' ' + o.ty; }
  function int2w(s, o) {
    s = s.replace(/^0+(?=\d)/, '');
    if (/^0+$/.test(s)) return U[0];
    var gs = [], e, out = [], st = false, i;
    for (e = s.length; e > 0; e -= 3) gs.push(+s.slice(Math.max(0, e - 3), e));
    for (i = gs.length - 1; i >= 0; i--) { if (!gs[i]) continue; out.push((r3(gs[i], st, o) + ' ' + gn(i, o)).trim()); st = true; }
    return out.join(' ');
  }
  function parse(str, vn) {
    var s = String(str).trim().replace(/\s/g, ''), neg = /^[-−–]/.test(s);
    s = s.replace(/^[-+−–]/, '');
    var th = vn ? '.' : ',', de = vn ? ',' : '.', p = s.split(de);
    if (p.length > 2) return null;
    var i = p[0].split(th).join(''), f = p[1] || '';
    if (!/^\d+$/.test(i) || (f && !/^\d+$/.test(f))) return null;
    return { neg: neg, i: i, f: f };
  }
  /* opt: {vn:true, linh:'linh'|'lẻ', ng:'nghìn'|'ngàn', ty:'tỷ'|'tỉ', cap:'f'|'u'|'n', suffix:''} */
  function docso(v, opt) {
    opt = opt || {};
    var o = { linh: opt.linh || 'linh', ng: opt.ng || 'nghìn', ty: opt.ty || 'tỷ', cap: opt.cap || 'f' };
    var n = parse(v, opt.vn !== false); if (!n) return null;
    var r = (n.neg ? 'âm ' : '') + int2w(n.i, o) +
      (n.f ? ' phẩy ' + n.f.split('').map(function (d) { return U[d]; }).join(' ') : '') + (opt.suffix || '');
    return o.cap == 'u' ? r.toUpperCase() : o.cap == 'f' ? r.charAt(0).toUpperCase() + r.slice(1) : r;
  }
  function convertText(text, opt) {
    var o = Object.assign({}, opt, { cap: 'n', suffix: '' });
    return String(text).replace(/\d[\d.,]*\d|\d/g, function (m) { var r = docso(m, o); return r == null ? m : r; });
  }
  /* Chuỗi tùy chọn gọn cho hàm Excel: "le,ngan,ti,HOA,thuong,en" */
  function optsFrom(str) {
    var o = {}; String(str || '').split(',').forEach(function (t) {
      t = t.trim(); if (t == 'le') o.linh = 'lẻ'; else if (t == 'ngan') o.ng = 'ngàn'; else if (t == 'ti') o.ty = 'tỉ';
      else if (t == 'HOA') o.cap = 'u'; else if (t == 'thuong') o.cap = 'n'; else if (t == 'en') o.vn = false;
    }); return o;
  }
  g.DocSo = { docso: docso, convertText: convertText, optsFrom: optsFrom };
  if (typeof module !== 'undefined') module.exports = g.DocSo;
})(this);

/** Đọc số thành chữ. =DOCSO(A1; " đồng"; "le,HOA") */
function DOCSO(so, hauto, tuychon) {
  if (so === '' || so === null) return '';
  var o = DocSo.optsFrom(tuychon); o.suffix = hauto || '';
  if (typeof so === 'number') o.vn = false;
  var r = DocSo.docso(String(so), o);
  return r == null ? '#SỐ?' : r;
}
