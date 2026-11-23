// PKTTC TextHub - Db: thay font cua Style bi thieu va don Style khong dung. GHI vao ban ve (trong mot giao dich). C# 5.
using System;
using System.Collections.Generic;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.GraphicsInterface;

namespace Pkttc.Text.Db
{
    public sealed class SubItem
    {
        public string Style = "";
        public string OldFont = "";
        public string NewFont = "";
    }

    public static class StyleOps
    {
        /// <summary>
        /// Ke hoach thay font: Style dang dung, font chinh bi thieu va co goi y THAY THE DA CO SAN tren may.
        /// Font chi co trong kho (can cai) thi khong thay; phai cai truoc.
        /// </summary>
        public static List<SubItem> BuildSubPlan(ScanResult scan, List<FontUse> uses)
        {
            List<SubItem> plan = new List<SubItem>();
            foreach (FontUse u in uses)
            {
                if (u.Status != "missing" || u.SubstituteSource != "installed") continue;
                foreach (string sname in u.Styles)
                {
                    StyleInfo si = scan.Styles.Find(delegate(StyleInfo x) { return x.Name == sname; });
                    if (si == null || si.Count == 0 || si.FontName != u.Name) continue;
                    SubItem s = new SubItem();
                    s.Style = sname;
                    s.OldFont = u.Name;
                    s.NewFont = u.Substitute;
                    plan.Add(s);
                }
            }
            return plan;
        }

        /// <summary>Doi font cac Style trong mot giao dich. Co loi thi huy het. Tra ve so Style da doi.</summary>
        public static int ApplySub(Database db, List<SubItem> plan, out string error)
        {
            error = "";
            int n = 0;
            using (Transaction tr = db.TransactionManager.StartTransaction())
            {
                try
                {
                    TextStyleTable tst = (TextStyleTable)tr.GetObject(db.TextStyleTableId, OpenMode.ForRead);
                    foreach (SubItem s in plan)
                    {
                        if (!tst.Has(s.Style)) continue;
                        TextStyleTableRecord ts = (TextStyleTableRecord)tr.GetObject(tst[s.Style], OpenMode.ForWrite);
                        string ext = System.IO.Path.GetExtension(s.NewFont).ToLowerInvariant();
                        if (ext == ".shx") ts.FileName = s.NewFont;
                        else ts.Font = new FontDescriptor(s.NewFont, false, false, 0, 34);
                        n++;
                    }
                    tr.Commit();
                }
                catch (System.Exception ex)
                {
                    tr.Abort();
                    error = ex.GetType().Name + ": " + ex.Message;
                    return 0;
                }
            }
            return n;
        }

        // ------------------------------------------------------------------ don Style
        /// <summary>Ten cac Style co the xoa: khong dung o dau (ke ca DimStyle, MLeaderStyle, block). Khong bao gio gom Standard.</summary>
        public static List<string> PurgeCandidates(Database db)
        {
            List<string> names = new List<string>();
            using (Transaction tr = db.TransactionManager.StartTransaction())
            {
                TextStyleTable tst = (TextStyleTable)tr.GetObject(db.TextStyleTableId, OpenMode.ForRead);
                ObjectIdCollection ids = new ObjectIdCollection();
                foreach (ObjectId id in tst)
                {
                    TextStyleTableRecord ts = (TextStyleTableRecord)tr.GetObject(id, OpenMode.ForRead);
                    if (string.IsNullOrEmpty(ts.Name) || ts.IsShapeFile) continue;
                    if (string.Equals(ts.Name, "Standard", StringComparison.OrdinalIgnoreCase)) continue;
                    ids.Add(id);
                }
                db.Purge(ids); // con lai: nhung ID khong ai tham chieu
                foreach (ObjectId id in ids)
                    names.Add(((TextStyleTableRecord)tr.GetObject(id, OpenMode.ForRead)).Name);
                tr.Abort();
            }
            names.Sort(StringComparer.OrdinalIgnoreCase);
            return names;
        }

        public static int Purge(Database db, List<string> names, out string error)
        {
            error = "";
            int n = 0;
            using (Transaction tr = db.TransactionManager.StartTransaction())
            {
                try
                {
                    TextStyleTable tst = (TextStyleTable)tr.GetObject(db.TextStyleTableId, OpenMode.ForRead);
                    ObjectIdCollection ids = new ObjectIdCollection();
                    foreach (string nm in names) if (tst.Has(nm)) ids.Add(tst[nm]);
                    db.Purge(ids); // kiem lai luc ghi: ID nao con duoc tham chieu se bi loai
                    foreach (ObjectId id in ids)
                    {
                        DBObject o = tr.GetObject(id, OpenMode.ForWrite);
                        o.Erase();
                        n++;
                    }
                    tr.Commit();
                }
                catch (System.Exception ex)
                {
                    tr.Abort();
                    error = ex.GetType().Name + ": " + ex.Message;
                    return 0;
                }
            }
            return n;
        }
    }
}
