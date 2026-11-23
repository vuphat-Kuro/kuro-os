// PKTTC TextHub - Db: ap dung ke hoach len ban ve trong MOT giao dich (mot buoc UNDO). C# 5.
// Phu thuoc acdbmgd/accoremgd, chay duoc trong accoreconsole.
using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.GraphicsInterface;

namespace Pkttc.Text.Db
{
    public sealed class ItemResult
    {
        public string Handle = "";
        public string Kind = "";
        /// <summary>ok | skipped | error</summary>
        public string Status = "";
        public string Reason = "";
        public double WidthBefore;
        public double WidthAfter;
        /// <summary>Sai lech chieu rong con lai sau khi chinh WidthFactor (ty le, 0 = khop).</summary>
        public double Deviation;
        public bool Clamped;
        public bool Measured;
    }

    public sealed class ApplyReport
    {
        public string PlanId = "";
        public int Ok;
        public int Skipped;
        public int Errors;
        public int StylesCreated;
        public double MaxDeviation;
        public int Clamped;
        public Dictionary<string, int> OkByKind = new Dictionary<string, int>();
        public List<ItemResult> Results = new List<ItemResult>();
    }

    public static class Applier
    {
        private static readonly Regex CellRx = new Regex(@"^r(\d+)c(\d+)$", RegexOptions.Compiled);
        private const double MinWidthFactor = 0.5, MaxWidthFactor = 2.0;

        public static ApplyReport Apply(Database db, Plan plan)
        {
            ApplyReport rep = new ApplyReport();
            rep.PlanId = plan.PlanId;

            using (Transaction tr = db.TransactionManager.StartTransaction())
            {
                Dictionary<string, ObjectId> styleIds = new Dictionary<string, ObjectId>(StringComparer.OrdinalIgnoreCase);
                foreach (PlanItem it in plan.Items)
                {
                    ItemResult r = new ItemResult();
                    r.Handle = it.Handle;
                    r.Kind = it.Kind;
                    rep.Results.Add(r);
                    try
                    {
                        ObjectId styleId;
                        string newFont = string.IsNullOrEmpty(it.NewFont) ? plan.Options.TargetFont : it.NewFont;
                        string key = it.NewStyle + "|" + newFont;
                        if (!styleIds.TryGetValue(key, out styleId))
                        {
                            bool created;
                            styleId = EnsureStyle(tr, db, it.NewStyle, newFont, out created);
                            if (created) rep.StylesCreated++;
                            styleIds[key] = styleId;
                        }
                        ApplyOne(tr, db, plan, it, styleId, r);
                    }
                    catch (System.Exception ex)
                    {
                        r.Status = "error";
                        r.Reason = ex.GetType().Name + ": " + ex.Message;
                    }
                    if (r.Status == "ok")
                    {
                        rep.Ok++;
                        int n;
                        rep.OkByKind.TryGetValue(it.Kind, out n);
                        rep.OkByKind[it.Kind] = n + 1;
                        if (r.Measured && r.Deviation > rep.MaxDeviation && !r.Clamped) rep.MaxDeviation = r.Deviation;
                        if (r.Clamped) rep.Clamped++;
                    }
                    else if (r.Status == "error") rep.Errors++;
                    else rep.Skipped++;
                }
                // Co loi o bat ky muc nao: khong ghi gi ca (tat ca hoac khong).
                if (rep.Errors > 0) tr.Abort();
                else tr.Commit();
            }
            return rep;
        }

        // ------------------------------------------------------------------
        private static void ApplyOne(Transaction tr, Database db, Plan plan, PlanItem it, ObjectId styleId, ItemResult r)
        {
            ObjectId id;
            long h;
            if (!long.TryParse(it.Handle, System.Globalization.NumberStyles.HexNumber, System.Globalization.CultureInfo.InvariantCulture, out h)
                || !db.TryGetObjectId(new Handle(h), out id) || id.IsErased)
            {
                r.Status = "skipped"; r.Reason = "khong tim thay doi tuong";
                return;
            }

            bool force = plan.Options.IncludeLocked;
            DBObject obj = tr.GetObject(id, OpenMode.ForWrite, false, force);

            switch (it.Kind)
            {
                case "TEXT":
                case "ATTRIB":
                case "ATTDEF":
                    {
                        DBText dt = (DBText)obj;
                        AttributeReference ar = dt as AttributeReference;
                        if (ar != null && ar.IsMTextAttribute) { r.Status = "skipped"; r.Reason = "thuoc tinh nhieu dong"; return; }
                        if (dt.TextString != it.OldRaw) { r.Status = "skipped"; r.Reason = "noi dung da thay doi tu khi lap ke hoach"; return; }
                        double before = plan.Options.KeepWidth ? MeasureWidth(dt) : 0;
                        dt.TextString = it.NewText;
                        dt.TextStyleId = styleId;
                        if (plan.Options.KeepWidth) KeepWidth(dt, before, r);
                        if (dt.Justify != AttachmentPoint.BaseLeft)
                        {
                            try { dt.AdjustAlignment(db); } catch (System.Exception) { }
                        }
                        r.Status = "ok";
                        return;
                    }
                case "MTEXT":
                    {
                        MText mt = (MText)obj;
                        if (mt.Contents != it.OldRaw) { r.Status = "skipped"; r.Reason = "noi dung da thay doi tu khi lap ke hoach"; return; }
                        mt.Contents = it.NewText;
                        mt.TextStyleId = styleId;
                        r.Status = "ok";
                        return;
                    }
                case "MLEADER":
                    {
                        MLeader ml = (MLeader)obj;
                        MText m = ml.MText;
                        if (m.Contents != it.OldRaw) { r.Status = "skipped"; r.Reason = "noi dung da thay doi tu khi lap ke hoach"; return; }
                        m.Contents = it.NewText;
                        m.TextStyleId = styleId;
                        ml.MText = m;
                        r.Status = "ok";
                        return;
                    }
                case "TABLE_CELL":
                    {
                        Table tb = (Table)obj;
                        Match cm = CellRx.Match(it.Cell);
                        if (!cm.Success) { r.Status = "skipped"; r.Reason = "khong ro o bang"; return; }
                        int row = int.Parse(cm.Groups[1].Value), col = int.Parse(cm.Groups[2].Value);
                        if (tb.Cells[row, col].TextString != it.OldRaw) { r.Status = "skipped"; r.Reason = "noi dung da thay doi tu khi lap ke hoach"; return; }
                        tb.Cells[row, col].TextString = it.NewText;
                        tb.Cells[row, col].TextStyleId = styleId;
                        r.Status = "ok";
                        return;
                    }
                default:
                    r.Status = "skipped"; r.Reason = "loai " + it.Kind + " chua ho tro ghi";
                    return;
            }
        }

        // ------------------------------------------------------------------ giu do rong
        /// <summary>Chieu rong chu theo huong chu (quay ve 0 do tren ban sao). 0 neu khong do duoc.</summary>
        private static double MeasureWidth(DBText t)
        {
            try
            {
                DBText c = (DBText)t.Clone();
                c.Rotation = 0;
                Extents3d e = c.GeometricExtents;
                double w = e.MaxPoint.X - e.MinPoint.X;
                c.Dispose();
                return w > 1e-9 ? w : 0;
            }
            catch (System.Exception)
            {
                return 0;
            }
        }

        private static void KeepWidth(DBText dt, double before, ItemResult r)
        {
            if (before <= 0) return;
            double after = MeasureWidth(dt);
            if (after <= 0) return;
            r.Measured = true;
            r.WidthBefore = before;
            r.WidthAfter = after;
            double wf = dt.WidthFactor * before / after;
            double clamped = Math.Max(MinWidthFactor, Math.Min(MaxWidthFactor, wf));
            r.Clamped = Math.Abs(clamped - wf) > 1e-9;
            dt.WidthFactor = clamped;
            double final = MeasureWidth(dt);
            r.Deviation = final > 0 ? Math.Abs(final - before) / before : 0;
        }

        // ------------------------------------------------------------------ style dich
        private static ObjectId EnsureStyle(Transaction tr, Database db, string name, string typeface, out bool created)
        {
            created = false;
            TextStyleTable tst = (TextStyleTable)tr.GetObject(db.TextStyleTableId, OpenMode.ForRead);
            if (tst.Has(name))
            {
                // Style cung ten chi duoc dung lai neu dung dung font dich (neu khong, hoan tac ca giao dich).
                TextStyleTableRecord ex = (TextStyleTableRecord)tr.GetObject(tst[name], OpenMode.ForRead);
                bool shxTarget = PlanBuilder.IsShx(typeface);
                string face = "";
                try { face = shxTarget ? (ex.FileName ?? "") : (ex.Font.TypeFace ?? ""); } catch (System.Exception) { }
                if (!string.Equals(face, typeface, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidOperationException("Style '" + name + "' da co voi font khac ('" + face + "'), khong phai '" + typeface + "'. Lap lai ke hoach.");
                return tst[name];
            }
            tst.UpgradeOpen();
            TextStyleTableRecord ts = new TextStyleTableRecord();
            ts.Name = name;
            if (PlanBuilder.IsShx(typeface)) ts.FileName = typeface;   // font SHX (vi du VN_UNI.shx): dat theo ten tep, khong qua FontDescriptor
            else ts.Font = new FontDescriptor(typeface, false, false, 0, 34);
            ObjectId id = tst.Add(ts);
            tr.AddNewlyCreatedDBObject(ts, true);
            created = true;
            return id;
        }
    }
}
