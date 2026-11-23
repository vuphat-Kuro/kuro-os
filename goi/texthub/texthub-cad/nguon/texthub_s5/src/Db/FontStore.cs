// PKTTC TextHub - Db: kho font cua phong (thu muc cau hinh), CHI DOC. C# 5.
// Cau hinh: bien moi truong PKTTC_FONT_STORE (cac thu muc cach nhau dau ';') hoac tep %LOCALAPPDATA%\PKTTC\fontstore.txt (moi dong mot thu muc).
// TextHub KHONG tu cai font, KHONG ghi registry: chi doi chieu va sinh script cai de nguoi dung tu chay.
using System;
using System.Collections.Generic;
using System.IO;
using Pkttc.Text.Core;

namespace Pkttc.Text.Db
{
    public sealed class FontStore
    {
        public List<string> Roots = new List<string>();
        public int FileCount;
        // khoa chuan hoa (ten khong dau cham/cach/gach) + duoi -> duong dan day du
        private readonly Dictionary<string, string> _index = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

        private static readonly string[] Exts = new string[] { ".shx", ".ttf", ".otf", ".ttc" };

        // Ten ho font (chuan hoa) -> ten tep chuan hoa, khi tep khong dat theo ten ho font (vi du "Arial Unicode MS" nam trong ARIALUNI.ttf).
        private static readonly Dictionary<string, string> FileAlias = new Dictionary<string, string> { { "arialunicodems", "arialuni" } };

        public static FontStore Load()
        {
            List<string> roots = new List<string>();
            string env = Environment.GetEnvironmentVariable("PKTTC_FONT_STORE");
            if (string.Equals(env == null ? "" : env.Trim(), "NONE", StringComparison.OrdinalIgnoreCase))
                return Build(roots); // PKTTC_FONT_STORE=NONE: khong dung kho (bo qua ca tep cau hinh)
            if (!string.IsNullOrWhiteSpace(env))
                roots.AddRange(env.Split(new char[] { ';' }, StringSplitOptions.RemoveEmptyEntries));
            else
            {
                string cfg = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "PKTTC", "fontstore.txt");
                if (File.Exists(cfg))
                    foreach (string line in File.ReadAllLines(cfg))
                        if (!string.IsNullOrWhiteSpace(line) && !line.TrimStart().StartsWith("#")) roots.Add(line.Trim());
            }
            return Build(roots);
        }

        public static FontStore Build(IEnumerable<string> roots)
        {
            FontStore s = new FontStore();
            foreach (string r in roots)
            {
                string root = r.Trim().Trim('"');
                if (!Directory.Exists(root)) continue;
                s.Roots.Add(root);
                foreach (string f in Directory.EnumerateFiles(root, "*.*", SearchOption.AllDirectories))
                {
                    string ext = Path.GetExtension(f).ToLowerInvariant();
                    if (Array.IndexOf(Exts, ext) < 0) continue;
                    s.FileCount++;
                    string key = Norm(Path.GetFileNameWithoutExtension(f)) + ext;
                    if (!s._index.ContainsKey(key)) s._index[key] = f; // thu muc dau tien thang
                }
            }
            return s;
        }

        /// <summary>Duong dan moi tep trong kho co duoi ext (".shx", ".ttf"), moi ten chuan hoa mot tep.</summary>
        public List<string> FilesByExt(string ext)
        {
            List<string> r = new List<string>();
            foreach (string p in _index.Values)
                if (string.Equals(Path.GetExtension(p), ext, StringComparison.OrdinalIgnoreCase)) r.Add(p);
            return r;
        }

        /// <summary>Tim tep font theo ten (ten tep co duoi, hoac ten font TrueType). Tra null neu khong co.</summary>
        public string Find(string fontName)
        {
            if (string.IsNullOrWhiteSpace(fontName)) return null;
            string n = fontName.Trim();
            string ext = Path.GetExtension(n).ToLowerInvariant();
            string path;
            if (Array.IndexOf(Exts, ext) >= 0)
            {
                string key = Norm(Path.GetFileNameWithoutExtension(n)) + ext;
                return _index.TryGetValue(key, out path) ? path : null;
            }
            // Ten font TrueType (typeface): thu cac duoi theo thu tu uu tien; bo hau to bo ky tu (TUR, Baltic...)
            string baseName = Norm(Scanner.StripScript(n));
            string alias;
            if (FileAlias.TryGetValue(baseName, out alias)) baseName = alias;
            foreach (string e in new string[] { ".ttf", ".otf", ".ttc", ".shx" })
                if (_index.TryGetValue(baseName + e, out path)) return path;
            // Ho font ghi tep kieu "<ho>-Regular.ttf" (vi du Be Vietnam Pro)
            foreach (string e in new string[] { ".ttf", ".otf", ".ttc" })
                if (_index.TryGetValue(baseName + "regular" + e, out path)) return path;
            return null;
        }

        /// <summary>Chuan hoa: chu thuong, bo dau cham, cach, gach noi, gach duoi.</summary>
        internal static string Norm(string s)
        {
            System.Text.StringBuilder sb = new System.Text.StringBuilder(s.Length);
            foreach (char c in s.ToLowerInvariant())
                if (c != '.' && c != ' ' && c != '-' && c != '_') sb.Append(c);
            return sb.ToString();
        }
    }
}
