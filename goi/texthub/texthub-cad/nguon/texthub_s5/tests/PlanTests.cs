// PKTTC TextHub - S4: kiem thu cach dat ten style dich (khong can AutoCAD). Thoat 0 neu dat.
using System;
using System.Collections.Generic;
using Pkttc.Text.Db;

namespace Pkttc.Text.Tests
{
    internal static class PlanTests
    {
        private static int _fail, _pass;

        private static void Eq(string expected, string actual, string name)
        {
            if (expected == actual) { _pass++; return; }
            _fail++;
            Console.WriteLine("  [LOI] " + name + ": mong doi '" + expected + "', thuc te '" + actual + "'");
        }

        private static ScanResult Scan(params string[] nameFace)
        {
            ScanResult r = new ScanResult();
            for (int i = 0; i + 1 < nameFace.Length; i += 2)
            {
                StyleInfo s = new StyleInfo();
                s.Name = nameFace[i];
                s.TypeFace = nameFace[i + 1];
                s.FontName = s.TypeFace;
                r.Styles.Add(s);
            }
            return r;
        }

        private static TextItem Item(string handle, string font)
        {
            TextItem t = new TextItem();
            t.Handle = handle; t.Kind = "TEXT"; t.Charset = "Tcvn3"; t.Font = font; t.Style = "S" + handle;
            t.Raw = "raw" + handle; t.Converted = "new" + handle; t.Confidence = 1; t.OwnerKind = "model";
            return t;
        }

        private static string Resolve(ScanResult r, string target, string font)
        {
            PlanOptions o = new PlanOptions();
            o.TargetStyle = target;
            o.TargetFont = font;
            return PlanBuilder.ResolveStyle(r, o);
        }

        private static int Main()
        {
            Console.WriteLine("Ten style dich");
            Eq("Arial", Resolve(Scan(), "", "Arial"), "chua co style: dat theo ten font, khong tien to");
            Eq("Arial", Resolve(Scan("Standard", ""), "", "Arial"), "Standard khong lien quan");
            Eq("Arial", Resolve(Scan("Arial", "Arial"), "", "Arial"), "style Arial da dung font Arial: dung lai");
            Eq("Arial", Resolve(Scan("arial", "Arial"), "", "Arial").ToLowerInvariant() == "arial" ? "Arial" : "?", "khong phan biet hoa thuong");
            Eq("Arial_2", Resolve(Scan("Arial", "Times New Roman"), "", "Arial"), "ten Arial da co voi font khac: Arial_2");
            Eq("Arial_2", Resolve(Scan("Arial", "Times New Roman", "Arial_2", "Arial"), "", "Arial"), "Arial_2 da dung font Arial: dung lai");
            Eq("Arial_3", Resolve(Scan("Arial", "Times New Roman", "Arial_2", "Tahoma"), "", "Arial"), "Arial va Arial_2 deu khac font: Arial_3");
            Eq("My Style", Resolve(Scan("Arial", "Times New Roman"), " My Style ", "Arial"), "nguoi dung chi dinh: dung nguyen (bo khoang trang dau cuoi)");
            Eq(".VnTime", Resolve(Scan(), "", ".VnTime"), "ten font co dau cham dau: giu nguyen");
            Console.WriteLine("Font nguon -> font dich");
            ScanResult m = Scan("Arial Unicode MS", "Times New Roman");
            StyleInfo vu = new StyleInfo(); vu.Name = "VN_UNI"; vu.FileName = "VN_UNI.shx"; vu.IsShx = true; m.Styles.Add(vu);
            m.Items.Add(Item("1", ".VnAvantH")); m.Items.Add(Item("2", "vn-abc.shx")); m.Items.Add(Item("3", ".VnArial")); m.Items.Add(Item("4", ".VnAvantH")); m.Items.Add(Item("5", "vntime.shx"));
            PlanOptions mo = new PlanOptions();
            mo.FontMap[".VnAvantH"] = "Calibri";
            mo.FontMap["VN-ABC.SHX"] = "VN_UNI.shx";
            Plan mp = PlanBuilder.Build(m, mo);
            Eq("5", mp.Items.Count.ToString(), "5 muc vao ke hoach");
            Eq("Calibri|Calibri", mp.Items[0].NewFont + "|" + mp.Items[0].NewStyle, ".VnAvantH -> Calibri, style theo ten font");
            Eq("VN_UNI.shx|VN_UNI", mp.Items[1].NewFont + "|" + mp.Items[1].NewStyle, "vn-abc.shx (khong phan biet hoa thuong) -> VN_UNI.shx, dung lai style VN_UNI da dung tep do");
            Eq("Arial Unicode MS|Arial Unicode MS_2", mp.Items[2].NewFont + "|" + mp.Items[2].NewStyle, "font nguon TrueType khong co trong bang: Arial Unicode MS; ten da co voi font khac: _2");
            Eq("uv-abc.shx|uv-abc", mp.Items[4].NewFont + "|" + mp.Items[4].NewStyle, "font nguon SHX khong co trong bang: uv-abc.shx, style theo ten font");
            Eq("Calibri|Calibri", mp.Items[3].NewFont + "|" + mp.Items[3].NewStyle, "hai muc cung font nguon dung chung style dich");
            vu.FileName = "khac.shx";
            Eq("VN_UNI_2", PlanBuilder.ResolveStyleName(m, "VN_UNI.shx", ""), "style VN_UNI da dung tep SHX khac: VN_UNI_2");
            Eq("Arial Unicode MS", PlanBuilder.TargetFor(new PlanOptions(), "bat ky"), "khong co bang, nguon TrueType: Arial Unicode MS");
            Eq("uv-abc.shx", PlanBuilder.TargetFor(new PlanOptions(), "abc.SHX"), "khong co bang, nguon SHX: uv-abc.shx");
            Eq("True", PlanBuilder.IsShx("txt.SHX").ToString(), "IsShx khong phan biet hoa thuong");
            Console.WriteLine("Dat: " + _pass + "  Loi: " + _fail);
            return _fail == 0 ? 0 : 1;
        }
    }
}
