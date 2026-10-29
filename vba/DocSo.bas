Attribute VB_Name = "DocSo"
Option Explicit
' So thanh chu tieng Viet. Dung: =DOCSO(A1)  =DOCSO(A1; " dong")  =DOCSO(A1;"";"le,ngan,ti,HOA,thuong")
' Neu o chua VAN BAN, so duoc hieu theo kieu Viet Nam (1.234,5).

Private Function W(ByVal k As String) As String
  Select Case k
    Case "d0": W = "kh" & ChrW(&HF4) & "ng"
    Case "d1": W = "m" & ChrW(&H1ED9) & "t"
    Case "d2": W = "hai"
    Case "d3": W = "ba"
    Case "d4": W = "b" & ChrW(&H1ED1) & "n"
    Case "d5": W = "n" & ChrW(&H103) & "m"
    Case "d6": W = "s" & ChrW(&HE1) & "u"
    Case "d7": W = "b" & ChrW(&H1EA3) & "y"
    Case "d8": W = "t" & ChrW(&HE1) & "m"
    Case "d9": W = "ch" & ChrW(&HED) & "n"
    Case "tram": W = "tr" & ChrW(&H103) & "m"
    Case "muoi2": W = "m" & ChrW(&H1B0) & ChrW(&H1A1) & "i"
    Case "muoi1": W = "m" & ChrW(&H1B0) & ChrW(&H1EDD) & "i"
    Case "mot": W = "m" & ChrW(&H1ED1) & "t"
    Case "lam": W = "l" & ChrW(&H103) & "m"
    Case "am": W = ChrW(&HE2) & "m"
    Case "phay": W = "ph" & ChrW(&H1EA9) & "y"
    Case "trieu": W = "tri" & ChrW(&H1EC7) & "u"
    Case "nghin": W = "ngh" & ChrW(&HEC) & "n"
    Case "ngan": W = "ng" & ChrW(&HE0) & "n"
    Case "ty": W = "t" & ChrW(&H1EF7)
    Case "ti": W = "t" & ChrW(&H1EC9)
    Case "linh": W = "linh"
    Case "le": W = "l" & ChrW(&H1EBB)
    Case "loi": W = "#S" & ChrW(&H1ED0) & "?"
  End Select
End Function

Private Function R3(ByVal n As Long, ByVal full As Boolean, ByVal linh As String) As String
  Dim h As Long, t As Long, u As Long, r As String
  h = n \ 100: t = (n Mod 100) \ 10: u = n Mod 10
  If h > 0 Or full Then r = W("d" & h) & " " & W("tram")
  If t > 1 Then
    r = r & " " & W("d" & t) & " " & W("muoi2")
    If u = 1 Then
      r = r & " " & W("mot")
    ElseIf u = 5 Then
      r = r & " " & W("lam")
    ElseIf u > 0 Then
      r = r & " " & W("d" & u)
    End If
  ElseIf t = 1 Then
    r = r & " " & W("muoi1")
    If u = 5 Then
      r = r & " " & W("lam")
    ElseIf u > 0 Then
      r = r & " " & W("d" & u)
    End If
  ElseIf u > 0 Then
    If h > 0 Or full Then r = r & " " & linh
    r = r & " " & W("d" & u)
  End If
  R3 = Trim(r)
End Function

Private Function GN(ByVal i As Long, ByVal ng As String, ByVal ty As String) As String
  If i = 0 Then
    GN = ""
  ElseIf i = 1 Then
    GN = ng
  ElseIf i = 2 Then
    GN = W("trieu")
  ElseIf i = 3 Then
    GN = ty
  Else
    GN = GN(i - 3, ng, ty) & " " & ty
  End If
End Function

Private Function Int2W(ByVal s As String, ByVal linh As String, ByVal ng As String, ByVal ty As String) As String
  Dim n As Long, i As Long, e As Long, b As Long, st As Boolean, r As String, g() As Long
  Do While Len(s) > 1 And Left(s, 1) = "0"
    s = Mid(s, 2)
  Loop
  If s = "0" Then Int2W = W("d0"): Exit Function
  n = (Len(s) + 2) \ 3
  ReDim g(0 To n - 1)
  For i = 0 To n - 1
    e = Len(s) - 3 * i
    b = e - 2
    If b < 1 Then b = 1
    g(i) = CLng(Mid(s, b, e - b + 1))
  Next i
  For i = n - 1 To 0 Step -1
    If g(i) > 0 Then
      r = r & " " & Trim(R3(g(i), st, linh) & " " & GN(i, ng, ty))
      st = True
    End If
  Next i
  Int2W = Trim(r)
End Function

Private Function Opt(ByVal o As String, ByVal k As String) As Boolean
  Opt = (InStr("," & Replace(o, " ", "") & ",", "," & k & ",") > 0)
End Function

Public Function DOCSO(ByVal v As Variant, Optional ByVal suffix As String = "", Optional ByVal opts As String = "") As String
  Dim s As String, neg As Boolean, ip As String, fp As String, p As Long, r As String, i As Long
  Dim linh As String, ng As String, ty As String
  On Error GoTo bad
  If IsEmpty(v) Then DOCSO = "": Exit Function
  If VarType(v) = vbString Then
    s = Replace(Replace(Replace(Trim(v), " ", ""), ".", ""), ",", ".")
  Else
    s = Trim(Str(CDec(v)))
  End If
  If s = "" Then DOCSO = "": Exit Function
  If Left(s, 1) = "-" Then neg = True: s = Mid(s, 2)
  p = InStr(s, ".")
  If p > 0 Then ip = Left(s, p - 1): fp = Mid(s, p + 1) Else ip = s
  If ip = "" Or ip Like "*[!0-9]*" Or fp Like "*[!0-9]*" Then GoTo bad
  linh = W("linh"): ng = W("nghin"): ty = W("ty")
  If Opt(opts, "le") Then linh = W("le")
  If Opt(opts, "ngan") Then ng = W("ngan")
  If Opt(opts, "ti") Then ty = W("ti")
  r = Int2W(ip, linh, ng, ty)
  If neg Then r = W("am") & " " & r
  If fp <> "" Then
    r = r & " " & W("phay")
    For i = 1 To Len(fp)
      r = r & " " & W("d" & Mid(fp, i, 1))
    Next i
  End If
  r = r & suffix
  If Opt(opts, "HOA") Then
    r = UCase(r)
  ElseIf Not Opt(opts, "thuong") Then
    r = UCase(Left(r, 1)) & Mid(r, 2)
  End If
  DOCSO = r
  Exit Function
bad:
  DOCSO = W("loi")
End Function
