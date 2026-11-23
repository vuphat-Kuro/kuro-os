// PKTTC TextHub - Db: quet moi loai chu trong ban ve, CHI DOC. C# 5.
// Phu thuoc: acdbmgd, accoremgd (khong Acmgd) de chay duoc trong accoreconsole.exe.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing.Text;
using Autodesk.AutoCAD.DatabaseServices;
using Pkttc.Text.Core;

namespace Pkttc.Text.Db
{
    public static class Scanner
    {
        private sealed class Ctx
        {
            public Database Db;
            public Transaction Tr;
            public int CodePage;
            public ScanResult Res;
            public Dictionary<string, StyleInfo> Styles = new Dictionary<string, StyleInfo>(StringComparer.OrdinalIgnoreCase);
            public Dictionary<ObjectId, string> LayerName = new Dictionary<ObjectId, string>();
            public Dictionary<ObjectId, bool> LayerLocked = new Dictionary<ObjectId, bool>();
            public string OwnerKind = "";
            public string Owner = "";
        }

        public static ScanResult Scan(Database db, int codePage)
        {
            Stopwatch sw = Stopwatch.StartNew();
            FontRules.ClearOverrides(); // ket qua doc tu tep font chi dung cho mot lan quet
            ScanResult res = new ScanResult();
            res.Drawing = db.Filename ?? "";
            res.CodePage = codePage;
            res.ScannedAt = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");

            Ctx cx = new Ctx();
            cx.Db = db;
            cx.CodePage = codePage;
            cx.Res = res;

            HashSet<string> installed = InstalledFamilies();

            using (Transaction tr = db.TransactionManager.StartTransaction())
            {
                cx.Tr = tr;
                LoadStyles(cx, installed);
                LoadLayers(cx);

                BlockTable bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                foreach (ObjectId btrId in bt)
                {
                    BlockTableRecord btr = (BlockTableRecord)tr.GetObject(btrId, OpenMode.ForRead);
                    if (btr.IsLayout)
                    {
                        cx.OwnerKind = string.Equals(btr.Name, BlockTableRecord.ModelSpace, StringComparison.OrdinalIgnoreCase) ? "model" : "layout";
                        Layout lay = (Layout)tr.GetObject(btr.LayoutId, OpenMode.ForRead);
                        cx.Owner = lay.LayoutName;
                    }
                    else
                    {
                        if (btr.IsAnonymous || btr.IsFromExternalReference || btr.IsFromOverlayReference || btr.IsDependent) continue;
                        cx.OwnerKind = "block";
                        cx.Owner = btr.Name;
                    }
                    foreach (ObjectId eid in btr)
                    {
                        try { ScanEntity(cx, eid); }
                        catch (System.Exception ex) { Fail(res, ex); }
                    }
                }
                tr.Abort(); // chi doc
            }

            foreach (TextItem it in res.Items)
            {
                StyleInfo si;
                if (cx.Styles.TryGetValue(it.Style, out si)) si.Count++;
            }
            foreach (StyleInfo si in cx.Styles.Values) res.Styles.Add(si);
            res.ElapsedMs = (int)sw.ElapsedMilliseconds;
            return res;
        }

        // ------------------------------------------------------------------ nap bang
        private static void LoadStyles(Ctx cx, HashSet<string> installed)
        {
            TextStyleTable tst = (TextStyleTable)cx.Tr.GetObject(cx.Db.TextStyleTableId, OpenMode.ForRead);
            foreach (ObjectId id in tst)
            {
                TextStyleTableRecord ts = (TextStyleTableRecord)cx.Tr.GetObject(id, OpenMode.ForRead);
                if (string.IsNullOrEmpty(ts.Name)) continue;
                StyleInfo si = new StyleInfo();
                si.Name = ts.Name;
                si.FileName = ts.FileName ?? "";
                si.BigFont = ts.BigFontFileName ?? "";
                try { si.TypeFace = ts.Font.TypeFace ?? ""; } catch (System.Exception) { si.TypeFace = ""; }
                si.FontName = si.TypeFace.Length > 0 ? si.TypeFace : si.FileName;
                // SHX: khong co TypeFace va (duoi .shx hoac khong co duoi, vi du "txt"); chuan hoa ten thanh co duoi .shx
                string ext0 = System.IO.Path.GetExtension(si.FileName);
                si.IsShx = si.TypeFace.Length == 0 && si.FileName.Length > 0 && (ext0.Length == 0 || ext0.Equals(".shx", StringComparison.OrdinalIgnoreCase));
                if (si.IsShx && ext0.Length == 0) { si.FileName += ".shx"; si.FontName = si.FileName; }
                string foundPath;
                si.FontExists = FontExists(cx.Db, si, installed, out foundPath);
                if (si.IsShx && !string.IsNullOrEmpty(foundPath))
                {
                    si.ShxKind = ShxHeader.Kind(foundPath);
                    // Header unifont = Unicode, thang ten font (vi du uv-abc, VN_UNI)
                    if (si.ShxKind == "unifont") FontRules.SetOverride(si.FontName, Charset.Unicode);
                }
                if (si.BigFont.Length > 0)
                {
                    try { HostApplicationServices.Current.FindFile(System.IO.Path.GetExtension(si.BigFont).Length == 0 ? si.BigFont + ".shx" : si.BigFont, cx.Db, FindFileHint.Default); }
                    catch (System.Exception) { si.BigFontExists = false; }
                }
                si.Hint = FontRules.DeduceCharset(si.FontName).ToString();
                cx.Styles[si.Name] = si;
            }
        }

        private static void LoadLayers(Ctx cx)
        {
            LayerTable lt = (LayerTable)cx.Tr.GetObject(cx.Db.LayerTableId, OpenMode.ForRead);
            foreach (ObjectId id in lt)
            {
                LayerTableRecord l = (LayerTableRecord)cx.Tr.GetObject(id, OpenMode.ForRead);
                cx.LayerName[id] = l.Name;
                cx.LayerLocked[id] = l.IsLocked;
            }
        }

        internal static HashSet<string> InstalledFamilies()
        {
            HashSet<string> set = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            try
            {
                using (InstalledFontCollection c = new InstalledFontCollection())
                    foreach (System.Drawing.FontFamily f in c.Families) set.Add(f.Name);
            }
            catch (System.Exception) { }
            return set;
        }

        private static bool FontExists(Database db, StyleInfo si, HashSet<string> installed, out string foundPath)
        {
            foundPath = "";
            try
            {
                if (si.IsShx)
                {
                    foundPath = HostApplicationServices.Current.FindFile(si.FileName, db, FindFileHint.Default);
                    return true;
                }
                if (si.TypeFace.Length > 0) return installed.Contains(si.TypeFace) || installed.Contains(StripScript(si.TypeFace));
                if (si.FileName.Length == 0) return true;
                string b = FontRules.BaseName(si.FileName);
                if (installed.Contains(b)) return true;
                HostApplicationServices.Current.FindFile(si.FileName, db, FindFileHint.Default);
                return true;
            }
            catch (System.Exception)
            {
                return false;
            }
        }

        /// <summary>"Arial Baltic", "Arial TUR"... la cung ho font Arial voi bo ky tu (script) khac.</summary>
        internal static string StripScript(string face)
        {
            string[] scripts = new string[] { " TUR", " Baltic", " CE", " Cyr", " Greek", " Hebrew", " Arabic", " Vietnamese", " Western" };
            foreach (string s in scripts)
                if (face.EndsWith(s, StringComparison.OrdinalIgnoreCase)) return face.Substring(0, face.Length - s.Length);
            return face;
        }

        // ------------------------------------------------------------------ quet doi tuong
        private static void ScanEntity(Ctx cx, ObjectId eid)
        {
            Entity ent = cx.Tr.GetObject(eid, OpenMode.ForRead) as Entity;
            if (ent == null) return;

            AttributeDefinition ad = ent as AttributeDefinition;
            if (ad != null) { AddText(cx, ent, "ATTDEF", ad.TextString, ad.TextStyleName, "", false); return; }

            DBText dt = ent as DBText;
            if (dt != null) { AddText(cx, ent, "TEXT", dt.TextString, dt.TextStyleName, "", false); return; }

            MText mt = ent as MText;
            if (mt != null) { AddText(cx, ent, "MTEXT", mt.Contents, mt.TextStyleName, "", true); return; }

            Table tb = ent as Table; // Table ke thua BlockReference: kiem tra truoc
            if (tb != null) { ScanTable(cx, tb); return; }

            BlockReference br = ent as BlockReference;
            if (br != null) { ScanInsert(cx, br); return; }

            MLeader ml = ent as MLeader;
            if (ml != null)
            {
                if (ml.ContentType == ContentType.MTextContent)
                {
                    MText m = ml.MText;
                    AddText(cx, ent, "MLEADER", m.Contents, m.TextStyleName, "", true);
                }
                return;
            }

            Dimension dm = ent as Dimension;
            if (dm != null)
            {
                string t = dm.DimensionText;
                if (!string.IsNullOrEmpty(t) && t != "<>") AddText(cx, ent, "DIMENSION", t, DimTextStyle(cx, dm), "", false);
                return;
            }

            string dxf = ent.GetRXClass().DxfName;
            if (dxf == "TOLERANCE" || dxf == "ARCALIGNEDTEXT")
            {
                int n;
                cx.Res.Unsupported.TryGetValue(dxf, out n);
                cx.Res.Unsupported[dxf] = n + 1;
            }
        }

        private static void ScanInsert(Ctx cx, BlockReference br)
        {
            if (br.AttributeCollection == null || br.AttributeCollection.Count == 0) return;
            string name = br.Name;
            try
            {
                if (br.IsDynamicBlock)
                    name = ((BlockTableRecord)cx.Tr.GetObject(br.DynamicBlockTableRecord, OpenMode.ForRead)).Name;
            }
            catch (System.Exception) { }
            foreach (ObjectId aid in br.AttributeCollection)
            {
                AttributeReference ar = (AttributeReference)cx.Tr.GetObject(aid, OpenMode.ForRead);
                AddText(cx, ar, "ATTRIB", ar.TextString, ar.TextStyleName, name, false);
            }
        }

        private static void ScanTable(Ctx cx, Table tb)
        {
            for (int r = 0; r < tb.Rows.Count; r++)
            {
                for (int c = 0; c < tb.Columns.Count; c++)
                {
                    string s;
                    try { s = tb.Cells[r, c].TextString; }
                    catch (System.Exception) { continue; }
                    if (string.IsNullOrEmpty(s)) continue;
                    string style = "";
                    try
                    {
                        // TextStyle(r,c) tra ve style hieu luc (ke ca ke thua tu kieu bang); Cell.TextStyleId co the null.
                        ObjectId sid = tb.TextStyle(r, c);
                        if (!sid.IsNull)
                            style = ((TextStyleTableRecord)cx.Tr.GetObject(sid, OpenMode.ForRead)).Name;
                    }
                    catch (System.Exception) { }
                    AddText(cx, tb, "TABLE_CELL", s, style, "r" + r + "c" + c, true);
                }
            }
        }

        private static string DimTextStyle(Ctx cx, Dimension dm)
        {
            try
            {
                DimStyleTableRecord dst = (DimStyleTableRecord)cx.Tr.GetObject(dm.DimensionStyle, OpenMode.ForRead);
                TextStyleTableRecord ts = (TextStyleTableRecord)cx.Tr.GetObject(dst.Dimtxsty, OpenMode.ForRead);
                return ts.Name;
            }
            catch (System.Exception) { return ""; }
        }

        // ------------------------------------------------------------------ them muc va phan tich
        private static void AddText(Ctx cx, Entity ent, string kind, string raw, string style, string block, bool mtextFormat)
        {
            if (string.IsNullOrEmpty(raw)) return;
            TextItem it = new TextItem();
            it.Handle = ent.Handle.ToString();
            it.Kind = kind;
            it.OwnerKind = cx.OwnerKind;
            it.Owner = cx.Owner;
            it.Block = block;
            string ln;
            it.Layer = cx.LayerName.TryGetValue(ent.LayerId, out ln) ? ln : "";
            it.Style = style ?? "";
            it.Raw = raw;
            it.Length = raw.Length;

            StyleInfo si;
            string font = "";
            if (cx.Styles.TryGetValue(it.Style, out si)) font = si.FontName;
            it.Font = font;

            Analyze(cx, it, si, mtextFormat);

            bool locked;
            if (cx.LayerLocked.TryGetValue(ent.LayerId, out locked) && locked) it.Flags.Add("locked");
            if (si != null && !si.FontExists) it.Flags.Add("fontMissing");
            cx.Res.Items.Add(it);
        }

        private static void Analyze(Ctx cx, TextItem it, StyleInfo si, bool mtextFormat)
        {
            ConvertOptions opt = new ConvertOptions();
            opt.CodePage = cx.CodePage;
            opt.Target = Charset.Unicode;
            opt.DefaultFont = it.Font;
            MTextConvertResult r = mtextFormat ? MTextConverter.ConvertMText(it.Raw, opt) : MTextConverter.ConvertPlain(it.Raw, opt);

            Charset best = Charset.Ascii;
            double conf = 1;
            bool ambiguous = false;
            foreach (RunReport run in r.Runs)
            {
                if (run.Detected == Charset.Ascii) continue;
                if (run.Detected == Charset.Unknown) { ambiguous = true; continue; }
                if (best == Charset.Ascii) { best = run.Detected; conf = run.Confidence; }
            }
            if (best == Charset.Ascii && ambiguous) { best = Charset.Unknown; conf = 0; }
            it.Charset = best.ToString();
            it.Confidence = Math.Round(conf, 2);
            it.UnmappedCount = r.Unmapped;
            if (r.Changed)
            {
                string p = r.Text;
                it.Converted = p;
                it.Preview = p.Length > 200 ? p.Substring(0, 200) : p;
            }

            bool legacy = best == Charset.Tcvn3 || best == Charset.Vni;
            if (legacy) it.Flags.Add("legacy");
            if (ambiguous || r.Ambiguous > 0) it.Flags.Add("ambiguous");

            Charset hint = FontRules.DeduceCharset(it.Font);
            if ((hint == Charset.Unicode && legacy) || (hint == Charset.Tcvn3 && best == Charset.Unicode) || (hint == Charset.Vni && best == Charset.Unicode)
                || (hint == Charset.Tcvn3 && best == Charset.Vni) || (hint == Charset.Vni && best == Charset.Tcvn3))
                it.Flags.Add("mismatch");

            if (it.Raw.IndexOf("%<\\Ac", StringComparison.Ordinal) >= 0) it.Flags.Add("field");
            if (it.Kind == "MTEXT" && it.Length > 250) it.Flags.Add("long");
            if (it.Raw.IndexOf("\\U+", StringComparison.OrdinalIgnoreCase) >= 0) it.Flags.Add("unicodeEscape");
        }

        private static void Fail(ScanResult res, System.Exception ex)
        {
            res.Errors++;
            if (res.ErrorSamples.Count < 5) res.ErrorSamples.Add(ex.GetType().Name + ": " + ex.Message);
        }
    }
}
