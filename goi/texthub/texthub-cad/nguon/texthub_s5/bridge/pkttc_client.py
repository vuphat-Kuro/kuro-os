# -*- coding: utf-8 -*-
"""Client cho cong PKTTC TextHub (named pipe cuc bo, JSON moi dong). Khong can thu vien ngoai.

Dung:
    from pkttc_client import Client
    c = Client(client_name="Kuro")        # tu tim cong dang mo (lenh PKTEXTBRIDGE trong AutoCAD)
    c.call("ping")
Dong lenh:
    python pkttc_client.py list
    python pkttc_client.py ping
    python pkttc_client.py scan --items flagged
"""
import ctypes
import glob
import json
import os
import sys
import threading
import time

BRIDGE_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "PKTTC", "bridge")


class BridgeError(Exception):
    def __init__(self, code, message):
        Exception.__init__(self, "[%s] %s" % (code, message))
        self.code = code
        self.message = message


def _alive(pid):
    # PROCESS_QUERY_LIMITED_INFORMATION = 0x1000; STILL_ACTIVE = 259
    h = ctypes.windll.kernel32.OpenProcess(0x1000, False, int(pid))
    if not h:
        return False
    try:
        code = ctypes.c_ulong()
        ok = ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
        return bool(ok) and code.value == 259
    finally:
        ctypes.windll.kernel32.CloseHandle(h)


def _pipe_exists(name):
    """Pipe con ton tai khong (tep JSON cua cong cu co the con sot lai, PID co the da duoc tien trinh khac dung lai)."""
    try:
        return name in os.listdir("\\\\.\\pipe\\")
    except OSError:
        return True   # khong liet ke duoc thi giu ket qua kiem tien trinh


def find_bridges():
    """Danh sach cong dang mo: [{pid, pipe, started, drawing}], bo cong cua tien trinh da thoat."""
    out = []
    for f in sorted(glob.glob(os.path.join(BRIDGE_DIR, "*.json"))):
        try:
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            continue
        if _alive(d.get("pid", 0)) and _pipe_exists(d.get("pipe", "")):
            out.append(d)
    return out


class Client:
    def __init__(self, pipe=None, client_name="Kuro"):
        self.client_name = client_name
        if pipe is None:
            br = find_bridges()
            if not br:
                raise BridgeError("no-bridge", "Khong co cong nao dang mo. Nguoi dung go lenh PKTEXTBRIDGE trong AutoCAD.")
            pipe = br[-1]["pipe"]
        self.pipe = pipe
        self._id = 0

    def _open(self):
        path = r"\\.\pipe\\" + self.pipe
        last = None
        for _ in range(60):          # cong tao lai ong sau moi ket noi: thu lai ngan
            try:
                return open(path, "r+b", buffering=0)
            except OSError as e:
                last = e
                time.sleep(0.05)
        raise BridgeError("connect", "Khong noi duoc cong %s: %s" % (self.pipe, last))

    def call(self, method, params=None, timeout=120):
        """Gui mot yeu cau, doi tra loi. Yeu cau GHI co the doi nguoi dung go YES: dat timeout lon (mac dinh 120 s)."""
        self._id += 1
        p = dict(params or {})
        p.setdefault("client", self.client_name)
        line = json.dumps({"id": self._id, "method": method, "params": p}, ensure_ascii=False).encode("utf-8") + b"\n"
        f = self._open()
        box = {}

        def work():
            try:
                f.write(line)
                buf = b""
                while b"\n" not in buf:
                    chunk = f.read(65536)
                    if not chunk:
                        raise OSError("cong dong ket noi")
                    buf += chunk
                box["resp"] = buf.split(b"\n", 1)[0]
            except Exception as e:          # noqa: BLE001
                box["err"] = e

        t = threading.Thread(target=work, daemon=True)
        t.start()
        t.join(timeout)
        if t.is_alive():
            try:
                f.close()
            except OSError:
                pass
            raise TimeoutError("Het %s giay cho tra loi (nguoi dung co the chua go YES)." % timeout)
        try:
            f.close()
        except OSError:
            pass
        if "err" in box:
            raise BridgeError("io", str(box["err"]))
        resp = json.loads(box["resp"].decode("utf-8"))
        if "error" in resp and resp["error"]:
            raise BridgeError(resp["error"].get("code"), resp["error"].get("message"))
        return resp.get("result")


def _main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[1]
    if cmd == "list":
        print(json.dumps(find_bridges(), ensure_ascii=False, indent=2))
        return 0
    params = {}
    i = 2
    while i < len(argv):
        if argv[i].startswith("--") and i + 1 < len(argv):
            v = argv[i + 1]
            params[argv[i][2:]] = int(v) if v.isdigit() else (v.lower() == "true" if v.lower() in ("true", "false") else v)
            i += 2
        else:
            i += 1
    print(json.dumps(Client(client_name="cli").call(cmd, params, timeout=600), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
