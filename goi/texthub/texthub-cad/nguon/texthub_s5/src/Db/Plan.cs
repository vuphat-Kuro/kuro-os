// PKTTC TextHub - Db: ke hoach doi chu (xem truoc, luu JSON, ap dung sau). C# 5.
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Web.Script.Serialization;

namespace Pkttc.Text.Db
{
    public sealed class PlanItem
    {
        public string Handle = "";
        public string Kind = "";
        /// <summary>Chi so o bang dang "r0c1" (chi TABLE_CELL).</summary>
        public string Cell = "";
        public string OwnerKind = "";
        public string Owner = "";
        public string OldRaw = "";
        public string NewText = "";
        public string OldStyle = "";
        public string NewStyle = "";
        /// <summary>Font dich cua muc nay (TrueType: ten ho font; SHX: ten tep .shx). Trong ke hoach cu khong co thi dung Options.TargetFont.</summary>
        public string NewFont = "";
    }

    public sealed class PlanOptions
    {
        /// <summary>Ten style dich. De trong = tu dat theo ten font (vi du "Arial"); tranh trung ten voi style khac font bang hau to _2, _3.</summary>
        public string TargetStyle = "";
        // Font dich mac dinh (anh Nghia chon 2026-11-23): nguon TrueType -> Arial Unicode MS, nguon SHX -> uv-abc.shx.
        // Khong dung Arial thuong: tren AutoCAD 2020 (da thu bang in PDF) style TrueType Arial kieu thuong KHONG ve duoc cac chu Viet
        // U+1EA0..U+1EF9 (A hoi, E mu sac, o cham, O mu sac, O ngã...); Arial Unicode MS, Segoe UI, Calibri thi ve du.
        public string TargetFont = "Arial Unicode MS";
        /// <summary>Font dich mac dinh cho chu co font nguon la SHX (tep .shx; phai la SHX Unicode).</summary>
        public string TargetShxFont = "uv-abc.shx";
        /// <summary>Font nguon (ten font cua Style, vi du ".VnAvantH", "vn-abc.shx") -> font dich. Font nguon khong co trong bang dung TargetFont.</summary>
        public Dictionary<string, string> FontMap = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        public bool KeepWidth = true;
        public bool IncludeLocked;
        public double MinConfidence = 0.6;
    }

    public sealed class Plan
    {
        public string PlanId = "";
        public string Drawing = "";
        public string CreatedAt = "";
        public PlanOptions Options = new PlanOptions();
        public List<PlanItem> Items = new List<PlanItem>();
        /// <summary>Ly do bo qua -> so luong (khong co trong Items).</summary>
        public Dictionary<string, int> Skipped = new Dictionary<string, int>();
    }

    public static class PlanBuilder
    {
        /// <summary>Lap ke hoach tu ket qua quet: chi doi chu TCVN3/VNI chac chan sang Unicode.</summary>
        public static Plan Build(ScanResult scan, PlanOptions o)
        {
            Plan p = new Plan();
            p.Drawing = scan.Drawing;
            p.CreatedAt = scan.ScannedAt;
            p.Options = o;
            o.TargetStyle = ResolveStyle(scan, o);
            Dictionary<string, string> styleOf = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

            foreach (TextItem it in scan.Items)
            {
                if (it.Charset != "Tcvn3" && it.Charset != "Vni") continue;
                string why = null;
                if (it.Kind == "DIMENSION") why = "dimension (chu thuoc DimStyle, chua ho tro)";
                else if (it.Flags.Contains("locked") && !o.IncludeLocked) why = "layer khoa";
                else if (it.Flags.Contains("field")) why = "co field";
                else if (it.Confidence < o.MinConfidence) why = "do tin cay thap";
                else if (it.UnmappedCount > 0) why = "co ky tu khong doi duoc";
                else if (string.IsNullOrEmpty(it.Converted) || it.Converted == it.Raw) why = "khong doi";
                if (why != null) { Inc(p.Skipped, why); continue; }

                PlanItem pi = new PlanItem();
                pi.Handle = it.Handle;
                pi.Kind = it.Kind;
                pi.Cell = it.Kind == "TABLE_CELL" ? it.Block : "";
                pi.OwnerKind = it.OwnerKind;
                pi.Owner = it.Owner;
                pi.OldRaw = it.Raw;
                pi.NewText = it.Converted;
                pi.OldStyle = it.Style;
                pi.NewFont = TargetFor(o, it.Font);
                string st;
                if (!styleOf.TryGetValue(pi.NewFont, out st))
                {
                    // Font dich mac dinh dung ten style da giai (co the do nguoi dung chi dinh); font khac thi dat theo TEN FONT.
                    st = string.Equals(pi.NewFont, o.TargetFont, StringComparison.OrdinalIgnoreCase) ? o.TargetStyle : ResolveStyleName(scan, pi.NewFont, "");
                    styleOf[pi.NewFont] = st;
                }
                pi.NewStyle = st;
                p.Items.Add(pi);
            }
            p.PlanId = ComputeId(p);
            return p;
        }

        /// <summary>
        /// Ten style dich. Nguoi dung chi dinh thi dung nguyen. Khong thi dat theo TEN FONT (khong tien to):
        /// dung lai style cung ten neu no da dung font do, trung ten khac font thi them _2, _3...
        /// </summary>
        public static string ResolveStyle(ScanResult scan, PlanOptions o)
        {
            return ResolveStyleName(scan, o.TargetFont, o.TargetStyle);
        }

        public static bool IsShx(string font)
        {
            return font != null && font.EndsWith(".shx", StringComparison.OrdinalIgnoreCase);
        }

        /// <summary>Font dich cho mot font nguon: theo bang FontMap, khong co thi TargetFont.</summary>
        public static string TargetFor(PlanOptions o, string sourceFont)
        {
            string t;
            if (!string.IsNullOrEmpty(sourceFont) && o.FontMap != null && o.FontMap.TryGetValue(sourceFont, out t) && !string.IsNullOrWhiteSpace(t)) return t.Trim();
            if (IsShx(sourceFont) && !string.IsNullOrWhiteSpace(o.TargetShxFont)) return o.TargetShxFont.Trim();
            return o.TargetFont;
        }

        /// <summary>Ten style cho mot font dich (explicitName khong rong thi dung nguyen). Dung lai style cung ten da dung dung font do (TrueType: so ten ho font; SHX: so ten tep).</summary>
        public static string ResolveStyleName(ScanResult scan, string font, string explicitName)
        {
            if (!string.IsNullOrWhiteSpace(explicitName)) return explicitName.Trim();
            string baseName = IsShx(font) ? font.Substring(0, font.Length - 4) : font;
            for (int n = 1; ; n++)
            {
                string cand = n == 1 ? baseName : baseName + "_" + n;
                StyleInfo found = null;
                foreach (StyleInfo s in scan.Styles)
                    if (string.Equals(s.Name, cand, StringComparison.OrdinalIgnoreCase)) { found = s; break; }
                if (found == null) return cand;
                bool same = IsShx(font)
                    ? string.Equals(found.FileName, font, StringComparison.OrdinalIgnoreCase)
                    : string.Equals(found.TypeFace, font, StringComparison.OrdinalIgnoreCase);
                if (same) return found.Name;
            }
        }

        internal static string ComputeId(Plan p)
        {
            StringBuilder sb = new StringBuilder();
            foreach (PlanItem i in p.Items)
                sb.Append(i.Handle).Append('|').Append(i.Cell).Append('|').Append(i.OldRaw).Append('|').Append(i.NewText).Append('|').Append(i.NewStyle).Append(i.NewFont.Length > 0 ? "|" + i.NewFont : "").Append('\n'); // ke hoach cu (khong co font dich tung muc) giu nguyen ma
            sb.Append(p.Options.TargetStyle).Append(p.Options.KeepWidth).Append(p.Options.IncludeLocked);
            using (SHA256 h = SHA256.Create())
            {
                byte[] d = h.ComputeHash(Encoding.UTF8.GetBytes(sb.ToString()));
                StringBuilder hex = new StringBuilder();
                for (int k = 0; k < 6; k++) hex.Append(d[k].ToString("x2"));
                return hex.ToString();
            }
        }

        private static void Inc(Dictionary<string, int> d, string k)
        {
            int n;
            d.TryGetValue(k, out n);
            d[k] = n + 1;
        }
    }

    public static class PlanIo
    {
        public static void Write(Plan p, string path)
        {
            Dictionary<string, object> root = new Dictionary<string, object>();
            root["planId"] = p.PlanId;
            root["drawing"] = p.Drawing;
            root["createdAt"] = p.CreatedAt;
            Dictionary<string, object> o = new Dictionary<string, object>();
            o["targetStyle"] = p.Options.TargetStyle;
            o["targetFont"] = p.Options.TargetFont;
            o["targetShxFont"] = p.Options.TargetShxFont;
            Dictionary<string, object> fm = new Dictionary<string, object>();
            foreach (KeyValuePair<string, string> kv in p.Options.FontMap) fm[kv.Key] = kv.Value;
            o["fontMap"] = fm;
            o["keepWidth"] = p.Options.KeepWidth;
            o["includeLocked"] = p.Options.IncludeLocked;
            o["minConfidence"] = p.Options.MinConfidence;
            root["options"] = o;
            root["skipped"] = p.Skipped;
            List<object> items = new List<object>();
            foreach (PlanItem i in p.Items)
            {
                Dictionary<string, object> d = new Dictionary<string, object>();
                d["handle"] = i.Handle; d["kind"] = i.Kind; d["cell"] = i.Cell;
                d["ownerKind"] = i.OwnerKind; d["owner"] = i.Owner;
                d["oldRaw"] = i.OldRaw; d["newText"] = i.NewText;
                d["oldStyle"] = i.OldStyle; d["newStyle"] = i.NewStyle; d["newFont"] = i.NewFont;
                items.Add(d);
            }
            root["items"] = items;

            JavaScriptSerializer js = new JavaScriptSerializer();
            js.MaxJsonLength = int.MaxValue;
            string dir = Path.GetDirectoryName(path);
            if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
            File.WriteAllText(path, js.Serialize(root), new UTF8Encoding(false));
        }

        public static Plan Read(string path)
        {
            JavaScriptSerializer js = new JavaScriptSerializer();
            js.MaxJsonLength = int.MaxValue;
            Dictionary<string, object> root = js.Deserialize<Dictionary<string, object>>(File.ReadAllText(path, Encoding.UTF8));
            Plan p = new Plan();
            p.PlanId = Str(root, "planId");
            p.Drawing = Str(root, "drawing");
            p.CreatedAt = Str(root, "createdAt");
            Dictionary<string, object> o = (Dictionary<string, object>)root["options"];
            p.Options.TargetStyle = Str(o, "targetStyle");
            p.Options.TargetFont = Str(o, "targetFont");
            if (o.ContainsKey("targetShxFont")) p.Options.TargetShxFont = Str(o, "targetShxFont");
            object fmo;
            if (o.TryGetValue("fontMap", out fmo) && fmo is Dictionary<string, object>)
                foreach (KeyValuePair<string, object> kv in (Dictionary<string, object>)fmo) p.Options.FontMap[kv.Key] = Convert.ToString(kv.Value);
            p.Options.KeepWidth = Convert.ToBoolean(o["keepWidth"]);
            p.Options.IncludeLocked = Convert.ToBoolean(o["includeLocked"]);
            p.Options.MinConfidence = Convert.ToDouble(o["minConfidence"]);
            foreach (object x in (System.Collections.IEnumerable)root["items"])
            {
                Dictionary<string, object> d = (Dictionary<string, object>)x;
                PlanItem i = new PlanItem();
                i.Handle = Str(d, "handle"); i.Kind = Str(d, "kind"); i.Cell = Str(d, "cell");
                i.OwnerKind = Str(d, "ownerKind"); i.Owner = Str(d, "owner");
                i.OldRaw = Str(d, "oldRaw"); i.NewText = Str(d, "newText");
                i.OldStyle = Str(d, "oldStyle"); i.NewStyle = Str(d, "newStyle"); i.NewFont = Str(d, "newFont");
                p.Items.Add(i);
            }
            // Ma ke hoach phai khop noi dung: file bi sua tay thi tu choi (xem Applier).
            string stated = p.PlanId;
            p.PlanId = PlanBuilder.ComputeId(p);
            if (stated != p.PlanId) throw new InvalidDataException("Ke hoach bi sua sau khi lap (ma " + stated + " khong khop " + p.PlanId + ").");
            return p;
        }

        private static string Str(Dictionary<string, object> d, string k)
        {
            object v;
            return d.TryGetValue(k, out v) && v != null ? Convert.ToString(v) : "";
        }
    }
}
