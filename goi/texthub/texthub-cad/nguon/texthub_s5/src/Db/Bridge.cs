// PKTTC TextHub - Db: cong cho tro ly (Kuro) dieu khien TextHub qua named pipe cuc bo. C# 5.
//
// Mo hinh an toan:
//  - Cong chi mo khi NGUOI DUNG go lenh PKTEXTBRIDGE va xac nhan YES; tat bang "shutdown", tep .stop hoac het gio khong dung.
//  - Named pipe cuc bo, chi nguoi dung hien tai (ACL), tu choi ket noi qua mang.
//  - Doc (ping, scan, fonts, plan.*, fontsub.plan, purge.plan) khong sua gi.
//  - Ghi (plan.apply, fontsub.apply, purge.apply) CHI chay sau khi nguoi dung go YES ngay trong AutoCAD cho tung lan.
//    Tro ly khong the tu phe duyet. Ke hoach nam trong bo nho cua AutoCAD; tro ly chi gui ma ke hoach, khong gui noi dung de ghi.
//  - Ghi: sao luu truoc, mot giao dich (mot buoc UNDO), nhat ky; moi yeu cau ghi vao audit.log.
//  - Moi yeu cau chay tren luong chinh cua AutoCAD, tung cai mot. Hai che do:
//      idle (mac dinh trong AutoCAD giao dien): khong chan dong lenh; xu ly khi AutoCAD ranh (Application.Idle); xin phep bang hop thoai;
//        viec GHI chay trong mot lenh that (PKTEXTBRIDGEEXEC) de co mot buoc UNDO.
//      loop (accoreconsole hoac PKTTC_BRIDGE_MODE=loop): vong lap chan trong lenh PKTEXTBRIDGE; xin phep tren dong lenh.
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.IO.Pipes;
using System.Security.AccessControl;
using System.Security.Cryptography;
using System.Security.Principal;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using System.Web.Script.Serialization;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.EditorInput;
using AcApp = Autodesk.AutoCAD.ApplicationServices.Core.Application;

namespace Pkttc.Text.Db
{
    public static class Bridge
    {
        public const int ProtocolVersion = 1;
        private const int MaxRequestBytes = 4 * 1024 * 1024;

        private sealed class Pending
        {
            public string Request;
            public string Response;
            public readonly ManualResetEvent Done = new ManualResetEvent(false);
        }

        private static BlockingCollection<Pending> _queue;
        private static volatile bool _stop;
        private static readonly Dictionary<string, object> Store = new Dictionary<string, object>();
        private static string _dir = "";
        private static volatile string _acl = "";
        private static readonly JavaScriptSerializer Js = new JavaScriptSerializer { MaxJsonLength = int.MaxValue };

        // ================================================================== khoi dong, dong, hai che do
        private static string _pipe = "", _info = "", _stopFile = "";
        private static volatile bool _idleMode, _busy, _active;
        private static Document _doc;
        private static int _idleMinutes = 30;
        private static DateTime _last = DateTime.Now, _execSince = DateTime.Now, _fileCheck = DateTime.Now;

        private sealed class ExecItem
        {
            public Pending P;
            public WriteJob Job;
            public object Id;
            public string Method = "", Client = "";
        }

        private static ExecItem _exec;

        /// <summary>True neu dang chay trong AutoCAD giao dien (co Acmgd) va khong ep che do loop.</summary>
        public static bool UseIdle()
        {
            string m = (Environment.GetEnvironmentVariable("PKTTC_BRIDGE_MODE") ?? "").Trim().ToLowerInvariant();
            if (m == "loop") return false;
            foreach (System.Reflection.Assembly a in AppDomain.CurrentDomain.GetAssemblies())
                if (string.Equals(a.GetName().Name, "acmgd", StringComparison.OrdinalIgnoreCase)) return true;
            return false;
        }

        private static void Begin(Document doc, int idleMinutes, string mode)
        {
            if (_active) throw new InvalidOperationException("Cong dang mo.");
            int pid = System.Diagnostics.Process.GetCurrentProcess().Id;
            _pipe = "PKTTC.TextHub." + pid;
            _dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "PKTTC", "bridge");
            Directory.CreateDirectory(_dir);
            _info = Path.Combine(_dir, pid + ".json");
            _stopFile = Path.Combine(_dir, pid + ".stop");
            if (File.Exists(_stopFile)) File.Delete(_stopFile);

            _queue = new BlockingCollection<Pending>();
            _stop = false;
            _busy = false;
            _exec = null;
            _doc = doc;
            _idleMinutes = idleMinutes;
            _last = DateTime.Now;
            Store.Clear();

            Dictionary<string, object> meta = new Dictionary<string, object>();
            meta["pid"] = pid; meta["pipe"] = _pipe; meta["protocol"] = ProtocolVersion; meta["mode"] = mode;
            meta["started"] = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"); meta["drawing"] = doc.Database.Filename ?? "";
            File.WriteAllText(_info, Js.Serialize(meta), new UTF8Encoding(false));

            string pipe = _pipe;
            Thread server = new Thread(delegate() { ServerLoop(pipe); });
            server.IsBackground = true;
            server.Start();
            _active = true;
            Audit("-", "bridge.start", _pipe + " (" + mode + ")");
        }

        private static void End()
        {
            _stop = true;
            _active = false;
            try { using (NamedPipeClientStream c = new NamedPipeClientStream(".", _pipe, PipeDirection.InOut)) c.Connect(300); } catch (System.Exception) { } // mo khoa WaitForConnection
            try { File.Delete(_info); } catch (System.Exception) { }
            try { if (File.Exists(_stopFile)) File.Delete(_stopFile); } catch (System.Exception) { }
            ExecItem e = _exec;
            _exec = null;
            if (e != null) { e.P.Response = Err(e.Id, -32001, "Cong da dong."); e.P.Done.Set(); }
            Pending rest;
            while (_queue.TryTake(out rest)) { rest.Response = Err(null, -32001, "Cong da dong."); rest.Done.Set(); }
            Audit("-", "bridge.closed", _pipe);
            try { _doc.Editor.WriteMessage("\n[PKTTC] Cong Kuro da DONG.\n"); } catch (System.Exception) { }
        }

        // ---------------------------------------------------------- che do loop (chan, dung cho accoreconsole)
        public static void Run(Document doc, int idleMinutes)
        {
            Editor ed = doc.Editor;
            Begin(doc, idleMinutes, "loop");
            _idleMode = false;
            ed.WriteMessage("\n[PKTTC] Cong Kuro dang MO, che do CHAN (pipe " + _pipe + "). Kuro doc va lap ke hoach duoc; moi thao tac GHI se hoi ban go YES. AutoCAD chi nhan lenh tu Kuro cho den khi cong dong"
                + " (Kuro gui shutdown, hoac tao tep " + _stopFile + ", hoac sau " + idleMinutes + " phut khong dung).\n");
            try
            {
                while (!_stop)
                {
                    Pending p;
                    if (_queue.TryTake(out p, 200))
                    {
                        _last = DateTime.Now;
                        try
                        {
                            WriteJob job; object id; string method, client;
                            string resp = HandleBegin(doc, p.Request, out job, out id, out method, out client);
                            if (job != null)
                            {
                                bool yes = Approve(ed, client, job.What, job.Lines, job.Note);
                                resp = FinishJob(doc, job, yes, id, method, client);
                            }
                            p.Response = resp;
                        }
                        catch (System.Exception ex) { p.Response = Err(null, -32000, "Loi noi bo: " + ex.GetType().Name + ": " + ex.Message); }
                        p.Done.Set();
                        continue;
                    }
                    try { System.Windows.Forms.Application.DoEvents(); } catch (System.Exception) { }
                    if (File.Exists(_stopFile)) { _stop = true; Audit("-", "bridge.stop", "tep .stop"); }
                    else if ((DateTime.Now - _last).TotalMinutes > idleMinutes) { _stop = true; Audit("-", "bridge.stop", "het gio khong dung"); }
                }
            }
            finally { End(); }
        }

        // ---------------------------------------------------------- che do idle (khong chan dong lenh)
        public static void StartIdle(Document doc, int idleMinutes)
        {
            Begin(doc, idleMinutes, "idle");
            _idleMode = true;
            IdlePump.Attach();
            doc.Editor.WriteMessage("\n[PKTTC] Cong Kuro dang MO, che do KHONG CHAN (pipe " + _pipe + "). Ban van dung AutoCAD binh thuong. Moi thao tac GHI cua Kuro hien hop thoai xin phep."
                + " Dong cong: lenh PKTEXTBRIDGESTOP, hoac Kuro gui shutdown, hoac tao tep " + _stopFile + ", hoac sau " + idleMinutes + " phut khong dung.\n");
        }

        public static bool IsActive { get { return _active; } }

        /// <summary>Dong cong (che do idle). Che do loop dong khi Kuro gui shutdown.</summary>
        public static void Stop(string reason)
        {
            if (!_active) return;
            Audit("-", "bridge.stop", reason);
            if (_idleMode)
            {
                try { IdlePump.Detach(); } catch (System.Exception) { }
                End();
            }
            else _stop = true;
        }

        /// <summary>Goi tren luong chinh moi khi AutoCAD ranh (Application.Idle).</summary>
        internal static void IdleTick()
        {
            if (!_active || !_idleMode || _busy) return;
            if (_exec != null)
            {
                if ((DateTime.Now - _execSince).TotalSeconds > 30)
                {
                    ExecItem dead = _exec; _exec = null;
                    dead.P.Response = Err(dead.Id, -32002, "Khong chay duoc lenh ghi trong AutoCAD (qua 30 giay). Ban ve khong doi.");
                    dead.P.Done.Set();
                }
                return;
            }
            Document doc = _doc;
            if (doc == null || !doc.Editor.IsQuiescent) return;

            Pending p;
            if (!_queue.TryTake(out p))
            {
                if ((DateTime.Now - _fileCheck).TotalSeconds >= 1)
                {
                    _fileCheck = DateTime.Now;
                    if (File.Exists(_stopFile)) Stop("tep .stop");
                    else if ((DateTime.Now - _last).TotalMinutes > _idleMinutes) Stop("het gio khong dung");
                }
                return;
            }

            _last = DateTime.Now;
            _busy = true;
            bool keepBusy = false;
            try
            {
                WriteJob job; object id; string method, client;
                string resp = HandleBegin(doc, p.Request, out job, out id, out method, out client);
                if (job == null)
                {
                    p.Response = resp;
                    p.Done.Set();
                    if (_stop) Stop("shutdown");
                    return;
                }
                bool yes = ApproveDialog(client, job);
                if (!yes)
                {
                    p.Response = FinishJob(doc, job, false, id, method, client);
                    p.Done.Set();
                    return;
                }
                // Da dong y: GHI trong mot lenh that de co mot buoc UNDO
                ExecItem e = new ExecItem();
                e.P = p; e.Job = job; e.Id = id; e.Method = method; e.Client = client;
                _exec = e;
                _execSince = DateTime.Now;
                keepBusy = true;
                doc.SendStringToExecute("PKTEXTBRIDGEEXEC ", true, false, false);
            }
            catch (System.Exception ex)
            {
                p.Response = Err(null, -32000, "Loi noi bo: " + ex.GetType().Name + ": " + ex.Message);
                p.Done.Set();
            }
            finally { if (!keepBusy) _busy = false; }
        }

        /// <summary>Lenh PKTEXTBRIDGEEXEC: chay viec GHI da duoc nguoi dung dong y, ben trong mot lenh AutoCAD.</summary>
        public static void ExecPending()
        {
            ExecItem e = _exec;
            _exec = null;
            if (e == null) { _busy = false; return; }
            try { e.P.Response = FinishJob(_doc, e.Job, true, e.Id, e.Method, e.Client); }
            catch (System.Exception ex) { e.P.Response = Err(e.Id, -32000, "Loi noi bo: " + ex.GetType().Name + ": " + ex.Message); }
            e.P.Done.Set();
            _last = DateTime.Now;
            _busy = false;
        }

        // ================================================================== luong pipe
        private static PipeSecurity Security()
        {
            PipeSecurity ps = new PipeSecurity();
            ps.AddAccessRule(new PipeAccessRule(WindowsIdentity.GetCurrent().User, PipeAccessRights.FullControl, AccessControlType.Allow));
            ps.AddAccessRule(new PipeAccessRule(new SecurityIdentifier(WellKnownSidType.NetworkSid, null), PipeAccessRights.FullControl, AccessControlType.Deny));
            return ps;
        }

        private static void ServerLoop(string pipe)
        {
            while (!_stop)
            {
                try
                {
                    using (NamedPipeServerStream srv = new NamedPipeServerStream(pipe, PipeDirection.InOut, 1, PipeTransmissionMode.Byte,
                        PipeOptions.None, 65536, 65536, Security()))
                    {
                        // DACL that su cua pipe (de nguoi kiem tra thay no chi cho nguoi dung hien tai)
                        try { _acl = srv.GetAccessControl().GetSecurityDescriptorSddlForm(AccessControlSections.Access); } catch (System.Exception) { }
                        srv.WaitForConnection();
                        if (_stop) break;
                        Serve(srv);
                    }
                }
                catch (IOException) { }
                catch (System.Exception) { if (_stop) break; Thread.Sleep(100); }
            }
        }

        private static void Serve(Stream s)
        {
            MemoryStream acc = new MemoryStream();
            byte[] buf = new byte[8192];
            while (!_stop)
            {
                int n = s.Read(buf, 0, buf.Length);
                if (n <= 0) return;
                acc.Write(buf, 0, n);
                while (true)
                {
                    byte[] all = acc.ToArray();
                    int nl = Array.IndexOf(all, (byte)'\n');
                    if (nl < 0)
                    {
                        if (all.Length > MaxRequestBytes) { WriteLine(s, Err(null, -32600, "Yeu cau qua lon (toi da " + MaxRequestBytes + " byte).")); return; }
                        break;
                    }
                    string line = Encoding.UTF8.GetString(all, 0, nl).TrimEnd('\r');
                    acc = new MemoryStream();
                    acc.Write(all, nl + 1, all.Length - nl - 1);
                    if (line.Length == 0) continue;

                    Pending p = new Pending();
                    p.Request = line;
                    try { _queue.Add(p); } catch (InvalidOperationException) { return; }
                    if (_idleMode) Win32Nudge.Poke();   // danh thuc vong lap thong diep de Application.Idle chay
                    p.Done.WaitOne();
                    WriteLine(s, p.Response);
                }
            }
        }

        private static void WriteLine(Stream s, string text)
        {
            byte[] b = Encoding.UTF8.GetBytes(text + "\n");
            s.Write(b, 0, b.Length);
            s.Flush();
        }

        // ================================================================== xu ly yeu cau (luong chinh)
        /// <summary>Viec GHI da duoc kiem tra, dang cho nguoi dung dong y. Run chay sau khi dong y; OnReject khi tu choi.</summary>
        private sealed class WriteJob
        {
            public string What = "", Note = "";
            public List<string> Lines = new List<string>();
            public Func<object> Run;
            public Func<object> OnReject;
        }

        /// <summary>
        /// Xu ly mot yeu cau. Doc: tra ve chuoi tra loi. Ghi: tra ve null va dat job (noi goi xin phep nguoi dung roi goi FinishJob).
        /// </summary>
        private static string HandleBegin(Document doc, string line, out WriteJob job, out object id, out string method, out string client)
        {
            job = null; id = null; method = ""; client = "?";
            Dictionary<string, object> req;
            try { req = Js.Deserialize<Dictionary<string, object>>(line); }
            catch (System.Exception) { return Err(null, -32700, "JSON khong hop le."); }
            if (req == null) return Err(null, -32700, "JSON khong hop le.");

            id = req.ContainsKey("id") ? req["id"] : null;
            method = req.ContainsKey("method") ? Convert.ToString(req["method"]) : "";
            Dictionary<string, object> prm = req.ContainsKey("params") ? req["params"] as Dictionary<string, object> : null;
            if (prm == null) prm = new Dictionary<string, object>();
            client = Str(prm, "client", "?");
            if (client.Length > 40) client = client.Substring(0, 40);

            try
            {
                object result;
                switch (method)
                {
                    case "ping": result = Ping(doc); break;
                    case "scan": result = ScanDict(Ops.Scan(doc), prm); break;
                    case "fonts": result = FontsDict(doc); break;
                    case "plan.create": result = PlanCreate(doc, prm); break;
                    case "plan.get": result = PlanGet(prm); break;
                    case "plan.apply": result = PlanApply(doc, prm); break;
                    case "fontsub.plan": result = FontSubPlan(doc); break;
                    case "fontsub.apply": result = FontSubApply(doc, prm); break;
                    case "purge.plan": result = PurgePlan(doc); break;
                    case "purge.apply": result = PurgeApply(doc, prm); break;
                    case "shutdown": _stop = true; result = Dict("status", "stopping"); break;
                    default:
                        Audit(client, method, "phuong thuc khong biet");
                        return Err(id, -32601, "Phuong thuc khong ton tai: " + method);
                }
                WriteJob wj = result as WriteJob;
                if (wj != null) { job = wj; return null; }
                return Ok(id, client, method, result);
            }
            catch (BridgeException bx)
            {
                Audit(client, method, "loi " + bx.Code + ": " + bx.Message);
                return Err(id, bx.Code, bx.Message);
            }
        }

        /// <summary>Hoan tat viec GHI sau khi nguoi dung tra loi: dong y thi chay, tu choi thi bao rejected.</summary>
        private static string FinishJob(Document doc, WriteJob job, bool approved, object id, string method, string client)
        {
            Audit(client, "approval", job.What + " -> " + (approved ? "DONG Y" : "TU CHOI"));
            try
            {
                object result = approved ? job.Run() : job.OnReject();
                Dictionary<string, object> d = result as Dictionary<string, object>;
                if (d != null)
                {
                    string cmd = "";
                    try { cmd = AcApp.DocumentManager.MdiActiveDocument.CommandInProgress ?? ""; } catch (System.Exception) { }
                    d["commandContext"] = cmd;   // lenh AutoCAD dang chay khi ghi (PKTEXTBRIDGEEXEC hoac PKTEXTBRIDGE): ban ve co mot buoc UNDO
                }
                return Ok(id, client, method, result);
            }
            catch (BridgeException bx)
            {
                Audit(client, method, "loi " + bx.Code + ": " + bx.Message);
                return Err(id, bx.Code, bx.Message);
            }
        }

        private static string Ok(object id, string client, string method, object result)
        {
            Audit(client, method, Brief(result));
            Dictionary<string, object> ok = new Dictionary<string, object>();
            ok["id"] = id; ok["result"] = result;
            return Js.Serialize(ok);
        }

        private sealed class BridgeException : Exception
        {
            public readonly int Code;
            public BridgeException(int code, string msg) : base(msg) { Code = code; }
        }

        // ------------------------------------------------------------------ doc
        private static object Ping(Document doc)
        {
            Dictionary<string, object> d = new Dictionary<string, object>();
            d["ok"] = true;
            d["protocol"] = ProtocolVersion;
            d["acad"] = AcApp.Version.ToString();
            d["drawing"] = doc.Database.Filename ?? "";
            d["pid"] = System.Diagnostics.Process.GetCurrentProcess().Id;
            d["pending"] = new List<string>(Store.Keys);
            d["fontStoreFiles"] = FontStore.Load().FileCount;
            d["pipeAcl"] = _acl;
            return d;
        }

        private static object ScanDict(ScanResult r, Dictionary<string, object> prm)
        {
            string mode = Str(prm, "items", "none");
            int offset = Math.Max(0, Int(prm, "offset", 0));
            int limit = Math.Min(500, Math.Max(1, Int(prm, "limit", 50)));

            Dictionary<string, object> d = new Dictionary<string, object>();
            Dictionary<string, object> meta = new Dictionary<string, object>();
            meta["drawing"] = r.Drawing; meta["acadVersion"] = r.AcadVersion; meta["codePage"] = r.CodePage;
            meta["itemsTotal"] = r.Items.Count; meta["elapsedMs"] = r.ElapsedMs; meta["errors"] = r.Errors;
            d["meta"] = meta;

            Dictionary<string, int> byKind = new Dictionary<string, int>(), byOwner = new Dictionary<string, int>(),
                byCharset = new Dictionary<string, int>(), byFlag = new Dictionary<string, int>();
            foreach (TextItem i in r.Items)
            {
                Inc(byKind, i.Kind); Inc(byOwner, i.OwnerKind); Inc(byCharset, i.Charset);
                foreach (string f in i.Flags) Inc(byFlag, f);
            }
            Dictionary<string, object> sum = new Dictionary<string, object>();
            sum["byKind"] = byKind; sum["byOwnerKind"] = byOwner; sum["byCharset"] = byCharset; sum["byFlag"] = byFlag; sum["unsupported"] = r.Unsupported;
            d["summary"] = sum;

            List<object> styles = new List<object>();
            foreach (StyleInfo s in r.Styles)
            {
                Dictionary<string, object> sd = new Dictionary<string, object>();
                sd["name"] = s.Name; sd["font"] = s.FontName; sd["fontExists"] = s.FontExists; sd["count"] = s.Count; sd["hint"] = s.Hint; sd["shxKind"] = s.ShxKind;
                styles.Add(sd);
            }
            d["styles"] = styles;

            if (mode == "flagged" || mode == "all")
            {
                List<TextItem> sel = new List<TextItem>();
                foreach (TextItem i in r.Items)
                    if (mode == "all" || i.Flags.Count > 0 || i.Charset != "Ascii") sel.Add(i);
                List<object> items = new List<object>();
                for (int k = offset; k < sel.Count && items.Count < limit; k++)
                {
                    TextItem i = sel[k];
                    Dictionary<string, object> it = new Dictionary<string, object>();
                    it["handle"] = i.Handle; it["kind"] = i.Kind; it["ownerKind"] = i.OwnerKind; it["owner"] = i.Owner; it["block"] = i.Block;
                    it["layer"] = i.Layer; it["style"] = i.Style; it["font"] = i.Font; it["length"] = i.Length; it["charset"] = i.Charset;
                    it["confidence"] = i.Confidence; it["flags"] = i.Flags; it["raw"] = Cut(i.Raw, 200); it["preview"] = Cut(i.Preview, 200);
                    items.Add(it);
                }
                d["itemsReturned"] = items.Count; d["itemsMatching"] = sel.Count; d["offset"] = offset; d["items"] = items;
            }
            return d;
        }

        private static object FontsDict(Document doc)
        {
            ScanResult scan = Ops.Scan(doc);
            FontStore store = FontStore.Load();
            List<FontUse> uses = FontReporter.Build(scan, new FontEnv(doc.Database), store);
            int ok = 0, inStore = 0, missing = 0;
            List<object> list = new List<object>();
            foreach (FontUse u in uses)
            {
                if (u.Status == "ok") ok++; else if (u.Status == "inStore") inStore++; else missing++;
                Dictionary<string, object> f = new Dictionary<string, object>();
                f["name"] = u.Name; f["isShx"] = u.IsShx; f["shxKind"] = u.ShxKind; f["status"] = u.Status; f["hint"] = u.Hint; f["count"] = u.Count;
                f["sources"] = u.Sources; f["styles"] = u.Styles; f["storePath"] = u.StorePath; f["substitute"] = u.Substitute; f["substituteSource"] = u.SubstituteSource;
                list.Add(f);
            }
            Dictionary<string, object> d = new Dictionary<string, object>();
            d["fontsTotal"] = uses.Count; d["ok"] = ok; d["inStore"] = inStore; d["missing"] = missing;
            d["storeFiles"] = store.FileCount; d["storeRoots"] = store.Roots; d["fonts"] = list;
            return d;
        }

        private static object PlanCreate(Document doc, Dictionary<string, object> prm)
        {
            PlanOptions o = new PlanOptions();
            string font = Str(prm, "targetFont", "");
            if (font.Length > 0) o.TargetFont = CleanName(font, "targetFont");
            string shxFont = Str(prm, "targetShxFont", "");
            if (shxFont.Length > 0) o.TargetShxFont = CleanName(shxFont, "targetShxFont");
            string style = Str(prm, "targetStyle", "");
            if (style.Length > 0) o.TargetStyle = CleanName(style, "targetStyle");
            object fmObj;
            if (prm.TryGetValue("fontMap", out fmObj) && fmObj is Dictionary<string, object>)
                foreach (KeyValuePair<string, object> kv in (Dictionary<string, object>)fmObj)
                {
                    string dst = Convert.ToString(kv.Value);
                    if (dst.Length > 0) o.FontMap[kv.Key] = CleanName(dst, "fontMap[" + kv.Key + "]");
                }
            o.KeepWidth = Bool(prm, "keepWidth", true);
            o.IncludeLocked = Bool(prm, "includeLocked", false);

            Plan plan = Ops.BuildPlan(doc, o);
            Store[plan.PlanId] = plan;
            string file = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "PKTTC", "out", "plan_" + plan.PlanId + ".json");
            try { PlanIo.Write(plan, file); } catch (System.Exception) { file = ""; }

            Dictionary<string, object> d = PlanSummary(plan);
            d["planFile"] = file;
            return d;
        }

        private static Dictionary<string, object> PlanSummary(Plan plan)
        {
            Dictionary<string, int> byKind = new Dictionary<string, int>();
            foreach (PlanItem i in plan.Items) Inc(byKind, i.Kind);
            Dictionary<string, object> d = new Dictionary<string, object>();
            d["planId"] = plan.PlanId; d["count"] = plan.Items.Count; d["byKind"] = byKind; d["skipped"] = plan.Skipped;
            d["targetStyle"] = plan.Options.TargetStyle; d["targetFont"] = plan.Options.TargetFont; d["keepWidth"] = plan.Options.KeepWidth;
            d["fontMap"] = plan.Options.FontMap; d["targetShxFont"] = plan.Options.TargetShxFont;
            d["includeLocked"] = plan.Options.IncludeLocked;
            d["sample"] = PlanItems(plan, 0, 10);
            d["needsApproval"] = "plan.apply se hoi nguoi dung go YES trong AutoCAD";
            return d;
        }

        private static List<object> PlanItems(Plan plan, int offset, int limit)
        {
            List<object> list = new List<object>();
            for (int k = offset; k < plan.Items.Count && list.Count < limit; k++)
            {
                PlanItem i = plan.Items[k];
                Dictionary<string, object> d = new Dictionary<string, object>();
                d["handle"] = i.Handle; d["kind"] = i.Kind; d["owner"] = i.Owner; d["oldStyle"] = i.OldStyle; d["newStyle"] = i.NewStyle;
                d["oldRaw"] = Cut(i.OldRaw, 80); d["newText"] = Cut(i.NewText, 80);
                list.Add(d);
            }
            return list;
        }

        private static object PlanGet(Dictionary<string, object> prm)
        {
            Plan plan = GetStored<Plan>(Str(prm, "planId", ""));
            int offset = Math.Max(0, Int(prm, "offset", 0));
            int limit = Math.Min(200, Math.Max(1, Int(prm, "limit", 50)));
            Dictionary<string, object> d = PlanSummary(plan);
            d["offset"] = offset;
            d["items"] = PlanItems(plan, offset, limit);
            return d;
        }

        // ------------------------------------------------------------------ ghi (hoi nguoi dung)
        private static object PlanApply(Document doc, Dictionary<string, object> prm)
        {
            Plan plan = GetStored<Plan>(Str(prm, "planId", ""));
            if (plan.Items.Count == 0) return Dict("status", "nothing", "message", "Ke hoach khong co muc nao.");

            WriteJob job = new WriteJob();
            job.What = "ap dung ke hoach chu";
            job.Note = Str(prm, "note", "");
            job.Lines.Add("Ke hoach " + plan.PlanId + ": doi " + plan.Items.Count + " muc chu TCVN3/VNI sang Unicode, style dich '" + plan.Options.TargetStyle + "', giu do rong: " + plan.Options.KeepWidth);
            job.Lines.Add("Bo qua: " + Commands.Fmt(plan.Skipped));
            for (int k = 0; k < plan.Items.Count && k < 5; k++)
                job.Lines.Add("  " + plan.Items[k].Kind + " (" + plan.Items[k].OldStyle + "): " + Cut(plan.Items[k].OldRaw, 40) + "  ->  " + Cut(plan.Items[k].NewText, 40));
            job.OnReject = delegate() { return Dict("status", "rejected", "planId", plan.PlanId); };
            job.Run = delegate()
            {
                ApplyOutcome o = Ops.ApplyPlan(doc, plan);
                doc.Editor.WriteMessage(o.Message);
                Dictionary<string, object> d = Dict("status", o.Ok ? "applied" : "failed", "planId", plan.PlanId, "message", o.Message.Trim());
                d["backup"] = o.BackupPath; d["log"] = o.LogJsonPath;
                if (o.Report != null)
                {
                    d["ok"] = o.Report.Ok; d["skipped"] = o.Report.Skipped; d["errors"] = o.Report.Errors; d["stylesCreated"] = o.Report.StylesCreated;
                    d["maxDeviation"] = o.Report.MaxDeviation; d["clamped"] = o.Report.Clamped;
                }
                if (o.Ok) Store.Remove(plan.PlanId); // moi ke hoach chi ap dung mot lan
                return d;
            };
            return job;
        }

        private static object FontSubPlan(Document doc)
        {
            ScanResult scan = Ops.Scan(doc);
            List<SubItem> plan = StyleOps.BuildSubPlan(scan, FontReporter.Build(scan, new FontEnv(doc.Database), FontStore.Load()));
            StringBuilder sb = new StringBuilder();
            foreach (SubItem s in plan) sb.Append(s.Style).Append('|').Append(s.OldFont).Append('|').Append(s.NewFont).Append('\n');
            string id = "fs-" + Hash(sb.ToString());
            Store[id] = plan;
            List<object> items = new List<object>();
            foreach (SubItem s in plan) items.Add(Dict("style", s.Style, "oldFont", s.OldFont, "newFont", s.NewFont));
            return Dict("planId", id, "count", plan.Count, "items", items, "needsApproval", "fontsub.apply se hoi nguoi dung go YES trong AutoCAD");
        }

        private static object FontSubApply(Document doc, Dictionary<string, object> prm)
        {
            string pid = Str(prm, "planId", "");
            List<SubItem> plan = GetStored<List<SubItem>>(pid);
            if (plan.Count == 0) return Dict("status", "nothing");
            WriteJob job = new WriteJob();
            job.What = "thay font " + plan.Count + " style";
            job.Note = Str(prm, "note", "");
            foreach (SubItem s in plan) job.Lines.Add("  " + s.Style + ": " + s.OldFont + " -> " + s.NewFont);
            job.OnReject = delegate() { return Dict("status", "rejected"); };
            job.Run = delegate()
            {
                ApplyOutcome o = Ops.ApplyFontSub(doc, plan);
                doc.Editor.WriteMessage(o.Message);
                if (o.Ok) Store.Remove(pid);
                return Dict("status", o.Ok ? "applied" : "failed", "count", o.Count, "backup", o.BackupPath, "message", o.Message.Trim());
            };
            return job;
        }

        private static object PurgePlan(Document doc)
        {
            List<string> names = StyleOps.PurgeCandidates(doc.Database);
            string id = "pg-" + Hash(string.Join("\n", names.ToArray()));
            Store[id] = names;
            return Dict("planId", id, "count", names.Count, "styles", names, "needsApproval", "purge.apply se hoi nguoi dung go YES trong AutoCAD");
        }

        private static object PurgeApply(Document doc, Dictionary<string, object> prm)
        {
            string pid = Str(prm, "planId", "");
            List<string> names = GetStored<List<string>>(pid);
            if (names.Count == 0) return Dict("status", "nothing");
            WriteJob job = new WriteJob();
            job.What = "don " + names.Count + " style";
            job.Note = Str(prm, "note", "");
            job.Lines.Add("Xoa " + names.Count + " style khong dung: " + string.Join(", ", names.ToArray()));
            job.OnReject = delegate() { return Dict("status", "rejected"); };
            job.Run = delegate()
            {
                ApplyOutcome o = Ops.ApplyPurge(doc, names);
                doc.Editor.WriteMessage(o.Message);
                if (o.Ok) Store.Remove(pid);
                return Dict("status", o.Ok ? "applied" : "failed", "count", o.Count, "backup", o.BackupPath, "message", o.Message.Trim());
            };
            return job;
        }

        // ------------------------------------------------------------------ phe duyet boi nguoi dung
        private static bool Approve(Editor ed, string client, string what, List<string> lines, string note)
        {
            StringBuilder sb = new StringBuilder("\n[PKTTC] '" + client + "' de nghi " + what + ":");
            foreach (string l in lines) sb.Append("\n  ").Append(l);
            if (note.Length > 0) sb.Append("\n  Ghi chu cua tro ly: ").Append(Cut(note, 200));
            ed.WriteMessage(sb.ToString() + "\n");
            PromptStringOptions pso = new PromptStringOptions("\nGo YES de cho phep (khac = tu choi): ");
            pso.AllowSpaces = false;
            PromptResult pr = ed.GetString(pso);
            return pr.Status == PromptStatus.OK && string.Equals(pr.StringResult.Trim(), "YES", StringComparison.OrdinalIgnoreCase);
        }

        /// <summary>Hop thoai xin phep (che do idle). Mac dinh la "Khong". Chay tren luong chinh cua AutoCAD.</summary>
        private static bool ApproveDialog(string client, WriteJob job)
        {
            StringBuilder sb = new StringBuilder("Tro ly '" + client + "' de nghi " + job.What + ":\n");
            int n = 0;
            foreach (string l in job.Lines) { if (n++ >= 12) { sb.Append("\n  ..."); break; } sb.Append("\n").Append(l); }
            if (job.Note.Length > 0) sb.Append("\n\nGhi chu cua tro ly: ").Append(Cut(job.Note, 200));
            sb.Append("\n\nCho phep ghi vao ban ve? Se sao luu truoc; hoan tac bang lenh U (mot buoc).");
            DialogResult r = MessageBox.Show(new Win32Owner(IdlePumpHandle()), sb.ToString(), "PKTTC TextHub - tro ly de nghi ghi vao ban ve",
                MessageBoxButtons.YesNo, MessageBoxIcon.Question, MessageBoxDefaultButton.Button2);
            return r == DialogResult.Yes;
        }

        private static IntPtr IdlePumpHandle() { return Win32Nudge.Handle; }

        private sealed class Win32Owner : IWin32Window
        {
            private readonly IntPtr _h;
            public Win32Owner(IntPtr h) { _h = h; }
            public IntPtr Handle { get { return _h; } }
        }

        // ------------------------------------------------------------------ tien ich
        private static T GetStored<T>(string id) where T : class
        {
            object o;
            if (id.Length == 0 || !Store.TryGetValue(id, out o) || !(o is T))
                throw new BridgeException(-32004, "Khong co ke hoach '" + id + "' (chua lap, da ap dung, hoac cong da khoi dong lai).");
            return (T)o;
        }

        private static string CleanName(string s, string field)
        {
            s = s.Trim();
            if (s.Length == 0 || s.Length > 64) throw new BridgeException(-32602, field + " phai co 1 den 64 ky tu.");
            foreach (char c in s)
                if (c < 0x20 || c == '<' || c == '>' || c == '/' || c == '\\' || c == '"' || c == ':' || c == ';' || c == '?' || c == '*' || c == '|' || c == ',' || c == '=' || c == '`')
                    throw new BridgeException(-32602, field + " chua ky tu khong hop le.");
            return s;
        }

        private static string Str(Dictionary<string, object> d, string k, string def)
        {
            object v;
            return d.TryGetValue(k, out v) && v != null ? Convert.ToString(v) : def;
        }

        private static int Int(Dictionary<string, object> d, string k, int def)
        {
            object v;
            if (!d.TryGetValue(k, out v) || v == null) return def;
            try { return Convert.ToInt32(v); } catch (System.Exception) { return def; }
        }

        private static bool Bool(Dictionary<string, object> d, string k, bool def)
        {
            object v;
            if (!d.TryGetValue(k, out v) || v == null) return def;
            try { return Convert.ToBoolean(v); } catch (System.Exception) { return def; }
        }

        private static string Cut(string s, int n)
        {
            if (s == null) return "";
            return s.Length > n ? s.Substring(0, n) : s;
        }

        private static void Inc(Dictionary<string, int> d, string k)
        {
            int n;
            d.TryGetValue(k, out n);
            d[k] = n + 1;
        }

        private static Dictionary<string, object> Dict(params object[] kv)
        {
            Dictionary<string, object> d = new Dictionary<string, object>();
            for (int i = 0; i + 1 < kv.Length; i += 2) d[(string)kv[i]] = kv[i + 1];
            return d;
        }

        private static string Hash(string s)
        {
            using (SHA256 h = SHA256.Create())
            {
                byte[] b = h.ComputeHash(Encoding.UTF8.GetBytes(s));
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < 6; i++) sb.Append(b[i].ToString("x2"));
                return sb.ToString();
            }
        }

        private static string Err(object id, int code, string msg)
        {
            Dictionary<string, object> e = new Dictionary<string, object>();
            e["code"] = code; e["message"] = msg;
            Dictionary<string, object> d = new Dictionary<string, object>();
            d["id"] = id; d["error"] = e;
            return Js.Serialize(d);
        }

        private static string Brief(object result)
        {
            Dictionary<string, object> d = result as Dictionary<string, object>;
            if (d != null && d.ContainsKey("status")) return "status=" + d["status"];
            if (d != null && d.ContainsKey("planId")) return "planId=" + d["planId"];
            return "ok";
        }

        private static void Audit(string client, string method, string what)
        {
            try
            {
                if (string.IsNullOrEmpty(_dir)) return;
                File.AppendAllText(Path.Combine(_dir, "audit.log"),
                    DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + " | " + client + " | " + method + " | " + what + "\n", new UTF8Encoding(false));
            }
            catch (System.Exception) { }
        }
    }
}
