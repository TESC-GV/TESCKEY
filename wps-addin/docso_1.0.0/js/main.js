/* Add-in WPS Spreadsheets: đọc số thành chữ tiếng Việt. */
var CAU_HINH = { kieuSoVN: true, linh: "linh", nghin: "nghìn", ty: "tỷ", hoa: "f" };
var U = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"];

function r3(n, full, o) {
  var h = Math.floor(n / 100), t = Math.floor(n % 100 / 10), u = n % 10, p = [];
  if (h || full) p.push(U[h] + " trăm");
  if (t > 1) { p.push(U[t] + " mươi"); if (u == 1) p.push("mốt"); else if (u == 5) p.push("lăm"); else if (u) p.push(U[u]); }
  else if (t == 1) { p.push("mười"); if (u == 5) p.push("lăm"); else if (u) p.push(U[u]); }
  else if (u) { if (h || full) p.push(o.linh); p.push(U[u]); }
  return p.join(" ");
}
function gn(i, o) { return i == 0 ? "" : i == 1 ? o.nghin : i == 2 ? "triệu" : i == 3 ? o.ty : gn(i - 3, o) + " " + o.ty; }
function int2w(s, o) {
  s = s.replace(/^0+(?=\d)/, "");
  if (/^0+$/.test(s)) return U[0];
  var gs = [], e, out = [], st = false, i;
  for (e = s.length; e > 0; e -= 3) gs.push(parseInt(s.slice(Math.max(0, e - 3), e), 10));
  for (i = gs.length - 1; i >= 0; i--) {
    if (!gs[i]) continue;
    out.push((r3(gs[i], st, o) + " " + gn(i, o)).replace(/^\s+|\s+$/g, ""));
    st = true;
  }
  return out.join(" ");
}
function parseSo(str, vn) {
  var s = String(str).replace(/\s/g, ""), neg = /^[-−–]/.test(s);
  s = s.replace(/^[-+−–]/, "");
  var th = vn ? "." : ",", de = vn ? "," : ".", p = s.split(de);
  if (p.length > 2) return null;
  var i = p[0].split(th).join(""), f = p[1] || "";
  if (!/^\d+$/.test(i) || (f && !/^\d+$/.test(f))) return null;
  return { neg: neg, i: i, f: f };
}
function docso(v, vn, hauTo) {
  var n = parseSo(v, vn); if (!n) return null;
  var r = (n.neg ? "âm " : "") + int2w(n.i, CAU_HINH), k;
  if (n.f) { r += " phẩy"; for (k = 0; k < n.f.length; k++) r += " " + U[n.f.charAt(k)]; }
  r += hauTo || "";
  if (CAU_HINH.hoa == "u") return r.toUpperCase();
  if (CAU_HINH.hoa == "f") return r.charAt(0).toUpperCase() + r.slice(1);
  return r;
}

function getApp() {
  try { if (wps.EtApplication) return wps.EtApplication(); } catch (e) {}
  return wps.Application;
}
function cell(sh, r, c) {
  try { return sh.Cells.Item(r, c); } catch (e) { return sh.Cells(r, c); }
}
function thongBao(m) {
  try { alert(m); } catch (e) { try { getApp().Alert(m); } catch (e2) {} }
}

function chayDocSo(taiCho, hauTo) {
  var app = getApp(), sel = app.Selection, sh = app.ActiveSheet;
  var r0 = sel.Row, c0 = sel.Column, nr = sel.Rows.Count, nc = sel.Columns.Count, i, j, v, res, dem = 0;
  for (i = 0; i < nr; i++) {
    for (j = 0; j < nc; j++) {
      v = cell(sh, r0 + i, c0 + j).Value2;
      if (v === null || v === undefined || v === "") continue;
      res = (typeof v === "number") ? docso(String(v), false, hauTo) : docso(String(v), CAU_HINH.kieuSoVN, hauTo);
      cell(sh, r0 + i, c0 + (taiCho ? j : nc + j)).Value2 = (res === null) ? "(không đọc được số)" : res;
      dem++;
    }
  }
  return dem;
}

/* ---- Hàm được ribbon.xml gọi ---- */
function OnAddinLoad(ribbonUI) {
  try { if (typeof window.Application.ribbonUI !== "object") window.Application.ribbonUI = ribbonUI; } catch (e) {}
  return true;
}
function OnAction(control) {
  var id = control.Id, dem = 0;
  try {
    if (id == "btnRight") dem = chayDocSo(false, "");
    else if (id == "btnRightDong") dem = chayDocSo(false, " đồng");
    else if (id == "btnInPlace") dem = chayDocSo(true, "");
    thongBao("Đã đổi " + dem + " ô.");
  } catch (e) { thongBao("Lỗi: " + e); }
  return true;
}
function GetImage(control) { return "images/docso.svg"; }
window.ribbon = { OnAddinLoad: OnAddinLoad, OnAction: OnAction, GetImage: GetImage };
