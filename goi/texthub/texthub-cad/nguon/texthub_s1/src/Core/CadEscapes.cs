// PKTTC TextHub - Core: ma thoat cua AutoCAD trong chuoi chu (\U+XXXX, %%nnn). C# 5.
using System;
using System.Globalization;
using System.Text;

namespace Pkttc.Text.Core
{
    public static class CadEscapes
    {
        /// <summary>Giai \U+XXXX thanh ky tu Unicode. Giu nguyen moi thu khac.</summary>
        public static string DecodeUnicodeEscapes(string s)
        {
            if (string.IsNullOrEmpty(s) || s.IndexOf("\\U+", StringComparison.OrdinalIgnoreCase) < 0) return s;
            StringBuilder sb = new StringBuilder(s.Length);
            int i = 0;
            while (i < s.Length)
            {
                int cp;
                if (TryReadUnicodeEscape(s, i, out cp))
                {
                    sb.Append((char)cp);
                    i += 7;
                }
                else sb.Append(s[i++]);
            }
            return sb.ToString();
        }

        /// <summary>True neu tai vi tri i co dung \U+XXXX (4 so hex).</summary>
        internal static bool TryReadUnicodeEscape(string s, int i, out int codePoint)
        {
            codePoint = 0;
            if (i + 7 > s.Length) return false;
            if (s[i] != '\\') return false;
            if (s[i + 1] != 'U' && s[i + 1] != 'u') return false;
            if (s[i + 2] != '+') return false;
            for (int k = 3; k < 7; k++)
                if (!Uri.IsHexDigit(s[i + k])) return false;
            codePoint = int.Parse(s.Substring(i + 3, 4), NumberStyles.HexNumber, CultureInfo.InvariantCulture);
            return true;
        }

        /// <summary>Doi moi ky tu ngoai ASCII thanh \U+XXXX (dang an toan cho DXF/LISP).</summary>
        public static string EncodeUnicodeEscapes(string s)
        {
            if (string.IsNullOrEmpty(s)) return s;
            StringBuilder sb = new StringBuilder(s.Length + 8);
            foreach (char c in s)
            {
                if (c < 0x80) sb.Append(c);
                else sb.Append("\\U+").Append(((int)c).ToString("X4", CultureInfo.InvariantCulture));
            }
            return sb.ToString();
        }

        /// <summary>Doi %%nnn (3 chu so thap phan, byte 0..255) thanh ky tu theo trang ma. Khong dung %%c %%d %%p.</summary>
        public static string DecodePercentCodes(string s, int codePage)
        {
            if (string.IsNullOrEmpty(s) || s.IndexOf("%%", StringComparison.Ordinal) < 0) return s;
            StringBuilder sb = new StringBuilder(s.Length);
            int i = 0;
            while (i < s.Length)
            {
                if (s[i] == '%' && i + 4 < s.Length && s[i + 1] == '%'
                    && IsDigit(s, i + 2) && IsDigit(s, i + 3) && IsDigit(s, i + 4))
                {
                    int v = (s[i + 2] - '0') * 100 + (s[i + 3] - '0') * 10 + (s[i + 4] - '0');
                    if (v >= 0 && v <= 255)
                    {
                        sb.Append(VietnameseConverter.FromByteChars(((char)v).ToString(), codePage));
                        i += 5;
                        continue;
                    }
                }
                sb.Append(s[i++]);
            }
            return sb.ToString();
        }

        private static bool IsDigit(string s, int i)
        {
            return i < s.Length && s[i] >= '0' && s[i] <= '9';
        }
    }
}
