Attribute VB_Name = "DocSoWord"
Option Explicit
' Boi den mot so, chay macro nay: so duoc thay bang chu.
Sub DocSoChon()
  Dim t As String
  t = Replace(Replace(Selection.Text, vbCr, ""), Chr(7), "")
  If Len(Trim(t)) = 0 Then Exit Sub
  Selection.Text = DOCSO(t)
End Sub
