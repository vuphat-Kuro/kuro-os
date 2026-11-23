// PKTTC TextHub - Core: nhan dang bang ma cua mot doan chu. C# 5.
// Hai tang: (1) goi y tu ten font, (2) cham diem noi dung bang ty le am tiet tieng Viet hop le sau khi thu tung bang ma.
using System;

namespace Pkttc.Text.Core
{
    public static class CharsetDetector
    {
        /// <summary>Uu tien cong cho bang ma ma ten font goi y (theo diem, khong ep).</summary>
        private const double FontPrior = 0.25;

        /// <param name="ansiText">Chuoi doan chu (da giai %%nnn va \U+XXXX).</param>
        /// <param name="fontName">Ten font hieu luc (co the rong).</param>
        public static DetectionResult Detect(string ansiText, string fontName, int codePage)
        {
            DetectionResult r = new DetectionResult();
            if (string.IsNullOrEmpty(ansiText))
            {
                r.Charset = Charset.Ascii;
                r.Confidence = 1;
                return r;
            }

            bool anyHigh = false;
            foreach (char c in ansiText) if (c >= 0x80) { anyHigh = true; break; }
            if (!anyHigh)
            {
                r.Charset = Charset.Ascii;
                r.Confidence = 1;
                return r;
            }

            // Ky tu khong ma hoa duoc thanh 1 byte (vi du "a" co dau cham duoi U+1EA1) => chac chan Unicode.
            if (!VietnameseConverter.IsEncodable(ansiText, codePage))
            {
                r.Charset = Charset.Unicode;
                r.Confidence = 0.95;
                r.Note = "co ky tu ngoai trang ma " + codePage;
                return r;
            }

            Charset hint = FontRules.DeduceCharset(fontName);
            bool upper = FontRules.IsUpperFont(fontName);

            // Ung vien 1: chuoi la Unicode san.
            r.ScoreAsIs = Candidate(ansiText, ansiText, true);
            // Ung vien 2: TCVN3.
            ConversionResult t = VietnameseConverter.TcvnToUnicode(ansiText, upper && hint == Charset.Tcvn3, codePage);
            r.ScoreTcvn3 = Candidate(ansiText, t.Text, false) * Coverage(ansiText, t);
            // Ung vien 3: VNI.
            ConversionResult v = VietnameseConverter.VniToUnicode(ansiText, codePage);
            r.ScoreVni = Candidate(ansiText, v.Text, false) * Coverage(ansiText, v);

            double sa = r.ScoreAsIs, st = r.ScoreTcvn3, sv = r.ScoreVni;
            if (hint == Charset.Unicode) sa += FontPrior;
            else if (hint == Charset.Tcvn3) st += FontPrior;
            else if (hint == Charset.Vni) sv += FontPrior;

            Charset best = Charset.Unicode;
            double bs = sa;
            if (st > bs) { best = Charset.Tcvn3; bs = st; }
            if (sv > bs) { best = Charset.Vni; bs = sv; }

            double second = 0;
            if (best != Charset.Unicode) second = Math.Max(second, sa);
            if (best != Charset.Tcvn3) second = Math.Max(second, st);
            if (best != Charset.Vni) second = Math.Max(second, sv);

            // Do tin cay: diem tot nhat tru nua diem ung vien thu hai (hai ung vien cung cao => nham lan, tin cay thap).
            double conf = Math.Max(0, Math.Min(1, bs - 0.5 * second));
            if (bs < 0.5) { best = Charset.Unknown; conf = 0; r.Note = "khong ung vien nao dat 0,5"; }
            r.Charset = best;
            r.Confidence = conf;
            return r;
        }

        /// <summary>Diem ung vien = ty le am tiet hop le; chuoi khong co chu cai thi 0.</summary>
        private static double Candidate(string original, string decoded, bool asIs)
        {
            double s = SyllableValidator.Score(decoded);
            if (s < 0) return 0;
            if (asIs)
            {
                // Ky tu ANSI cao khong phai chu Viet (vi du ' µ ', ' ¸ ') la dau hieu SAI bang ma.
                int high = 0, ok = 0;
                foreach (char c in original)
                {
                    if (c < 0x80) continue;
                    high++;
                    if (CharsetTables.IsVietLetter(c)) ok++;
                }
                if (high > 0) s *= (double)ok / high;
            }
            return s;
        }

        /// <summary>Ty le byte cao duoc anh xa thanh chu Viet (ky tu khong anh xa duoc la dau hieu sai bang ma).</summary>
        private static double Coverage(string original, ConversionResult conv)
        {
            int high = 0;
            foreach (char c in original) if (c >= 0x80) high++;
            if (high == 0) return 1;
            int mapped = high - conv.Unmapped.Count;
            if (mapped < 0) mapped = 0;
            return (double)mapped / high;
        }
    }
}
