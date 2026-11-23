// PKTTC TextHub - lenh PKTEXTABOUT: phien ban, thanh phan, trang thai. Chi doc. C# 5.
using System;
using System.Collections.Generic;
using System.Reflection;
using System.Text;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.Runtime;
using AcApp = Autodesk.AutoCAD.ApplicationServices.Core.Application;

[assembly: CommandClass(typeof(Pkttc.Text.Db.AboutCommands))]

namespace Pkttc.Text.Db
{
    public class AboutCommands
    {
        [CommandMethod("PKTEXTABOUT")]
        public void About()
        {
            Document doc = AcApp.DocumentManager.MdiActiveDocument;
            Assembly asm = Assembly.GetExecutingAssembly();
            string ver = "?";
            object[] a = asm.GetCustomAttributes(typeof(AssemblyInformationalVersionAttribute), false);
            if (a.Length > 0) ver = ((AssemblyInformationalVersionAttribute)a[0]).InformationalVersion;

            List<string> cmds = new List<string>();
            foreach (Type t in asm.GetTypes())
                foreach (MethodInfo m in t.GetMethods())
                    foreach (object o in m.GetCustomAttributes(typeof(CommandMethodAttribute), false))
                        cmds.Add(((CommandMethodAttribute)o).GlobalName);
            cmds.Sort(StringComparer.Ordinal);

            FontStore store = FontStore.Load();
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("\n[PKTTC TextHub] Phien ban " + ver + " | AutoCAD " + AcApp.Version);
            sb.AppendLine("  Tep    : " + asm.Location);
            sb.AppendLine("  Lenh   : " + string.Join(", ", cmds.ToArray()));
            sb.AppendLine("  Kho font: " + store.FileCount + " tep trong " + store.Roots.Count + " thu muc");
            sb.AppendLine("  Cong tro ly: " + (Bridge.IsActive ? "dang mo" : "dong"));
            doc.Editor.WriteMessage(sb.ToString());
        }
    }
}
