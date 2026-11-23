// PKTTC TextHub - Db: noi Application.Idle (Acmgd) vao cong Kuro. Chi tai khi AutoCAD giao dien chay che do idle;
// accoreconsole khong co Acmgd nen khong bao gio goi lop nay. C# 5.
using System;
using System.Runtime.InteropServices;

namespace Pkttc.Text.Db
{
    /// <summary>Danh thuc vong lap thong diep cua AutoCAD tu luong khac (de Application.Idle chay ngay). Khong phu thuoc Acmgd.</summary>
    internal static class Win32Nudge
    {
        [DllImport("user32.dll")]
        private static extern bool PostMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);

        internal static volatile IntPtr Handle = IntPtr.Zero;

        internal static void Poke()
        {
            IntPtr h = Handle;
            if (h != IntPtr.Zero) PostMessage(h, 0 /* WM_NULL */, IntPtr.Zero, IntPtr.Zero);
        }
    }

    internal static class IdlePump
    {
        internal static void Attach()
        {
            Win32Nudge.Handle = Autodesk.AutoCAD.ApplicationServices.Application.MainWindow.Handle;
            Autodesk.AutoCAD.ApplicationServices.Application.Idle += OnIdle;
        }

        internal static void Detach()
        {
            Autodesk.AutoCAD.ApplicationServices.Application.Idle -= OnIdle;
            Win32Nudge.Handle = IntPtr.Zero;
        }

        private static void OnIdle(object sender, EventArgs e)
        {
            Bridge.IdleTick();
        }
    }
}
