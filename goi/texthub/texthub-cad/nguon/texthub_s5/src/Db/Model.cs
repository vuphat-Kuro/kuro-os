// PKTTC TextHub - Db: mo hinh du lieu quet. C# 5.
using System.Collections.Generic;

namespace Pkttc.Text.Db
{
    public sealed class StyleInfo
    {
        public string Name = "";
        public string FileName = "";
        public string TypeFace = "";
        public string BigFont = "";
        /// <summary>Ten font dung de suy bang ma (TypeFace neu co, khong thi ten tep).</summary>
        public string FontName = "";
        public bool IsShx;
        public bool FontExists;
        public bool BigFontExists = true;
        /// <summary>Loai SHX doc tu header: unifont, shapes, bigfont (rong neu khong phai SHX hoac khong doc duoc).</summary>
        public string ShxKind = "";
        public string Hint = "";
        public int Count;
    }

    public sealed class TextItem
    {
        public string Handle = "";
        /// <summary>TEXT, MTEXT, ATTRIB, ATTDEF, MLEADER, DIMENSION, TABLE_CELL.</summary>
        public string Kind = "";
        /// <summary>model, layout, block.</summary>
        public string OwnerKind = "";
        public string Owner = "";
        /// <summary>Ten block cua INSERT (cho ATTRIB).</summary>
        public string Block = "";
        public string Layer = "";
        public string Style = "";
        public string Font = "";
        public string Raw = "";
        public int Length;
        public string Charset = "";
        public double Confidence;
        /// <summary>Ban doi sang Unicode (chi co khi se thay doi).</summary>
        public string Preview = "";
        /// <summary>Chuoi day du sau khi doi (khong cat), dung de lap ke hoach. Khong xuat ra JSON quet.</summary>
        public string Converted = "";
        /// <summary>So ky tu khong anh xa duoc khi doi.</summary>
        public int UnmappedCount;
        public List<string> Flags = new List<string>();
    }

    public sealed class ScanResult
    {
        public string Drawing = "";
        public string AcadVersion = "";
        public int CodePage;
        public string ScannedAt = "";
        public int ElapsedMs;
        public List<TextItem> Items = new List<TextItem>();
        public List<StyleInfo> Styles = new List<StyleInfo>();
        /// <summary>Loai doi tuong co chu nhung chua xu ly (vi du TOLERANCE): ten -> so luong.</summary>
        public Dictionary<string, int> Unsupported = new Dictionary<string, int>();
        public int Errors;
        public List<string> ErrorSamples = new List<string>();
    }
}
