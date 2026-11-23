// PKTTC TextHub - Core: kieu du lieu chung. C# 5, khong phu thuoc AutoCAD.
using System.Collections.Generic;

namespace Pkttc.Text.Core
{
    /// <summary>Bang ma cua mot doan chu.</summary>
    public enum Charset
    {
        /// <summary>Chi co ky tu ASCII (khong can doi).</summary>
        Ascii = 0,
        /// <summary>Unicode (hoac font khong phu thuoc bang ma tieng Viet cu).</summary>
        Unicode = 1,
        /// <summary>TCVN3 (ABC), font .Vn...</summary>
        Tcvn3 = 2,
        /// <summary>VNI Windows.</summary>
        Vni = 3,
        /// <summary>Khong xac dinh duoc.</summary>
        Unknown = 4
    }

    /// <summary>Ket qua doi mot chuoi.</summary>
    public sealed class ConversionResult
    {
        public string Text;
        public Charset From;
        public Charset To;
        /// <summary>Vi tri (trong chuoi NGUON) cua ky tu khong doi duoc.</summary>
        public List<int> Unmapped = new List<int>();
        public bool Changed;
    }

    /// <summary>Ket qua nhan dang bang ma.</summary>
    public sealed class DetectionResult
    {
        public Charset Charset;
        /// <summary>0..1. Thap thi nguoi dung nen xem lai.</summary>
        public double Confidence;
        public double ScoreAsIs;
        public double ScoreTcvn3;
        public double ScoreVni;
        public string Note = "";
    }
}
