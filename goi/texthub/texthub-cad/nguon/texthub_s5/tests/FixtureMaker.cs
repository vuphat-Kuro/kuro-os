// PKTTC TextHub - S2: tao ban ve mau 20 muc chu (CHI dung trong thu muc test, tren ban sao mau trong).
// Co chot an toan: tu choi chay neu ban ve dang mo khong nam trong ...\texthub_s5\test\.
using System;
using System.IO;
using System.Text;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.EditorInput;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.GraphicsInterface;
using Autodesk.AutoCAD.Runtime;
using AcApp = Autodesk.AutoCAD.ApplicationServices.Core.Application;

[assembly: CommandClass(typeof(Pkttc.Text.Tests.FixtureCommands))]

namespace Pkttc.Text.Tests
{
    public class FixtureCommands
    {
        // Chuoi "ANSI" (byte = ky tu 0..255)
        private static string Bytes(params int[] b)
        {
            char[] c = new char[b.Length];
            for (int i = 0; i < b.Length; i++) c[i] = (char)b[i];
            return new string(c);
        }

        private static readonly string DaNangTcvn = Bytes(0xA7, 0xB5, 0x20, 0x4E, 0xBD, 0x6E, 0x67);            // Da Nang
        private static readonly string VietNamTcvn = Bytes(0x56, 0x69, 0xD6, 0x74, 0x20, 0x4E, 0x61, 0x6D);    // Viet Nam
        private static readonly string DaNangVni = Bytes(0xD1, 0x61, 0xF8, 0x20, 0x4E, 0x61, 0xFC, 0x6E, 0x67); // Da Nang
        private static readonly string VietNamVni = Bytes(0x56, 0x69, 0x65, 0xE4, 0x74, 0x20, 0x4E, 0x61, 0x6D);

        [CommandMethod("PKTMAKEFIXTURE")]
        public void Make()
        {
            var doc = AcApp.DocumentManager.MdiActiveDocument;
            Editor ed = doc.Editor;
            Database db = doc.Database;

            string cur = db.Filename ?? "";
            if (cur.IndexOf("texthub_s5", StringComparison.OrdinalIgnoreCase) < 0 || cur.IndexOf("\\test\\", StringComparison.OrdinalIgnoreCase) < 0)
            {
                ed.WriteMessage("\n[FIXTURE] Tu choi: ban ve khong nam trong texthub_s5\\test.\n");
                return;
            }
            string outPath = Path.Combine(Path.GetDirectoryName(cur), "fixture_20.dwg");

            using (Transaction tr = db.TransactionManager.StartTransaction())
            {
                BlockTable bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForWrite);
                BlockTableRecord ms = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                BlockTableRecord ps = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.PaperSpace], OpenMode.ForWrite);

                // --- Style ---
                TextStyleTable tst = (TextStyleTable)tr.GetObject(db.TextStyleTableId, OpenMode.ForWrite);
                ObjectId sVn = AddStyle(tr, tst, "S_VNTIME", ".VnTime");
                ObjectId sArial = AddStyle(tr, tst, "S_ARIAL", "Arial");
                ObjectId sVni = AddStyle(tr, tst, "S_VNI", "VNI-Times");
                AddStyle(tr, tst, "Arial Unicode MS", "Times New Roman"); // trung ten voi style dich mac dinh nhung khac font: dich phai thanh Arial Unicode MS_2

                // --- Layer khoa ---
                LayerTable lt = (LayerTable)tr.GetObject(db.LayerTableId, OpenMode.ForWrite);
                LayerTableRecord ll = new LayerTableRecord();
                ll.Name = "LOCKED";
                lt.Add(ll);
                tr.AddNewlyCreatedDBObject(ll, true);
                ll.IsLocked = true;

                // --- Block KHUNG: TEXT (VNI) + ATTDEF (TCVN3) ---
                BlockTableRecord khung = new BlockTableRecord();
                khung.Name = "KHUNG";
                bt.Add(khung);
                tr.AddNewlyCreatedDBObject(khung, true);
                Add(tr, khung, NewText(DaNangVni, sVni, new Point3d(0, 0, 0)));
                AttributeDefinition adef = new AttributeDefinition();
                adef.SetDatabaseDefaults();
                adef.Position = new Point3d(0, 5, 0);
                adef.Tag = "NOIDUNG";
                adef.Prompt = "noi dung";
                adef.TextString = VietNamTcvn;
                adef.Height = 2.5;
                adef.TextStyleId = sVn;
                Add(tr, khung, adef);

                // --- Block BANG: TEXT ASCII + INSERT KHUNG (co ATTRIB VNI) ---
                BlockTableRecord bang = new BlockTableRecord();
                bang.Name = "BANG";
                bt.Add(bang);
                tr.AddNewlyCreatedDBObject(bang, true);
                Add(tr, bang, NewText("BANG", ObjectId.Null, new Point3d(0, 0, 0)));
                AddInsert(tr, bang, khung.ObjectId, adef, new Point3d(20, 0, 0), VietNamVni);

                // --- Model: 4 TEXT (3 + 1 tren layer khoa) + 1 TEXT TCVN3 trong style Arial ---
                Add(tr, ms, NewText(DaNangTcvn, sVn, new Point3d(0, 0, 0)));
                Add(tr, ms, NewText(VietNamTcvn, sVn, new Point3d(0, 5, 0)));
                Add(tr, ms, NewText("Đường Nguyễn Trãi", sArial, new Point3d(0, 10, 0)));
                DBText locked = NewText(DaNangTcvn, sVn, new Point3d(0, 15, 0));
                locked.Layer = "LOCKED";
                Add(tr, ms, locked);
                Add(tr, ms, NewText(DaNangTcvn, sArial, new Point3d(0, 20, 0))); // sai bang ma: TCVN3 trong style Arial

                // --- MTEXT dai (TCVN3, co \f) va MTEXT Unicode ---
                StringBuilder lg = new StringBuilder("{\\fVnTime|b0|i0|c0|p34;");
                for (int i = 0; i < 70; i++) lg.Append(DaNangTcvn).Append(' ');
                lg.Append('}');
                Add(tr, ms, NewMText(lg.ToString(), sVn, new Point3d(40, 0, 0)));
                Add(tr, ms, NewMText("Mặt cắt A-A\\Ptỷ lệ 1:100", sArial, new Point3d(40, 10, 0)));

                // --- INSERT KHUNG x2 (ATTRIB TCVN3 va ATTRIB ASCII), INSERT BANG x1 ---
                AddInsert(tr, ms, khung.ObjectId, adef, new Point3d(80, 0, 0), DaNangTcvn);
                AddInsert(tr, ms, khung.ObjectId, adef, new Point3d(80, 10, 0), "KM1");
                BlockReference br = new BlockReference(new Point3d(80, 20, 0), bang.ObjectId);
                br.SetDatabaseDefaults();
                ms.AppendEntity(br);
                tr.AddNewlyCreatedDBObject(br, true);

                // --- MLEADER (TCVN3) ---
                MLeader ml = new MLeader();
                ml.SetDatabaseDefaults();
                ml.ContentType = ContentType.MTextContent;
                MText mt = new MText();
                mt.SetDatabaseDefaults();
                mt.Contents = VietNamTcvn;
                mt.TextStyleId = sVn;
                mt.Location = new Point3d(130, 10, 0);
                ml.MText = mt;
                int li = ml.AddLeaderLine(new Point3d(120, 0, 0));
                ml.AddFirstVertex(li, new Point3d(120, 0, 0));
                ml.AddLastVertex(li, new Point3d(128, 8, 0));
                ms.AppendEntity(ml);
                tr.AddNewlyCreatedDBObject(ml, true);

                // --- DIMENSION co chu ghi de (VNI) ---
                AlignedDimension dim = new AlignedDimension(new Point3d(0, 40, 0), new Point3d(30, 40, 0), new Point3d(15, 45, 0), DaNangVni, db.Dimstyle);
                dim.SetDatabaseDefaults();
                ms.AppendEntity(dim);
                tr.AddNewlyCreatedDBObject(dim, true);

                // --- TABLE 2x2: TCVN3, VNI, ASCII, Unicode ---
                Table tb = new Table();
                tb.TableStyle = db.Tablestyle;
                tb.SetSize(2, 2);
                tb.SetRowHeight(10);
                tb.SetColumnWidth(40);
                tb.Position = new Point3d(0, 80, 0);
                tb.Cells[0, 0].TextString = VietNamTcvn;
                tb.Cells[0, 1].TextString = DaNangVni;
                tb.Cells[1, 0].TextString = "STT 01";
                tb.Cells[1, 1].TextString = "Tên công trình";
                tb.GenerateLayout();
                ms.AppendEntity(tb);
                tr.AddNewlyCreatedDBObject(tb, true);

                // --- Paper space: 1 TEXT ASCII ---
                Add(tr, ps, NewText("Km12+500", ObjectId.Null, new Point3d(0, 0, 0)));

                tr.Commit();
            }
            db.SaveAs(outPath, DwgVersion.Current);
            ed.WriteMessage("\n[FIXTURE] Da tao: " + outPath + "\n");
        }

        /// <summary>Ban ve mau cho kiem thu font va don style (S4).</summary>
        [CommandMethod("PKTMAKEFONTFIXTURE")]
        public void MakeFontFixture()
        {
            var doc = AcApp.DocumentManager.MdiActiveDocument;
            Editor ed = doc.Editor;
            Database db = doc.Database;
            string cur = db.Filename ?? "";
            if (cur.IndexOf("texthub_s5", StringComparison.OrdinalIgnoreCase) < 0 || cur.IndexOf("\\test\\", StringComparison.OrdinalIgnoreCase) < 0)
            {
                ed.WriteMessage("\n[FIXTURE] Tu choi: ban ve khong nam trong texthub_s5\\test.\n");
                return;
            }
            string outPath = Path.Combine(Path.GetDirectoryName(cur), "fixture_font.dwg");

            using (Transaction tr = db.TransactionManager.StartTransaction())
            {
                BlockTable bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                BlockTableRecord ms = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                TextStyleTable tst = (TextStyleTable)tr.GetObject(db.TextStyleTableId, OpenMode.ForWrite);

                ObjectId sAlumni = AddShxStyle(tr, tst, "S_ALUMNI", "pkttdemo.shx");
                ObjectId sNoShx = AddShxStyle(tr, tst, "S_NOSHX", "khongco.shx");
                ObjectId sNoTtf = AddStyle(tr, tst, "S_NOTTF", "Font Khong Ton Tai");
                ObjectId sArial = AddStyle(tr, tst, "S_ARIAL", "Arial");
                AddStyle(tr, tst, "S_UNUSED", "Arial");
                AddShxStyle(tr, tst, "S_UNUSED2", "txt.shx");

                Add(tr, ms, NewText("Alumni", sAlumni, new Point3d(0, 0, 0)));
                Add(tr, ms, NewText("Khong co shx", sNoShx, new Point3d(0, 5, 0)));
                Add(tr, ms, NewText("Khong co ttf", sNoTtf, new Point3d(0, 10, 0)));
                Add(tr, ms, NewText("Unicode ok", sArial, new Point3d(0, 15, 0)));
                Add(tr, ms, NewMText("{\\fFont Khac Khong Co|b0|i0|c0|p34;abc}", ObjectId.Null, new Point3d(0, 20, 0)));
                // \F (chu hoa) = SHX, "font,bigfont", khong co duoi: phai thanh txt.shx va romans.shx (deu co san), khong thanh "txt,romans"
                Add(tr, ms, NewMText("{\\Ftxt,romans;abc}", ObjectId.Null, new Point3d(0, 25, 0)));
                tr.Commit();
            }
            db.SaveAs(outPath, DwgVersion.Current);
            ed.WriteMessage("\n[FIXTURE] Da tao: " + outPath + "\n");
        }

        private static ObjectId AddShxStyle(Transaction tr, TextStyleTable tst, string name, string shx)
        {
            TextStyleTableRecord ts = new TextStyleTableRecord();
            ts.Name = name;
            ts.FileName = shx;
            ObjectId id = tst.Add(ts);
            tr.AddNewlyCreatedDBObject(ts, true);
            return id;
        }

        private static ObjectId AddStyle(Transaction tr, TextStyleTable tst, string name, string typeface)
        {
            TextStyleTableRecord ts = new TextStyleTableRecord();
            ts.Name = name;
            ts.Font = new FontDescriptor(typeface, false, false, 0, 34);
            ObjectId id = tst.Add(ts);
            tr.AddNewlyCreatedDBObject(ts, true);
            return id;
        }

        private static DBText NewText(string s, ObjectId style, Point3d p)
        {
            DBText t = new DBText();
            t.SetDatabaseDefaults();
            t.Position = p;
            t.Height = 2.5;
            t.TextString = s;
            if (!style.IsNull) t.TextStyleId = style;
            return t;
        }

        private static MText NewMText(string s, ObjectId style, Point3d p)
        {
            MText m = new MText();
            m.SetDatabaseDefaults();
            m.Location = p;
            m.TextHeight = 2.5;
            m.Width = 100;
            m.Contents = s;
            if (!style.IsNull) m.TextStyleId = style;
            return m;
        }

        private static void Add(Transaction tr, BlockTableRecord space, Entity e)
        {
            space.AppendEntity(e);
            tr.AddNewlyCreatedDBObject(e, true);
        }

        private static void AddInsert(Transaction tr, BlockTableRecord space, ObjectId blockId, AttributeDefinition adef, Point3d p, string attText)
        {
            BlockReference br = new BlockReference(p, blockId);
            br.SetDatabaseDefaults();
            space.AppendEntity(br);
            tr.AddNewlyCreatedDBObject(br, true);
            AttributeReference ar = new AttributeReference();
            ar.SetAttributeFromBlock(adef, br.BlockTransform);
            ar.TextString = attText;
            br.AttributeCollection.AppendAttribute(ar);
            tr.AddNewlyCreatedDBObject(ar, true);
        }
    }
}

