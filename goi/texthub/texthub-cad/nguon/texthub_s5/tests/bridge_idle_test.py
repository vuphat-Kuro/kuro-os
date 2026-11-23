# -*- coding: utf-8 -*-
"""Kiem thu che do KHONG CHAN tren mot AutoCAD giao dien (phien rieng). Chay boi run_tests_idle.ps1:
    python bridge_idle_test.py <thu_muc_s5> <pid_acad> <scan_json_do_script_ghi>
Hop thoai xin phep duoc tra loi bang UI Automation (click_dialog.ps1), nhu mot nguoi bam nut.
"""
import json
import os
import subprocess
import sys
import threading
import time

root, pid, scan_json = sys.argv[1], int(sys.argv[2]), sys.argv[3]
sys.path.insert(0, os.path.join(root, "bridge"))
from pkttc_client import BridgeError, Client  # noqa: E402

fails = []


def check(cond, name, got=None):
    if cond:
        print("  dat  " + name)
    else:
        print("  LOI  %s (thuc te: %r)" % (name, got))
        fails.append(name)


def codeof(fn):
    try:
        fn()
    except BridgeError as e:
        return e.code
    return None


def call_with_click(c, method, params, button, timeout=240):
    """Goi mot yeu cau GHI trong luong rieng, bam nut tren hop thoai, tra ve (ket_qua, noi_dung_hop_thoai)."""
    box = {}

    def work():
        try:
            box["r"] = c.call(method, params, timeout=timeout)
        except Exception as e:  # noqa: BLE001
            box["e"] = e

    t = threading.Thread(target=work, daemon=True)
    t.start()
    cp = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(root, "tests", "click_dialog.ps1"),
                         "-ProcId", str(pid), "-Button", button, "-TimeoutSec", "120"], capture_output=True, text=True, timeout=200)
    t.join(timeout)
    if "e" in box:
        raise box["e"]
    return box.get("r"), cp.stdout


disc = os.path.join(os.environ["LOCALAPPDATA"], "PKTTC", "bridge", "%d.json" % pid)
t0 = time.time()
while not os.path.exists(disc) and time.time() - t0 < 240:
    time.sleep(0.5)
if not os.path.exists(disc):
    print("  LOI  cong khong mo (khong thay %s)" % disc)
    sys.exit(1)
info = json.load(open(disc, encoding="utf-8"))
print("Cong mo: %s (che do %s)" % (info["pipe"], info.get("mode")))
c = Client(pipe=info["pipe"], client_name="TestKuroIdle")
audit = os.path.join(os.environ["LOCALAPPDATA"], "PKTTC", "bridge", "audit.log")
audit_before = os.path.getsize(audit) if os.path.exists(audit) else 0

print("Khong chan")
check(info.get("mode") == "idle", "che do idle", info.get("mode"))
# Script chay PKTEXTSCAN SAU PKTEXTBRIDGE: neu cong chan dong lenh thi file nay khong co
time.sleep(2)
check(os.path.exists(scan_json) and os.path.getsize(scan_json) > 100, "lenh PKTEXTSCAN sau PKTEXTBRIDGE da chay (dong lenh khong bi chan)", scan_json)

print("Doc qua cong khi AutoCAD ranh")
t1 = time.time()
r = c.call("ping", timeout=60)
check(r["ok"] and r["drawing"].lower().endswith("idle_work.dwg"), "ping tra loi (Application.Idle chay)", r.get("drawing"))
print("   do tre ping: %.2f s" % (time.time() - t1))
s = c.call("scan", timeout=60)
check(s["summary"]["byCharset"] == {"Tcvn3": 9, "Vni": 4, "Unicode": 3, "Ascii": 4}, "scan: 9/4/3/4", s["summary"]["byCharset"])
# targetFont ghi ro: phien AutoCAD thu tu nap ca bundle TextHub da cai (co the la ban cu, mac dinh font khac) truoc DLL dang thu.
p = c.call("plan.create", {"targetFont": "Arial Unicode MS"}, timeout=60)
check(p["count"] == 11 and p["targetStyle"] == "Arial Unicode MS_2", "plan.create: 11 muc, style Arial Unicode MS_2", (p["count"], p["targetStyle"]))
check(codeof(lambda: c.call("plan.apply", {"planId": "khongco"})) == -32004, "ma ke hoach la -> -32004, khong hien hop thoai")

print("Phe duyet bang hop thoai")
r1, d1 = call_with_click(c, "plan.apply", {"planId": p["planId"], "note": "Doi chu cu sang Unicode"}, "No")
print("   hop thoai:", d1.strip().replace("\n", " | ")[:600])
check(r1 and r1["status"] == "rejected", "bam No -> rejected", r1)
check(("TestKuroIdle" in d1) and (p["planId"] in d1) and ("11 muc" in d1) and ("Doi chu cu sang Unicode" in d1), "hop thoai co ten tro ly, ma ke hoach, so muc, ghi chu", d1[:300])
check("DA BAM: No" in d1, "da bam nut No")
check(c.call("scan", timeout=60)["summary"]["byCharset"]["Tcvn3"] == 9, "bi tu choi: ban ve khong doi")

r2, d2 = call_with_click(c, "plan.apply", {"planId": p["planId"]}, "Yes")
check(r2 and r2["status"] == "applied" and r2["ok"] == 11 and r2["errors"] == 0, "bam Yes -> applied 11 muc, 0 loi", r2)
check(r2 and r2.get("commandContext", "").upper() == "PKTEXTBRIDGEEXEC", "ghi chay trong lenh that PKTEXTBRIDGEEXEC (co mot buoc UNDO)", r2 and r2.get("commandContext"))
check(r2 and os.path.exists(r2["backup"]), "co tep sao luu")
s2 = c.call("scan", timeout=60)
check(s2["summary"]["byCharset"] == {"Tcvn3": 1, "Vni": 1, "Unicode": 14, "Ascii": 4}, "sau khi ghi: Unicode 14", s2["summary"]["byCharset"])
check(c.call("plan.create", timeout=60)["count"] == 0, "lap lai: 0 muc")

pg = c.call("purge.plan", timeout=60)
rp, dp = call_with_click(c, "purge.apply", {"planId": pg["planId"]}, "No")
check(rp and rp["status"] == "rejected", "purge: bam No -> rejected", rp)

print("Do ben")
check(c.call("ping", timeout=60)["ok"], "cong van chay sau cac hop thoai")
check(codeof(lambda: c.call("khong.ton.tai")) == -32601, "phuong thuc la -> -32601")
sddl = c.call("ping")["pipeAcl"]
check(";NU)" in sddl and sddl.count("(A;") == 1, "ACL: mot nguoi duoc phep, mang bi cam", sddl)

print("Nhat ky")
log = open(audit, "rb").read()[audit_before:].decode("utf-8")
check("TestKuroIdle | approval" in log and "TU CHOI" in log and "DONG Y" in log, "audit.log ghi TU CHOI va DONG Y")

print("Dong cong (AutoCAD van mo)")
sd = c.call("shutdown", timeout=60)
check(sd["status"] == "stopping", "shutdown")
time.sleep(2)
check(not os.path.exists(disc), "tep phat hien cong da xoa")
try:
    open(r"\\.\pipe\\" + info["pipe"], "r+b", buffering=0).close()
    check(False, "pipe da dong")
except OSError:
    check(True, "pipe da dong")
alive = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid, "/NH"], capture_output=True, text=True).stdout
check(str(pid) in alive, "AutoCAD van chay sau khi dong cong (khong bi thoat)")

print()
print("KET QUA: %s" % ("DAT" if not fails else "CO LOI (%d)" % len(fails)))
sys.exit(0 if not fails else 1)
