// PKTTC TextHub - Core: kiem tra am tiet tieng Viet hop le (dung de CHAM DIEM nhan dang bang ma). C# 5.
// Chi la quy tac am vi co ban, khong phai tu dien: du de phan biet van ban tieng Viet voi chuoi byte sai bang ma.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using System.Text.RegularExpressions;

namespace Pkttc.Text.Core
{
    public static class SyllableValidator
    {
        // a ă â e ê i o ô ơ u ư y  va cac to hop nguyen am hop le (khong dau thanh).
        private const string A = "a", AW = "ă", AC = "â", E = "e", EC = "ê", I = "i",
                             O = "o", OC = "ô", OH = "ơ", U = "u", UH = "ư", Y = "y", DD = "đ";

        private static readonly Regex Rx;

        static SyllableValidator()
        {
            string[] nuclei = new string[]
            {
                A, AW, AC, E, EC, I, O, OC, OH, U, UH, Y,
                "ai", "ao", "au", "ay", AC + "u", AC + "y", "eo", EC + "u", "ia", I + EC, "iu",
                "oa", "oai", "oay", "oe", "oi", OC + "i", OH + "i", "ua", U + AC, U + AC + "y", U + EC, "ui",
                U + OC, U + OC + "i", U + OH, "uy", "uya", "uy" + EC, UH + "a", UH + "i", UH + "u",
                UH + OH, UH + OH + "i", UH + OH + "u", "y" + EC, "y" + EC + "u", "oe" + "o", "oa" + AW,
                "i" + EC + "u", "oo", OC + OC, "uyu"
            };
            string[] initials = new string[]
            {
                "ngh", "ng", "nh", "ph", "th", "tr", "ch", "kh", "gh", "gi", "qu",
                "b", "c", "d", DD, "g", "h", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "x"
            };
            string[] finals = new string[] { "ch", "ng", "nh", "c", "m", "n", "p", "t" };

            Rx = new Regex(
                "^(" + string.Join("|", initials) + ")?(" + string.Join("|", nuclei) + ")(" + string.Join("|", finals) + ")?$",
                RegexOptions.Compiled | RegexOptions.CultureInvariant);
        }

        /// <summary>Tach dau thanh. Tra ve (nen khong dau thanh, ma dau thanh: 0 ngang, 1 huyen, 2 sac, 3 hoi, 4 nga, 5 nang).</summary>
        internal static string StripTone(string s, out int tone)
        {
            tone = 0;
            string d = s.Normalize(NormalizationForm.FormD);
            StringBuilder sb = new StringBuilder(d.Length);
            foreach (char c in d)
            {
                switch ((int)c)
                {
                    case 0x0300: tone = 1; continue;
                    case 0x0301: tone = 2; continue;
                    case 0x0309: tone = 3; continue;
                    case 0x0303: tone = 4; continue;
                    case 0x0323: tone = 5; continue;
                }
                sb.Append(c);
            }
            return sb.ToString().Normalize(NormalizationForm.FormC);
        }

        /// <summary>Mot "tu" (chuoi chu cai) co phai am tiet tieng Viet hop le khong.</summary>
        public static bool IsValid(string word)
        {
            if (string.IsNullOrEmpty(word)) return false;
            string w = word.ToLowerInvariant();
            int tone;
            string bare = StripTone(w, out tone);
            if (!Rx.IsMatch(bare)) return false;
            // am tiet ket thuc bang c, ch, p, t chi mang dau sac hoac nang (hoac khong dau)
            if (bare.EndsWith("c", StringComparison.Ordinal) || bare.EndsWith("ch", StringComparison.Ordinal)
                || bare.EndsWith("p", StringComparison.Ordinal) || bare.EndsWith("t", StringComparison.Ordinal))
            {
                if (tone != 0 && tone != 2 && tone != 5) return false;
            }
            return true;
        }

        /// <summary>
        /// Diem 0..1 = tu hop le / (tu hop le + tu sai co ky tu ngoai ASCII + 0,1 x tu ASCII khong hop le).
        /// Tu ASCII khong hop le (viet tat ky thuat: BTCT, L, x, mm) chi bi phat nhe, vi ban ma sai thuong sinh ky tu la.
        /// Khong co tu nao co the danh gia: tra -1.
        /// </summary>
        public static double Score(string text)
        {
            if (string.IsNullOrEmpty(text)) return -1;
            int valid = 0, bad = 0, neutral = 0;
            StringBuilder cur = new StringBuilder();
            bool ascii = true;
            for (int i = 0; i <= text.Length; i++)
            {
                char c = i < text.Length ? text[i] : ' ';
                if (char.IsLetter(c) || c == '̀' || c == '́' || c == '̃' || c == '̉' || c == '̣')
                {
                    cur.Append(c);
                    if (c >= 0x80) ascii = false;
                }
                else
                {
                    if (cur.Length > 0)
                    {
                        if (IsValid(cur.ToString())) valid++;
                        else if (ascii) neutral++;
                        else bad++;
                        cur.Length = 0;
                        ascii = true;
                    }
                }
            }
            if (valid + bad == 0) return -1;
            return valid / (valid + bad + 0.1 * neutral);
        }
    }
}
