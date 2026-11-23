// PKTTC TextHub - Core: quy tac suy bang ma tu TEN FONT (khong tu ten Style). C# 5.
// Quy uoc dat ten font tieng Viet cu: .VnTime, .VnArial (TCVN3); ...H = font HOA; VNI-Times, VNI-Helve (VNI).
using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;

namespace Pkttc.Text.Core
{
    public static class FontRules
    {
        private static readonly Regex UpperFontRx =
            new Regex(@"^\.?vn(?!i)[a-z0-9_\- ]*h$", RegexOptions.Compiled | RegexOptions.CultureInvariant);

        /// <summary>Ten co so: bo duong dan, bo duoi .ttf/.otf/.shx/.ttc, chu thuong, giu dau cham dau ten.</summary>
        public static string BaseName(string font)
        {
            if (string.IsNullOrWhiteSpace(font)) return "";
            string f = font.Trim();
            int slash = Math.Max(f.LastIndexOf('\\'), f.LastIndexOf('/'));
            if (slash >= 0) f = f.Substring(slash + 1);
            f = f.ToLowerInvariant();
            string[] exts = new string[] { ".ttf", ".otf", ".ttc", ".shx" };
            foreach (string e in exts)
            {
                if (f.EndsWith(e, StringComparison.Ordinal)) { f = f.Substring(0, f.Length - e.Length); break; }
            }
            return f;
        }

        /// <summary>True neu la font HOA TCVN3 (vi du .VnTimeH, vntimeh.shx).</summary>
        public static bool IsUpperFont(string font)
        {
            string b = BaseName(font);
            return b.Length > 0 && UpperFontRx.IsMatch(b);
        }

        // Ket qua da xac dinh tu NOI DUNG tep font (vi du header SHX "unifont"); thang ten font. Lop tren dang ky.
        private static readonly Dictionary<string, Charset> Overrides = new Dictionary<string, Charset>();

        public static void SetOverride(string font, Charset cs)
        {
            string b = BaseName(font);
            if (b.Length > 0) Overrides[b] = cs;
        }

        public static void ClearOverrides()
        {
            Overrides.Clear();
        }

        /// <summary>Suy bang ma tu ten font. Khong chac thi tra Unknown (khong doan).</summary>
        public static Charset DeduceCharset(string font)
        {
            string b = BaseName(font);
            if (b.Length == 0) return Charset.Unknown;

            Charset ov;
            if (Overrides.TryGetValue(b, out ov)) return ov;

            // Font Unicode tieng Viet dat ten kieu VN_UNI.shx, 3T-Unicode: phai xet truoc quy tac tien to "vn".
            if (b.IndexOf("unicode", StringComparison.Ordinal) >= 0 || b.EndsWith("_uni", StringComparison.Ordinal)
                || b.EndsWith("-uni", StringComparison.Ordinal) || b.EndsWith(" uni", StringComparison.Ordinal))
                return Charset.Unicode;

            if (b.StartsWith("vni", StringComparison.Ordinal)) return Charset.Vni;
            if (b.StartsWith(".vn", StringComparison.Ordinal)) return Charset.Tcvn3;
            if (b.StartsWith("vn", StringComparison.Ordinal)) return Charset.Tcvn3;

            string[] unicodeFonts = new string[]
            {
                "arial", "times new roman", "times", "tahoma", "calibri", "segoe ui", "verdana", "3t-unicode",
                "romans", "txt", "simplex", "standard", "uv-abc"
            };
            foreach (string u in unicodeFonts)
            {
                if (b == u || b.StartsWith(u + " ", StringComparison.Ordinal) || b.StartsWith(u + "-", StringComparison.Ordinal)
                    || (u == "arial" && b.StartsWith("arial", StringComparison.Ordinal))
                    || (u == "times" && b.StartsWith("times", StringComparison.Ordinal)))
                    return Charset.Unicode;
            }
            return Charset.Unknown;
        }

        /// <summary>True neu bang ma cu (can doi khi chuyen sang Unicode).</summary>
        public static bool IsLegacy(string font)
        {
            Charset c = DeduceCharset(font);
            return c == Charset.Tcvn3 || c == Charset.Vni;
        }
    }
}
