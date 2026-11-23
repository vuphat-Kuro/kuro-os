// PKTTC TextHub - Core: tach chuoi MTEXT thanh ma dinh dang va doan chu. C# 5.
// Bao dam: Join(Tokenize(s)) == s voi moi s.
using System;
using System.Collections.Generic;
using System.Text;

namespace Pkttc.Text.Core
{
    public enum MTextTokenKind
    {
        /// <summary>Doan chu thuong (co the chua %%nnn).</summary>
        Text,
        /// <summary>\U+XXXX.</summary>
        UnicodeEscape,
        /// <summary>\\ \{ \}.</summary>
        EscapedChar,
        /// <summary>Ma co tham so ket thuc bang dau cham phay: \f \C \c \H \W \Q \T \A \p.</summary>
        Format,
        /// <summary>Phan so/xep chong \S...;</summary>
        Stack,
        /// <summary>Ma khong tham so: \P \L \l \O \o \K \k \~ \N.</summary>
        Flag,
        GroupOpen,
        GroupClose
    }

    public sealed class MTextToken
    {
        public MTextTokenKind Kind;
        /// <summary>Chuoi goc cua token (noi lai cac Raw se ra chuoi ban dau).</summary>
        public string Raw;
        /// <summary>Text/UnicodeEscape/EscapedChar: noi dung chu. Stack: phan trong \S...; Format: tham so.</summary>
        public string Text;
        /// <summary>Format/Stack/Flag: chu cai ma (vi du 'f', 'C', 'S').</summary>
        public char Code;

        public override string ToString()
        {
            return Kind + ":" + Raw;
        }
    }

    public static class MTextTokenizer
    {
        private const string ParamCodes = "fFCcHWQTAapS";
        private const string FlagCodes = "PLlOoKk~N";

        public static List<MTextToken> Tokenize(string s)
        {
            List<MTextToken> list = new List<MTextToken>();
            if (string.IsNullOrEmpty(s)) return list;

            int i = 0;
            StringBuilder text = new StringBuilder();
            while (i < s.Length)
            {
                char c = s[i];
                if (c == '{' || c == '}')
                {
                    Flush(list, text);
                    MTextToken g = new MTextToken();
                    g.Kind = c == '{' ? MTextTokenKind.GroupOpen : MTextTokenKind.GroupClose;
                    g.Raw = c.ToString();
                    g.Text = "";
                    list.Add(g);
                    i++;
                    continue;
                }
                if (c != '\\')
                {
                    text.Append(c);
                    i++;
                    continue;
                }

                // c == '\\'
                if (i + 1 >= s.Length)
                {
                    text.Append(c); // gach nguoc cuoi chuoi: coi nhu chu
                    i++;
                    continue;
                }
                char n = s[i + 1];
                int cp;
                if (CadEscapes.TryReadUnicodeEscape(s, i, out cp))
                {
                    Flush(list, text);
                    MTextToken u = new MTextToken();
                    u.Kind = MTextTokenKind.UnicodeEscape;
                    u.Raw = s.Substring(i, 7);
                    u.Text = ((char)cp).ToString();
                    list.Add(u);
                    i += 7;
                    continue;
                }
                if (n == '\\' || n == '{' || n == '}')
                {
                    Flush(list, text);
                    MTextToken e = new MTextToken();
                    e.Kind = MTextTokenKind.EscapedChar;
                    e.Raw = s.Substring(i, 2);
                    e.Text = n.ToString();
                    list.Add(e);
                    i += 2;
                    continue;
                }
                if (FlagCodes.IndexOf(n) >= 0)
                {
                    Flush(list, text);
                    MTextToken f = new MTextToken();
                    f.Kind = MTextTokenKind.Flag;
                    f.Raw = s.Substring(i, 2);
                    f.Text = "";
                    f.Code = n;
                    list.Add(f);
                    i += 2;
                    continue;
                }
                if (ParamCodes.IndexOf(n) >= 0)
                {
                    int semi = s.IndexOf(';', i + 2);
                    if (semi >= 0)
                    {
                        Flush(list, text);
                        MTextToken p = new MTextToken();
                        p.Kind = n == 'S' ? MTextTokenKind.Stack : MTextTokenKind.Format;
                        p.Raw = s.Substring(i, semi - i + 1);
                        p.Text = s.Substring(i + 2, semi - (i + 2));
                        p.Code = n;
                        list.Add(p);
                        i = semi + 1;
                        continue;
                    }
                }
                // Gach nguoc khong nhan ra: giu lai nhu chu.
                text.Append(c);
                i++;
            }
            Flush(list, text);
            return list;
        }

        public static string Join(IEnumerable<MTextToken> tokens)
        {
            StringBuilder sb = new StringBuilder();
            foreach (MTextToken t in tokens) sb.Append(t.Raw);
            return sb.ToString();
        }

        private static void Flush(List<MTextToken> list, StringBuilder text)
        {
            if (text.Length == 0) return;
            MTextToken t = new MTextToken();
            t.Kind = MTextTokenKind.Text;
            t.Raw = text.ToString();
            t.Text = t.Raw;
            list.Add(t);
            text.Length = 0;
        }

        /// <summary>Ten font trong ma \f: phan truoc dau '|' dau tien.</summary>
        public static string FontNameOf(MTextToken fontToken)
        {
            if (fontToken == null || (fontToken.Code != 'f' && fontToken.Code != 'F')) return null;
            string p = fontToken.Text ?? "";
            int bar = p.IndexOf('|');
            return bar >= 0 ? p.Substring(0, bar) : p;
        }
    }
}
