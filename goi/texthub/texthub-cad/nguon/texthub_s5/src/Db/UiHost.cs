// PKTTC TextHub - Ui: lenh PKTEXTUI (bang PaletteSet), chay viec GHI trong ngu canh lenh, cai menu KTTC. C# 5.
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.Windows;
using AcApp = Autodesk.AutoCAD.ApplicationServices.Core.Application;

[assembly: CommandClass(typeof(Pkttc.Text.Db.UiCommands))]

namespace Pkttc.Text.Db
{
    public class UiCommands
    {
        /// <summary>Mo bang PKTTC TextHub (quet, doi chu, font, kho font, tro ly).</summary>
        [CommandMethod("PKTEXTUI")]
        public void ShowUi() { UiHost.Show(); }

        /// <summary>Noi bo: chay viec GHI ma bang PKTEXTUI da xin phep (de co dung mot buoc UNDO). Khong co viec thi khong lam gi.</summary>
        [CommandMethod("PKTEXTUIEXEC")]
        public void ExecUi() { UiHost.RunPending(); }
    }

    public static class UiLog
    {
        /// <summary>Nhat ky chan doan nho cua phan giao dien: %LOCALAPPDATA%\PKTTC\ui.log (them dong, bo qua loi ghi).</summary>
        public static void Write(string line)
        {
            try
            {
                string dir = System.IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "PKTTC");
                System.IO.Directory.CreateDirectory(dir);
                System.IO.File.AppendAllText(System.IO.Path.Combine(dir, "ui.log"), DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + " | " + line + Environment.NewLine);
            }
            catch (System.Exception) { }
        }
    }

    public static class UiHost
    {
        private static PaletteSet _ps;
        private static UiPanel _panel;
        private static Action _pending;

        public static void Show()
        {
            try { ShowCore(); }
            catch (System.Exception ex)
            {
                UiLog.Write("PKTEXTUI loi: " + ex);
                Document doc = AcApp.DocumentManager.MdiActiveDocument;
                if (doc != null) doc.Editor.WriteMessage(Environment.NewLine + "[PKTTC] Khong mo duoc bang: " + ex.Message + Environment.NewLine);
            }
        }

        private static void ShowCore()
        {
            if (_ps == null)
            {
                _panel = new UiPanel();
                _ps = new PaletteSet("PKTTC TextHub", new Guid("B3A1E3C0-7C2E-4D7A-9E55-0A8D3E0C5F11"));
                _ps.Style = PaletteSetStyles.ShowPropertiesMenu | PaletteSetStyles.ShowAutoHideButton | PaletteSetStyles.ShowCloseButton;
                _ps.MinimumSize = new Size(430, 420);
                _ps.Size = new Size(560, 680);
                _ps.Add("TextHub", _panel);
                try { _ps.DockEnabled = DockSides.Left | DockSides.Right; _ps.Dock = DockSides.Right; } catch (System.Exception) { }
            }
            _ps.Visible = true;
            try { _ps.Size = new Size(560, 720); } catch (System.Exception) { }
            _panel.OnShown();
            UiLog.Write("PKTEXTUI: bang da mo");
        }

        /// <summary>Dat viec GHI cho lenh PKTEXTUIEXEC (ngu canh lenh: khoa ban ve, UNDO mot buoc). Viec chay ngay sau khi bang tra quyen dieu khien.</summary>
        public static void Run(Action job)
        {
            Document doc = AcApp.DocumentManager.MdiActiveDocument;
            if (doc == null) return;
            _pending = job;
            doc.SendStringToExecute("PKTEXTUIEXEC ", true, false, false);
        }

        public static void RunPending()
        {
            Action job = _pending;
            _pending = null;
            if (job == null) return;
            try { job(); }
            catch (System.Exception ex)
            {
                Document doc = AcApp.DocumentManager.MdiActiveDocument;
                if (doc != null) doc.Editor.WriteMessage("\n[PKTTC] LOI: " + ex.Message + "\n");
            }
        }
    }

    /// <summary>Menu KTTC tren thanh menu: KTTC > Text > Convert Font > cac lenh. Tao moi lan AutoCAD khoi dong, khong sua tep CUIX cua nguoi dung.</summary>
    public static class MenuInstaller
    {
        private const string MenuName = "KTTC";

        // (nhan hien tren menu, lenh, giai thich dai hien o thanh trang thai). null = dong ke ngang.
        private static readonly string[][] Items = new string[][]
        {
            new string[] { "PKTEXTUI  -  Mở bảng PKTTC TextHub", "PKTEXTUI", "Mở bảng TextHub dock bên phải: quét chữ, xem trước và đổi TCVN3/VNI sang Unicode, font, kho font, trợ lý Kuro" },
            null,
            new string[] { "PKTEXTSCAN  -  Quét chữ, xuất tệp JSON", "PKTEXTSCAN", "Quét mọi loại chữ (TEXT, MTEXT, ATTRIB, MLEADER, DIMENSION, ô bảng), nhận bảng mã, ghi tệp JSON. Chỉ đọc, không sửa bản vẽ" },
            new string[] { "PKTEXTAUDIT  -  Tóm tắt kết quả quét", "PKTEXTAUDIT", "In tóm tắt số lượng chữ theo bảng mã và cờ lỗi ngay trên dòng lệnh. Chỉ đọc" },
            new string[] { "PKTEXTPLAN  -  Lập kế hoạch đổi sang Unicode", "PKTEXTPLAN", "Lập kế hoạch đổi chữ TCVN3/VNI sang Unicode, ghi tệp JSON để xem lại. Chỉ đọc, không sửa bản vẽ" },
            new string[] { "PKTEXTAPPLY  -  Áp dụng kế hoạch đã lập", "PKTEXTAPPLY", "Áp dụng tệp kế hoạch JSON: hỏi YES, sao lưu bản vẽ vào _backup, đổi trong một bước, hoàn tác bằng U" },
            new string[] { "PKTEXTFIX  -  Lập kế hoạch và đổi ngay", "PKTEXTFIX", "Lập kế hoạch rồi áp dụng luôn: hỏi YES, sao lưu, đổi trong một bước, hoàn tác bằng U" },
            null,
            new string[] { "PKTEXTFONT  -  Báo cáo font, đối chiếu kho", "PKTEXTFONT", "Liệt kê font của Style và mã font trong MTEXT, báo font thiếu, gợi ý thay, sinh script cài font. Chỉ đọc" },
            new string[] { "PKTEXTFONTSUB  -  Thay font Style bị thiếu", "PKTEXTFONTSUB", "Thay font của các Style bị thiếu bằng font có sẵn trên máy: hỏi YES, sao lưu, hoàn tác bằng U" },
            new string[] { "PKTEXTPURGE  -  Dọn Style chữ không dùng", "PKTEXTPURGE", "Xóa các Style chữ không còn dùng (không kể Standard): hỏi YES, sao lưu, hoàn tác bằng U" },
            null,
            new string[] { "PKTEXTBRIDGE  -  Mở cổng cho trợ lý Kuro", "PKTEXTBRIDGE", "Mở cổng để trợ lý Kuro đọc và lập kế hoạch; mọi thao tác ghi đều hỏi lại bạn bằng hộp thoại Yes/No" },
            new string[] { "PKTEXTBRIDGESTOP  -  Đóng cổng Kuro", "PKTEXTBRIDGESTOP", "Đóng cổng trợ lý Kuro" },
            new string[] { "PKTEXTABOUT  -  Phiên bản và trạng thái", "PKTEXTABOUT", "Hiện phiên bản TextHub, danh sách lệnh, số tệp trong kho font và trạng thái cổng trợ lý" }
        };

        /// <summary>Hen cai menu khi AutoCAD ranh (giao dien da san sang).</summary>
        public static void Schedule()
        {
            UiLog.Write("menu KTTC: hen cai khi AutoCAD ranh");
            AcApp.Idle += OnIdle;
        }

        private static void OnIdle(object sender, EventArgs e)
        {
            AcApp.Idle -= OnIdle;
            try { Install(); }
            catch (System.Exception ex) { UiLog.Write("menu KTTC loi: " + ex.Message); /* menu la phan tien ich: loi thi bo qua, lenh van dung duoc */ }
        }

        private static void Install()
        {
            dynamic app = Autodesk.AutoCAD.ApplicationServices.Application.AcadApplication;
            dynamic groups = app.MenuGroups;
            dynamic baseGroup = null;
            int ng = (int)groups.Count;
            for (int i = 0; i < ng; i++)
            {
                dynamic g = groups.Item(i);
                if (string.Equals((string)g.Name, "ACAD", StringComparison.OrdinalIgnoreCase)) { baseGroup = g; break; }
            }
            if (baseGroup == null) return;

            dynamic menus = baseGroup.Menus;
            int nm = (int)menus.Count;
            for (int i = 0; i < nm; i++)
            {
                dynamic existing = menus.Item(i);
                if (string.Equals((string)existing.Name, MenuName, StringComparison.OrdinalIgnoreCase)) return; // da co (nap lai plugin)
            }

            dynamic pm = menus.Add(MenuName);
            dynamic text = pm.AddSubMenu((int)pm.Count, "Text");
            dynamic conv = text.AddSubMenu((int)text.Count, "Convert Font");
            foreach (string[] it in Items)
            {
                if (it == null) { conv.AddSeparator((int)conv.Count); continue; }
                dynamic mi = conv.AddMenuItem((int)conv.Count, it[0], "\u0003\u0003" + it[1] + " "); // Ctrl+C that (ma 3): qua COM, chuoi "^C^C" khong duoc dich va bi go nguyen vao dong lenh
                try { mi.HelpString = it[2]; } catch (System.Exception) { }
            }
            pm.InsertInMenuBar((int)app.MenuBar.Count);
            // Doc lai de chac menu that su nam tren thanh menu
            bool onBar = (bool)pm.OnMenuBar;
            int barCount = (int)app.MenuBar.Count;
            string first = (string)conv.Item(0).Label;
            string last = (string)conv.Item((int)conv.Count - 1).Label;
            UiLog.Write("menu KTTC: da tao, tren thanh menu=" + onBar + ", so muc thanh menu=" + barCount + ", Convert Font co " + (int)conv.Count + " dong; dau: " + first + " | cuoi: " + last);
        }
    }
}
