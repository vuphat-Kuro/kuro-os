// PKTTC TextHub - Db: thao tac "khong hoi" dung chung cho lenh (co hoi YES) va cong Kuro (hoi qua nguoi dung). C# 5.
// Moi ham GHI deu: sao luu truoc (that bai thi khong ghi), mot giao dich, ghi nhat ky. Viec hoi xac nhan nam o NOI GOI.
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Autodesk.AutoCAD.ApplicationServices;
using AcApp = Autodesk.AutoCAD.ApplicationServices.Core.Application;

namespace Pkttc.Text.Db
{
    public sealed class ApplyOutcome
    {
        public bool Ok;
        public string Message = "";
        public ApplyReport Report;
        public string BackupPath = "";
        public string LogJsonPath = "";
        public int Count;
    }

    public static class Ops
    {
        public static ScanResult Scan(Document doc)
        {
            ScanResult res = Scanner.Scan(doc.Database, Commands.CodePageOf());
            res.AcadVersion = AcApp.Version.ToString();
            return res;
        }

        public static Plan BuildPlan(Document doc, PlanOptions o)
        {
            return PlanBuilder.Build(Scan(doc), o);
        }

        public static List<FontUse> FontReport(Document doc, ScanResult scan)
        {
            return FontReporter.Build(scan, new FontEnv(doc.Database), FontStore.Load());
        }

        // ------------------------------------------------------------------ ghi
        public static ApplyOutcome ApplyPlan(Document doc, Plan plan)
        {
            ApplyOutcome o = new ApplyOutcome();
            BackupInfo bk = Backup.Make(doc.Database, "truoc_PKTEXT");
            if (!bk.Ok)
            {
                o.Message = "\n[PKTTC] KHONG sao luu duoc (" + bk.Error + "). Huy, ban ve khong doi.\n";
                return o;
            }
            o.BackupPath = bk.DwgPath;
            ApplyReport rep = Applier.Apply(doc.Database, plan);
            o.Report = rep;
            o.Count = rep.Ok;
            o.LogJsonPath = Path.Combine(bk.Dir, Path.GetFileNameWithoutExtension(bk.DwgPath) + "_apply.json");
            Commands.WriteApplyLog(rep, plan, o.LogJsonPath);
            Backup.AppendLog(bk, doc.Database.Filename, "PKTEXTAPPLY ke hoach " + plan.PlanId + ": ok " + rep.Ok + ", bo qua " + rep.Skipped + ", loi " + rep.Errors);

            if (rep.Errors > 0)
            {
                o.Message = "\n[PKTTC] Sao luu: " + bk.DwgPath + "\n[PKTTC] CO LOI (" + rep.Errors + " muc): khong ghi gi ca. Xem " + o.LogJsonPath + "\n";
                return o;
            }
            try { doc.Editor.Regen(); } catch (System.Exception) { }
            o.Ok = true;
            o.Message = "\n[PKTTC] Da sao luu: " + bk.DwgPath
                + "\n[PKTTC] Da doi " + rep.Ok + " muc (" + Commands.Fmt(rep.OkByKind) + "), bo qua " + rep.Skipped
                + ", style moi " + rep.StylesCreated + ", lech rong toi da " + (rep.MaxDeviation * 100).ToString("0.0") + "%, bi chan " + rep.Clamped
                + ".\n[PKTTC] Hoan tac: go U (mot buoc). Nhat ky: " + o.LogJsonPath + "\n";
            return o;
        }

        public static ApplyOutcome ApplyFontSub(Document doc, List<SubItem> plan)
        {
            ApplyOutcome o = new ApplyOutcome();
            BackupInfo bk = Backup.Make(doc.Database, "truoc_PKTEXTFONTSUB");
            if (!bk.Ok) { o.Message = "\n[PKTTC] KHONG sao luu duoc (" + bk.Error + "). Huy, ban ve khong doi.\n"; return o; }
            o.BackupPath = bk.DwgPath;
            string err;
            int n = StyleOps.ApplySub(doc.Database, plan, out err);
            if (err.Length > 0) { o.Message = "\n[PKTTC] LOI: " + err + ". Khong ghi gi ca.\n"; return o; }
            Backup.AppendLog(bk, doc.Database.Filename, "PKTEXTFONTSUB: da thay font " + n + " style");
            try { doc.Editor.Regen(); } catch (System.Exception) { }
            o.Ok = true;
            o.Count = n;
            o.Message = "\n[PKTTC] Da thay font " + n + " style. Sao luu: " + bk.DwgPath + "\n[PKTTC] Hoan tac: go U (mot buoc).\n";
            return o;
        }

        public static ApplyOutcome ApplyPurge(Document doc, List<string> names)
        {
            ApplyOutcome o = new ApplyOutcome();
            BackupInfo bk = Backup.Make(doc.Database, "truoc_PKTEXTPURGE");
            if (!bk.Ok) { o.Message = "\n[PKTTC] KHONG sao luu duoc (" + bk.Error + "). Huy, ban ve khong doi.\n"; return o; }
            o.BackupPath = bk.DwgPath;
            string err;
            int n = StyleOps.Purge(doc.Database, names, out err);
            if (err.Length > 0) { o.Message = "\n[PKTTC] LOI: " + err + ". Khong ghi gi ca.\n"; return o; }
            Backup.AppendLog(bk, doc.Database.Filename, "PKTEXTPURGE: da xoa " + n + " style");
            o.Ok = true;
            o.Count = n;
            o.Message = "\n[PKTTC] Da xoa " + n + " style. Sao luu: " + bk.DwgPath + "\n[PKTTC] Hoan tac: go U (mot buoc).\n";
            return o;
        }
    }
}
