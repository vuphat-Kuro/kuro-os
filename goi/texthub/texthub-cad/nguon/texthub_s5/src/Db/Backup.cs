// PKTTC TextHub - Db: sao luu ban ve truoc khi ghi va ghi nhat ky. C# 5.
// Sao luu = ban chup TRANG THAI TRONG BO NHO (ke ca thay doi chua luu) bang Database.Wblock(); khong doi ten ban ve dang mo.
using System;
using System.IO;
using System.Text;
using Autodesk.AutoCAD.DatabaseServices;

namespace Pkttc.Text.Db
{
    public sealed class BackupInfo
    {
        public string Dir = "";
        public string DwgPath = "";
        public string LogPath = "";
        public string Error = "";
        public bool Ok { get { return Error.Length == 0 && File.Exists(DwgPath) && new FileInfo(DwgPath).Length > 0; } }
    }

    public static class Backup
    {
        /// <summary>Tao ban sao luu. Thu muc: &lt;thu muc ban ve&gt;\_backup\YYYYMMDD\ (ban chua luu: %LOCALAPPDATA%\PKTTC\backup\YYYYMMDD\).</summary>
        public static BackupInfo Make(Database db, string tag)
        {
            BackupInfo b = new BackupInfo();
            try
            {
                string drawing = db.Filename ?? "";
                string name = string.IsNullOrEmpty(drawing) ? "chua_luu" : Path.GetFileNameWithoutExtension(drawing);
                foreach (char c in Path.GetInvalidFileNameChars()) name = name.Replace(c, '_');

                string root = null;
                if (!string.IsNullOrEmpty(drawing))
                {
                    string d = Path.GetDirectoryName(drawing);
                    if (!string.IsNullOrEmpty(d) && Directory.Exists(d)) root = Path.Combine(d, "_backup");
                }
                if (root == null) root = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "PKTTC", "backup");

                DateTime now = DateTime.Now;
                b.Dir = Path.Combine(root, now.ToString("yyyyMMdd"));
                Directory.CreateDirectory(b.Dir);
                b.LogPath = Path.Combine(root, "_log.md");
                b.DwgPath = Path.Combine(b.Dir, name + "_" + now.ToString("HHmmss") + "_" + tag + ".dwg");

                using (Database copy = db.Wblock())
                    copy.SaveAs(b.DwgPath, DwgVersion.Current);

                if (!File.Exists(b.DwgPath) || new FileInfo(b.DwgPath).Length == 0)
                    b.Error = "Tep sao luu khong duoc tao.";
            }
            catch (System.Exception ex)
            {
                b.Error = ex.GetType().Name + ": " + ex.Message;
            }
            return b;
        }

        /// <summary>Them mot dong vao _backup\_log.md (tao tep voi dong tieu de neu chua co).</summary>
        public static void AppendLog(BackupInfo b, string drawing, string what)
        {
            if (string.IsNullOrEmpty(b.LogPath)) return;
            bool isNew = !File.Exists(b.LogPath);
            StringBuilder sb = new StringBuilder();
            if (isNew)
            {
                sb.AppendLine("# Nhat ky sao luu (PKTTC TextHub)");
                sb.AppendLine();
                sb.AppendLine("| Thoi gian | Ban ve | Ban sao luu | Noi dung |");
                sb.AppendLine("|---|---|---|---|");
            }
            sb.AppendLine("| " + DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + " | " + Path.GetFileName(drawing ?? "")
                + " | " + Path.GetFileName(b.DwgPath) + " | " + what.Replace("|", "/") + " |");
            File.AppendAllText(b.LogPath, sb.ToString(), new UTF8Encoding(false));
        }
    }
}
