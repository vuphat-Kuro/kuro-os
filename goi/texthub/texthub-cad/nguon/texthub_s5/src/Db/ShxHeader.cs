// PKTTC TextHub - Db: doc loai tep SHX tu header (chi doc). C# 5.
// Header "AutoCAD-86 unifont 1.0" = font Unicode; "shapes" = font 8 bit (TCVN3/VNI tuy ten); "bigfont" = BigFont.
using System;
using System.IO;
using System.Text;

namespace Pkttc.Text.Db
{
    public static class ShxHeader
    {
        /// <summary>"unifont", "shapes", "bigfont" hoac "" (khong doc duoc / khong phai SHX).</summary>
        public static string Kind(string path)
        {
            try
            {
                if (string.IsNullOrEmpty(path) || !File.Exists(path)) return "";
                byte[] b = new byte[32];
                int n;
                using (FileStream f = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
                    n = f.Read(b, 0, b.Length);
                string h = Encoding.ASCII.GetString(b, 0, n);
                const string prefix = "AutoCAD-86 ";
                if (!h.StartsWith(prefix, StringComparison.Ordinal)) return "";
                string rest = h.Substring(prefix.Length);
                foreach (string k in new string[] { "unifont", "shapes", "bigfont" })
                    if (rest.StartsWith(k, StringComparison.Ordinal)) return k;
                return "";
            }
            catch (System.Exception)
            {
                return "";
            }
        }
    }
}
