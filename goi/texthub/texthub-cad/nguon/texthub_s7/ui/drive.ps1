# Dieu khien bang PKTEXTUI cua phien AutoCAD THU (theo PID) bang Win32: bam nut, doi the, chup RIENG cua so bang (PrintWindow, khong chup man hinh).
Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @"
using System;using System.Text;using System.Runtime.InteropServices;using System.Collections.Generic;using System.Drawing;using System.Drawing.Imaging;
public class Drv{
 public delegate bool P(IntPtr h,IntPtr l);
 [DllImport("user32.dll")] static extern bool EnumWindows(P p,IntPtr l);
 [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr h,P p,IntPtr l);
 [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h,out uint pid);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern int GetWindowText(IntPtr h,StringBuilder s,int n);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern int GetClassName(IntPtr h,StringBuilder s,int n);
 [DllImport("user32.dll")] static extern IntPtr SendMessage(IntPtr h,uint m,IntPtr w,IntPtr l);
 [DllImport("user32.dll")] static extern bool PostMessage(IntPtr h,uint m,IntPtr w,IntPtr l);
 [DllImport("user32.dll")] static extern bool GetWindowRect(IntPtr h,out RECT r);
 [DllImport("user32.dll")] static extern bool PrintWindow(IntPtr h,IntPtr hdc,uint f);
 [StructLayout(LayoutKind.Sequential)] public struct RECT{public int L,T,R,B;}
 public static IntPtr Pal(uint pid){IntPtr f=IntPtr.Zero;EnumWindows((h,l)=>{uint p;GetWindowThreadProcessId(h,out p);if(p!=pid)return true;var t=new StringBuilder(256);GetWindowText(h,t,256);if(t.ToString()=="PKTTC TextHub"){f=h;return false;}EnumChildWindows(h,(k,l2)=>{var t2=new StringBuilder(256);GetWindowText(k,t2,256);if(t2.ToString()=="PKTTC TextHub"){f=k;return false;}return true;},IntPtr.Zero);return f==IntPtr.Zero;},IntPtr.Zero);return f;}
 public static List<string> Kids(IntPtr top){var r=new List<string>();EnumChildWindows(top,(k,l)=>{var t=new StringBuilder(512);var c=new StringBuilder(256);GetWindowText(k,t,512);GetClassName(k,c,256);r.Add(k.ToInt64().ToString("X")+"|"+c.ToString().Replace("WindowsForms10.","").Split('.')[0]+"|"+t.ToString().Replace("\r"," ").Replace("\n"," "));return true;},IntPtr.Zero);return r;}
 public static IntPtr FindKid(IntPtr top,string cls,string text){IntPtr f=IntPtr.Zero;EnumChildWindows(top,(k,l)=>{var t=new StringBuilder(512);var c=new StringBuilder(256);GetWindowText(k,t,512);GetClassName(k,c,256);if(c.ToString().Contains(cls)&&(text==null||t.ToString()==text)){f=k;return false;}return true;},IntPtr.Zero);return f;}
 [DllImport("user32.dll",EntryPoint="SendMessageW",CharSet=CharSet.Unicode)] static extern IntPtr SendMessageS(IntPtr h,uint m,IntPtr w,string s);
 [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
 public static IntPtr FindVisible(IntPtr top,string cls,int nth){IntPtr f=IntPtr.Zero;int k0=0;EnumChildWindows(top,(k,l)=>{var c=new StringBuilder(256);GetClassName(k,c,256);if(c.ToString().Contains(cls)&&IsWindowVisible(k)){if(k0==nth){f=k;return false;}k0++;}return true;},IntPtr.Zero);return f;}
 public static void SetText(IntPtr h,string t){SendMessageS(h,0x000C,IntPtr.Zero,t);}
 public static void Click(IntPtr h){PostMessage(h,0x00F5,IntPtr.Zero,IntPtr.Zero);}
 public static string Dialog(uint pid,int id){string r="";EnumWindows((h,l)=>{uint p;GetWindowThreadProcessId(h,out p);if(p!=pid)return true;var c=new StringBuilder(64);GetClassName(h,c,64);if(c.ToString()=="#32770"){var t=new StringBuilder(256);GetWindowText(h,t,256);var tx=new StringBuilder(2048);r=t.ToString();var kids=new List<string>();EnumChildWindows(h,(k,l2)=>{var kt=new StringBuilder(2048);GetWindowText(k,kt,2048);kids.Add(kt.ToString());return true;},IntPtr.Zero);r=r+"::"+string.Join(" | ",kids.ToArray()).Replace((char)10,' ');if(id>0)SendMessage(h,0x0111,(IntPtr)id,IntPtr.Zero);return false;}return true;},IntPtr.Zero);return r;}
 public static void ClickAt(IntPtr h,int x,int y){IntPtr lp=(IntPtr)((y<<16)|(x&0xFFFF));PostMessage(h,0x0201,(IntPtr)1,lp);PostMessage(h,0x0202,IntPtr.Zero,lp);}
 public static string Shot(IntPtr h,string path){RECT r;GetWindowRect(h,out r);int w=r.R-r.L,ht=r.B-r.T;using(var bm=new Bitmap(w,ht)){using(var g=Graphics.FromImage(bm)){IntPtr dc=g.GetHdc();PrintWindow(h,dc,2);g.ReleaseHdc(dc);}bm.Save(path,ImageFormat.Png);}return w+"x"+ht;}
}
"@
function Get-Pal([int]$ProcId) { $h = [Drv]::Pal([uint32]$ProcId); if ($h -eq [IntPtr]::Zero) { throw 'khong thay cua so PKTTC TextHub' }; return $h }
function Click-Btn($pal, [string]$text) { $b = [Drv]::FindKid($pal, 'BUTTON', $text); if ($b -eq [IntPtr]::Zero) { throw "khong thay nut: $text" }; [Drv]::Click($b); "bam: $text" }
function Click-Tab($pal, [int]$index) {
    $t = [Drv]::FindKid($pal, 'SysTabControl32', $null)
    $xs = @(30, 80, 135, 185, 240)
    [Drv]::ClickAt($t, $xs[$index], 10); "the $index"
}

function Dialog-Text([int]$ProcId) { [Drv]::Dialog([uint32]$ProcId, 0) }
function Dialog-Yes([int]$ProcId) { [Drv]::Dialog([uint32]$ProcId, 6) }
function Dialog-No([int]$ProcId) { [Drv]::Dialog([uint32]$ProcId, 7) }
