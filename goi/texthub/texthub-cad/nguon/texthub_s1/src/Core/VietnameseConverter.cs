// PKTTC TextHub - Core: doi ma TCVN3 / VNI / Unicode. C# 5.
// Chuoi "ANSI" = chuoi ma AutoCAD tra ve khi byte cu duoc hieu theo trang ma he thong (mac dinh 1252).
using System;
using System.Text;

namespace Pkttc.Text.Core
{
    public static class VietnameseConverter
    {
        public const int DefaultCodePage = 1252;

        // ---------- Tien ich byte <-> chuoi theo trang ma ----------

        internal static Encoding GetCp(int codePage)
        {
            // Thay the ky tu khong ma hoa duoc bang '?', khong nem loi.
            return Encoding.GetEncoding(codePage, new EncoderReplacementFallback("?"), new DecoderReplacementFallback("?"));
        }

        /// <summary>True neu moi ky tu ma hoa duoc thanh dung 1 byte trong trang ma.</summary>
        public static bool IsEncodable(string text, int codePage)
        {
            Encoding strict = Encoding.GetEncoding(codePage, EncoderFallback.ExceptionFallback, DecoderFallback.ExceptionFallback);
            try
            {
                return strict.GetByteCount(text) == text.Length;
            }
            catch (EncoderFallbackException)
            {
                return false;
            }
        }

        public static bool IsEncodable(char c, int codePage)
        {
            return IsEncodable(c.ToString(), codePage);
        }

        /// <summary>Chuyen chuoi ANSI thanh chuoi "byte-ky-tu" (moi ky tu = 1 byte, 0..255).</summary>
        internal static string ToByteChars(string ansi, int codePage)
        {
            byte[] bytes = GetCp(codePage).GetBytes(ansi);
            char[] cs = new char[bytes.Length];
            for (int i = 0; i < bytes.Length; i++) cs[i] = (char)bytes[i];
            return new string(cs);
        }

        internal static string FromByteChars(string byteChars, int codePage)
        {
            byte[] bytes = new byte[byteChars.Length];
            for (int i = 0; i < byteChars.Length; i++) bytes[i] = (byte)byteChars[i];
            return GetCp(codePage).GetString(bytes);
        }

        // ---------- TCVN3 -> Unicode ----------

        /// <param name="ansi">Chuoi ANSI (byte TCVN3 duoc hieu theo trang ma).</param>
        /// <param name="sourceUpperFont">True neu font nguon la font HOA (.VnTimeH...).</param>
        public static ConversionResult TcvnToUnicode(string ansi, bool sourceUpperFont, int codePage)
        {
            ConversionResult r = new ConversionResult();
            r.From = Charset.Tcvn3;
            r.To = Charset.Unicode;
            if (string.IsNullOrEmpty(ansi)) { r.Text = ansi ?? ""; return r; }

            string bc = ToByteChars(ansi, codePage);
            StringBuilder sb = new StringBuilder(bc.Length);
            for (int i = 0; i < bc.Length; i++)
            {
                byte b = (byte)bc[i];
                char u;
                if (b < 0x80) sb.Append((char)b);
                else if (CharsetTables.TcvnToUni.TryGetValue(b, out u)) sb.Append(u);
                else
                {
                    r.Unmapped.Add(i);
                    sb.Append(FromByteChars(bc.Substring(i, 1), codePage));
                }
            }
            string res = sb.ToString();
            if (sourceUpperFont) res = res.ToUpperInvariant();
            r.Text = res;
            r.Changed = res != ansi;
            return r;
        }

        // ---------- VNI -> Unicode ----------

        public static ConversionResult VniToUnicode(string ansi, int codePage)
        {
            ConversionResult r = new ConversionResult();
            r.From = Charset.Vni;
            r.To = Charset.Unicode;
            if (string.IsNullOrEmpty(ansi)) { r.Text = ansi ?? ""; return r; }

            string bc = ToByteChars(ansi, codePage);
            StringBuilder sb = new StringBuilder(bc.Length);
            int i = 0;
            while (i < bc.Length)
            {
                char c = bc[i];
                char u;
                if (i + 1 < bc.Length && CharsetTables.VniPairToUni.TryGetValue(bc.Substring(i, 2), out u))
                {
                    sb.Append(u);
                    i += 2;
                }
                else if (c >= 0x80 && CharsetTables.VniSingleToUni.TryGetValue(c, out u))
                {
                    sb.Append(u);
                    i++;
                }
                else
                {
                    if (c >= 0x80)
                    {
                        r.Unmapped.Add(i);
                        sb.Append(FromByteChars(bc.Substring(i, 1), codePage));
                    }
                    else sb.Append(c);
                    i++;
                }
            }
            r.Text = sb.ToString();
            r.Changed = r.Text != ansi;
            return r;
        }

        // ---------- Unicode -> TCVN3 ----------

        /// <param name="targetUpperFont">True neu font dich la font HOA: moi chu dung ma cua chu thuong, hien thi thanh chu HOA.</param>
        public static ConversionResult UnicodeToTcvn(string unicode, bool targetUpperFont, int codePage)
        {
            ConversionResult r = new ConversionResult();
            r.From = Charset.Unicode;
            r.To = Charset.Tcvn3;
            if (string.IsNullOrEmpty(unicode)) { r.Text = unicode ?? ""; return r; }

            StringBuilder sb = new StringBuilder(unicode.Length);
            for (int i = 0; i < unicode.Length; i++)
            {
                char c = unicode[i];
                byte b;
                if (c < 0x80)
                {
                    sb.Append(c);
                    continue;
                }
                bool found = targetUpperFont
                    ? CharsetTables.UniToTcvnUpperFont.TryGetValue(c, out b)
                    : CharsetTables.UniToTcvnNormal.TryGetValue(c, out b);
                if (found) sb.Append(FromByteChars(((char)b).ToString(), codePage));
                else
                {
                    if (CharsetTables.IsVietLetter(c)) r.Unmapped.Add(i); // chu HOA co dau thanh can font HOA
                    sb.Append(c);
                }
            }
            r.Text = sb.ToString();
            r.Changed = r.Text != unicode;
            return r;
        }

        // ---------- Unicode -> VNI ----------

        public static ConversionResult UnicodeToVni(string unicode, int codePage)
        {
            ConversionResult r = new ConversionResult();
            r.From = Charset.Unicode;
            r.To = Charset.Vni;
            if (string.IsNullOrEmpty(unicode)) { r.Text = unicode ?? ""; return r; }

            StringBuilder sb = new StringBuilder(unicode.Length * 2);
            for (int i = 0; i < unicode.Length; i++)
            {
                char c = unicode[i];
                string v;
                if (CharsetTables.UniToVni.TryGetValue(c, out v)) sb.Append(FromByteChars(v, codePage));
                else sb.Append(c);
            }
            r.Text = sb.ToString();
            r.Changed = r.Text != unicode;
            return r;
        }

        // ---------- Dieu phoi ----------

        /// <summary>Doi tu bang ma nguon sang bang ma dich (qua Unicode).</summary>
        public static ConversionResult Convert(string text, Charset from, Charset to, bool sourceUpperFont, bool targetUpperFont, int codePage)
        {
            if (from == to || from == Charset.Ascii || from == Charset.Unknown)
            {
                ConversionResult same = new ConversionResult();
                same.Text = text;
                same.From = from;
                same.To = to;
                return same;
            }

            string uni = text;
            ConversionResult first = null;
            if (from == Charset.Tcvn3) { first = TcvnToUnicode(text, sourceUpperFont, codePage); uni = first.Text; }
            else if (from == Charset.Vni) { first = VniToUnicode(text, codePage); uni = first.Text; }

            if (to == Charset.Unicode || to == Charset.Ascii)
            {
                ConversionResult r = new ConversionResult();
                r.Text = uni;
                r.From = from;
                r.To = Charset.Unicode;
                if (first != null) r.Unmapped = first.Unmapped;
                r.Changed = uni != text;
                return r;
            }

            ConversionResult second = (to == Charset.Tcvn3)
                ? UnicodeToTcvn(uni, targetUpperFont, codePage)
                : UnicodeToVni(uni, codePage);
            second.From = from;
            if (first != null) second.Unmapped.InsertRange(0, first.Unmapped);
            second.Changed = second.Text != text;
            return second;
        }
    }
}
