// PKTTC TextHub - Db: bao cao font (style, BigFont, ma \f trong MTEXT), doi chieu voi kho font, goi y thay the, script cai. C# 5.
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Autodesk.AutoCAD.DatabaseServices;
using Pkttc.Text.Core;

namespace Pkttc.Text.Db
{
    public sealed class FontUse
    {
        public string Name = "";
        public bool IsShx;
        /// <summary>Nguon: style, bigfont, mtext (co the nhieu).</summary>
        public List<string> Sources = new List<string>();
        /// <summary>Ten cac style dung font nay lam font chinh.</summary>
        public List<string> Styles = new List<string>();
        public int Count;
        public string Hint = "";
        /// <summary>Loai SHX theo header: unifont, shapes, bigfont (rong neu khong phai SHX hoac khong doc duoc).</summary>
        public string ShxKind = "";
        /// <summary>ok | inStore | missing</summary>
        public string Status = "";
        public string StorePath = "";
        public string Substitute = "";
        /// <summary>installed | store | (rong)</summary>
        public string SubstituteSource = "";
    }

    /// <summary>Moi truong tra cuu font co san (ban ve + he thong). Khong ghi gi.</summary>
    public sealed class FontEnv
    {
        private readonly Database _db;
        private readonly HashSet<string> _installed;

        public FontEnv(Database db)
        {
            _db = db;
            _installed = Scanner.InstalledFamilies();
        }

        /// <summary>Duong dan day du cua SHX trong duong dan ho tro cua AutoCAD, hoac rong.</summary>
        public string ResolvePath(string name)
        {
            try { return HostApplicationServices.Current.FindFile(name, _db, FindFileHint.Default); }
            catch (System.Exception) { return ""; }
        }

        /// <summary>Font co dung duoc ngay khong: SHX tim thay trong duong dan ho tro, TrueType da cai.</summary>
        public bool Available(string name)
        {
            if (string.IsNullOrWhiteSpace(name)) return true;
            try
            {
                string ext = Path.GetExtension(name).ToLowerInvariant();
                if (ext == ".shx" || ext == ".shp")
                {
                    HostApplicationServices.Current.FindFile(name, _db, FindFileHint.Default);
                    return true;
                }
                if (ext == ".ttf" || ext == ".otf" || ext == ".ttc")
                {
                    if (_installed.Contains(Path.GetFileNameWithoutExtension(name))) return true;
                    HostApplicationServices.Current.FindFile(name, _db, FindFileHint.Default);
                    return true;
                }
                return _installed.Contains(name) || _installed.Contains(Scanner.StripScript(name));
            }
            catch (System.Exception)
            {
                return false;
            }
        }
    }

    public static class FontReporter
    {
        public static List<FontUse> Build(ScanResult scan, FontEnv env, FontStore store)
        {
            Dictionary<string, FontUse> by = new Dictionary<string, FontUse>(StringComparer.OrdinalIgnoreCase);

            foreach (StyleInfo s in scan.Styles)
            {
                if (s.FontName.Length > 0)
                {
                    FontUse u = Get(by, s.FontName, s.IsShx);
                    AddSource(u, "style");
                    if (!u.Styles.Contains(s.Name)) u.Styles.Add(s.Name);
                    u.Count += s.Count;
                }
                if (s.BigFont.Length > 0)
                {
                    string bf = Path.GetExtension(s.BigFont).Length == 0 ? s.BigFont + ".shx" : s.BigFont;
                    FontUse b = Get(by, bf, true);
                    AddSource(b, "bigfont");
                    b.Count += s.Count;
                }
            }

            // Font dat bang ma \f ngay trong chuoi MTEXT (MTEXT, MLEADER, o bang)
            foreach (TextItem it in scan.Items)
            {
                if (it.Raw.IndexOf("\\f", StringComparison.OrdinalIgnoreCase) < 0) continue;
                foreach (MTextToken t in MTextTokenizer.Tokenize(it.Raw))
                {
                    string name = MTextTokenizer.FontNameOf(t);
                    if (string.IsNullOrWhiteSpace(name)) continue;
                    // \F (chu hoa) = tep SHX, co the "font,bigfont" va khong co duoi; \f (chu thuong) = ho font TrueType.
                    if (t.Code == 'F')
                    {
                        foreach (string part in name.Split(new char[] { ',' }, StringSplitOptions.RemoveEmptyEntries))
                        {
                            string p = part.Trim();
                            if (p.Length == 0) continue;
                            if (Path.GetExtension(p).Length == 0) p += ".shx";
                            FontUse us = Get(by, p, true);
                            AddSource(us, "mtext");
                            us.Count++;
                        }
                        continue;
                    }
                    FontUse u = Get(by, name, name.EndsWith(".shx", StringComparison.OrdinalIgnoreCase));
                    AddSource(u, "mtext");
                    u.Count++;
                }
            }

            List<FontUse> list = new List<FontUse>(by.Values);
            foreach (FontUse u in list)
            {
                // SHX: doc header cua tep (tren may hoac trong kho) de biet Unicode hay 8 bit, thang ten font
                string sp0 = null;
                if (u.IsShx)
                {
                    string path = env.ResolvePath(u.Name);
                    if (string.IsNullOrEmpty(path)) { sp0 = store.Find(u.Name); path = sp0; }
                    u.ShxKind = ShxHeader.Kind(path);
                    if (u.ShxKind == "unifont") FontRules.SetOverride(u.Name, Charset.Unicode);
                }
                u.Hint = u.ShxKind == "bigfont" ? "BigFont" : FontRules.DeduceCharset(u.Name).ToString();
                if (env.Available(u.Name)) { u.Status = "ok"; continue; }
                string sp = store.Find(u.Name);
                if (sp != null) { u.Status = "inStore"; u.StorePath = sp; }
                else u.Status = "missing";
                if (u.Status != "ok") Suggest(u, env, store);
            }
            list.Sort(delegate(FontUse a, FontUse b) { return string.Compare(a.Name, b.Name, StringComparison.OrdinalIgnoreCase); });
            return list;
        }

        private static FontUse Get(Dictionary<string, FontUse> by, string name, bool shx)
        {
            FontUse u;
            if (!by.TryGetValue(name, out u))
            {
                u = new FontUse();
                u.Name = name;
                u.IsShx = shx;
                by[name] = u;
            }
            return u;
        }

        private static void AddSource(FontUse u, string s)
        {
            if (!u.Sources.Contains(s)) u.Sources.Add(s);
        }

        /// <summary>Goi y font thay the cung ho bang ma: uu tien font da co san, roi font trong kho.</summary>
        private static void Suggest(FontUse u, FontEnv env, FontStore store)
        {
            Charset cs = FontRules.DeduceCharset(u.Name);
            bool upper = FontRules.IsUpperFont(u.Name);
            string[] prefs;
            if (cs == Charset.Tcvn3)
                prefs = upper ? new string[] { ".VnArialH", ".VnTimeH", ".VnAvantH", "vntimeh.shx" }
                              : new string[] { ".VnArial", ".VnTime", ".VnAvant", "vntime.shx", "vn-abc.shx" };
            else if (cs == Charset.Vni)
                prefs = new string[] { "VNI-Times", "VNI-Helve", "VNI-Avo" };
            else
                prefs = new string[] { "Segoe UI", "Arial Unicode MS", "Calibri", "Arial", "Times New Roman" }; // Arial va Times thuong thieu glyph chu Viet o AutoCAD: de cuoi

            foreach (string p in prefs)
                if (!p.Equals(u.Name, StringComparison.OrdinalIgnoreCase) && env.Available(p)) { u.Substitute = p; u.SubstituteSource = "installed"; return; }
            foreach (string p in prefs)
                if (store.Find(p) != null) { u.Substitute = p; u.SubstituteSource = "store"; return; }
        }

        // ------------------------------------------------------------------ xuat
        public static string ToJson(string drawing, FontStore store, List<FontUse> uses, ScanResult scan)
        {
            int ok = 0, inStore = 0, missing = 0;
            foreach (FontUse u in uses)
            {
                if (u.Status == "ok") ok++; else if (u.Status == "inStore") inStore++; else missing++;
            }
            StringBuilder sb = new StringBuilder();
            sb.Append("{\"meta\":{\"drawing\":").Append(JsonOut.Q(drawing));
            sb.Append(",\"fontsTotal\":").Append(uses.Count).Append(",\"ok\":").Append(ok).Append(",\"inStore\":").Append(inStore).Append(",\"missing\":").Append(missing);
            sb.Append(",\"storeFiles\":").Append(store.FileCount).Append(",\"storeRoots\":[");
            for (int i = 0; i < store.Roots.Count; i++) { if (i > 0) sb.Append(','); sb.Append(JsonOut.Q(store.Roots[i])); }
            sb.Append("]},\"fonts\":[");
            for (int i = 0; i < uses.Count; i++)
            {
                FontUse u = uses[i];
                if (i > 0) sb.Append(',');
                sb.Append("{\"name\":").Append(JsonOut.Q(u.Name)).Append(",\"isShx\":").Append(u.IsShx ? "true" : "false");
                sb.Append(",\"status\":").Append(JsonOut.Q(u.Status)).Append(",\"hint\":").Append(JsonOut.Q(u.Hint)).Append(",\"shxKind\":").Append(JsonOut.Q(u.ShxKind));
                sb.Append(",\"count\":").Append(u.Count);
                sb.Append(",\"sources\":").Append(Arr(u.Sources)).Append(",\"styles\":").Append(Arr(u.Styles));
                sb.Append(",\"storePath\":").Append(JsonOut.Q(u.StorePath));
                sb.Append(",\"substitute\":").Append(JsonOut.Q(u.Substitute)).Append(",\"substituteSource\":").Append(JsonOut.Q(u.SubstituteSource)).Append('}');
            }
            sb.Append("],\"styles\":[");
            for (int i = 0; i < scan.Styles.Count; i++)
            {
                StyleInfo s = scan.Styles[i];
                if (i > 0) sb.Append(',');
                sb.Append("{\"name\":").Append(JsonOut.Q(s.Name)).Append(",\"font\":").Append(JsonOut.Q(s.FontName));
                sb.Append(",\"bigFont\":").Append(JsonOut.Q(s.BigFont)).Append(",\"fontExists\":").Append(s.FontExists ? "true" : "false");
                sb.Append(",\"bigFontExists\":").Append(s.BigFontExists ? "true" : "false").Append(",\"count\":").Append(s.Count).Append('}');
            }
            sb.Append("]}");
            return sb.ToString();
        }

        private static string Arr(List<string> l)
        {
            StringBuilder sb = new StringBuilder("[");
            for (int i = 0; i < l.Count; i++) { if (i > 0) sb.Append(','); sb.Append(JsonOut.Q(l[i])); }
            return sb.Append(']').ToString();
        }

        /// <summary>
        /// Sinh script PowerShell de NGUOI DUNG tu chay. Mac dinh chi xem; -Apply chep vao %APPDATA%\PKTTC\Fonts;
        /// ghi registry (cai TrueType cho nguoi dung hien tai) chi khi co them -RegisterFonts.
        /// </summary>
        public static string InstallScript(List<FontUse> uses)
        {
            List<FontUse> items = new List<FontUse>();
            foreach (FontUse u in uses) if (u.Status == "inStore" && u.StorePath.Length > 0) items.Add(u);

            StringBuilder sb = new StringBuilder();
            sb.AppendLine("# Sinh boi PKTTC TextHub. TextHub khong tu cai font va khong ghi registry; script nay do ban tu chay.");
            sb.AppendLine("#   powershell -File cai_font.ps1                   (chi xem, khong sao chep gi)");
            sb.AppendLine("#   powershell -File cai_font.ps1 -Apply            (chep font vao %APPDATA%\\PKTTC\\Fonts)");
            sb.AppendLine("#   powershell -File cai_font.ps1 -Apply -RegisterFonts   (them: cai TrueType cho nguoi dung hien tai, GHI REGISTRY HKCU)");
            sb.AppendLine("param([switch]$Apply, [switch]$RegisterFonts)");
            sb.AppendLine("$ErrorActionPreference = 'Stop'");
            sb.AppendLine("$dst = Join-Path $env:APPDATA 'PKTTC\\Fonts'");
            sb.AppendLine("$items = @(");
            foreach (FontUse u in items)
                sb.AppendLine("    @{ Name = '" + Esc(u.Name) + "'; Src = '" + Esc(u.StorePath) + "' },");
            sb.AppendLine(")");
            sb.AppendLine("if ($items.Count -eq 0) { 'Khong co font nao can cai tu kho.'; return }");
            sb.AppendLine("foreach ($i in $items) {");
            sb.AppendLine("    if (-not (Test-Path -LiteralPath $i.Src)) { \"[BO QUA] khong thay: $($i.Src)\"; continue }");
            sb.AppendLine("    if (-not $Apply) { \"[XEM] se chep $($i.Src) -> $dst\"; continue }");
            sb.AppendLine("    New-Item -ItemType Directory -Force $dst | Out-Null");
            sb.AppendLine("    Copy-Item -LiteralPath $i.Src -Destination $dst -Force");
            sb.AppendLine("    \"[DA CHEP] $($i.Name)\"");
            sb.AppendLine("}");
            sb.AppendLine("if ($Apply) {");
            sb.AppendLine("    'Font SHX: them thu muc sau vao AutoCAD (OPTIONS > Files > Support File Search Path):'");
            sb.AppendLine("    $dst");
            sb.AppendLine("}");
            sb.AppendLine("if ($Apply -and $RegisterFonts) {");
            sb.AppendLine("    # Chi chay khi ban chu dong them -RegisterFonts: ghi registry HKCU\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Fonts");
            sb.AppendLine("    $fontsDir = Join-Path $env:LOCALAPPDATA 'Microsoft\\Windows\\Fonts'");
            sb.AppendLine("    New-Item -ItemType Directory -Force $fontsDir | Out-Null");
            sb.AppendLine("    foreach ($i in $items) {");
            sb.AppendLine("        $ext = [IO.Path]::GetExtension($i.Src).ToLower()");
            sb.AppendLine("        if ($ext -notin '.ttf', '.otf') { continue }");
            sb.AppendLine("        $f = Join-Path $fontsDir (Split-Path $i.Src -Leaf)");
            sb.AppendLine("        Copy-Item -LiteralPath $i.Src -Destination $f -Force");
            sb.AppendLine("        New-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Fonts' -Name ($i.Name + ' (TrueType)') -Value $f -PropertyType String -Force | Out-Null");
            sb.AppendLine("        \"[DA CAI] $($i.Name)\"");
            sb.AppendLine("    }");
            sb.AppendLine("} elseif ($Apply) { 'Font TrueType: bam phai tep trong thu muc tren > Install for current user, hoac chay lai voi -RegisterFonts.' }");
            return sb.ToString();
        }

        private static string Esc(string s) { return s.Replace("'", "''"); }
    }
}
