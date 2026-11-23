// PKTTC TextHub - Core: doi bang ma cho MTEXT va TEXT, chi tac dong len doan chu, giu nguyen ma dinh dang. C# 5.
using System;
using System.Collections.Generic;
using System.Text;

namespace Pkttc.Text.Core
{
    public sealed class ConvertOptions
    {
        /// <summary>Trang ma ANSI cua ban ve (1252 mac dinh; may Viet co the 1258).</summary>
        public int CodePage = VietnameseConverter.DefaultCodePage;
        /// <summary>Bang ma dich.</summary>
        public Charset Target = Charset.Unicode;
        /// <summary>True neu font dich la font HOA TCVN3 (chi co nghia khi Target = Tcvn3).</summary>
        public bool TargetUpperFont;
        /// <summary>Ep bang ma nguon (null = tu nhan dang theo font + noi dung).</summary>
        public Charset? SourceOverride;
        /// <summary>Font hieu luc cua Style (dung khi doan chu khong co ma \f).</summary>
        public string DefaultFont = "";
        /// <summary>Do tin cay toi thieu de tu dong doi; thap hon thi giu nguyen va bao.</summary>
        public double MinConfidence = 0.6;
        /// <summary>Bo ma \f cua font bang ma cu sau khi doi (de Style dich quyet dinh font).</summary>
        public bool StripLegacyFontCodes = true;
        /// <summary>Xuat Unicode dang \U+XXXX (an toan cho DXF/LISP) thay cho ky tu that.</summary>
        public bool EncodeUnicodeAsEscapes;
    }

    public sealed class RunReport
    {
        public string Original;
        public string Converted;
        public Charset Detected;
        public double Confidence;
        public string Font;
        public bool Applied;
        public string Reason = "";
    }

    public sealed class MTextConvertResult
    {
        public string Text;
        public bool Changed;
        public List<RunReport> Runs = new List<RunReport>();
        /// <summary>So doan bi bo qua vi khong chac chan.</summary>
        public int Ambiguous;
        /// <summary>So ky tu khong anh xa duoc.</summary>
        public int Unmapped;
    }

    /// <summary>Tach cac ma %%U %%O %%D %%P %%C %%K ra khoi chuoi chu (phan tu le = ma).</summary>
    internal static class CodeSplit
    {
        private static readonly System.Text.RegularExpressions.Regex Rx =
            new System.Text.RegularExpressions.Regex("(%%[UuOoDdPpCcKk])", System.Text.RegularExpressions.RegexOptions.Compiled);

        internal static string[] Split(string s)
        {
            return Rx.Split(s);
        }

        /// <summary>Phan tu o vi tri le cua ket qua Regex.Split (co nhom bat) la ma.</summary>
        internal static bool IsCode(string part, int index)
        {
            return (index & 1) == 1;
        }

        internal static string TextOnly(string[] parts)
        {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < parts.Length; i += 2) sb.Append(parts[i]).Append(' ');
            return sb.ToString();
        }
    }

    public static class MTextConverter
    {
        /// <summary>Doi mot chuoi MTEXT day du.</summary>
        public static MTextConvertResult ConvertMText(string raw, ConvertOptions opt)
        {
            MTextConvertResult res = new MTextConvertResult();
            if (string.IsNullOrEmpty(raw)) { res.Text = raw ?? ""; return res; }

            List<MTextToken> tokens = MTextTokenizer.Tokenize(raw);
            Stack<string> fontStack = new Stack<string>();
            string font = opt.DefaultFont ?? "";
            StringBuilder outSb = new StringBuilder(raw.Length + 16);

            int i = 0;
            while (i < tokens.Count)
            {
                MTextToken t = tokens[i];
                switch (t.Kind)
                {
                    case MTextTokenKind.GroupOpen:
                        fontStack.Push(font);
                        outSb.Append(t.Raw);
                        i++;
                        break;
                    case MTextTokenKind.GroupClose:
                        if (fontStack.Count > 0) font = fontStack.Pop();
                        outSb.Append(t.Raw);
                        i++;
                        break;
                    case MTextTokenKind.Format:
                        if (t.Code == 'f' || t.Code == 'F')
                        {
                            string name = MTextTokenizer.FontNameOf(t);
                            font = name ?? font;
                            // Chi bo ma font cu khi ket qua da la Unicode/khac bang ma cu (xem cuoi ham).
                            outSb.Append(t.Raw);
                        }
                        else outSb.Append(t.Raw);
                        i++;
                        break;
                    case MTextTokenKind.Text:
                    case MTextTokenKind.UnicodeEscape:
                        {
                            // Gom cac token chu lien nhau (Text, UnicodeEscape) thanh mot doan.
                            StringBuilder runRaw = new StringBuilder();
                            StringBuilder runText = new StringBuilder();
                            int j = i;
                            while (j < tokens.Count && (tokens[j].Kind == MTextTokenKind.Text || tokens[j].Kind == MTextTokenKind.UnicodeEscape))
                            {
                                runRaw.Append(tokens[j].Raw);
                                runText.Append(tokens[j].Text);
                                j++;
                            }
                            outSb.Append(ConvertRun(runRaw.ToString(), runText.ToString(), font, opt, res));
                            i = j;
                        }
                        break;
                    case MTextTokenKind.Stack:
                        {
                            string inner = t.Text ?? "";
                            string conv = ConvertRun(t.Raw, inner, font, opt, res);
                            // ConvertRun tra ve chuoi chu; giu khung \S...;
                            if (conv == t.Raw) outSb.Append(t.Raw);
                            else outSb.Append("\\S").Append(conv).Append(';');
                            i++;
                        }
                        break;
                    default: // Flag, EscapedChar
                        outSb.Append(t.Raw);
                        i++;
                        break;
                }
            }

            string result = outSb.ToString();
            if (opt.StripLegacyFontCodes && res.Changed) result = StripLegacyFonts(result, opt);
            res.Text = result;
            res.Changed = result != raw;
            return res;
        }

        /// <summary>Doi mot chuoi TEXT/ATTRIB (khong co ma dinh dang MTEXT; chi \U+XXXX va %%nnn).</summary>
        public static MTextConvertResult ConvertPlain(string raw, ConvertOptions opt)
        {
            MTextConvertResult res = new MTextConvertResult();
            if (string.IsNullOrEmpty(raw)) { res.Text = raw ?? ""; return res; }
            string text = CadEscapes.DecodeUnicodeEscapes(raw);
            string conv = ConvertRun(raw, text, opt.DefaultFont ?? "", opt, res);
            res.Text = conv;
            res.Changed = conv != raw;
            return res;
        }

        // ---- noi bo ----

        /// <summary>Doi mot doan chu. Tra ve chuoi thay the cho `raw` (neu khong doi thi tra ve raw).</summary>
        private static string ConvertRun(string raw, string text, string font, ConvertOptions opt, MTextConvertResult res)
        {
            RunReport rep = new RunReport();
            rep.Original = raw;
            rep.Font = font;
            res.Runs.Add(rep);

            // Chuan hoa %%nnn thanh ky tu theo trang ma de nhan dang.
            string norm = CadEscapes.DecodePercentCodes(text, opt.CodePage);

            // Ma %%U %%O %%D %%P %%C %%K khong phai chu: tach ra khoi doan khi nhan dang va khi doi, giu nguyen trong ket qua.
            string[] parts = CodeSplit.Split(norm);
            string plain = parts.Length > 1 ? CodeSplit.TextOnly(parts) : norm;

            Charset src;
            double conf;
            if (opt.SourceOverride.HasValue)
            {
                src = opt.SourceOverride.Value;
                conf = 1;
            }
            else
            {
                DetectionResult d = CharsetDetector.Detect(plain, font, opt.CodePage);
                src = d.Charset;
                conf = d.Confidence;
            }
            rep.Detected = src;
            rep.Confidence = conf;

            if (src == Charset.Ascii)
            {
                rep.Converted = raw;
                rep.Reason = "chi ASCII";
                return raw;
            }
            // %%nnn (nnn >= 128) trong chuoi con lai toan ASCII la ma ky hieu cua font SHX (vi du %%136 = duong kinh): khong phai chu.
            if (src == Charset.Unknown && OnlySymbolCodes(text))
            {
                rep.Detected = Charset.Ascii;
                rep.Converted = raw;
                rep.Reason = "ma ky hieu %%nnn";
                return raw;
            }
            if (src == Charset.Unknown || conf < opt.MinConfidence)
            {
                res.Ambiguous++;
                rep.Converted = raw;
                rep.Reason = "khong chac chan (" + conf.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture) + ")";
                return raw;
            }
            if (src == opt.Target || (src == Charset.Unicode && opt.Target == Charset.Unicode))
            {
                // Da dung bang ma dich; chi can xu ly %%nnn/\U+ neu muon, giu nguyen.
                if (opt.Target == Charset.Unicode && opt.EncodeUnicodeAsEscapes)
                {
                    string enc = CadEscapes.EncodeUnicodeEscapes(norm);
                    rep.Converted = enc;
                    rep.Applied = enc != raw;
                    return enc;
                }
                rep.Converted = raw;
                rep.Reason = "da dung bang ma dich";
                return raw;
            }

            // Chu TCVN3 nam trong style font Unicode (lech): khong co font TCVN3 de biet HOA hay thuong. Neu moi chu cai ASCII deu HOA
            // thi coi la chu HOA (nguoi ve go HOA o font HOA roi doi style); con lai giu theo font. [GIA THIET]
            bool upperSrc = src == Charset.Tcvn3 && (FontRules.IsUpperFont(font)
                || (FontRules.DeduceCharset(font) != Charset.Tcvn3 && AllAsciiLettersUpper(text)));
            StringBuilder conv = new StringBuilder();
            for (int pi = 0; pi < parts.Length; pi++)
            {
                if (CodeSplit.IsCode(parts[pi], pi)) { conv.Append(parts[pi]); continue; }
                ConversionResult cr = VietnameseConverter.Convert(parts[pi], src, opt.Target, upperSrc, opt.TargetUpperFont, opt.CodePage);
                res.Unmapped += cr.Unmapped.Count;
                conv.Append(cr.Text);
            }
            string outText = conv.ToString();
            if (opt.Target == Charset.Unicode && opt.EncodeUnicodeAsEscapes) outText = CadEscapes.EncodeUnicodeEscapes(outText);
            rep.Converted = outText;
            rep.Applied = outText != raw;
            if (rep.Applied) res.Changed = true;
            return outText;
        }

        /// <summary>True neu co it nhat 2 chu cai ASCII va tat ca deu HOA.</summary>
        private static bool AllAsciiLettersUpper(string text)
        {
            int n = 0;
            foreach (char c in text)
            {
                if (c >= 'a' && c <= 'z') return false;
                if (c >= 'A' && c <= 'Z') n++;
            }
            return n >= 2;
        }

        private static readonly System.Text.RegularExpressions.Regex HighPercent =
            new System.Text.RegularExpressions.Regex("%%(1[2-9][0-9]|2[0-5][0-9])", System.Text.RegularExpressions.RegexOptions.Compiled);

        /// <summary>True neu chuoi co %%nnn (128..259 cat ve 255) va phan con lai chi la ASCII.</summary>
        private static bool OnlySymbolCodes(string text)
        {
            if (!HighPercent.IsMatch(text)) return false;
            string rest = HighPercent.Replace(text, "");
            foreach (char c in rest) if (c >= 0x80) return false;
            return true;
        }

        /// <summary>Bo cac ma \f cua font bang ma cu (.VnTime, VNI-Times...) vi chu da doi sang bang ma khac.</summary>
        private static string StripLegacyFonts(string mtext, ConvertOptions opt)
        {
            List<MTextToken> tokens = MTextTokenizer.Tokenize(mtext);
            StringBuilder sb = new StringBuilder(mtext.Length);
            foreach (MTextToken t in tokens)
            {
                if (t.Kind == MTextTokenKind.Format && (t.Code == 'f' || t.Code == 'F'))
                {
                    string name = MTextTokenizer.FontNameOf(t);
                    if (FontRules.IsLegacy(name)) continue;
                }
                sb.Append(t.Raw);
            }
            return sb.ToString();
        }
    }
}
