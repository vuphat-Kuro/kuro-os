# -*- coding: utf-8 -*-
"""Kiem tra MCP cua bundle DA CAI (stdio JSON-RPC) voi cong dang mo. Chi goi lenh doc."""
import json
import os
import subprocess
import sys

mcp = os.path.join(os.environ["APPDATA"], "Autodesk", "ApplicationPlugins", "PKTTC.TextHub.bundle", "Contents", "Bridge", "pkttc_mcp.py")
env = dict(os.environ, PKTTC_CLIENT_NAME="Kuro")
p = subprocess.Popen([sys.executable, "-X", "utf8", mcp], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)


def rpc(i, method, params=None):
    p.stdin.write((json.dumps({"jsonrpc": "2.0", "id": i, "method": method, "params": params or {}}) + "\n").encode())
    p.stdin.flush()
    return json.loads(p.stdout.readline().decode("utf-8"))


print("initialize:", rpc(1, "initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "Kuro", "version": "0"}}).get("result", {}).get("serverInfo"))
p.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
p.stdin.flush()
tools = rpc(2, "tools/list")["result"]["tools"]
print("tools:", len(tools), [t["name"] for t in tools])
for i, (name, args) in enumerate([("pkttc_ping", {}), ("pkttc_scan", {"items": "none"}), ("pkttc_fonts", {})], start=3):
    r = rpc(i, "tools/call", {"name": name, "arguments": args})
    txt = json.dumps(r.get("result", r), ensure_ascii=False)
    print(name, "->", txt[:700])
p.stdin.close()
p.terminate()
