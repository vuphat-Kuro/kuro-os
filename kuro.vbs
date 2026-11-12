' Mo Kuro tu bieu tuong tren man hinh chinh, khong hien cua so den.
' Uu tien khoi chay ung dung Desktop native (WebView2).
Option Explicit
Dim sh, fso, dir, pythonw, desktopPy, url, i
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = dir & "\.venv\Scripts\pythonw.exe"
desktopPy = dir & "\app_desktop.py"

sh.CurrentDirectory = dir

' 1. Uu tien tuyet doi: Mo app Desktop native (Edge WebView2)
If fso.FileExists(pythonw) And fso.FileExists(desktopPy) Then
  sh.Run """" & pythonw & """ """ & desktopPy & """", 0, False
  WScript.Quit
End If

' 2. Fallback sang che do Web neu khong tim thay app_desktop.py
url = "http://127.0.0.1:7788"

Function Up()
  Dim http
  Up = False
  On Error Resume Next
  Set http = CreateObject("MSXML2.ServerXMLHTTP")
  http.setTimeouts 1000, 1000, 1000, 1000
  http.Open "GET", url & "/health", False
  http.Send
  If Err.Number = 0 Then Up = (http.Status = 200)
  On Error GoTo 0
End Function

If Not Up() Then
  If Not fso.FileExists(dir & "\.venv\Scripts\python.exe") Then
    MsgBox "Kuro chua cai xong. Vao thu muc Kuro, bam dup setup.bat truoc.", 48, "Kuro"
    WScript.Quit
  End If
  If Not fso.FolderExists(dir & "\state") Then fso.CreateFolder dir & "\state"
  sh.Run "cmd /c ""set PYTHONUTF8=1&& .venv\Scripts\python.exe server\main.py > state\kuro.log 2>&1""", 0, False
  For i = 1 To 60
    WScript.Sleep 500
    If Up() Then Exit For
  Next
  If Not Up() Then
    MsgBox "Kuro khong khoi dong duoc. Xem loi trong state\kuro.log, hoac bam dup run.bat de thay loi.", 16, "Kuro"
    WScript.Quit
  End If
End If
sh.Run url
