# Chan doan: mo phien AutoCAD thu, goi plan.apply, liet ke cua so de biet hop thoai xin phep o dau. PowerShell 5.1.
$ErrorActionPreference = 'Continue'
$w = Split-Path $PSScriptRoot -Parent
$t = Join-Path $w 'test'
$bin = (Get-Content "$w\bin\latest.txt" -Raw).Trim()
function Lisp($p) { return $p -replace '\\', '/' }
Copy-Item "$t\fixture_20.dwg" "$t\idle_work.dwg" -Force
[IO.File]::WriteAllLines("$t\idle.scr", @(('(command "_.NETLOAD" "' + (Lisp "$bin\Pkttc.TextHub.dll") + '")'), 'PKTEXTBRIDGE', 'YES'), (New-Object Text.UTF8Encoding($false)))
$p = Start-Process 'C:\Program Files\Autodesk\AutoCAD 2020\acad.exe' -ArgumentList @("`"$t\idle_work.dwg`"", '/nologo', '/b', "`"$t\idle.scr`"") -PassThru -WindowStyle Minimized
"PID $($p.Id)"
$disc = Join-Path $env:LOCALAPPDATA "PKTTC\bridge\$($p.Id).json"
for ($i = 0; $i -lt 240 -and -not (Test-Path $disc); $i++) { Start-Sleep -Milliseconds 500 }
'cong mo: ' + (Test-Path $disc)
$py = @"
import sys, json
sys.path.insert(0, r'$w\bridge')
from pkttc_client import Client
c = Client(pipe='PKTTC.TextHub.$($p.Id)', client_name='Debug')
p = c.call('plan.create')
print('plan', p['planId'], flush=True)
print(c.call('plan.apply', {'planId': p['planId'], 'note': 'debug'}, timeout=60), flush=True)
"@
$pyFile = Join-Path $t 'debug_call.py'
[IO.File]::WriteAllText($pyFile, $py)
$job = Start-Process python -ArgumentList @('-X', 'utf8', '-I', "`"$pyFile`"") -PassThru -WindowStyle Hidden -RedirectStandardOutput "$t\debug_call.out" -RedirectStandardError "$t\debug_call.err"
Start-Sleep -Seconds 8
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
$root = [System.Windows.Automation.AutomationElement]::RootElement
'--- cua so cap cao co chu PKTTC (moi tien trinh):'
foreach ($w2 in $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {
    if ($w2.Current.Name -like '*PKTTC*' -or $w2.Current.ProcessId -eq $p.Id) { '  pid={0} [{1}] "{2}" offscreen={3}' -f $w2.Current.ProcessId, $w2.Current.ControlType.ProgrammaticName, $w2.Current.Name, $w2.Current.IsOffscreen }
}
'--- EnumWindows theo PID:'
Add-Type @'
using System; using System.Text; using System.Collections.Generic; using System.Runtime.InteropServices;
public class W3 { public delegate bool CB(IntPtr h, IntPtr l);
 [DllImport("user32.dll")] static extern bool EnumWindows(CB c, IntPtr l);
 [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
 [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
 public static List<string> Get(uint pid){ var r=new List<string>(); EnumWindows((h,l)=>{ uint p; GetWindowThreadProcessId(h,out p); if(p==pid){ var s=new StringBuilder(256); GetWindowText(h,s,256); r.Add((IsWindowVisible(h)?"V ":"- ")+h+" "+s);} return true;}, IntPtr.Zero); return r; } }
'@
[W3]::Get($p.Id) | Select-Object -First 30 | ForEach-Object { '  ' + $_ }
'--- ket qua goi:'
Get-Content "$t\debug_call.out" -ErrorAction SilentlyContinue
Get-Content "$t\debug_call.err" -ErrorAction SilentlyContinue | Select-Object -First 5
Stop-Process -Id $job.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $p.Id -Force
