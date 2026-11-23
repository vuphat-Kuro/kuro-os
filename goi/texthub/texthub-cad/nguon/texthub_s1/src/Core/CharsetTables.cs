// PKTTC TextHub - Core: bang ma TCVN3 / VNI dung tu data/charsets.csv (xem tools/build_charsets.py).
using System;
using System.Collections.Generic;
using System.Globalization;

namespace Pkttc.Text.Core
{
    internal static class CharsetTables
    {
        /// <summary>byte TCVN3 -> ky tu (chu thuong; 0xA1..0xA7 la chu hoa khong dau thanh).</summary>
        internal static readonly Dictionary<byte, char> TcvnToUni = new Dictionary<byte, char>();

        /// <summary>ky tu -> byte TCVN3 dung voi font THUONG (chu hoa co dau thanh khong co).</summary>
        internal static readonly Dictionary<char, byte> UniToTcvnNormal = new Dictionary<char, byte>();

        /// <summary>ky tu -> byte TCVN3 dung voi font HOA (.VnTimeH): ma cua chu thuong tuong ung.</summary>
        internal static readonly Dictionary<char, byte> UniToTcvnUpperFont = new Dictionary<char, byte>();

        /// <summary>cap 2 byte VNI (dang chuoi 2 ky tu) -> ky tu.</summary>
        internal static readonly Dictionary<string, char> VniPairToUni = new Dictionary<string, char>();

        /// <summary>1 byte VNI -> ky tu.</summary>
        internal static readonly Dictionary<char, char> VniSingleToUni = new Dictionary<char, char>();

        /// <summary>ky tu -> chuoi byte VNI (dang chuoi ky tu 0..255).</summary>
        internal static readonly Dictionary<char, string> UniToVni = new Dictionary<char, string>();

        /// <summary>134 chu cai Viet dung san.</summary>
        internal static readonly HashSet<char> VietLetters = new HashSet<char>();

        static CharsetTables()
        {
            foreach (string row in CharsetData.Rows)
            {
                string[] p = row.Split('|');
                char u = (char)int.Parse(p[0], NumberStyles.HexNumber, CultureInfo.InvariantCulture);
                byte t = byte.Parse(p[1], NumberStyles.HexNumber, CultureInfo.InvariantCulture);
                bool upperFontOnly = p[2] == "H";
                string[] vb = p[3].Split(new char[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);

                VietLetters.Add(u);

                // TCVN3
                if (!upperFontOnly)
                {
                    TcvnToUni[t] = u;
                    UniToTcvnNormal[u] = t;
                }

                // VNI
                char[] seq = new char[vb.Length];
                for (int i = 0; i < vb.Length; i++)
                    seq[i] = (char)byte.Parse(vb[i], NumberStyles.HexNumber, CultureInfo.InvariantCulture);
                string s = new string(seq);
                UniToVni[u] = s;
                if (seq.Length == 1) VniSingleToUni[seq[0]] = u;
                else VniPairToUni[s] = u;
            }

            // Font HOA: moi chu (ke ca HOA) dung ma cua chu THUONG tuong ung.
            foreach (char u in VietLetters)
            {
                byte b;
                char lower = char.ToLowerInvariant(u);
                if (!UniToTcvnNormal.TryGetValue(lower, out b))
                    throw new InvalidOperationException("Bang TCVN3 thieu chu thuong cho U+" + ((int)u).ToString("X4"));
                UniToTcvnUpperFont[u] = b;
            }
        }

        internal static bool IsVietLetter(char c)
        {
            return VietLetters.Contains(c);
        }
    }
}
