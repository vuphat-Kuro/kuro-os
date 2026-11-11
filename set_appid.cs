using System;
using System.IO;
using System.Runtime.InteropServices;

namespace KuroShortcut {
    [StructLayout(LayoutKind.Sequential, Pack = 4)]
    public struct PROPERTYKEY {
        public Guid fmtid;
        public uint pid;
    }

    [StructLayout(LayoutKind.Explicit)]
    public struct PROPVARIANT {
        [FieldOffset(0)] public ushort vt;
        [FieldOffset(8)] public IntPtr pwszVal;
    }

    [ComImport]
    [Guid("00021401-0000-0000-C000-000000000046")]
    public class ShellLink {}

    [ComImport]
    [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    [Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99")]
    public interface IPropertyStore {
        uint GetCount();
        void GetAt(uint iprop, out PROPERTYKEY pkey);
        void GetValue(ref PROPERTYKEY key, out PROPVARIANT pv);
        void SetValue(ref PROPERTYKEY key, ref PROPVARIANT pv);
        void Commit();
    }

    [ComImport]
    [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    [Guid("0000010b-0000-0000-C000-000000000046")]
    public interface IPersistFile {
        void GetClassID(out Guid pClassID);
        void IsDirty();
        void Load([MarshalAs(UnmanagedType.LPWStr)] string pszFileName, uint dwMode);
        void Save([MarshalAs(UnmanagedType.LPWStr)] string pszFileName, [MarshalAs(UnmanagedType.Bool)] bool fRemember);
        void SaveCompleted([MarshalAs(UnmanagedType.LPWStr)] string pszFileName);
        void GetCurFile([Out, MarshalAs(UnmanagedType.LPWStr)] string ppszFileName);
    }

    public class Program {
        private static readonly PROPERTYKEY AppUserModelIDKey = new PROPERTYKEY {
            fmtid = new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3"),
            pid = 5
        };

        // STGM_READWRITE = 2
        private const uint STGM_READWRITE = 0x00000002;

        public static int Main(string[] args) {
            if (args.Length < 2) {
                Console.WriteLine("Usage: set_appid.exe <shortcut.lnk> <appId>");
                return 1;
            }
            string path = Path.GetFullPath(args[0]);
            string appId = args[1];

            if (!File.Exists(path)) {
                Console.WriteLine("File not found: " + path);
                return 2;
            }

            try {
                ShellLink link = new ShellLink();
                IPersistFile persistFile = (IPersistFile)link;
                persistFile.Load(path, STGM_READWRITE);

                IPropertyStore store = (IPropertyStore)link;
                PROPVARIANT pv = new PROPVARIANT();
                pv.vt = 31; // VT_LPWSTR
                pv.pwszVal = Marshal.StringToCoTaskMemUni(appId);

                PROPERTYKEY key = AppUserModelIDKey;
                store.SetValue(ref key, ref pv);
                store.Commit();

                persistFile.Save(path, true);
                Marshal.FreeCoTaskMem(pv.pwszVal);

                Console.WriteLine("Successfully set AppUserModelID on: " + path);
                return 0;
            } catch (Exception ex) {
                Console.WriteLine("Error on " + path + ": " + ex.Message);
                return 3;
            }
        }
    }
}
