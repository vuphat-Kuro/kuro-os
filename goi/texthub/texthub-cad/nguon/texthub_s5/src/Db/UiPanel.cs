// PKTTC TextHub - Ui: noi dung bang PKTEXTUI (WinForms). Chi goi lai lop Db (Ops, PlanBuilder, FontReporter...). C# 5.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Text;
using System.Windows.Forms;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Pkttc.Text.Core;
using AcApp = Autodesk.AutoCAD.ApplicationServices.Core.Application;
using GFont = System.Drawing.Font;

namespace Pkttc.Text.Db
{
    public sealed class UiPanel : UserControl
    {
        // Font da thu bang in PDF tren AutoCAD 2020: ve du 134 chu Viet. Arial, Tahoma, Verdana, Times (thuong) KHONG ve duoc U+1EA0..U+1EF9.
        private static readonly string[] TestedFonts = new string[] { "segoe ui", "calibri", "arial unicode ms" };
        private static readonly string[] TestedFonts2 = new string[] { "Segoe UI", "Calibri", "Arial Unicode MS" };
        private static readonly string[] BadFonts = new string[] { "arial", "tahoma", "verdana", "times new roman" };

        private ScanResult _scan;
        private Plan _plan;
        private List<FontUse> _fonts;
        private readonly Dictionary<string, TextItem> _byHandle = new Dictionary<string, TextItem>();
        private readonly Dictionary<string, GFont> _fontCache = new Dictionary<string, GFont>(StringComparer.OrdinalIgnoreCase);
        private HashSet<string> _installed;

        private Label _lblDoc, _lblStatus;
        private TabControl _tabs;

        // Quet
        private Button _btnScan;
        private ComboBox _cbFilter;
        private Label _lblScanSum;
        private ListView _lvScan;
        // Doi chu
        private ComboBox _cbFont, _cbShx;
        private Label _lblFontWarn, _lblPlanSum;
        private CheckBox _chkWidth;
        private Button _btnSrc, _btnReset, _btnInstall;
        private Label _lblInstall;
        private DataGridView _gridSrc;
        private DataGridViewComboBoxColumn _colTarget;
        private List<string> _targetFonts;
        private Button _btnPlan, _btnAll, _btnNone, _btnApply;
        private DataGridView _grid;
        private DataGridViewTextBoxColumn _colPrev;
        // Font
        private Button _btnFonts, _btnSub, _btnPurge;
        private ListView _lvFonts;
        // Kho font
        private Label _lblStore;
        private Button _btnOpenStore, _btnSaveScript;
        // Tro ly
        private Label _lblBridge;
        private Button _btnBridgeOn, _btnBridgeOff, _btnLog;
        private TextBox _txtLog;

        public UiPanel()
        {
            Dock = DockStyle.Fill;
            Font = new GFont("Segoe UI", 9f);
            BuildUi();
            AcApp.DocumentManager.DocumentActivated += delegate { OnDocChanged(); };
            OnDocChanged();
        }

        public void OnShown()
        {
            OnDocChanged();
            RefreshStore();
            RefreshBridge();
        }

        // ================================================================== dung giao dien
        private void BuildUi()
        {
            _lblDoc = new Label(); _lblDoc.Dock = DockStyle.Top; _lblDoc.Height = 22; _lblDoc.Font = new GFont(Font, FontStyle.Bold); _lblDoc.TextAlign = ContentAlignment.MiddleLeft;
            _lblStatus = new Label(); _lblStatus.Dock = DockStyle.Bottom; _lblStatus.Height = 44; _lblStatus.BorderStyle = BorderStyle.FixedSingle; _lblStatus.Padding = new Padding(4);
            _tabs = new TabControl(); _tabs.Dock = DockStyle.Fill;
            _tabs.TabPages.Add(BuildScanTab());
            _tabs.TabPages.Add(BuildConvertTab());
            _tabs.TabPages.Add(BuildFontTab());
            _tabs.TabPages.Add(BuildStoreTab());
            _tabs.TabPages.Add(BuildBridgeTab());
            Controls.Add(_tabs);
            Controls.Add(_lblStatus);
            Controls.Add(_lblDoc);
            _tabs.SelectedIndexChanged += delegate { if (_tabs.SelectedIndex == 3) RefreshStore(); if (_tabs.SelectedIndex == 4) RefreshBridge(); };
        }

        private static Button MakeButton(string text, int w)
        {
            Button b = new Button(); b.Text = text; b.Width = w; b.Height = 28; b.Margin = new Padding(2, 3, 2, 3); b.UseVisualStyleBackColor = true;
            return b;
        }

        private TabPage BuildScanTab()
        {
            TabPage p = new TabPage("Quét");
            FlowLayoutPanel top = new FlowLayoutPanel(); top.Dock = DockStyle.Top; top.Height = 36; top.WrapContents = false;
            _btnScan = MakeButton("Quét bản vẽ", 100); _btnScan.Click += delegate { DoScan(); };
            Label l = new Label(); l.Text = "Hiện:"; l.AutoSize = true; l.Margin = new Padding(8, 9, 2, 0);
            _cbFilter = new ComboBox(); _cbFilter.DropDownStyle = ComboBoxStyle.DropDownList; _cbFilter.Width = 190; _cbFilter.Margin = new Padding(2, 5, 2, 0);
            _cbFilter.Items.AddRange(new object[] { "Cần đổi (TCVN3, VNI)", "Có cờ lỗi", "Tất cả", "Unicode", "ASCII" });
            _cbFilter.SelectedIndex = 0; _cbFilter.SelectedIndexChanged += delegate { FillScanList(); };
            top.Controls.Add(_btnScan); top.Controls.Add(l); top.Controls.Add(_cbFilter);
            _lblScanSum = new Label(); _lblScanSum.Dock = DockStyle.Top; _lblScanSum.Height = 54; _lblScanSum.Text = "Bấm \"Quét bản vẽ\" để đếm chữ theo bảng mã.";
            _lvScan = new ListView(); _lvScan.Dock = DockStyle.Fill; _lvScan.View = View.Details; _lvScan.FullRowSelect = true; _lvScan.GridLines = true; _lvScan.HideSelection = false;
            _lvScan.Columns.Add("Mã", 60); _lvScan.Columns.Add("Loại", 70); _lvScan.Columns.Add("Vị trí", 90); _lvScan.Columns.Add("Style", 90); _lvScan.Columns.Add("Bảng mã", 70); _lvScan.Columns.Add("Cờ", 80); _lvScan.Columns.Add("Chữ", 220);
            _lvScan.DoubleClick += delegate { ZoomToSelected(); };
            p.Controls.Add(_lvScan); p.Controls.Add(_lblScanSum); p.Controls.Add(top);
            return p;
        }

        private TabPage BuildConvertTab()
        {
            TabPage p = new TabPage("Đổi chữ");

            // ---- phan tren: font nguon trong ban ve -> font dich cho tung loai
            Label l0 = new Label(); l0.Text = "1. Font nguồn trong bản vẽ và font đích cho từng loại:"; l0.Dock = DockStyle.Top; l0.Height = 20; l0.Font = new GFont(Font, FontStyle.Bold);
            FlowLayoutPanel o1 = new FlowLayoutPanel(); o1.Dock = DockStyle.Top; o1.Height = 36; o1.WrapContents = false;
            _btnSrc = MakeButton("Quét font nguồn", 120); _btnSrc.Click += delegate { DoSrcScan(); };
            _btnReset = MakeButton("Đặt lại theo mặc định", 150); _btnReset.Click += delegate { ResetDefaults(); };
            _btnInstall = MakeButton("Cài font đích thiếu từ kho", 190); _btnInstall.Click += delegate { DoInstall(); }; _btnInstall.Visible = false;
            o1.Controls.Add(_btnSrc); o1.Controls.Add(_btnReset); o1.Controls.Add(_btnInstall);
            FlowLayoutPanel o1b = new FlowLayoutPanel(); o1b.Dock = DockStyle.Top; o1b.Height = 36; o1b.WrapContents = false;
            Label l1 = new Label(); l1.Text = "Nguồn TrueType →"; l1.AutoSize = true; l1.Margin = new Padding(2, 9, 2, 0);
            _cbFont = new ComboBox(); _cbFont.Width = 150; _cbFont.Margin = new Padding(2, 5, 2, 0);
            _cbFont.Items.AddRange(GetTargetFonts().ToArray());
            _cbFont.Text = new PlanOptions().TargetFont;
            _cbFont.TextChanged += delegate { UpdateFontWarn(); };
            Label l1b = new Label(); l1b.Text = "Nguồn SHX →"; l1b.AutoSize = true; l1b.Margin = new Padding(8, 9, 2, 0);
            _cbShx = new ComboBox(); _cbShx.Width = 130; _cbShx.Margin = new Padding(2, 5, 2, 0);
            _cbShx.Items.AddRange(GetTargetFonts().ToArray());
            _cbShx.Text = new PlanOptions().TargetShxFont;
            _cbShx.TextChanged += delegate { UpdateFontWarn(); };
            o1b.Controls.Add(l1); o1b.Controls.Add(_cbFont); o1b.Controls.Add(l1b); o1b.Controls.Add(_cbShx);
            _lblFontWarn = new Label(); _lblFontWarn.Dock = DockStyle.Top; _lblFontWarn.Height = 36;
            _lblInstall = new Label(); _lblInstall.Dock = DockStyle.Top; _lblInstall.Height = 34;

            _gridSrc = new DataGridView(); _gridSrc.Dock = DockStyle.Fill; _gridSrc.AllowUserToAddRows = false; _gridSrc.AllowUserToDeleteRows = false; _gridSrc.RowHeadersVisible = false;
            _gridSrc.BackgroundColor = Color.White; _gridSrc.AllowUserToResizeRows = false; _gridSrc.EditMode = DataGridViewEditMode.EditOnEnter;
            _gridSrc.SelectionMode = DataGridViewSelectionMode.CellSelect;
            DataGridViewTextBoxColumn c0 = new DataGridViewTextBoxColumn(); c0.HeaderText = "Font nguồn"; c0.Width = 130; c0.ReadOnly = true; _gridSrc.Columns.Add(c0);
            DataGridViewTextBoxColumn c1 = new DataGridViewTextBoxColumn(); c1.HeaderText = "Loại"; c1.Width = 40; c1.ReadOnly = true; _gridSrc.Columns.Add(c1);
            DataGridViewTextBoxColumn c2 = new DataGridViewTextBoxColumn(); c2.HeaderText = "Mục"; c2.Width = 42; c2.ReadOnly = true; _gridSrc.Columns.Add(c2);
            _colTarget = new DataGridViewComboBoxColumn(); _colTarget.HeaderText = "Font đích (chọn)"; _colTarget.Width = 150; _colTarget.FlatStyle = FlatStyle.Flat;
            _colTarget.Items.AddRange(GetTargetFonts().ToArray());
            _gridSrc.Columns.Add(_colTarget);
            DataGridViewTextBoxColumn c4 = new DataGridViewTextBoxColumn(); c4.HeaderText = "Ghi chú về font đích"; c4.Width = 330; c4.ReadOnly = true; _gridSrc.Columns.Add(c4);
            _gridSrc.CurrentCellDirtyStateChanged += delegate { if (_gridSrc.IsCurrentCellDirty) _gridSrc.CommitEdit(DataGridViewDataErrorContexts.Commit); };
            _gridSrc.CellValueChanged += delegate(object s, DataGridViewCellEventArgs e)
            {
                if (e.RowIndex >= 0 && e.ColumnIndex == 3) _gridSrc.Rows[e.RowIndex].Cells[4].Value = NoteFor(Convert.ToString(_gridSrc.Rows[e.RowIndex].Cells[3].Value));
            };
            _gridSrc.DataError += delegate(object s, DataGridViewDataErrorEventArgs e) { e.ThrowException = false; };

            // ---- phan duoi: tuy chon, ke hoach, xem truoc
            FlowLayoutPanel o2 = new FlowLayoutPanel(); o2.Dock = DockStyle.Top; o2.Height = 36; o2.WrapContents = false;
            _chkWidth = new CheckBox(); _chkWidth.Text = "Giữ chiều dài chuỗi (chỉnh hệ số rộng)"; _chkWidth.Checked = true; _chkWidth.AutoSize = true; _chkWidth.Margin = new Padding(4, 8, 6, 0);
            _btnPlan = MakeButton("2. Lập kế hoạch", 110); _btnPlan.Click += delegate { DoPlan(); };
            o2.Controls.Add(_chkWidth); o2.Controls.Add(_btnPlan);
            _lblPlanSum = new Label(); _lblPlanSum.Dock = DockStyle.Top; _lblPlanSum.Height = 36; _lblPlanSum.Text = "Bấm \"Quét font nguồn\", chọn font đích cho từng loại, rồi \"Lập kế hoạch\". Bản vẽ chưa bị sửa cho đến khi bấm \"Áp dụng\".";

            _grid = new DataGridView(); _grid.Dock = DockStyle.Fill; _grid.AllowUserToAddRows = false; _grid.AllowUserToDeleteRows = false; _grid.RowHeadersVisible = false;
            _grid.SelectionMode = DataGridViewSelectionMode.FullRowSelect; _grid.RowTemplate.Height = 50; _grid.BackgroundColor = Color.White; _grid.AllowUserToResizeRows = false;
            DataGridViewCheckBoxColumn cc = new DataGridViewCheckBoxColumn(); cc.HeaderText = "Đổi"; cc.Width = 36;
            _grid.Columns.Add(cc);
            AddGridCol("Mã", 56, true); AddGridCol("Loại", 60, true); AddGridCol("Vị trí", 80, true);
            _colPrev = new DataGridViewTextBoxColumn(); _colPrev.HeaderText = "Xem trước (cũ / mới)"; _colPrev.Width = 270; _colPrev.ReadOnly = true; _grid.Columns.Add(_colPrev);
            AddGridCol("Style (font đích)", 150, true);
            _grid.CellPainting += GridCellPainting;
            _grid.DoubleClick += delegate { ZoomToGridRow(); };

            FlowLayoutPanel bot = new FlowLayoutPanel(); bot.Dock = DockStyle.Bottom; bot.Height = 38; bot.WrapContents = false;
            _btnAll = MakeButton("Chọn tất cả", 90); _btnAll.Click += delegate { SetAllChecked(true); };
            _btnNone = MakeButton("Bỏ chọn", 80); _btnNone.Click += delegate { SetAllChecked(false); };
            _btnApply = MakeButton("3. Áp dụng mục đã chọn", 170); _btnApply.Click += delegate { DoApply(); };
            bot.Controls.Add(_btnAll); bot.Controls.Add(_btnNone); bot.Controls.Add(_btnApply);

            SplitContainer sc = new SplitContainer(); sc.Dock = DockStyle.Fill; sc.Orientation = Orientation.Horizontal; sc.SplitterDistance = 270;
            sc.Panel1.Controls.Add(_gridSrc); sc.Panel1.Controls.Add(_lblInstall); sc.Panel1.Controls.Add(_lblFontWarn); sc.Panel1.Controls.Add(o1b); sc.Panel1.Controls.Add(o1); sc.Panel1.Controls.Add(l0);
            sc.Panel2.Controls.Add(_grid); sc.Panel2.Controls.Add(bot); sc.Panel2.Controls.Add(_lblPlanSum); sc.Panel2.Controls.Add(o2);
            p.Controls.Add(sc);
            UpdateFontWarn();
            return p;
        }

        private void AddGridCol(string head, int w, bool ro)
        {
            DataGridViewTextBoxColumn c = new DataGridViewTextBoxColumn(); c.HeaderText = head; c.Width = w; c.ReadOnly = ro; _grid.Columns.Add(c);
        }

        // ================================================================== danh sach font dich va ghi chu
        private bool IsInstalledFont(string name)
        {
            if (_installed == null)
            {
                _installed = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                foreach (FontFamily ff in FontFamily.Families) _installed.Add(ff.Name);
            }
            return _installed.Contains(name);
        }

        // Font Unicode anh Nghia dung nhieu nhat: ghim dau danh sach font dich (ke ca khi chua cai tren may).
        private static readonly string[] PinnedFonts = new string[] { "Arial Unicode MS", "uv-abc.shx", "3T-Unicode.shx" };

        /// <summary>Font dich co the chon: 3 font ghim dau, roi TrueType da cai (tru font TCVN3/VNI cu), roi SHX Unicode (kho font, thu muc Fonts cua AutoCAD, Style dang dung trong ban ve).</summary>
        private List<string> GetTargetFonts()
        {
            if (_targetFonts != null) return _targetFonts;
            List<string> r = new List<string>();
            HashSet<string> seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (string f in PinnedFonts) if (seen.Add(f)) r.Add(f);
            foreach (string f in TestedFonts2)
                if (IsInstalledFont(f) && seen.Add(f)) r.Add(f);
            List<string> ttf = new List<string>();
            foreach (FontFamily ff in FontFamily.Families)
            {
                string n = ff.Name;
                if (n.StartsWith("@") || FontRules.IsLegacy(n)) continue;
                if (seen.Add(n)) ttf.Add(n);
            }
            ttf.Sort(StringComparer.OrdinalIgnoreCase);
            r.AddRange(ttf);

            List<string> shx = new List<string>();
            HashSet<string> seenShx = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (string f in PinnedFonts) seenShx.Add(f);
            try
            {
                foreach (string pth in FontStore.Load().FilesByExt(".shx"))
                    if (ShxHeader.Kind(pth) == "unifont" && seenShx.Add(Path.GetFileName(pth))) shx.Add(Path.GetFileName(pth));
            }
            catch (System.Exception) { }
            try
            {
                string exe = Process.GetCurrentProcess().MainModule.FileName;
                string dir = Path.Combine(Path.GetDirectoryName(exe), "Fonts");
                if (Directory.Exists(dir))
                    foreach (string pth in Directory.GetFiles(dir, "*.shx"))
                        if (ShxHeader.Kind(pth) == "unifont" && seenShx.Add(Path.GetFileName(pth))) shx.Add(Path.GetFileName(pth));
            }
            catch (System.Exception) { }
            if (_scan != null)
                foreach (StyleInfo s in _scan.Styles)
                    if (s.IsShx && s.ShxKind == "unifont" && !string.IsNullOrEmpty(s.FileName) && seenShx.Add(s.FileName)) shx.Add(s.FileName);
            shx.Sort(StringComparer.OrdinalIgnoreCase);
            r.AddRange(shx);
            _targetFonts = r;
            return r;
        }

        private void FillTargetCombos()
        {
            string curT = _cbFont.Text, curS = _cbShx.Text;
            _targetFonts = null;
            List<string> all = GetTargetFonts();
            _cbFont.Items.Clear(); _cbFont.Items.AddRange(all.ToArray()); _cbFont.Text = curT;
            _cbShx.Items.Clear(); _cbShx.Items.AddRange(all.ToArray()); _cbShx.Text = curS;
            _colTarget.Items.Clear(); _colTarget.Items.AddRange(all.ToArray());
        }

        /// <summary>Font dich mac dinh cho mot font nguon: nguon SHX -> o "Nguon SHX", nguon TrueType -> o "Nguon TTF".</summary>
        private string DefaultFor(string srcFont)
        {
            PlanOptions d = new PlanOptions();
            string v = PlanBuilder.IsShx(srcFont) ? _cbShx.Text.Trim() : _cbFont.Text.Trim();
            return v.Length > 0 ? v : (PlanBuilder.IsShx(srcFont) ? d.TargetShxFont : d.TargetFont);
        }

        private string NoteFor(string font)
        {
            string f = (font ?? "").Trim();
            if (f.Length == 0) return "";
            string l = f.ToLowerInvariant();
            bool shx = f.EndsWith(".shx", StringComparison.OrdinalIgnoreCase);
            string n;
            if (shx) n = "SHX Unicode: vẽ đủ chữ Việt, nét mảnh, không có kiểu đậm hoặc nghiêng.";
            else if (Array.IndexOf(TestedFonts2, f) >= 0 || Array.IndexOf(TestedFonts, l) >= 0) n = "Đã in thử bằng AutoCAD 2020: vẽ đủ 134 chữ Việt.";
            else if (Array.IndexOf(BadFonts, l) >= 0) n = "LƯU Ý: em in thử bằng AutoCAD 2020 trên máy này, kiểu thường của font này không vẽ Ả Ế ọ Ố Ỡ Ơ Ư (hiện ô trống).";
            else n = "Chưa in thử với AutoCAD: nên in thử vài chữ có dấu thanh trên mũ (Ẩ Ế Ố) trước khi dùng.";
            if (!shx && !IsInstalledFont(f)) n += " CHƯA CÀI trên máy này.";
            return n;
        }

        private void UpdateFontWarn()
        {
            string a = NoteFor(_cbFont.Text), b = NoteFor(_cbShx.Text);
            _lblFontWarn.Text = "Nguồn TrueType → " + a + Environment.NewLine + "Nguồn SHX → " + b;
            string all = a + b;
            _lblFontWarn.ForeColor = all.Contains("LƯU Ý") ? Color.Firebrick : (all.Contains("CHƯA CÀI") || all.Contains("Chưa in thử") ? Color.DarkOrange : Color.DarkGreen);
            RefreshInstall();
        }

        /// <summary>Font dich dang chon ma may chua co nhung kho font co: co the cai tu kho.</summary>
        private List<FontUse> MissingTargets()
        {
            List<FontUse> r = new List<FontUse>();
            List<string> want = new List<string>();
            want.Add(_cbFont.Text.Trim()); want.Add(_cbShx.Text.Trim());
            foreach (DataGridViewRow row in _gridSrc.Rows) want.Add(Convert.ToString(row.Cells[3].Value));
            HashSet<string> seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            FontStore st = FontStore.Load();
            Document doc = Doc();
            FontEnv env = doc != null ? new FontEnv(doc.Database) : null;
            foreach (string f in want)
            {
                if (string.IsNullOrWhiteSpace(f) || !seen.Add(f.Trim())) continue;
                string name = f.Trim();
                bool shx = PlanBuilder.IsShx(name);
                bool ok = shx ? (env != null && env.Available(name)) : IsInstalledFont(name);
                if (ok) continue;
                string path = st.Find(name);
                if (path == null) continue;
                FontUse u = new FontUse(); u.Name = name; u.IsShx = shx; u.Status = "inStore"; u.StorePath = path;
                r.Add(u);
            }
            return r;
        }

        private void RefreshInstall()
        {
            if (_lblInstall == null || _btnInstall == null) return;
            List<FontUse> m;
            try { m = MissingTargets(); } catch (System.Exception) { m = new List<FontUse>(); }
            _btnInstall.Visible = m.Count > 0;
            if (m.Count == 0) { _lblInstall.Text = ""; return; }
            List<string> names = new List<string>();
            foreach (FontUse u in m) names.Add(u.Name);
            _lblInstall.Text = "Font đích chưa cài trên máy, có trong kho: " + string.Join(", ", names.ToArray()) + ".";
            _lblInstall.ForeColor = Color.DarkOrange;
        }

        private void DoInstall()
        {
            List<FontUse> m = MissingTargets();
            if (m.Count == 0) { Status("Không có font đích nào cần cài."); RefreshInstall(); return; }
            StringBuilder sb = new StringBuilder();
            foreach (FontUse u in m) sb.AppendLine("  " + u.Name + (u.IsShx ? " (SHX)" : " (TrueType)") + "  <-  " + u.StorePath);
            DialogResult dr = MessageBox.Show("Cài các font đích còn thiếu từ kho font?\n\n" + sb
                + "\nChép vào %APPDATA%\\PKTTC\\Fonts. Font TrueType được cài cho người dùng hiện tại (ghi registry HKCU của riêng bạn). Font SHX: thêm thư mục đó vào Support File Search Path của AutoCAD.\nCần mở lại AutoCAD để nhận font mới. Font Arial Unicode MS thuộc Microsoft Office: chỉ cài trên máy có giấy phép.",
                "PKTTC TextHub", MessageBoxButtons.YesNo, MessageBoxIcon.Question, MessageBoxDefaultButton.Button2);
            if (dr != DialogResult.Yes) { Status("Đã hủy, không cài font nào."); return; }
            try
            {
                string script = Path.Combine(Path.GetTempPath(), "PKTTC_cai_font_dich.ps1");
                File.WriteAllText(script, FontReporter.InstallScript(m), new UTF8Encoding(true));
                ProcessStartInfo psi = new ProcessStartInfo("powershell.exe", "-NoProfile -ExecutionPolicy Bypass -File \"" + script + "\" -Apply -RegisterFonts");
                psi.UseShellExecute = false; psi.CreateNoWindow = true; psi.RedirectStandardOutput = true; psi.RedirectStandardError = true;
                Cursor = Cursors.WaitCursor;
                string outp;
                using (Process p = Process.Start(psi))
                {
                    outp = p.StandardOutput.ReadToEnd() + p.StandardError.ReadToEnd();
                    p.WaitForExit(120000);
                }
                Cursor = Cursors.Default;
                Status("Đã chạy cài font. " + outp.Replace("\r", " ").Replace("\n", " ").Trim() + " Mở lại AutoCAD để nhận font mới.");
            }
            catch (System.Exception ex) { Cursor = Cursors.Default; Status("Không cài được font: " + ex.Message); }
            _installed = null; _fontCache.Clear();
            RefreshInstall();
        }

        /// <summary>Dat lai font dich cua moi dong theo mac dinh: nguon TrueType -> o "Nguon TrueType", nguon SHX -> o "Nguon SHX".</summary>
        private void ResetDefaults()
        {
            foreach (DataGridViewRow r in _gridSrc.Rows)
            {
                string src = Convert.ToString(r.Cells[0].Value);
                r.Cells[3].Value = DefaultFor(src == "(không rõ)" ? "" : src);
            }
            RefreshInstall();
        }

        /// <summary>Liet ke font nguon (font cua cac chu TCVN3/VNI can doi), moi dong chon duoc font dich; mac dinh theo loai font nguon.</summary>
        private void DoSrcScan()
        {
            if (!EnsureScan(true)) return;
            FillTargetCombos();
            Dictionary<string, int> cnt = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
            foreach (TextItem t in _scan.Items)
                if (t.Charset == "Tcvn3" || t.Charset == "Vni") Inc(cnt, string.IsNullOrEmpty(t.Font) ? "(không rõ)" : t.Font);
            List<KeyValuePair<string, int>> rows = new List<KeyValuePair<string, int>>(cnt);
            rows.Sort(delegate(KeyValuePair<string, int> a, KeyValuePair<string, int> b) { return b.Value.CompareTo(a.Value); });
            foreach (string f in new string[] { _cbFont.Text.Trim(), _cbShx.Text.Trim() })
                if (f.Length > 0 && !_colTarget.Items.Contains(f)) _colTarget.Items.Add(f);
            _gridSrc.Rows.Clear();
            foreach (KeyValuePair<string, int> kv in rows)
            {
                string def = DefaultFor(kv.Key == "(không rõ)" ? "" : kv.Key);
                _gridSrc.Rows.Add(kv.Key, PlanBuilder.IsShx(kv.Key) ? "SHX" : "TTF", kv.Value, def, NoteFor(def));
            }
            _lblPlanSum.Text = rows.Count + " font nguồn có chữ cần đổi. Font đích đã chọn sẵn theo loại (TrueType → " + _cbFont.Text.Trim() + ", SHX → " + _cbShx.Text.Trim() + "); đổi riêng từng dòng nếu cần, rồi bấm \"Lập kế hoạch\".";
            RefreshInstall();
            Status("Đã quét font nguồn. Bản vẽ chưa bị sửa.");
        }

        private void DoPlan()
        {
            if (_gridSrc.Rows.Count == 0) { DoSrcScan(); if (_gridSrc.Rows.Count == 0) { Status("Không có chữ TCVN3 hay VNI nào cần đổi."); return; } }
            if (!EnsureScan(true)) return;
            PlanOptions o = new PlanOptions();
            if (_cbFont.Text.Trim().Length > 0) o.TargetFont = _cbFont.Text.Trim();
            if (_cbShx.Text.Trim().Length > 0) o.TargetShxFont = _cbShx.Text.Trim();
            foreach (DataGridViewRow r in _gridSrc.Rows)
            {
                string src = Convert.ToString(r.Cells[0].Value), dst = Convert.ToString(r.Cells[3].Value);
                if (!string.IsNullOrWhiteSpace(src) && src != "(không rõ)" && !string.IsNullOrWhiteSpace(dst)) o.FontMap[src] = dst.Trim();
            }
            o.KeepWidth = _chkWidth.Checked;
            _plan = PlanBuilder.Build(_scan, o);
            _grid.Rows.Clear();
            Dictionary<string, int> byFont = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
            foreach (PlanItem it in _plan.Items)
            {
                Inc(byFont, it.NewFont);
                int r = _grid.Rows.Add(true, it.Handle, it.Kind, it.OwnerKind + " " + it.Owner, "", it.OldStyle + " > " + it.NewStyle + " (" + it.NewFont + ")");
                _grid.Rows[r].Tag = it;
            }
            _lblPlanSum.Text = _plan.Items.Count + " mục sẽ đổi: " + (byFont.Count == 0 ? "không" : Commands.Fmt(byFont)) + ". Bỏ qua: " + Commands.Fmt(_plan.Skipped) + ".";
            Status(_plan.Items.Count == 0 ? "Không có mục nào cần đổi." : "Kế hoạch đã lập, bản vẽ chưa bị sửa. Xem cột cũ/mới rồi bỏ chọn mục không muốn đổi.");
        }

        private TabPage BuildFontTab()
        {
            TabPage p = new TabPage("Font");
            FlowLayoutPanel top = new FlowLayoutPanel(); top.Dock = DockStyle.Top; top.Height = 36; top.WrapContents = false;
            _btnFonts = MakeButton("Báo cáo font", 100); _btnFonts.Click += delegate { DoFonts(); };
            _btnSub = MakeButton("Thay font thiếu", 110); _btnSub.Click += delegate { DoSub(); };
            _btnPurge = MakeButton("Dọn style không dùng", 150); _btnPurge.Click += delegate { DoPurge(); };
            top.Controls.Add(_btnFonts); top.Controls.Add(_btnSub); top.Controls.Add(_btnPurge);
            _lvFonts = new ListView(); _lvFonts.Dock = DockStyle.Fill; _lvFonts.View = View.Details; _lvFonts.FullRowSelect = true; _lvFonts.GridLines = true;
            _lvFonts.Columns.Add("Font", 150); _lvFonts.Columns.Add("Loại", 55); _lvFonts.Columns.Add("Trạng thái", 80); _lvFonts.Columns.Add("Dùng", 50); _lvFonts.Columns.Add("Gợi ý thay", 140);
            p.Controls.Add(_lvFonts); p.Controls.Add(top);
            return p;
        }

        private TabPage BuildStoreTab()
        {
            TabPage p = new TabPage("Kho font");
            _lblStore = new Label(); _lblStore.Dock = DockStyle.Top; _lblStore.Height = 120;
            FlowLayoutPanel top = new FlowLayoutPanel(); top.Dock = DockStyle.Top; top.Height = 38; top.WrapContents = false;
            _btnOpenStore = MakeButton("Mở thư mục kho", 120); _btnOpenStore.Click += delegate { OpenStore(); };
            _btnSaveScript = MakeButton("Lưu script cài font thiếu...", 190); _btnSaveScript.Click += delegate { SaveInstallScript(); };
            top.Controls.Add(_btnOpenStore); top.Controls.Add(_btnSaveScript);
            Label note = new Label(); note.Dock = DockStyle.Fill; note.Padding = new Padding(4);
            note.Text = "Kho chỉ để đối chiếu và lấy font khi bản vẽ thiếu. TextHub không tự cài font và không ghi registry: script cài chỉ chạy khi anh tự chạy với tham số -Apply.";
            p.Controls.Add(note); p.Controls.Add(top); p.Controls.Add(_lblStore);
            return p;
        }

        private TabPage BuildBridgeTab()
        {
            TabPage p = new TabPage("Trợ lý");
            _lblBridge = new Label(); _lblBridge.Dock = DockStyle.Top; _lblBridge.Height = 46; _lblBridge.Font = new GFont(Font, FontStyle.Bold);
            FlowLayoutPanel top = new FlowLayoutPanel(); top.Dock = DockStyle.Top; top.Height = 38; top.WrapContents = false;
            _btnBridgeOn = MakeButton("Mở cổng Kuro", 110); _btnBridgeOn.Click += delegate { DoBridgeOn(); };
            _btnBridgeOff = MakeButton("Đóng cổng", 90); _btnBridgeOff.Click += delegate { DoBridgeOff(); };
            _btnLog = MakeButton("Làm mới nhật ký", 120); _btnLog.Click += delegate { RefreshBridge(); };
            top.Controls.Add(_btnBridgeOn); top.Controls.Add(_btnBridgeOff); top.Controls.Add(_btnLog);
            _txtLog = new TextBox(); _txtLog.Dock = DockStyle.Fill; _txtLog.Multiline = true; _txtLog.ReadOnly = true; _txtLog.ScrollBars = ScrollBars.Both; _txtLog.WordWrap = false; _txtLog.Font = new GFont("Consolas", 8.5f);
            p.Controls.Add(_txtLog); p.Controls.Add(top); p.Controls.Add(_lblBridge);
            return p;
        }

        // ================================================================== chung
        private void Status(string s) { _lblStatus.Text = s; UiLog.Write("trang thai: " + s.Replace(Environment.NewLine, " ").Replace("\n", " ")); }

        private static Document Doc() { return AcApp.DocumentManager.MdiActiveDocument; }

        private void OnDocChanged()
        {
            Document d = Doc();
            _lblDoc.Text = d == null ? "Chưa có bản vẽ" : "Bản vẽ: " + Path.GetFileName(d.Name);
            _scan = null; _plan = null; _fonts = null; _byHandle.Clear();
            if (_lvScan != null) _lvScan.Items.Clear();
            if (_grid != null) _grid.Rows.Clear();
            if (_gridSrc != null) _gridSrc.Rows.Clear();
            if (_lblPlanSum != null) _lblPlanSum.Text = "Bấm \"Quét font nguồn\", chọn font đích cho từng loại, rồi \"Lập kế hoạch\". Bản vẽ chưa bị sửa cho đến khi bấm \"Áp dụng\".";
            if (_lvFonts != null) _lvFonts.Items.Clear();
            if (_lblScanSum != null) _lblScanSum.Text = "Bấm \"Quét bản vẽ\" để đếm chữ theo bảng mã.";
            Status("Sẵn sàng. Bảng chỉ đọc cho đến khi anh bấm một nút ghi và xác nhận.");
        }

        private bool EnsureScan(bool force)
        {
            Document doc = Doc();
            if (doc == null) { Status("Chưa có bản vẽ nào đang mở."); return false; }
            if (_scan != null && !force) return true;
            Cursor = Cursors.WaitCursor;
            try
            {
                using (doc.LockDocument()) { _scan = Ops.Scan(doc); }
            }
            catch (System.Exception ex) { Status("Lỗi khi quét: " + ex.Message); return false; }
            finally { Cursor = Cursors.Default; }
            _byHandle.Clear();
            foreach (TextItem t in _scan.Items) _byHandle[t.Handle] = t;
            return true;
        }

        // ================================================================== tab Quet
        private void DoScan()
        {
            if (!EnsureScan(true)) return;
            Dictionary<string, int> byCs = new Dictionary<string, int>();
            Dictionary<string, int> byFlag = new Dictionary<string, int>();
            foreach (TextItem t in _scan.Items)
            {
                Inc(byCs, t.Charset);
                foreach (string f in t.Flags) Inc(byFlag, f);
            }
            _lblScanSum.Text = _scan.Items.Count + " mục chữ trong " + _scan.ElapsedMs + " ms, lỗi " + _scan.Errors + "\r\nBảng mã: " + Commands.Fmt(byCs) + "\r\nCờ: " + (byFlag.Count == 0 ? "không" : Commands.Fmt(byFlag));
            FillScanList();
            Status("Đã quét xong. Bản vẽ chưa bị sửa.");
        }

        private static void Inc(Dictionary<string, int> d, string k)
        {
            int v; d.TryGetValue(k, out v); d[k] = v + 1;
        }

        private void FillScanList()
        {
            _lvScan.BeginUpdate();
            _lvScan.Items.Clear();
            if (_scan != null)
            {
                int shown = 0, idx = _cbFilter.SelectedIndex;
                foreach (TextItem t in _scan.Items)
                {
                    bool ok;
                    if (idx == 0) ok = t.Charset == "Tcvn3" || t.Charset == "Vni";
                    else if (idx == 1) ok = t.Flags.Count > 0;
                    else if (idx == 2) ok = true;
                    else if (idx == 3) ok = t.Charset == "Unicode";
                    else ok = t.Charset == "Ascii";
                    if (!ok) continue;
                    if (++shown > 5000) break;
                    ListViewItem li = new ListViewItem(t.Handle);
                    li.SubItems.Add(t.Kind); li.SubItems.Add(t.OwnerKind + " " + t.Owner); li.SubItems.Add(t.Style); li.SubItems.Add(t.Charset);
                    li.SubItems.Add(string.Join(",", t.Flags.ToArray())); li.SubItems.Add(string.IsNullOrEmpty(t.Preview) ? t.Raw : t.Preview);
                    li.Tag = t;
                    _lvScan.Items.Add(li);
                }
            }
            _lvScan.EndUpdate();
        }

        private void ZoomToSelected()
        {
            if (_lvScan.SelectedItems.Count == 0) return;
            TextItem t = _lvScan.SelectedItems[0].Tag as TextItem;
            if (t != null) ZoomTo(t);
        }

        private void ZoomToGridRow()
        {
            if (_grid.CurrentRow == null) return;
            PlanItem it = _grid.CurrentRow.Tag as PlanItem;
            TextItem t;
            if (it != null && _byHandle.TryGetValue(it.Handle, out t)) ZoomTo(t);
        }

        private void ZoomTo(TextItem t)
        {
            Document doc = Doc();
            if (doc == null) return;
            if (t.OwnerKind == "block") { Status("Mục " + t.Handle + " nằm trong định nghĩa block \"" + t.Owner + "\": không phóng tới được trực tiếp."); return; }
            try
            {
                ObjectId id;
                if (!doc.Database.TryGetObjectId(new Handle(Convert.ToInt64(t.Handle, 16)), out id) || id.IsNull) { Status("Không tìm thấy đối tượng " + t.Handle + "."); return; }
                doc.Editor.SetImpliedSelection(new ObjectId[] { id });
                doc.SendStringToExecute("_.ZOOM _O\n", true, false, false);
                Status("Đã chọn và phóng tới " + t.Kind + " " + t.Handle + ".");
            }
            catch (System.Exception ex) { Status("Không phóng tới được: " + ex.Message); }
        }

        // ================================================================== tab Doi chu


        private void SetAllChecked(bool v)
        {
            foreach (DataGridViewRow r in _grid.Rows) r.Cells[0].Value = v;
        }

        private static string Strip(string s)
        {
            if (s == null) return "";
            return s.Replace("%%U", "").Replace("%%u", "").Replace("%%O", "").Replace("%%o", "").Replace("%%C", "Ø").Replace("%%c", "Ø").Replace("%%D", "°").Replace("%%d", "°").Replace("%%P", "±").Replace("%%p", "±");
        }

        private GFont GetFont(string name)
        {
            if (string.IsNullOrEmpty(name) || name.EndsWith(".shx", StringComparison.OrdinalIgnoreCase)) return null;
            GFont f;
            if (_fontCache.TryGetValue(name, out f)) return f;
            if (_installed == null)
            {
                _installed = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                foreach (FontFamily ff in FontFamily.Families) _installed.Add(ff.Name);
            }
            f = null;
            if (_installed.Contains(name)) { try { f = new GFont(name, 14f, FontStyle.Regular, GraphicsUnit.Pixel); } catch (System.Exception) { f = null; } }
            _fontCache[name] = f;
            return f;
        }

        private void GridCellPainting(object sender, DataGridViewCellPaintingEventArgs e)
        {
            if (e.RowIndex < 0 || _colPrev == null || e.ColumnIndex != _colPrev.Index) return;
            e.Handled = true;
            e.PaintBackground(e.CellBounds, true);
            PlanItem it = _grid.Rows[e.RowIndex].Tag as PlanItem;
            if (it == null || _plan == null) return;
            TextItem ti;
            _byHandle.TryGetValue(it.Handle, out ti);
            string oldFont = ti != null ? ti.Font : "";
            GFont f1 = GetFont(oldFont);
            string newFont = it.NewFont.Length > 0 ? it.NewFont : _plan.Options.TargetFont;
            GFont f2 = GetFont(newFont);
            Graphics g = e.Graphics;
            g.SetClip(e.CellBounds);
            int x = e.CellBounds.X + 3, y = e.CellBounds.Y + 3;
            if (f1 != null) g.DrawString(Strip(it.OldRaw), f1, Brushes.Black, x, y);
            else g.DrawString("(font " + oldFont + ": không xem trước được)  " + Strip(it.OldRaw), _grid.Font, Brushes.Gray, x, y + 2);
            if (f2 != null) g.DrawString(Strip(it.NewText), f2, Brushes.DarkBlue, x, y + 24);
            else g.DrawString(Strip(it.NewText) + "   (font " + newFont + ": không xem trước được)", _grid.Font, Brushes.DarkBlue, x, y + 26);
            g.ResetClip();
        }

        private void DoApply()
        {
            if (_plan == null || _plan.Items.Count == 0) { Status("Chưa có kế hoạch. Bấm \"Lập kế hoạch\" trước."); return; }
            List<PlanItem> sel = new List<PlanItem>();
            foreach (DataGridViewRow r in _grid.Rows)
            {
                object v = r.Cells[0].Value;
                if (v != null && (bool)v && r.Tag is PlanItem) sel.Add((PlanItem)r.Tag);
            }
            if (sel.Count == 0) { Status("Chưa chọn mục nào."); return; }
            Document doc = Doc();
            if (doc == null) return;
            Dictionary<string, int> byFont = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
            foreach (PlanItem pi in sel) { int c; byFont.TryGetValue(pi.NewFont, out c); byFont[pi.NewFont] = c + 1; }
            DialogResult dr = MessageBox.Show("Đổi " + sel.Count + " mục chữ sang Unicode (font đích: " + Commands.Fmt(byFont) + ")?\n\nTextHub sao lưu bản vẽ vào thư mục _backup trước, đổi trong một bước và hoàn tác được bằng U. Bản vẽ chưa được lưu.",
                "PKTTC TextHub", MessageBoxButtons.YesNo, MessageBoxIcon.Question, MessageBoxDefaultButton.Button2);
            if (dr != DialogResult.Yes) { Status("Đã hủy, bản vẽ không đổi."); return; }

            Plan sub = new Plan();
            sub.PlanId = _plan.PlanId; sub.Drawing = _plan.Drawing; sub.CreatedAt = _plan.CreatedAt; sub.Options = _plan.Options; sub.Items = sel; sub.Skipped = _plan.Skipped;
            Status("Đang đổi " + sel.Count + " mục...");
            UiHost.Run(delegate
            {
                ApplyOutcome o = Ops.ApplyPlan(doc, sub);
                doc.Editor.WriteMessage(o.Message);
                if (o.Ok) Status("Đã đổi " + o.Count + " mục. Gõ U để hoàn tác một bước. Sao lưu: " + o.BackupPath + ". Bản vẽ chưa được lưu.");
                else Status("Không đổi được. " + o.Message.Trim());
                OnDocChanged();
            });
        }

        // ================================================================== tab Font
        private void DoFonts()
        {
            if (!EnsureScan(true)) return;
            Document doc = Doc();
            try { using (doc.LockDocument()) { _fonts = Ops.FontReport(doc, _scan); } }
            catch (System.Exception ex) { Status("Lỗi báo cáo font: " + ex.Message); return; }
            _lvFonts.BeginUpdate();
            _lvFonts.Items.Clear();
            int ok = 0, miss = 0;
            foreach (FontUse u in _fonts)
            {
                if (u.Status == "ok") ok++; else miss++;
                ListViewItem li = new ListViewItem(u.Name);
                li.SubItems.Add(u.IsShx ? "SHX" : "TTF"); li.SubItems.Add(u.Status); li.SubItems.Add(u.Count.ToString());
                li.SubItems.Add(u.Substitute.Length > 0 ? u.Substitute + " (" + u.SubstituteSource + ")" : "");
                if (u.Status != "ok") li.ForeColor = Color.Firebrick;
                _lvFonts.Items.Add(li);
            }
            _lvFonts.EndUpdate();
            Status(_fonts.Count + " font: " + ok + " có sẵn, " + miss + " thiếu hoặc chỉ có trong kho.");
        }

        private void DoSub()
        {
            if (_fonts == null) DoFonts();
            if (_fonts == null) return;
            List<SubItem> sub = StyleOps.BuildSubPlan(_scan, _fonts);
            if (sub.Count == 0) { Status("Không có Style nào cần thay font."); return; }
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < sub.Count && i < 10; i++) sb.AppendLine("  " + sub[i].Style + ": " + sub[i].OldFont + " > " + sub[i].NewFont);
            if (sub.Count > 10) sb.AppendLine("  ... và " + (sub.Count - 10) + " style nữa");
            DialogResult dr = MessageBox.Show("Thay font của " + sub.Count + " Style bị thiếu?\n\n" + sb + "\nSao lưu trước, hoàn tác được bằng U.", "PKTTC TextHub", MessageBoxButtons.YesNo, MessageBoxIcon.Question, MessageBoxDefaultButton.Button2);
            if (dr != DialogResult.Yes) { Status("Đã hủy, bản vẽ không đổi."); return; }
            Document doc = Doc();
            UiHost.Run(delegate
            {
                ApplyOutcome o = Ops.ApplyFontSub(doc, sub);
                doc.Editor.WriteMessage(o.Message);
                Status(o.Ok ? "Đã thay font " + o.Count + " style. Gõ U để hoàn tác." : "Không đổi được. " + o.Message.Trim());
                OnDocChanged();
            });
        }

        private void DoPurge()
        {
            Document doc = Doc();
            if (doc == null) { Status("Chưa có bản vẽ nào đang mở."); return; }
            List<string> names;
            try { using (doc.LockDocument()) { names = StyleOps.PurgeCandidates(doc.Database); } }
            catch (System.Exception ex) { Status("Lỗi: " + ex.Message); return; }
            if (names.Count == 0) { Status("Không có Style chữ nào để dọn."); return; }
            DialogResult dr = MessageBox.Show("Xóa " + names.Count + " Style chữ không dùng?\n\n" + string.Join(", ", names.ToArray()) + "\n\nSao lưu trước, hoàn tác được bằng U.", "PKTTC TextHub", MessageBoxButtons.YesNo, MessageBoxIcon.Question, MessageBoxDefaultButton.Button2);
            if (dr != DialogResult.Yes) { Status("Đã hủy, bản vẽ không đổi."); return; }
            UiHost.Run(delegate
            {
                ApplyOutcome o = Ops.ApplyPurge(doc, names);
                doc.Editor.WriteMessage(o.Message);
                Status(o.Ok ? "Đã xóa " + o.Count + " style. Gõ U để hoàn tác." : "Không đổi được. " + o.Message.Trim());
                OnDocChanged();
            });
        }

        // ================================================================== tab Kho font
        private void RefreshStore()
        {
            if (_lblStore == null) return;
            FontStore s = FontStore.Load();
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("Kho font: " + s.FileCount + " tệp trong " + s.Roots.Count + " thư mục");
            foreach (string r in s.Roots) sb.AppendLine("  " + r);
            if (s.Roots.Count == 0) sb.AppendLine("Chưa cấu hình. Ghi đường dẫn vào " + Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "PKTTC\\fontstore.txt"));
            _lblStore.Text = sb.ToString();
        }

        private void OpenStore()
        {
            FontStore s = FontStore.Load();
            if (s.Roots.Count == 0) { Status("Chưa cấu hình kho font."); return; }
            try { Process.Start("explorer.exe", "\"" + s.Roots[0] + "\""); } catch (System.Exception ex) { Status("Không mở được: " + ex.Message); }
        }

        private void SaveInstallScript()
        {
            if (_fonts == null) DoFonts();
            if (_fonts == null) return;
            SaveFileDialog d = new SaveFileDialog(); d.Filter = "Script PowerShell (*.ps1)|*.ps1"; d.FileName = "cai_font.ps1";
            if (d.ShowDialog() != DialogResult.OK) return;
            File.WriteAllText(d.FileName, FontReporter.InstallScript(_fonts), new UTF8Encoding(false));
            Status("Đã lưu script (mặc định chỉ xem, thêm -Apply mới chép font): " + d.FileName);
        }

        // ================================================================== tab Tro ly
        private void RefreshBridge()
        {
            if (_lblBridge == null) return;
            _lblBridge.Text = Bridge.IsActive ? "Cổng Kuro: ĐANG MỞ. Mọi thao tác ghi của trợ lý đều hỏi lại anh bằng hộp thoại Yes/No." : "Cổng Kuro: đóng.";
            _lblBridge.ForeColor = Bridge.IsActive ? Color.DarkGreen : Color.Black;
            string path = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "PKTTC\\bridge\\audit.log");
            if (!File.Exists(path)) { _txtLog.Text = "(chưa có nhật ký)"; return; }
            try
            {
                string[] lines = File.ReadAllLines(path);
                int from = Math.Max(0, lines.Length - 60);
                StringBuilder sb = new StringBuilder();
                for (int i = from; i < lines.Length; i++) sb.AppendLine(lines[i]);
                _txtLog.Text = sb.ToString();
                _txtLog.SelectionStart = _txtLog.Text.Length; _txtLog.ScrollToCaret();
            }
            catch (System.Exception ex) { _txtLog.Text = "Không đọc được nhật ký: " + ex.Message; }
        }

        private void DoBridgeOn()
        {
            Document doc = Doc();
            if (doc == null) return;
            if (Bridge.IsActive) { Status("Cổng đã mở."); return; }
            DialogResult dr = MessageBox.Show("Mở cổng cho trợ lý Kuro?\n\nTrợ lý đọc và lập kế hoạch được. Mọi thao tác ghi vẫn hỏi lại anh bằng hộp thoại Yes/No. Cổng làm việc trên bản vẽ đang hiện và tự đóng sau 30 phút không dùng.",
                "PKTTC TextHub", MessageBoxButtons.YesNo, MessageBoxIcon.Question, MessageBoxDefaultButton.Button2);
            if (dr != DialogResult.Yes) { Status("Đã hủy, cổng không mở."); return; }
            UiHost.Run(delegate
            {
                if (Bridge.UseIdle()) Bridge.StartIdle(doc, 30); else Bridge.Run(doc, 30);
                RefreshBridge();
                Status("Đã mở cổng Kuro.");
            });
        }

        private void DoBridgeOff()
        {
            if (!Bridge.IsActive) { Status("Cổng không mở."); return; }
            Bridge.Stop("nút Đóng cổng trong bảng PKTEXTUI");
            RefreshBridge();
            Status("Đã đóng cổng Kuro.");
        }
    }
}
