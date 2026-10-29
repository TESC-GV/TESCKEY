Attribute VB_Name = "DocSoExcel"
Option Explicit
' Chon cac o so, chay macro nay: ket qua ghi sang cot ben phai.
Sub DocSoChon()
  Dim c As Range
  For Each c In Selection.Cells
    If Not IsEmpty(c.Value) Then c.Offset(0, 1).Value = DOCSO(c.Value, " " & ChrW(&H111) & ChrW(&H1ED3) & "ng")
  Next c
End Sub
