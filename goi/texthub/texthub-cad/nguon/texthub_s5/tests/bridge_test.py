# -*- coding: utf-8 -*-
"""Kiem thu cong Kuro (headless). Chay: python bridge_test.py <thu_muc_s5> <thu_muc_bin> <duong_dan_dwg_mau>
Khoi dong accoreconsole voi lenh PKTEXTBRIDGE; cac dong 'nguoi dung go' cua script tra loi tung cau hoi xac nhan theo thu tu:
  1 YES  (mo cong)   2 no (tu choi plan.apply lan 1)   3 YES (dong y plan.apply lan 2)   4 no (tu choi purge.apply)
"""
import glob
import json
import os
import subprocess
import sys
import time

root, binp, dwg = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, os.path.join(root, "bridge"))
from pkttc_client import BridgeError, Client  # noqa: E402

test = os.path.join(root, "test")
fails = []


def check(cond, name, got=None):
    if cond:
        print("  dat  " + name)
    else:
        print("  LOI  %s (thuc te: %r)" % (name, got))
        fails.append(name)


def lisp(p):
    return p.replace("\\", "/")


# ---- chuan bi
bk = os.path.join(test, "_backup")
if os.path.isdir(bk):
    import shutil
    shutil.rmtree(bk, ignore_errors=True)
audit = os.path.join(os.environ["LOCALAPPDATA"], "PKTTC", "bridge", "audit.log")
audit_before = os.path.getsize(audit) if os.path.exists(audit) else 0

scr = os.path.join(test, "bridge.scr")
lines = ['(command "_.NETLOAD" "%s")' % lisp(os.path.join(binp, "Pkttc.TextHub.dll")), "PKTEXTBRIDGE", "YES", "no", "YES", "no", "QUIT", "Y"]
open(scr, "w", encoding="utf-8").write("\n".join(lines) + "\n")
out = open(os.path.join(test, "bridge.out.txt"), "wb")
proc = subprocess.Popen([r"C:\Program Files\Autodesk\AutoCAD 2020\accoreconsole.exe", "/i", dwg, "/s", scr, "/l", "en-US"],
                        stdout=out, stderr=subprocess.STDOUT, creationflags=0x08000000)
disc = os.path.join(os.environ["LOCALAPPDATA"], "PKTTC", "bridge", "%d.json" % proc.pid)
t0 = time.time()
while not os.path.exists(disc) and time.time() - t0 < 120 and proc.poll() is None:
    time.sleep(0.3)
if not os.path.exists(disc):
    print("  LOI  cong khong mo (khong thay %s)" % disc)
    proc.kill()
    sys.exit(1)
info = json.load(open(disc, encoding="utf-8"))
pipe = info["pipe"]
print("Cong mo: " + pipe)
c = Client(pipe=pipe, client_name="TestKuro")


def codeof(fn):
    try:
        fn()
    except BridgeError as e:
        return e.code
    return None


try:
    print("Ket noi va doc")
    r = c.call("ping")
    check(r["ok"] and r["protocol"] == 1 and r["acad"].startswith("23.1") and r["drawing"].lower().endswith("fixture_20.dwg"), "ping: phien ban, ban ve, giao thuc", r)
    check(r["fontStoreFiles"] >= 0, "ping: bao so tep kho font")

    s = c.call("scan")
    check(s["meta"]["itemsTotal"] == 20 and s["meta"]["errors"] == 0, "scan: 20 muc, 0 loi", s["meta"])
    check(s["summary"]["byCharset"] == {"Tcvn3": 9, "Vni": 4, "Unicode": 3, "Ascii": 4}, "scan: bang ma 9/4/3/4", s["summary"]["byCharset"])
    check("items" not in s, "scan: mac dinh khong tra danh sach muc")
    sf = c.call("scan", {"items": "flagged", "limit": 5})
    check(sf["itemsReturned"] == 5 and sf["itemsMatching"] >= 13 and sf["items"][0]["handle"], "scan flagged: phan trang, co handle", (sf["itemsReturned"], sf["itemsMatching"]))
    check(all(len(i["raw"]) <= 200 for i in sf["items"]), "scan: chuoi tra ve bi cat toi da 200 ky tu")

    f = c.call("fonts")
    names = {x["name"].lower() for x in f["fonts"]}
    check(f["fontsTotal"] >= 3 and "arial" in names, "fonts: co danh sach font", f["fontsTotal"])

    print("Lap ke hoach (khong sua ban ve)")
    p = c.call("plan.create", {"fontMap": {".VnTime": "Calibri"}})
    check(p["fontMap"].get(".VnTime") == "Calibri", "plan.create: tra lai bang font nguon -> font dich", p.get("fontMap"))
    check(p["count"] == 11 and len(p["planId"]) == 12 and p["targetStyle"] == "Arial Unicode MS_2", "plan.create: 11 muc, ma ke hoach, style dich Arial Unicode MS_2", (p["count"], p["targetStyle"]))
    check(len(p["sample"]) == 10 and "newText" in p["sample"][0], "plan.create: mau 10 muc")
    check(os.path.exists(p["planFile"]), "plan.create: co tep ke hoach cho nguoi xem")
    g = c.call("plan.get", {"planId": p["planId"], "offset": 2, "limit": 3})
    check(len(g["items"]) == 3 and g["offset"] == 2, "plan.get: phan trang", len(g["items"]))
    check(c.call("scan")["summary"]["byCharset"]["Tcvn3"] == 9, "lap ke hoach khong lam ban ve doi")

    print("Tu choi yeu cau khong hop le")
    check(codeof(lambda: c.call("plan.create", {"targetFont": "Ar;ial"})) == -32602, "tham so co ky tu cam bi tu choi (-32602)")
    check(codeof(lambda: c.call("plan.apply", {"planId": "khongco"})) == -32004, "plan.apply ma ke hoach la -> -32004")
    check(codeof(lambda: c.call("plan.apply", {"planId": "../../etc"})) == -32004, "ma ke hoach dang duong dan khong duoc dung")
    check(codeof(lambda: c.call("khong.ton.tai")) == -32601, "phuong thuc la -> -32601")

    print("Phe duyet boi nguoi dung (script tra loi 'no', roi 'YES')")
    r1 = c.call("plan.apply", {"planId": p["planId"], "note": "Doi chu TCVN3 sang Unicode"}, timeout=120)
    check(r1["status"] == "rejected", "nguoi dung tra loi 'no' -> rejected", r1)
    check(c.call("scan")["summary"]["byCharset"]["Tcvn3"] == 9, "bi tu choi: ban ve khong doi")
    r2 = c.call("plan.apply", {"planId": p["planId"]}, timeout=180)
    check(r2["status"] == "applied" and r2["ok"] == 11 and r2["errors"] == 0, "nguoi dung 'YES' -> applied 11 muc, 0 loi", r2)
    check(os.path.exists(r2["backup"]) and os.path.getsize(r2["backup"]) > 10000, "co tep sao luu truoc khi ghi", r2.get("backup"))
    s2 = c.call("scan")
    check(s2["summary"]["byCharset"] == {"Tcvn3": 1, "Vni": 1, "Unicode": 14, "Ascii": 4}, "sau khi ghi: Unicode 14 (con 1 layer khoa, 1 DIMENSION)", s2["summary"]["byCharset"])
    check(any(st["name"] == "Arial Unicode MS_2" for st in s2["styles"]), "style dich Arial Unicode MS_2 duoc tao")
    vu = [st for st in s2["styles"] if st["name"] == "Calibri"]
    check(len(vu) == 1 and vu[0]["font"].lower() == "calibri", "font nguon .VnTime -> Calibri: tao style Calibri dung font Calibri (ca SHX thu tren AutoCAD giao dien)", vu)
    check(codeof(lambda: c.call("plan.apply", {"planId": p["planId"]})) == -32004, "ke hoach chi ap dung mot lan")
    check(c.call("plan.create")["count"] == 0, "lap lai: 0 muc (idempotent)")

    print("Don style (nguoi dung tu choi)")
    pg = c.call("purge.plan")
    check(pg["count"] >= 1 and pg["planId"].startswith("pg-"), "purge.plan: co style co the don", pg)
    rp = c.call("purge.apply", {"planId": pg["planId"]}, timeout=120)
    check(rp["status"] == "rejected", "nguoi dung 'no' -> purge rejected", rp)
    names_after = {st["name"] for st in c.call("scan")["styles"]}
    check(set(pg["styles"]) <= names_after, "bi tu choi: cac style van con")

    print("Do ben cua cong")
    import ctypes  # noqa: F401

    def raw(payload, wait=True):
        f = open(r"\\.\pipe\\" + pipe, "r+b", buffering=0)
        try:
            f.write(payload)
            if not wait:
                return None
            buf = b""
            while b"\n" not in buf:
                ch = f.read(65536)
                if not ch:
                    break
                buf += ch
            return buf
        finally:
            f.close()

    resp = json.loads(raw(b"day khong phai json\n").decode("utf-8"))
    check(resp["error"]["code"] == -32700, "JSON hong -> -32700", resp)
    try:
        big = raw(b"x" * (5 * 1024 * 1024))
        okbig = big is not None and b"-32600" in big
    except OSError:
        okbig = True            # cong dong ket noi cung la chap nhan duoc
    check(okbig, "yeu cau qua 4 MB bi tu choi")
    check(c.call("ping")["ok"], "cong van chay sau khi gap yeu cau xau")

    print("ACL cua pipe")
    import re
    sddl = c.call("ping")["pipeAcl"]
    print("   SDDL:", sddl)
    ace = re.findall(r"\(([^)]*)\)", sddl)
    allows = [a for a in ace if a.startswith("A;")]
    denies = [a for a in ace if a.startswith("D;")]
    who = subprocess.run(["whoami", "/user", "/fo", "csv", "/nh"], capture_output=True, text=True, timeout=30).stdout.strip().split(",")[-1].strip('"')
    check(len(allows) == 1 and allows[0].endswith(";" + who), "chi mot muc cho phep: nguoi dung hien tai (%s)" % who, allows)
    check(any(d.endswith(";NU") for d in denies), "ket noi qua mang (NU) bi cam", denies)
    check(not any(x in sddl for x in (";WD)", ";BU)", ";AU)", ";AN)")), "khong mo cho Everyone/Users/Authenticated/Anonymous", sddl)

    print("May chu MCP")
    env = dict(os.environ)
    env["PKTTC_CLIENT_NAME"] = "TestKuroMCP"
    mcp = subprocess.Popen([sys.executable, "-X", "utf8", "-I", os.path.join(root, "bridge", "pkttc_mcp.py")], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)

    def rpc(msg):
        mcp.stdin.write((json.dumps(msg) + "\n").encode("utf-8"))
        mcp.stdin.flush()
        if "id" not in msg:
            return None
        return json.loads(mcp.stdout.readline().decode("utf-8"))

    ini = rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "t", "version": "1"}}})
    check(ini["result"]["serverInfo"]["name"] == "pkttc-text" and "YES" in ini["result"]["instructions"], "initialize: ten may chu va huong dan co quy tac YES")
    rpc({"jsonrpc": "2.0", "method": "notifications/initialized"})
    tl = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
    tn = {t["name"] for t in tl}
    check({"pkttc_ping", "pkttc_scan", "pkttc_plan_create", "pkttc_plan_apply", "pkttc_purge_apply", "pkttc_fontsub_apply", "pkttc_shutdown"} <= tn and len(tn) == 11, "tools/list: 11 cong cu pkttc_*", sorted(tn))
    ap = [t for t in tl if t["name"] == "pkttc_plan_apply"][0]
    check(set(ap["inputSchema"]["properties"]) == {"planId", "note"} and ap["inputSchema"]["required"] == ["planId"], "plan_apply chi nhan planId va note (khong nhan noi dung de ghi)", ap["inputSchema"])
    cp = rpc({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "pkttc_ping", "arguments": {}}})["result"]
    check(not cp.get("isError") and json.loads(cp["content"][0]["text"])["ok"], "tools/call pkttc_ping chay qua MCP -> cong -> AutoCAD")
    cs = rpc({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "pkttc_scan", "arguments": {"items": "none", "tham_so_la": 1}}})["result"]
    check(json.loads(cs["content"][0]["text"])["meta"]["itemsTotal"] == 20, "tham so la bi bo, scan chay dung")
    cu = rpc({"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "pkttc_khong_co", "arguments": {}}})["result"]
    check(cu["isError"] is True, "cong cu khong ton tai -> isError")
    ce = rpc({"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "pkttc_plan_apply", "arguments": {"planId": "khongco"}}})["result"]
    check(ce["isError"] is True and "-32004" in ce["content"][0]["text"], "plan_apply ma la -> isError, khong hoi nguoi dung")
    mcp.stdin.close()
    mcp.wait(timeout=20)

    print("Nhat ky")
    log = open(audit, "rb").read()[audit_before:].decode("utf-8")
    check("TestKuro | plan.apply" in log and "TU CHOI" in log and "DONG Y" in log, "audit.log ghi yeu cau, TU CHOI va DONG Y")
    check("TestKuroMCP | ping" in log, "audit.log ghi ten may khach MCP")

    print("Dong cong")
    sd = c.call("shutdown")
    check(sd["status"] == "stopping", "shutdown")
finally:
    try:
        proc.wait(timeout=90)
    except subprocess.TimeoutExpired:
        proc.kill()
        fails.append("accoreconsole khong thoat sau shutdown")
        print("  LOI  accoreconsole khong thoat sau shutdown")

time.sleep(0.5)
check(not os.path.exists(disc), "tep phat hien cong da xoa sau khi dong")
try:
    open(r"\\.\pipe\\" + pipe, "r+b", buffering=0).close()
    check(False, "pipe da dong")
except OSError:
    check(True, "pipe da dong")
out.close()
txt = open(os.path.join(test, "bridge.out.txt"), "rb").read().decode("utf-16-le", errors="replace")
check("Cong Kuro da DONG" in txt, "AutoCAD thong bao cong da dong")

print()
print("KET QUA: %s" % ("DAT" if not fails else "CO LOI (%d)" % len(fails)))
sys.exit(0 if not fails else 1)
