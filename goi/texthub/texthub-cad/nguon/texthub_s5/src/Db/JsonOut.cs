// PKTTC TextHub - Db: xuat ket qua quet ra JSON (UTF-8, chi ky tu ASCII, ky tu khac dang \uXXXX). C# 5.
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;

namespace Pkttc.Text.Db
{
    public static class JsonOut
    {
        public static void Write(ScanResult r, TextWriter w, bool onlyFlagged)
        {
            w.Write("{\"meta\":{");
            Kv(w, "drawing", r.Drawing); w.Write(',');
            Kv(w, "acadVersion", r.AcadVersion); w.Write(',');
            Kv(w, "codePage", r.CodePage); w.Write(',');
            Kv(w, "scannedAt", r.ScannedAt); w.Write(',');
            Kv(w, "elapsedMs", r.ElapsedMs); w.Write(',');
            Kv(w, "errors", r.Errors); w.Write(',');
            Kv(w, "itemsTotal", r.Items.Count); w.Write(',');
            Kv(w, "itemsOnlyFlagged", onlyFlagged ? 1 : 0);
            w.Write("},");

            w.Write("\"summary\":{");
            w.Write("\"byKind\":"); Counts(w, Group(r.Items, delegate(TextItem i) { return i.Kind; })); w.Write(',');
            w.Write("\"byOwnerKind\":"); Counts(w, Group(r.Items, delegate(TextItem i) { return i.OwnerKind; })); w.Write(',');
            w.Write("\"byCharset\":"); Counts(w, Group(r.Items, delegate(TextItem i) { return i.Charset; })); w.Write(',');
            w.Write("\"byFlag\":"); Counts(w, FlagCounts(r.Items)); w.Write(',');
            w.Write("\"unsupported\":"); Counts(w, r.Unsupported);
            w.Write("},");

            w.Write("\"styles\":[");
            for (int i = 0; i < r.Styles.Count; i++)
            {
                StyleInfo s = r.Styles[i];
                if (i > 0) w.Write(',');
                w.Write('{');
                Kv(w, "name", s.Name); w.Write(',');
                Kv(w, "fileName", s.FileName); w.Write(',');
                Kv(w, "typeFace", s.TypeFace); w.Write(',');
                Kv(w, "bigFont", s.BigFont); w.Write(',');
                Kv(w, "fontName", s.FontName); w.Write(',');
                Kv(w, "isShx", s.IsShx); w.Write(',');
                Kv(w, "fontExists", s.FontExists); w.Write(',');
                Kv(w, "hint", s.Hint); w.Write(',');
                Kv(w, "count", s.Count);
                w.Write('}');
            }
            w.Write("],");

            w.Write("\"items\":[");
            bool first = true;
            foreach (TextItem it in r.Items)
            {
                if (onlyFlagged && it.Flags.Count == 0 && it.Charset == "Ascii") continue;
                if (!first) w.Write(',');
                first = false;
                w.Write('{');
                Kv(w, "handle", it.Handle); w.Write(',');
                Kv(w, "kind", it.Kind); w.Write(',');
                Kv(w, "ownerKind", it.OwnerKind); w.Write(',');
                Kv(w, "owner", it.Owner); w.Write(',');
                Kv(w, "block", it.Block); w.Write(',');
                Kv(w, "layer", it.Layer); w.Write(',');
                Kv(w, "style", it.Style); w.Write(',');
                Kv(w, "font", it.Font); w.Write(',');
                Kv(w, "length", it.Length); w.Write(',');
                Kv(w, "charset", it.Charset); w.Write(',');
                Kv(w, "confidence", it.Confidence); w.Write(',');
                w.Write("\"flags\":[");
                for (int k = 0; k < it.Flags.Count; k++) { if (k > 0) w.Write(','); w.Write(Q(it.Flags[k])); }
                w.Write("],");
                Kv(w, "raw", it.Raw.Length > 400 ? it.Raw.Substring(0, 400) : it.Raw); w.Write(',');
                Kv(w, "preview", it.Preview);
                w.Write('}');
            }
            w.Write("]}");
        }

        // ---- tien ich ----
        private delegate string Key(TextItem i);

        private static Dictionary<string, int> Group(List<TextItem> items, Key key)
        {
            Dictionary<string, int> d = new Dictionary<string, int>();
            foreach (TextItem i in items)
            {
                string k = key(i);
                int n;
                d.TryGetValue(k, out n);
                d[k] = n + 1;
            }
            return d;
        }

        private static Dictionary<string, int> FlagCounts(List<TextItem> items)
        {
            Dictionary<string, int> d = new Dictionary<string, int>();
            foreach (TextItem i in items)
                foreach (string f in i.Flags)
                {
                    int n;
                    d.TryGetValue(f, out n);
                    d[f] = n + 1;
                }
            return d;
        }

        private static void Counts(TextWriter w, Dictionary<string, int> d)
        {
            w.Write('{');
            bool first = true;
            foreach (KeyValuePair<string, int> kv in d)
            {
                if (!first) w.Write(',');
                first = false;
                w.Write(Q(kv.Key)); w.Write(':'); w.Write(kv.Value.ToString(CultureInfo.InvariantCulture));
            }
            w.Write('}');
        }

        private static void Kv(TextWriter w, string k, string v) { w.Write(Q(k)); w.Write(':'); w.Write(Q(v)); }
        private static void Kv(TextWriter w, string k, int v) { w.Write(Q(k)); w.Write(':'); w.Write(v.ToString(CultureInfo.InvariantCulture)); }
        private static void Kv(TextWriter w, string k, bool v) { w.Write(Q(k)); w.Write(':'); w.Write(v ? "true" : "false"); }
        private static void Kv(TextWriter w, string k, double v) { w.Write(Q(k)); w.Write(':'); w.Write(v.ToString("0.##", CultureInfo.InvariantCulture)); }

        public static string Q(string s)
        {
            if (s == null) return "\"\"";
            StringBuilder sb = new StringBuilder(s.Length + 2);
            sb.Append('"');
            foreach (char c in s)
            {
                switch (c)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (c < 0x20 || c > 0x7E) sb.Append("\\u").Append(((int)c).ToString("x4", CultureInfo.InvariantCulture));
                        else sb.Append(c);
                        break;
                }
            }
            sb.Append('"');
            return sb.ToString();
        }
    }
}
