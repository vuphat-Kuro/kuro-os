# -*- coding: utf-8 -*-
"""Kiem thu goi cai dat PKTTC TextHub. Chay boi run_tests_package.ps1:  python package_test.py <thu_muc_s6> <fixture_dwg>
A: tinh (XML, MANIFEST, lenh, tai lieu, khong registry)   B: trinh cai tren thu muc tam, giai nen tu zip
C: tu nap THAT: cai vao ApplicationPlugins cua nguoi dung, mo phien AutoCAD rieng (khong NETLOAD), chay lenh, go ngay sau do.
"""
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
import zipfile

root, fixture = sys.argv[1], sys.argv[2]
dist = os.path.join(root, "dist")
version = open(os.path.join(root, "VERSION")).read().strip()
fails = []


def check(cond, name, got=None):
    if cond:
        print("  dat  " + name)
    else:
        print("  LOI  %s (thuc te: %r)" % (name, got))
        fails.append(name)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest().upper()


def ps(args, timeout=300):
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass"] + args, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


# =================================================================== A. tinh
print("A. Noi dung goi")
bundle = os.path.join(dist, "PKTTC.TextHub.bundle")
tree = ET.parse(os.path.join(bundle, "PackageContents.xml"))
pk = tree.getroot()
check(pk.tag == "ApplicationPackage" and pk.get("AppVersion") == version, "PackageContents: AppVersion = VERSION (%s)" % version, pk.get("AppVersion"))
guid = re.compile(r"^\{[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\}$")
check(guid.match(pk.get("ProductCode", "")) and guid.match(pk.get("UpgradeCode", "")), "ProductCode va UpgradeCode hop le", (pk.get("ProductCode"), pk.get("UpgradeCode")))
rr = pk.find("./Components/RuntimeRequirements")
check(rr.get("OS") == "Win64" and rr.get("Platform") == "AutoCAD" and rr.get("SeriesMin") == "R23.1" and rr.get("SeriesMax") == "R23.1", "chi AutoCAD 2020 (R23.1), Win64", rr.attrib)
ce = pk.find("./Components/ComponentEntry")
check(ce.get("LoadOnAutoCADStartup") == "true", "tu nap khi AutoCAD khoi dong")
mod = os.path.join(bundle, ce.get("ModuleName").replace("./", "").replace("/", os.sep))
check(os.path.exists(mod), "ModuleName tro toi tep co that", mod)

xml_cmds = {c.get("Global") for c in ce.iter("Command")}
src = ""
for f in glob.glob(os.path.join(root, "..", "texthub_s5", "src", "Db", "*.cs")) + glob.glob(os.path.join(root, "src", "*.cs")):
    src += open(f, encoding="utf-8-sig").read()
src_cmds = set(re.findall(r'CommandMethod\("([A-Za-z0-9_]+)"', src))
check(xml_cmds == src_cmds and len(xml_cmds) == 14, "danh sach lenh trong XML khop ma nguon (14 lenh, gom PKTEXTUI va PKTEXTUIEXEC)", (len(xml_cmds), sorted(xml_cmds ^ src_cmds)))
check(not any("FIXTURE" in c for c in xml_cmds), "khong co lenh chi dung cho kiem thu")

bad = []
for line in open(os.path.join(bundle, "MANIFEST.txt"), encoding="utf-8").read().splitlines():
    m = re.match(r"^([0-9A-F]{64})\s+(.+)$", line)
    if m and (not os.path.exists(os.path.join(bundle, m.group(2))) or sha(os.path.join(bundle, m.group(2))) != m.group(1)):
        bad.append(m.group(2))
files = [os.path.relpath(p, bundle) for p in glob.glob(os.path.join(bundle, "**", "*"), recursive=True) if os.path.isfile(p) and not p.endswith("MANIFEST.txt")]
listed = re.findall(r"^[0-9A-F]{64}\s+(.+)$", open(os.path.join(bundle, "MANIFEST.txt"), encoding="utf-8").read(), re.M)
check(not bad and sorted(files) == sorted(listed), "MANIFEST: moi tep co ma SHA-256 dung, khong thieu tep", (bad, set(files) ^ set(listed)))

rc, out = ps(["-Command", "(Get-Item '%s').VersionInfo | ForEach-Object { $_.FileVersion + '|' + $_.ProductVersion + '|' + $_.ProductName }" % mod])
check(out.strip().startswith(version + ".0|" + version), "DLL mang phien ban %s" % version, out.strip())

z = zipfile.ZipFile(os.path.join(dist, "PKTTC.TextHub-%s.zip" % version))
names = z.namelist()
check(any(n.endswith("Pkttc.TextHub.dll") for n in names) and "cai_dat.ps1" in names and "HUONG_DAN_CAI_DAT.md" in names, "zip co bundle, cai_dat.ps1, HUONG_DAN_CAI_DAT.md", [n for n in names][:6])

inst = open(os.path.join(dist, "cai_dat.ps1"), encoding="utf-8-sig").read()
inst_wo_comments = re.sub(r"(?m)^\s*#.*$", "", inst)
check(not re.search(r"HKCU|HKLM|reg add|New-ItemProperty|Set-ItemProperty|Registry::", inst_wo_comments), "trinh cai khong ghi registry")
texts = {}
for p in glob.glob(os.path.join(dist, "*.md")) + glob.glob(os.path.join(bundle, "Contents", "Docs", "*.md")) + [os.path.join(dist, "cai_dat.ps1")]:
    texts[os.path.basename(p)] = open(p, encoding="utf-8-sig").read()
check(not any("\u2014" in t for t in texts.values()), "khong co dau gach ngang dai (em dash) trong tai lieu va script", [k for k, t in texts.items() if "\u2014" in t])
check(not any(re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", t) for t in texts.values()), "khong co ky tu dieu khien la trong tai lieu", [k for k, t in texts.items() if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", t)])
check(all(len(t.strip()) > 500 for t in texts.values()), "tai lieu khong rong", {k: len(t) for k, t in texts.items()})

# =================================================================== B. trinh cai tren thu muc tam
print("B. Trinh cai (giai nen tu zip, thu muc tam)")
tmp = tempfile.mkdtemp(prefix="pkttc_pkg_")
ex = os.path.join(tmp, "goi")
z.extractall(ex)
tgt = os.path.join(tmp, "ApplicationPlugins")
cfg = os.path.join(os.environ["LOCALAPPDATA"], "PKTTC", "fontstore.txt")
cfg_hash = sha(cfg) if os.path.exists(cfg) else None
installer = os.path.join(ex, "cai_dat.ps1")
dst = os.path.join(tgt, "PKTTC.TextHub.bundle")

rc, out = ps(["-File", installer, "-Target", tgt, "-WhatIf"])
check(rc == 0 and not os.path.exists(dst), "-WhatIf: khong thay doi gi", (rc, out.strip()[:120]))
rc, out = ps(["-File", installer, "-Target", tgt, "-FontStore", os.path.join(root, "dist")])
check(rc == 0 and os.path.exists(os.path.join(dst, "PackageContents.xml")), "cai moi: thanh cong, co PackageContents.xml", (rc, out.strip()[:200]))
check(sha(os.path.join(dst, "Contents", "Windows", "Pkttc.TextHub.dll")) == sha(mod), "DLL da chep khop goc")
check(cfg_hash is None or sha(cfg) == cfg_hash, "cau hinh kho font san co khong bi ghi de")
rc, out = ps(["-File", installer, "-Target", tgt])
check(rc == 0 and os.path.isdir(os.path.join(tgt, "PKTTC.TextHub.old")) and os.path.exists(os.path.join(dst, "PackageContents.xml")), "nang cap: giu ban cu o PKTTC.TextHub.old, ban moi o dung cho", (rc, os.listdir(tgt)))
check(not any(n.endswith(".bundle") and n != "PKTTC.TextHub.bundle" for n in os.listdir(tgt)), "ban cu khong co duoi .bundle (AutoCAD khong nap nham)", os.listdir(tgt))

# goi hong: sua mot tep truoc khi cai
ex2 = os.path.join(tmp, "goi_hong")
shutil.copytree(ex, ex2)
with open(os.path.join(ex2, "PKTTC.TextHub.bundle", "Contents", "Bridge", "pkttc_mcp.py"), "ab") as f:
    f.write(b"\n# sua trai phep\n")
before = sha(os.path.join(dst, "Contents", "Windows", "Pkttc.TextHub.dll"))
rc, out = ps(["-File", os.path.join(ex2, "cai_dat.ps1"), "-Target", tgt])
check(rc == 1 and "MANIFEST" in out and sha(os.path.join(dst, "Contents", "Windows", "Pkttc.TextHub.dll")) == before, "goi bi sua: tu choi cai, ban dang co khong doi", (rc, out.strip()[:160]))

# DLL dang bi dung
holder = subprocess.Popen(["powershell", "-NoProfile", "-Command",
                           "$f=[IO.File]::Open('%s','Open','ReadWrite','None'); Start-Sleep 40" % os.path.join(dst, "Contents", "Windows", "Pkttc.TextHub.dll")])
time.sleep(4)
rc, out = ps(["-File", installer, "-Target", tgt])
check(rc == 2 and "AutoCAD dang dung" in out and os.path.exists(os.path.join(dst, "PackageContents.xml")), "DLL dang bi dung: bao dong AutoCAD, ban dang co nguyen ven", (rc, out.strip()[:160]))
rc, out = ps(["-File", installer, "-Target", tgt, "-Uninstall"])
check(rc == 2 and os.path.exists(dst), "go khi DLL dang bi dung: tu choi, khong xoa", rc)
holder.kill()
time.sleep(2)

rc, out = ps(["-File", installer, "-Target", tgt, "-Uninstall"])
check(rc == 0 and not os.path.exists(dst) and not os.path.exists(os.path.join(tgt, "PKTTC.TextHub.old")), "go: xoa bundle va ban cu", (rc, os.listdir(tgt)))
rc, out = ps(["-File", installer, "-Target", tgt, "-Uninstall"])
check(rc == 0 and "Chua cai dat" in out, "go lan hai: bao chua cai, khong loi")
shutil.rmtree(tmp, ignore_errors=True)

# =================================================================== C. tu nap that
print("C. Tu nap khi AutoCAD khoi dong (cai vao ApplicationPlugins cua nguoi dung, phien AutoCAD rieng)")
real = os.path.join(os.environ["APPDATA"], "Autodesk", "ApplicationPlugins")
real_b = os.path.join(real, "PKTTC.TextHub.bundle")
if os.path.exists(real_b):
    print("  LOI  da co %s, khong thu de tranh ghi de" % real_b)
    sys.exit(1)

work = os.path.join(root, "test")
os.makedirs(work, exist_ok=True)
dwg = os.path.join(work, "pkg_work.dwg")
shutil.copy(fixture, dwg)
out_json = os.path.join(work, "pkg_scan.json")
if os.path.exists(out_json):
    os.remove(out_json)
scr = os.path.join(work, "pkg.scr")
open(scr, "w", encoding="utf-8").write("PKTEXTSCAN\n" + out_json.replace("\\", "/") + "\n")

kcfg = os.path.join(os.environ["LOCALAPPDATA"], "PKTTC", "kuro_mcp_config.json")
kcfg_before = os.path.exists(kcfg)
rc, out = ps(["-File", os.path.join(dist, "cai_dat.ps1")])
check(rc == 0 and os.path.exists(os.path.join(real_b, "PackageContents.xml")), "cai vao ApplicationPlugins mac dinh", (rc, out.strip()[-200:]))
user_acad = subprocess.run(["tasklist", "/FI", "IMAGENAME eq acad.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
user_pids = re.findall(r'"acad.exe","(\d+)"', user_acad)
proc = None
try:
    proc = subprocess.Popen([r"C:\Program Files\Autodesk\AutoCAD 2020\acad.exe", dwg, "/nologo", "/b", scr])
    t0 = time.time()
    while time.time() - t0 < 300 and not (os.path.exists(out_json) and os.path.getsize(out_json) > 100):
        time.sleep(1)
    ok = os.path.exists(out_json) and os.path.getsize(out_json) > 100
    check(ok, "lenh PKTEXTSCAN co san khi AutoCAD khoi dong KHONG can NETLOAD (plugin tu nap)")
    if ok:
        time.sleep(1)
        d = json.load(open(out_json, encoding="utf-8"))
        check(d["meta"]["itemsTotal"] == 20 and d["meta"]["errors"] == 0, "ket qua quet dung (20 muc)", d["meta"])
finally:
    if proc is not None:
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            pass
    time.sleep(2)
    rc, out = ps(["-File", os.path.join(dist, "cai_dat.ps1"), "-Uninstall"])
    check(rc == 0 and not os.path.exists(real_b), "go sach khoi ApplicationPlugins cua nguoi dung", (rc, out.strip()[-160:]))
    check(kcfg_before or not os.path.exists(kcfg), "go cung tep cau hinh Kuro do trinh cai tao (khong de lai duong dan da xoa)", os.path.exists(kcfg))
    after = subprocess.run(["tasklist", "/FI", "IMAGENAME eq acad.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
    check(all(p in re.findall(r'"acad.exe","(\d+)"', after) for p in user_pids), "phien AutoCAD cua nguoi dung van chay", (user_pids, re.findall(r'"acad.exe","(\d+)"', after)))

print()
print("KET QUA: %s" % ("DAT" if not fails else "CO LOI (%d)" % len(fails)))
sys.exit(0 if not fails else 1)
