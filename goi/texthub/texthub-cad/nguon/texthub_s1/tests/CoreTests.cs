// PKTTC TextHub - S1: bo kiem thu Core. Chay: Pkttc.Text.Core.Tests.exe (thoat 0 neu dat, 1 neu co loi).
// Khong dung khung kiem thu ngoai (may khong co NuGet): tu viet bo chay don gian.
// Cac chuoi vang (golden) duoi day lay tu kien thuc chuan TCVN3/VNI, KHONG sinh tu bang du lieu.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using Pkttc.Text.Core;

namespace Pkttc.Text.Core.Tests
{
    internal static class Program
    {
        private static int _pass;
        private static int _fail;
        private static readonly List<string> Failures = new List<string>();

        private static void Check(bool ok, string name)
        {
            if (ok) { _pass++; return; }
            _fail++;
            Failures.Add(name);
            Console.WriteLine("  [LOI] " + name);
        }

        private static void Eq(string expected, string actual, string name)
        {
            if (expected == actual) { _pass++; return; }
            _fail++;
            Failures.Add(name);
            Console.WriteLine("  [LOI] " + name + "\n         mong doi: " + Show(expected) + "\n         thuc te : " + Show(actual));
        }

        private static string Show(string s)
        {
            if (s == null) return "(null)";
            StringBuilder sb = new StringBuilder();
            foreach (char c in s)
            {
                if (c < 0x20 || c > 0x7E) sb.Append("\\u").Append(((int)c).ToString("X4"));
                else sb.Append(c);
            }
            return sb.ToString();
        }

        // Tao chuoi ANSI tu danh sach byte (theo trang ma)
        private static string Ansi(int cp, params int[] bytes)
        {
            char[] cs = new char[bytes.Length];
            for (int i = 0; i < bytes.Length; i++) cs[i] = (char)bytes[i];
            return VietnameseConverter.FromByteChars(new string(cs), cp);
        }

        private static string U(params int[] cps)
        {
            char[] cs = new char[cps.Length];
            for (int i = 0; i < cps.Length; i++) cs[i] = (char)cps[i];
            return new string(cs);
        }

        private static int Main()
        {
            Console.OutputEncoding = Encoding.UTF8;
            TestTables();
            TestVniKnownGood();
            TestRoundTrips(1252);
            TestRoundTrips(1258);
            TestGolden(1252);
            TestSyllables();
            TestFontRules();
            TestTokenizer();
            TestDetector();
            TestMText();

            Console.WriteLine();
            Console.WriteLine("Dat: " + _pass + "  Loi: " + _fail);
            return _fail == 0 ? 0 : 1;
        }

        // ---------------------------------------------------------------- bang ma
        private static void TestTables()
        {
            Console.WriteLine("Bang ma");
            Check(CharsetTables.VietLetters.Count == 134, "134 chu Viet");
            Check(CharsetTables.TcvnToUni.Count == 74, "74 byte TCVN3 (67 thuong + 7 HOA khong dau thanh)");
            Check(CharsetTables.VniSingleToUni.Count + CharsetTables.VniPairToUni.Count == 134, "VNI du 134 muc");
            HashSet<string> seen = new HashSet<string>();
            foreach (KeyValuePair<char, string> kv in CharsetTables.UniToVni) seen.Add(kv.Value);
            Check(seen.Count == 134, "134 chuoi VNI khac nhau (don anh)");
            Check(CharsetTables.UniToTcvnNormal.Count == 74, "74 chu dung duoc voi font TCVN3 thuong");
            Check(CharsetTables.UniToTcvnUpperFont.Count == 134, "134 chu dung duoc voi font HOA");
        }

        // 17 muc VNI ma LISP v2.6 sai so voi BVC va VFCC; gia tri duoi day theo bang VNI chuan.
        private static void TestVniKnownGood()
        {
            Console.WriteLine("VNI: cac muc LISP v2.6 sai");
            Dictionary<int, string> good = new Dictionary<int, string>();
            // ky tu Unicode -> byte hex cua VNI chuan
            good[0x00C3] = "41 D5"; // A + o
            good[0x00EC] = "EC"; good[0x00ED] = "ED";
            good[0x0129] = "F3"; good[0x1EC9] = "E6"; good[0x1ECB] = "F2";
            good[0x1EF5] = "EE";
            good[0x1EB3] = "61 FA"; good[0x1EB5] = "61 FC"; good[0x1EB7] = "61 EB";
            good[0x1EB2] = "41 DA"; good[0x1EB4] = "41 DC"; good[0x1EB6] = "41 CB";
            good[0x1EDB] = "F4 F9"; good[0x1EDD] = "F4 F8";
            good[0x1EDA] = "D4 D9"; good[0x1EDC] = "D4 D8";
            foreach (KeyValuePair<int, string> kv in good)
            {
                string s = CharsetTables.UniToVni[(char)kv.Key];
                StringBuilder hex = new StringBuilder();
                foreach (char c in s) { if (hex.Length > 0) hex.Append(' '); hex.Append(((int)c).ToString("X2")); }
                Eq(kv.Value, hex.ToString(), "VNI U+" + kv.Key.ToString("X4"));
            }
        }

        // ---------------------------------------------------------------- vong
        private static void TestRoundTrips(int cp)
        {
            Console.WriteLine("Vong U->T->U, U->V->U (trang ma " + cp + ")");
            int tcvnLowerOk = 0, tcvnUpperFontOk = 0, vniOk = 0, unmappedUpperTonal = 0;
            foreach (char u in CharsetTables.VietLetters)
            {
                string s = u.ToString();
                // VNI
                ConversionResult v = VietnameseConverter.UnicodeToVni(s, cp);
                ConversionResult vb = VietnameseConverter.VniToUnicode(v.Text, cp);
                if (vb.Text == s && vb.Unmapped.Count == 0) vniOk++;
                else Check(false, "VNI vong U+" + ((int)u).ToString("X4"));

                // TCVN3 font thuong
                ConversionResult t = VietnameseConverter.UnicodeToTcvn(s, false, cp);
                if (t.Unmapped.Count > 0) unmappedUpperTonal++;
                else
                {
                    ConversionResult tb = VietnameseConverter.TcvnToUnicode(t.Text, false, cp);
                    if (tb.Text == s) tcvnLowerOk++;
                    else Check(false, "TCVN3 vong thuong U+" + ((int)u).ToString("X4"));
                }

                // TCVN3 font HOA: moi chu thanh chu HOA
                ConversionResult th = VietnameseConverter.UnicodeToTcvn(s, true, cp);
                ConversionResult thb = VietnameseConverter.TcvnToUnicode(th.Text, true, cp);
                if (thb.Text == s.ToUpperInvariant()) tcvnUpperFontOk++;
                else Check(false, "TCVN3 vong font HOA U+" + ((int)u).ToString("X4"));
            }
            Check(vniOk == 134, "VNI: 134/134 chu qua vong (" + vniOk + ")");
            Check(tcvnLowerOk == 74, "TCVN3 thuong: 74 chu qua vong (" + tcvnLowerOk + ")");
            Check(unmappedUpperTonal == 60, "TCVN3 thuong: 60 chu HOA co dau thanh duoc bao khong doi duoc (" + unmappedUpperTonal + ")");
            Check(tcvnUpperFontOk == 134, "TCVN3 font HOA: 134/134 (" + tcvnUpperFontOk + ")");

            // Tat ca 134 chu noi lien nhau (kiem tra khong nham ranh gioi cap byte VNI)
            StringBuilder all = new StringBuilder();
            foreach (char u in CharsetTables.VietLetters) all.Append(u);
            string allS = all.ToString();
            ConversionResult av = VietnameseConverter.UnicodeToVni(allS, cp);
            ConversionResult avb = VietnameseConverter.VniToUnicode(av.Text, cp);
            Check(avb.Text == allS, "VNI noi lien 134 chu");

            // Chuoi hon hop co dau cach va so
            string sent = "Hà Nội 2026, đường Nguyễn Trãi - Km12+500";
            ConversionResult sv = VietnameseConverter.UnicodeToVni(sent, cp);
            Eq(sent, VietnameseConverter.VniToUnicode(sv.Text, cp).Text, "VNI cau hon hop");
            // TCVN3 thuong: chu hoa co dau thanh (H, N, T khong dau; 'ộ' thuong) -> cau nay chi co chu hoa khong dau thanh
            string sent2 = "Ha Noi, duong Nguy\u1EC5n Tr\u00E3i";
            ConversionResult st = VietnameseConverter.UnicodeToTcvn(sent2, false, cp);
            Eq(sent2, VietnameseConverter.TcvnToUnicode(st.Text, false, cp).Text, "TCVN3 cau thuong");
        }

        // ---------------------------------------------------------------- golden
        private static void TestGolden(int cp)
        {
            Console.WriteLine("Chuoi vang");
            // TCVN3: Đ=A7, à=B5, ẵ=BD, ệ=D6
            Eq(U(0x0110, 0xE0) + " N" + U(0x1EB5) + "ng",
               VietnameseConverter.TcvnToUnicode(Ansi(cp, 0xA7, 0xB5, 0x20, 0x4E, 0xBD, 0x6E, 0x67), false, cp).Text,
               "TCVN3 'Da Nang'");
            Eq(U(0x56) + "i" + U(0x1EC7) + "t Nam",
               VietnameseConverter.TcvnToUnicode(Ansi(cp, 0x56, 0x69, 0xD6, 0x74, 0x20, 0x4E, 0x61, 0x6D), false, cp).Text,
               "TCVN3 'Viet Nam'");
            // VNI: Ñ=D1, ø=F8, ü=FC, ä=E4, ñ=F1, ö=F6, ô=F4
            Eq(U(0x0110, 0xE0) + " N" + U(0x1EB5) + "ng",
               VietnameseConverter.VniToUnicode(Ansi(cp, 0xD1, 0x61, 0xF8, 0x20, 0x4E, 0x61, 0xFC, 0x6E, 0x67), cp).Text,
               "VNI 'Da Nang'");
            Eq("Vi" + U(0x1EC7) + "t Nam",
               VietnameseConverter.VniToUnicode(Ansi(cp, 0x56, 0x69, 0x65, 0xE4, 0x74, 0x20, 0x4E, 0x61, 0x6D), cp).Text,
               "VNI 'Viet Nam'");
            Eq(U(0x111, 0x1B0, 0x1EDD) + "ng",
               VietnameseConverter.VniToUnicode(Ansi(cp, 0xF1, 0xF6, 0xF4, 0xF8, 0x6E, 0x67), cp).Text,
               "VNI 'duong' (o va dau huyen)");
        }

        // ---------------------------------------------------------------- am tiet
        private static void TestSyllables()
        {
            Console.WriteLine("Am tiet");
            string[] ok = new string[]
            {
                "vi\u1EC7t", "nam", "\u0111\u01B0\u1EDDng", "nguy\u1EC5n", "th\u00E0nh", "ph\u1ED1", "qu\u1ED1c", "tu\u1EA5n",
                "g\u00EC", "khuya", "ngh\u0129a", "nghi\u00EAng", "t\u1EA1p", "\u0103n", "\u00F4", "\u00E0"
            };
            foreach (string w in ok) Check(SyllableValidator.IsValid(w), "hop le: " + Show(w));
            string[] bad = new string[] { "xyz", "bcd", "trg", "\u00B5\u00B8", "f\u00E0", "ng\u00E0c", "kh", "qwe" };
            foreach (string w in bad) Check(!SyllableValidator.IsValid(w), "khong hop le: " + Show(w));
        }

        // ---------------------------------------------------------------- font
        private static void TestFontRules()
        {
            Console.WriteLine("Quy tac font");
            Check(FontRules.IsUpperFont(".VnTimeH"), ".VnTimeH la font HOA");
            Check(FontRules.IsUpperFont("vntimeh.shx"), "vntimeh.shx la font HOA");
            Check(FontRules.IsUpperFont(".VnArialH"), ".VnArialH");
            Check(FontRules.IsUpperFont("C:\\Fonts\\.VnAvantH.ttf"), "duong dan + duoi .ttf");
            Check(!FontRules.IsUpperFont(".VnTime"), ".VnTime khong HOA");
            Check(!FontRules.IsUpperFont("Arial"), "Arial khong HOA");
            Check(!FontRules.IsUpperFont("VNI-Helve"), "VNI khong co font H");
            Check(FontRules.DeduceCharset(".VnTime") == Charset.Tcvn3, ".VnTime -> TCVN3");
            Check(FontRules.DeduceCharset("VNI-Times") == Charset.Vni, "VNI-Times -> VNI");
            Check(FontRules.DeduceCharset("vni_helve") == Charset.Vni, "vni_helve -> VNI");
            Check(FontRules.DeduceCharset("Arial") == Charset.Unicode, "Arial -> Unicode");
            Check(FontRules.DeduceCharset("Times New Roman") == Charset.Unicode, "Times New Roman -> Unicode");
            Check(FontRules.DeduceCharset("3T-Unicode.shx") == Charset.Unicode, "3T-Unicode -> Unicode");
            Check(FontRules.DeduceCharset("VN_UNI.shx") == Charset.Unicode, "VN_UNI.shx -> Unicode (khong phai TCVN3)");
            Check(FontRules.DeduceCharset("vn-abc.shx") == Charset.Tcvn3, "vn-abc.shx -> TCVN3");
            Check(FontRules.DeduceCharset("uv-abc.shx") == Charset.Unicode, "uv-abc.shx -> Unicode (header unifont)");
            FontRules.SetOverride("SomeRandomFont.shx", Charset.Unicode);
            Check(FontRules.DeduceCharset("SomeRandomFont") == Charset.Unicode, "ket qua xac dinh tu noi dung tep thang ten font");
            FontRules.ClearOverrides();
            Check(FontRules.DeduceCharset("SomeRandomFont") == Charset.Unknown, "xoa ket qua da dang ky");
            Check(FontRules.DeduceCharset("") == Charset.Unknown, "rong -> Unknown");
            Check(FontRules.DeduceCharset("SomeRandomFont") == Charset.Unknown, "la -> Unknown (khong doan)");
        }

        // ---------------------------------------------------------------- tach MTEXT
        private static void TestTokenizer()
        {
            Console.WriteLine("Tach MTEXT");
            string[] samples = new string[]
            {
                "", "abc", "{\\fArial|b0|i0|c0|p34;Hello}\\P{\\C1;x}", "\\S1/2;", "\\S1^2;m", "a\\\\b\\{c\\}", "\\U+00E0\\U+1EA1",
                "\\H0.5x;abc\\L u\\l", "{{}}", "}}{{", "a\\", "abc\\f", "\\fabc", "%%c25 %%d %%181", "\\pxqc;text", "\\Pa\\PB"
            };
            foreach (string s in samples)
                Eq(s, MTextTokenizer.Join(MTextTokenizer.Tokenize(s)), "noi lai: " + Show(s));

            List<MTextToken> t = MTextTokenizer.Tokenize("{\\fVnTime|b0|i0|c0|p34;x\\S1/2;y}\\P\\U+00E0");
            Check(t.Count == 8, "so token (" + t.Count + ")");
            Check(t[0].Kind == MTextTokenKind.GroupOpen, "token 0 la {");
            Check(t[1].Kind == MTextTokenKind.Format && MTextTokenizer.FontNameOf(t[1]) == "VnTime", "ten font VnTime");
            Check(t[3].Kind == MTextTokenKind.Stack && t[3].Text == "1/2", "phan so");

            // fuzz: noi lai phai bang chuoi goc
            string[] frags = new string[]
            {
                "\\P", "{", "}", "\\fVnTime|b0;", "\\fArial;", "\\S1/2;", "\\U+00E0", "\\\\", "\\{", "\\}", "abc", "\u00B5", " ",
                "\\", ";", "%%c", "%%181", "\\C1;", "\\H2x;", "\\L", "\\~", "x\\Sab"
            };
            Random rnd = new Random(12345);
            int bad = 0;
            for (int n = 0; n < 20000; n++)
            {
                StringBuilder sb = new StringBuilder();
                int k = rnd.Next(0, 13);
                for (int j = 0; j < k; j++) sb.Append(frags[rnd.Next(frags.Length)]);
                string s = sb.ToString();
                if (MTextTokenizer.Join(MTextTokenizer.Tokenize(s)) != s) { bad++; if (bad <= 3) Console.WriteLine("  fuzz loi: " + Show(s)); }
            }
            Check(bad == 0, "fuzz 20000 chuoi noi lai chinh xac (loi " + bad + ")");
        }

        // ---------------------------------------------------------------- nhan dang
        private static void TestDetector()
        {
            Console.WriteLine("Nhan dang");
            int cp = 1252;
            DetectionResult d;

            d = CharsetDetector.Detect(Ansi(cp, 0x56, 0x69, 0xD6, 0x74, 0x20, 0x4E, 0x61, 0x6D), "", cp);
            Check(d.Charset == Charset.Tcvn3 && d.Confidence >= 0.6, "TCVN3 khong font (" + d.Charset + " " + d.Confidence.ToString("0.00") + ")");
            d = CharsetDetector.Detect(Ansi(cp, 0x56, 0x69, 0xD6, 0x74, 0x20, 0x4E, 0x61, 0x6D), ".VnTime", cp);
            Check(d.Charset == Charset.Tcvn3 && d.Confidence >= 0.6, "TCVN3 co font .VnTime");

            d = CharsetDetector.Detect(Ansi(cp, 0x56, 0x69, 0x65, 0xE4, 0x74, 0x20, 0x4E, 0x61, 0x6D), "", cp);
            Check(d.Charset == Charset.Vni && d.Confidence >= 0.6, "VNI khong font (" + d.Charset + " " + d.Confidence.ToString("0.00") + ")");
            d = CharsetDetector.Detect(Ansi(cp, 0xD1, 0x61, 0xF8, 0x20, 0x4E, 0x61, 0xFC, 0x6E, 0x67), "VNI-Times", cp);
            Check(d.Charset == Charset.Vni && d.Confidence >= 0.6, "VNI 'Da Nang' co font VNI-Times");

            d = CharsetDetector.Detect("Vi" + U(0x1EC7) + "t Nam", "", cp);
            Check(d.Charset == Charset.Unicode && d.Confidence >= 0.6, "Unicode (co chu ngoai trang ma 1252)");
            d = CharsetDetector.Detect("Km 12+500, BTCT M300", "", cp);
            Check(d.Charset == Charset.Ascii, "ASCII");
            d = CharsetDetector.Detect("Nam " + U(0xE0), "", cp);
            Check(d.Charset == Charset.Unicode, "Latin-1 hop le ('Nam a-huyen') la Unicode (" + d.Charset + ")");

            // Chu Unicode chi gom ky tu Latin-1 kem viet tat ky thuat (du lieu that tu ban ve): khong duoc la Unknown
            d = CharsetDetector.Detect("THÉP L75x75x8mm", "VN_UNI.shx", cp);
            Check(d.Charset == Charset.Unicode && d.Confidence >= 0.6, "Unicode 'THEP L75x75x8mm' (" + d.Charset + " " + d.Confidence.ToString("0.00") + ")");
            d = CharsetDetector.Detect("TÔN NHÁM 3mm", "VN_UNI.shx", cp);
            Check(d.Charset == Charset.Unicode && d.Confidence >= 0.6, "Unicode 'TON NHAM 3mm' (" + d.Charset + " " + d.Confidence.ToString("0.00") + ")");
            d = CharsetDetector.Detect(Ansi(cp, 0x78, 0x75, 0x79, 0xAA, 0x6E, 0x20, 0x74, 0xB8, 0x6F, 0x20, 0x64, 0x31, 0x36), ".VnAvantH", cp);
            Check(d.Charset == Charset.Tcvn3 && d.Confidence >= 0.6, "TCVN3 'xuyen tao d16' (font HOA) (" + d.Charset + " " + d.Confidence.ToString("0.00") + ")");

            // Duong Nguyen Trai bang TCVN3 va VNI
            string tc = VietnameseConverter.UnicodeToTcvn("\u0110\u01B0\u1EDDng Nguy\u1EC5n Tr\u00E3i", false, cp).Text;
            d = CharsetDetector.Detect(tc, "", cp);
            Check(d.Charset == Charset.Tcvn3, "TCVN3 duong Nguyen Trai (" + d.Charset + " " + d.Confidence.ToString("0.00") + ")");
            string vn = VietnameseConverter.UnicodeToVni("\u0110\u01B0\u1EDDng Nguy\u1EC5n Tr\u00E3i", cp).Text;
            d = CharsetDetector.Detect(vn, "", cp);
            Check(d.Charset == Charset.Vni, "VNI duong Nguyen Trai (" + d.Charset + " " + d.Confidence.ToString("0.00") + ")");
        }

        // ---------------------------------------------------------------- MTEXT
        private static void TestMText()
        {
            Console.WriteLine("Doi MTEXT/TEXT");
            int cp = 1252;
            ConvertOptions opt = new ConvertOptions();
            opt.CodePage = cp;
            opt.Target = Charset.Unicode;

            string dn = Ansi(cp, 0xA7, 0xB5, 0x20, 0x4E, 0xBD, 0x6E, 0x67); // "Da Nang" TCVN3
            string raw = "{\\fVnTime|b0|i0|c0|p34;" + dn + "}\\P{\\fArial|b0;Hello}";
            MTextConvertResult r = MTextConverter.ConvertMText(raw, opt);
            Eq("{" + U(0x0110, 0xE0) + " N" + U(0x1EB5) + "ng}\\P{\\fArial|b0;Hello}", r.Text, "MTEXT: doi doan TCVN3, bo \\f cu, giu \\P va Arial");
            Check(r.Changed, "MTEXT: Changed");

            opt.StripLegacyFontCodes = false;
            r = MTextConverter.ConvertMText(raw, opt);
            Eq("{\\fVnTime|b0|i0|c0|p34;" + U(0x0110, 0xE0) + " N" + U(0x1EB5) + "ng}\\P{\\fArial|b0;Hello}", r.Text, "MTEXT: giu \\f khi tat StripLegacyFontCodes");
            opt.StripLegacyFontCodes = true;

            // %%nnn: byte 189 = ẵ
            r = MTextConverter.ConvertMText("{\\fVnTime;N%%189ng}", opt);
            Eq("{N" + U(0x1EB5) + "ng}", r.Text, "MTEXT: %%189 -> ẵ (TCVN3)");

            // Phan so: noi dung trong \S duoc doi, khung giu nguyen
            string v = Ansi(cp, 0x56, 0x69, 0x65, 0xE4, 0x74); // "Viet" VNI
            r = MTextConverter.ConvertMText("\\S" + v + "/2;", opt);
            Eq("\\SVi" + U(0x1EC7) + "t/2;", r.Text, "MTEXT: trong \\S");

            // Khong co font, khong chac chan: giu nguyen va bao
            r = MTextConverter.ConvertMText("{\\fArial;" + U(0xB5) + "}", opt);
            Check(!r.Changed || r.Ambiguous >= 0, "MTEXT: chuoi 1 ky tu khong lam hong (khong nem loi)");

            // TEXT thuong: font TCVN3 -> Unicode
            ConvertOptions o2 = new ConvertOptions();
            o2.CodePage = cp;
            o2.DefaultFont = ".VnTime";
            MTextConvertResult p = MTextConverter.ConvertPlain(dn, o2);
            Eq(U(0x0110, 0xE0) + " N" + U(0x1EB5) + "ng", p.Text, "TEXT: .VnTime -> Unicode");

            // TEXT HOA: .VnTimeH
            o2.DefaultFont = ".VnTimeH";
            // "Ha Noi" co dau, ma hoa bang font HOA (byte cua chu thuong), doc lai phai ra chu HOA
            string hn = VietnameseConverter.UnicodeToTcvn("Hà Nội", true, cp).Text;
            p = MTextConverter.ConvertPlain(hn, o2);
            Eq("HÀ NỘI", p.Text, "TEXT: font HOA doi thanh chu HOA");
            Check(p.Text == p.Text.ToUpperInvariant(), "TEXT: font HOA cho ket qua toan chu HOA");

            // Ten font HOA co dau cach (.VnArial NarrowH) van la font HOA
            Check(FontRules.IsUpperFont(".VnArial NarrowH"), ".VnArial NarrowH la font HOA (co dau cach)");
            Check(!FontRules.IsUpperFont(".VnArial Narrow"), ".VnArial Narrow khong HOA");
            o2.DefaultFont = ".VnArial NarrowH";
            p = MTextConverter.ConvertPlain(VietnameseConverter.UnicodeToTcvn("đốt k1", true, cp).Text, o2);
            Eq("ĐỐT K1", p.Text, "TEXT: .VnArial NarrowH doi thanh chu HOA");

            // Chu TCVN3 nam trong style Unicode (lech), moi chu cai ASCII deu HOA: coi la chu HOA
            o2.DefaultFont = "VN_UNI.shx";
            p = MTextConverter.ConvertPlain("T1.2 B" + U(0xB6) + "N T" + U(0xAB) + "N D" + U(0xB5) + "Y 10MM", o2);
            Eq("T1.2 B" + U(0x1EA2) + "N T" + U(0xD4) + "N D" + U(0xC0) + "Y 10MM", p.Text, "TEXT: lech font Unicode + ASCII toan HOA => HOA");

            // Ma ky hieu %%136 (duong kinh trong font SHX) di kem so: giu nguyen, khong bao "khong chac"
            o2.DefaultFont = "VN_UNI.shx";
            p = MTextConverter.ConvertPlain("%%13610X145X270", o2);
            Eq("%%13610X145X270", p.Text, "TEXT: %%136 + ASCII giu nguyen");
            Check(p.Ambiguous == 0, "TEXT: %%136 + ASCII khong bi bao khong chac (" + p.Ambiguous + ")");

            // Ma %%U (gach chan) khong lam hong nhan dang va duoc giu nguyen
            o2.DefaultFont = ".VnTime";
            p = MTextConverter.ConvertPlain("%%U" + dn, o2);
            Eq("%%U" + U(0x0110, 0xE0) + " N" + U(0x1EB5) + "ng", p.Text, "TEXT: %%U giu nguyen, chu doi");
            p = MTextConverter.ConvertPlain(dn + "%%D", o2);
            Eq(U(0x0110, 0xE0) + " N" + U(0x1EB5) + "ng%%D", p.Text, "TEXT: %%D cuoi chuoi");

            // Unicode -> TCVN3 va ve lai
            ConvertOptions o3 = new ConvertOptions();
            o3.CodePage = cp;
            o3.Target = Charset.Tcvn3;
            o3.DefaultFont = "Arial";
            MTextConvertResult back = MTextConverter.ConvertPlain("\u0111\u01B0\u1EDDng", o3);
            ConvertOptions o4 = new ConvertOptions();
            o4.CodePage = cp;
            o4.Target = Charset.Unicode;
            o4.DefaultFont = ".VnTime";
            Eq("\u0111\u01B0\u1EDDng", MTextConverter.ConvertPlain(back.Text, o4).Text, "TEXT: Unicode -> TCVN3 -> Unicode");

            // Ma hoa \U+XXXX
            ConvertOptions o5 = new ConvertOptions();
            o5.CodePage = cp;
            o5.EncodeUnicodeAsEscapes = true;
            o5.DefaultFont = ".VnTime";
            Eq("\\U+0110\\U+00E0", MTextConverter.ConvertPlain(Ansi(cp, 0xA7, 0xB5), o5).Text, "TEXT: ket qua dang \\U+XXXX");
        }
    }
}
