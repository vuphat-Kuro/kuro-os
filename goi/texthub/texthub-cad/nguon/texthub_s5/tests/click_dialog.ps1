# Tim hop thoai xin phep cua TextHub trong mot tien trinh AutoCAD, in noi dung, bam nut Yes hoac No. PowerShell 5.1.
# Dung Win32 (hop thoai la MessageBox chuan): tim cua so cap cao theo PID va tieu de, doc cac Static con, bam nut bang WM_COMMAND(IDYES/IDNO).
# Dung: powershell -File click_dialog.ps1 -ProcId 1234 -Button Yes -TimeoutSec 90
param(
    [Parameter(Mandatory = $true)][int]$ProcId,
    [Parameter(Mandatory = $true)][ValidateSet('Yes', 'No')][string]$Button,
    [int]$TimeoutSec = 90
)
$ErrorActionPreference = 'Stop'
Add-Type @'
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public class DlgW
{
    public delegate bool CB(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] static extern bool EnumWindows(CB c, IntPtr l);
    [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr p, CB c, IntPtr l);
    [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern int GetClassName(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);

    public static IntPtr Find(uint pid, string contains)
    {
        IntPtr found = IntPtr.Zero;
        EnumWindows((h, l) =>
        {
            uint p; GetWindowThreadProcessId(h, out p);
            if (p == pid && IsWindowVisible(h))
            {
                StringBuilder s = new StringBuilder(256); GetWindowText(h, s, 256);
                if (s.ToString().Contains(contains)) { found = h; return false; }
            }
            return true;
        }, IntPtr.Zero);
        return found;
    }

    public static string Title(IntPtr h) { StringBuilder s = new StringBuilder(256); GetWindowText(h, s, 256); return s.ToString(); }

    public static List<string> Texts(IntPtr dlg)
    {
        List<string> r = new List<string>();
        EnumChildWindows(dlg, (h, l) =>
        {
            StringBuilder c = new StringBuilder(64); GetClassName(h, c, 64);
            if (c.ToString() == "Static")
            {
                StringBuilder s = new StringBuilder(8192); GetWindowText(h, s, 8192);
                if (s.Length > 0) r.Add(s.ToString());
            }
            return true;
        }, IntPtr.Zero);
        return r;
    }

    public static void Click(IntPtr dlg, int id) { PostMessage(dlg, 0x0111 /* WM_COMMAND */, (IntPtr)id, IntPtr.Zero); }
}
'@

$deadline = (Get-Date).AddSeconds($TimeoutSec)
$h = [IntPtr]::Zero
while ((Get-Date) -lt $deadline -and $h -eq [IntPtr]::Zero) {
    $h = [DlgW]::Find([uint32]$ProcId, 'PKTTC TextHub')
    if ($h -eq [IntPtr]::Zero) { Start-Sleep -Milliseconds 300 }
}
if ($h -eq [IntPtr]::Zero) { 'KHONG THAY HOP THOAI'; exit 2 }

'TITLE: ' + [DlgW]::Title($h)
foreach ($t in [DlgW]::Texts($h)) { 'TEXT: ' + ($t -replace "`r?`n", ' // ') }
$id = if ($Button -eq 'Yes') { 6 } else { 7 }
[DlgW]::Click($h, $id)
'DA BAM: ' + $Button
