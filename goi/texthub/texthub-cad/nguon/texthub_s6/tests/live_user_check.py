# -*- coding: utf-8 -*-
"""Noi thang theo ten pipe vao cong cua phien AutoCAD cua nguoi dung. Chi goi lenh doc."""
import json
import sys

sys.path.insert(0, sys.argv[1])
from pkttc_client import Client  # noqa: E402

c = Client(pipe=sys.argv[2], client_name="Kuro")
print("ping:", json.dumps(c.call("ping"), ensure_ascii=False))
s = c.call("scan", {"items": "none"})
print("scan meta:", json.dumps(s["meta"], ensure_ascii=False))
print("byCharset:", s["summary"].get("byCharset"))
print("byFlag:", s["summary"].get("byFlag"))
f = c.call("fonts")
print("fonts:", {k: f[k] for k in ("fontsTotal", "ok", "inStore", "missing", "storeFiles")})
