// PKTTC TextHub - Db: lenh PKTEXTSCAN (xuat JSON) va PKTEXTAUDIT (tom tat tren dong lenh). CHI DOC.
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.EditorInput;
using Autodesk.AutoCAD.Runtime;
using AcApp = Autodesk.AutoCAD.ApplicationServices.Core.Application;

[assembly: ExtensionApplication(typeof(Pkttc.Text.Db.Plugin))]
[assembly: CommandClass(typeof(Pkttc.Text.Db.Commands))]

namespace Pkttc.Text.Db
{
    public class Plugin : IExtensionApplication
    {
        public void Initialize()
        {
            MenuInstaller.Schedule();
            Document doc = AcApp.DocumentManager.MdiActiveDocument;
            if (doc != null) doc.Editor.WriteMessage("\n[PKTTC TextHub] Da nap. Mo bang: PKTEXTUI (menu KTTC). Doc: PKTEXTSCAN, PKTEXTAUDIT, PKTEXTPLAN, PKTEXTFONT. Ghi (hoi YES + sao luu): PKTEXTAPPLY, PKTEXTFIX, PKTEXTFONTSUB, PKTEXTPURGE. Tro ly: PKTEXTBRIDGE, PKTEXTBRIDGESTOP.\n");
        }

        public void Terminate() { }
    }

    public class Commands
    {
        [CommandMethod("PKTEXTSCAN")]
        public void ScanToJson()
        {
            Document doc = AcApp.DocumentManager.MdiActiveDocument;
            Editor ed = doc.Editor;

            PromptStringOptions pso = new PromptStringOptions("\nTep JSON dau ra (Enter = mac dinh): ");
            pso.AllowSpaces = true;
            PromptResult pr = ed.GetString(pso);
            if (pr.Status != PromptStatus.OK && pr.Status != PromptStatus.None) return;

            string path = (pr.Status == PromptStatus.OK && !string.IsNullOrWhiteSpace(pr.StringResult))
                ? pr.StringResult.Trim().Trim('"')
                : DefaultPath(doc);

            ScanResult res = Run(doc);
            string dir = Path.GetDirectoryName(path);
            if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
            using (StreamWriter w = new StreamWriter(path, false, new UTF8Encoding(false)))
                JsonOut.Write(res, w, false);

            ed.WriteMessage("\n[PKTTC] Da quet " + res.Items.Count + " muc chu trong " + res.ElapsedMs + " ms. Loi: " + res.Errors + "\n[PKTTC] JSON: " + path + "\n");
        }

        [CommandMethod("PKTEXTAUDIT")]
        public void Audit()
        {
            Document doc = AcApp.DocumentManager.MdiActiveDocument;
            Editor ed = doc.Editor;
            ScanResult res = Run(doc);

            StringBuilder sb = new StringBuilder();
            sb.AppendLine();
            sb.AppendLine("[PKTTC] Ban ve: " + (string.IsNullOrEmpty(res.Drawing) ? "(chua luu)" : Path.GetFileName(res.Drawing))
                + " | trang ma " + res.CodePage + " | " + res.Items.Count + " muc chu | " + res.ElapsedMs + " ms | loi " + res.Errors);
            sb.AppendLine("  Theo loai   : " + Fmt(Count(res.Items, "kind")));
            sb.AppendLine("  Theo vi tri : " + Fmt(Count(res.Items, "ownerKind")));
            sb.AppendLine("  Bang ma     : " + Fmt(Count(res.Items, "charset")));
            sb.AppendLine("  Co hieu     : " + Fmt(Count(res.Items, "flag")));
            if (res.Unsupported.Count > 0) sb.AppendLine("  Chua ho tro : " + Fmt(res.Unsupported));
            int missing = 0;
            foreach (StyleInfo s in res.Styles) if (!s.FontExists && s.Count > 0) missing++;
            sb.AppendLine("  Style dung nhung thieu font: " + missing + " / " + res.Styles.Count);
            foreach (StyleInfo s in res.Styles)
                if (!s.FontExists && s.Count > 0) sb.AppendLine("    - " + s.Name + " (" + s.FontName + ", " + s.Count + " muc)");
            ed.WriteMessage(sb.ToString());
        }

        // ================================================================== S5: CONG CHO TRO LY (KURO)

        /// <summary>Mo cong cho tro ly (Kuro) dieu khien TextHub. Hoi YES; moi thao tac GHI cua tro ly con phai hoi lai.</summary>
        [CommandMethod("PKTEXTBRIDGE")]
        public void BridgeCmd()
        {
            Document doc = AcApp.DocumentManager.MdiActiveDocument;
            Editor ed = doc.Editor;
            string ans = AskString(ed, "\nGo YES de MO CONG cho tro ly (tro ly doc va lap ke hoach duoc; moi thao tac ghi se hoi lai ban): ");
            if (!string.Equals(ans, "YES", StringComparison.OrdinalIgnoreCase)) { ed.WriteMessage("\n[PKTTC] Da huy, cong khong mo.\n"); return; }
            if (Bridge.IsActive) { ed.WriteMessage("\n[PKTTC] Cong da mo. Dong bang PKTEXTBRIDGESTOP.\n"); return; }
            if (Bridge.UseIdle()) Bridge.StartIdle(doc, 30);
            else Bridge.Run(doc, 30);
        }

        /// <summary>Dong cong Kuro (che do khong chan).</summary>
        [CommandMethod("PKTEXTBRIDGESTOP")]
        public void BridgeStopCmd()
        {
            if (!Bridge.IsActive) { AcApp.DocumentManager.MdiActiveDocument.Editor.WriteMessage("\n[PKTTC] Cong khong mo.\n"); return; }
            Bridge.Stop("lenh PKTEXTBRIDGESTOP");
        }

        /// <summary>Noi bo: chay viec GHI ma nguoi dung da dong y trong hop thoai (do cong goi). Khong co viec thi khong lam gi.</summary>
        [CommandMethod("PKTEXTBRIDGEEXEC")]
        public void BridgeExecCmd()
        {
            Bridge.ExecPending();
        }

        // ================================================================== S4: FONT VA STYLE

        /// <summary>Bao cao font: Style, BigFont, ma \f trong MTEXT; doi chieu he thong va kho font; goi y thay the; sinh script cai. CHI DOC.</summary>
        [CommandMethod("PKTEXTFONT")]
        public void FontCmd()
        {
            Document doc = AcApp.DocumentManager.MdiActiveDocument;
            Editor ed = doc.Editor;
            string defJson = DefaultPath(doc, "fonts", ".json");
            string json = AskPath(ed, "\nTep JSON bao cao font (Enter = mac dinh): ", defJson);
            if (json == null) return;
            string ps1 = AskPath(ed, "\nTep script cai font (Enter = canh JSON): ", Path.ChangeExtension(json, ".cai_font.ps1"));
            if (ps1 == null) return;

            ScanResult scan = Run(doc);
            FontStore store = FontStore.Load();
            List<FontUse> uses = FontReporter.Build(scan, new FontEnv(doc.Database), store);

            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(json)));
            File.WriteAllText(json, FontReporter.ToJson(scan.Drawing, store, uses, scan), new UTF8Encoding(false));
            File.WriteAllText(ps1, FontReporter.InstallScript(uses), new UTF8Encoding(false));

            int ok = 0, inStore = 0, missing = 0;
            foreach (FontUse u in uses) { if (u.Status == "ok") ok++; else if (u.Status == "inStore") inStore++; else missing++; }
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("\n[PKTTC] Font: " + uses.Count + " (co san " + ok + ", co trong kho " + inStore + ", thieu " + missing + ") | kho: " + store.FileCount + " tep trong " + store.Roots.Count + " thu muc");
            foreach (FontUse u in uses)
            {
                if (u.Status == "ok") continue;
                sb.AppendLine("  - " + u.Name + " [" + u.Status + "] dung " + u.Count + " lan (" + string.Join("+", u.Sources.ToArray()) + ")"
                    + (u.Substitute.Length > 0 ? " -> goi y " + u.Substitute + " (" + u.SubstituteSource + ")" : ""));
            }
            sb.AppendLine("[PKTTC] Bao cao: " + json);
            sb.AppendLine("[PKTTC] Script cai (ban tu chay, mac dinh chi xem): " + ps1);
            ed.WriteMessage(sb.ToString());
        }

        /// <summary>Thay font cua Style bi thieu bang font da co san tren may (khong cai gi, khong ghi registry). Hoi YES, sao luu, mot giao dich.</summary>
        [CommandMethod("PKTEXTFONTSUB")]
        public void FontSubCmd()
        {
            Document doc = AcApp.DocumentManager.MdiActiveDocument;
            Editor ed = doc.Editor;
            ScanResult scan = Run(doc);
            List<FontUse> uses = FontReporter.Build(scan, new FontEnv(doc.Database), FontStore.Load());
            List<SubItem> plan = StyleOps.BuildSubPlan(scan, uses);

            StringBuilder sb = new StringBuilder("\n[PKTTC] Thay font Style: " + plan.Count + " style");
            foreach (SubItem s in plan) sb.Append("\n  - " + s.Style + ": " + s.OldFont + " -> " + s.NewFont);
            ed.WriteMessage(sb.ToString() + "\n");
            if (plan.Count == 0) { ed.WriteMessage("[PKTTC] Khong co gi de thay (font co trong kho thi cai truoc bang script).\n"); return; }

            string ans = AskString(ed, "\nGo YES de thay font " + plan.Count + " style: ");
            if (!string.Equals(ans, "YES", StringComparison.OrdinalIgnoreCase)) { ed.WriteMessage("\n[PKTTC] Da huy, ban ve khong doi.\n"); return; }
            ed.WriteMessage(Ops.ApplyFontSub(doc, plan).Message);
        }

        /// <summary>Don cac Style chu khong dung o dau (khong ke Standard). Hoi YES, sao luu, mot giao dich.</summary>
        [CommandMethod("PKTEXTPURGE")]
        public void PurgeCmd()
        {
            Document doc = AcApp.DocumentManager.MdiActiveDocument;
            Editor ed = doc.Editor;
            List<string> names = StyleOps.PurgeCandidates(doc.Database);
            ed.WriteMessage("\n[PKTTC] Style chu co the don: " + names.Count + (names.Count > 0 ? " (" + string.Join(", ", names.ToArray()) + ")" : "") + "\n");
            if (names.Count == 0) return;

            string ans = AskString(ed, "\nGo YES de xoa " + names.Count + " style: ");
            if (!string.Equals(ans, "YES", StringComparison.OrdinalIgnoreCase)) { ed.WriteMessage("\n[PKTTC] Da huy, ban ve khong doi.\n"); return; }
            ed.WriteMessage(Ops.ApplyPurge(doc, names).Message);
        }

        // ================================================================== S3: GHI (co ke hoach, xac nhan, sao luu)

        /// <summary>Lap ke hoach doi TCVN3/VNI sang Unicode. CHI DOC: ghi tep ke hoach JSON, khong sua ban ve.</summary>
        [CommandMethod("PKTEXTPLAN")]
        public void PlanCmd()
        {
            Document doc = AcApp.DocumentManager.MdiActiveDocument;
            Editor ed = doc.Editor;

            string path = AskPath(ed, "\nTep ke hoach JSON dau ra (Enter = mac dinh): ", DefaultPlanPath(doc));
            if (path == null) return;
            PlanOptions opt = new PlanOptions();
            string ts = AskString(ed, "\nTen style dich (Enter = theo ten font, vi du " + opt.TargetFont + "): ");
            if (ts == null) return;
            if (ts.Length > 0) opt.TargetStyle = ts;

            Plan plan = BuildPlan(doc, opt);
            PlanIo.Write(plan, path);
            ed.WriteMessage(Summary(plan) + "\n[PKTTC] Ke hoach: " + path + "\n");
        }

        /// <summary>Ap dung ke hoach da lap: hoi xac nhan, sao luu, ghi trong mot giao dich (mot buoc UNDO).</summary>
        [CommandMethod("PKTEXTAPPLY")]
        public void ApplyCmd()
        {
            Document doc = AcApp.DocumentManager.MdiActiveDocument;
            Editor ed = doc.Editor;

            string path = AskPath(ed, "\nTep ke hoach JSON can ap dung: ", null);
            if (path == null) return;
            Plan plan;
            try { plan = PlanIo.Read(path); }
            catch (System.Exception ex)
            {
                ed.WriteMessage("\n[PKTTC] Khong doc duoc ke hoach: " + ex.Message + "\n");
                return;
            }
            ApplyWithConfirm(doc, plan);
        }

        /// <summary>Lap ke hoach roi hoi xac nhan va ap dung ngay (mac dinh: style dich dat theo ten font, vi du Arial; giu do rong).</summary>
        [CommandMethod("PKTEXTFIX")]
        public void FixCmd()
        {
            Document doc = AcApp.DocumentManager.MdiActiveDocument;
            Plan plan = BuildPlan(doc, new PlanOptions());
            ApplyWithConfirm(doc, plan);
        }

        private static Plan BuildPlan(Document doc, PlanOptions opt)
        {
            return PlanBuilder.Build(Run(doc), opt);
        }

        private static void ApplyWithConfirm(Document doc, Plan plan)
        {
            Editor ed = doc.Editor;
            ed.WriteMessage(Summary(plan));
            if (plan.Items.Count == 0) { ed.WriteMessage("\n[PKTTC] Khong co gi de ap dung.\n"); return; }

            string ans = AskString(ed, "\nGo YES de ap dung ke hoach " + plan.PlanId + " (" + plan.Items.Count + " muc): ");
            if (ans == null || !string.Equals(ans, "YES", StringComparison.OrdinalIgnoreCase)) { ed.WriteMessage("\n[PKTTC] Da huy, ban ve khong doi.\n"); return; }

            ApplyOutcome o = Ops.ApplyPlan(doc, plan);
            ed.WriteMessage(o.Message);
        }

        /// <summary>Cac style dich dung trong ke hoach (nhieu font dich thi nhieu style).</summary>
        internal static string StylesOf(Plan plan)
        {
            List<string> names = new List<string>();
            foreach (PlanItem i in plan.Items) if (i.NewStyle.Length > 0 && !names.Contains(i.NewStyle)) names.Add(i.NewStyle);
            return names.Count == 0 ? plan.Options.TargetStyle : string.Join(", ", names.ToArray());
        }

        private static string Summary(Plan plan)
        {
            Dictionary<string, int> byKind = new Dictionary<string, int>();
            foreach (PlanItem i in plan.Items) Inc(byKind, i.Kind);
            return "\n[PKTTC] Ke hoach " + plan.PlanId + ": " + plan.Items.Count + " muc se doi (" + Fmt(byKind) + ")"
                + "\n        Style dich: " + StylesOf(plan) + " | giu do rong: " + plan.Options.KeepWidth
                + "\n        Bo qua: " + Fmt(plan.Skipped);
        }

        internal static void WriteApplyLog(ApplyReport rep, Plan plan, string path)
        {
            StringBuilder sb = new StringBuilder();
            sb.Append("{\"planId\":").Append(JsonOut.Q(plan.PlanId));
            sb.Append(",\"ok\":").Append(rep.Ok).Append(",\"skipped\":").Append(rep.Skipped).Append(",\"errors\":").Append(rep.Errors);
            sb.Append(",\"stylesCreated\":").Append(rep.StylesCreated);
            sb.Append(",\"maxDeviation\":").Append(rep.MaxDeviation.ToString("0.####", System.Globalization.CultureInfo.InvariantCulture));
            sb.Append(",\"clamped\":").Append(rep.Clamped).Append(",\"results\":[");
            for (int i = 0; i < rep.Results.Count; i++)
            {
                ItemResult r = rep.Results[i];
                if (i > 0) sb.Append(',');
                sb.Append("{\"handle\":").Append(JsonOut.Q(r.Handle)).Append(",\"kind\":").Append(JsonOut.Q(r.Kind));
                sb.Append(",\"status\":").Append(JsonOut.Q(r.Status)).Append(",\"reason\":").Append(JsonOut.Q(r.Reason));
                sb.Append(",\"measured\":").Append(r.Measured ? "true" : "false");
                sb.Append(",\"widthBefore\":").Append(r.WidthBefore.ToString("0.####", System.Globalization.CultureInfo.InvariantCulture));
                sb.Append(",\"widthAfter\":").Append(r.WidthAfter.ToString("0.####", System.Globalization.CultureInfo.InvariantCulture));
                sb.Append(",\"deviation\":").Append(r.Deviation.ToString("0.####", System.Globalization.CultureInfo.InvariantCulture));
                sb.Append(",\"clamped\":").Append(r.Clamped ? "true" : "false").Append('}');
            }
            sb.Append("]}");
            File.WriteAllText(path, sb.ToString(), new UTF8Encoding(false));
        }

        private static string AskPath(Editor ed, string prompt, string def)
        {
            PromptStringOptions pso = new PromptStringOptions(prompt);
            pso.AllowSpaces = true;
            PromptResult pr = ed.GetString(pso);
            if (pr.Status != PromptStatus.OK && pr.Status != PromptStatus.None) return null;
            string s = pr.Status == PromptStatus.OK ? pr.StringResult.Trim().Trim('"') : "";
            if (s.Length == 0) return def;
            return s;
        }

        private static string AskString(Editor ed, string prompt)
        {
            PromptStringOptions pso = new PromptStringOptions(prompt);
            pso.AllowSpaces = true;
            PromptResult pr = ed.GetString(pso);
            if (pr.Status == PromptStatus.None) return "";
            if (pr.Status != PromptStatus.OK) return null;
            return pr.StringResult.Trim();
        }

        private static string DefaultPlanPath(Document doc)
        {
            return DefaultPath(doc, "plan", ".json");
        }

        private static string DefaultPath(Document doc, string prefix, string ext)
        {
            string name = Path.GetFileNameWithoutExtension(doc.Name);
            foreach (char c in Path.GetInvalidFileNameChars()) name = name.Replace(c, '_');
            string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "PKTTC", "out");
            return Path.Combine(dir, prefix + "_" + name + "_" + DateTime.Now.ToString("yyyyMMdd_HHmmss") + ext);
        }

        // ------------------------------------------------------------------
        private static ScanResult Run(Document doc)
        {
            return Ops.Scan(doc);
        }

        /// <summary>Trang ma ANSI cua ban ve tu bien DWGCODEPAGE (vi du "ANSI_1252"). Mac dinh 1252.</summary>
        internal static int CodePageOf()
        {
            try
            {
                string v = Convert.ToString(AcApp.GetSystemVariable("DWGCODEPAGE"));
                int us = v.LastIndexOf('_');
                int cp;
                if (us >= 0 && int.TryParse(v.Substring(us + 1), out cp) && cp > 0) return cp;
            }
            catch (System.Exception) { }
            return 1252;
        }

        private static string DefaultPath(Document doc)
        {
            string name = Path.GetFileNameWithoutExtension(doc.Name);
            foreach (char c in Path.GetInvalidFileNameChars()) name = name.Replace(c, '_');
            string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "PKTTC", "out");
            return Path.Combine(dir, "scan_" + name + "_" + DateTime.Now.ToString("yyyyMMdd_HHmmss") + ".json");
        }

        private static Dictionary<string, int> Count(List<TextItem> items, string what)
        {
            Dictionary<string, int> d = new Dictionary<string, int>();
            foreach (TextItem i in items)
            {
                if (what == "flag")
                {
                    foreach (string f in i.Flags) Inc(d, f);
                }
                else if (what == "kind") Inc(d, i.Kind);
                else if (what == "ownerKind") Inc(d, i.OwnerKind);
                else Inc(d, i.Charset);
            }
            return d;
        }

        private static void Inc(Dictionary<string, int> d, string k)
        {
            int n;
            d.TryGetValue(k, out n);
            d[k] = n + 1;
        }

        internal static string Fmt(Dictionary<string, int> d)
        {
            List<string> parts = new List<string>();
            foreach (KeyValuePair<string, int> kv in d) parts.Add(kv.Key + "=" + kv.Value);
            return parts.Count == 0 ? "-" : string.Join(", ", parts.ToArray());
        }
    }
}
