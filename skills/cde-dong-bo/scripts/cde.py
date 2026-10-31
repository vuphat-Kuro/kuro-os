#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cde — Làm việc với CDE qua API thay vì bấm tay trên trình duyệt.

Hỗ trợ hai loại nguồn:
  • acc  — Autodesk Construction Cloud / BIM 360 (Autodesk Platform Services)
  • rest — CDE nội bộ bất kỳ có REST API, mô tả bằng một file cấu hình JSON

Các lệnh:
    du-an       Liệt kê hub và dự án
    cay         Liệt kê cây thư mục / tài liệu trong một thư mục
    dang-ky     Xuất bảng đăng ký tài liệu (document register) ra Excel
    tai-ve      Tải hàng loạt tài liệu về máy
    tai-len     Tải hàng loạt file lên một thư mục
    issue       Xuất danh sách Issue/RFI ra Excel để làm báo cáo

BẢO MẬT — đọc kỹ:
  Script không bao giờ chứa mật khẩu. Khai báo bằng biến môi trường:

      $env:APS_CLIENT_ID     = "..."       # PowerShell
      $env:APS_CLIENT_SECRET = "..."
      $env:APS_TOKEN         = "..."       # nếu đã có token 3-legged sẵn

  Hoặc đặt trong file .env cùng thư mục (thêm .env vào .gitignore).
  Không commit token lên Git, không dán token vào chat.

Ví dụ:
    python cde.py du-an --nguon acc
    python cde.py cay --nguon acc --du-an b.xxxx --thu-muc urn:adsk.wipprod:fs.folder:co.yyyy
    python cde.py tai-ve --nguon acc --du-an b.xxxx --thu-muc urn:... --ra ./tai-ve --loc "*.pdf"
    python cde.py issue --nguon acc --du-an xxxx --ra issues.xlsx
"""

import argparse
import fnmatch
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

APS = "https://developer.api.autodesk.com"


# ----------------------------------------------------------------------------
# Cấu hình & tiện ích
# ----------------------------------------------------------------------------

def nap_env():
    """Nạp file .env nếu có — mỗi dòng dạng KHOA=giá trị."""
    for thu_muc in (Path.cwd(), Path(__file__).parent):
        f = thu_muc / ".env"
        if not f.exists():
            continue
        for dong in f.read_text(encoding="utf-8").splitlines():
            dong = dong.strip()
            if not dong or dong.startswith("#") or "=" not in dong:
                continue
            k, v = dong.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def bat_buoc_env(ten):
    v = os.environ.get(ten)
    if not v:
        raise SystemExit(
            f"❌ Thiếu biến môi trường {ten}.\n"
            f"   PowerShell:  $env:{ten} = \"giá trị\"\n"
            f"   Hoặc thêm dòng  {ten}=giá trị  vào file .env"
        )
    return v


def goi(phuong_thuc, url, **kw):
    """Gọi HTTP có thử lại khi bị giới hạn tần suất hoặc lỗi tạm thời."""
    cho = 1.5
    for lan in range(5):
        r = requests.request(phuong_thuc, url, timeout=kw.pop("timeout", 120), **kw)
        if r.status_code == 429 or 500 <= r.status_code < 600:
            cho_them = float(r.headers.get("Retry-After", cho))
            print(f"   ⏳ Máy chủ bận ({r.status_code}), đợi {cho_them:.0f}s "
                  f"rồi thử lại (lần {lan + 1}/5)")
            time.sleep(cho_them)
            cho *= 2
            continue
        return r
    return r


# ----------------------------------------------------------------------------
# Nguồn ACC / BIM 360
# ----------------------------------------------------------------------------

class ACC:
    """Client tối thiểu cho Data Management + Issues API của Autodesk.

    Ghi chú quan trọng về mã dự án — đây là chỗ gây lỗi 404 nhiều nhất:
      • Data Management API dùng project id CÓ tiền tố "b." (b.abc-123)
      • Issues API và các API xây dựng khác dùng id KHÔNG có "b."
    Script tự thêm/bỏ tiền tố, nhưng khi tự gọi tay thì cần nhớ.
    """

    def __init__(self):
        nap_env()
        self.token = os.environ.get("APS_TOKEN")
        if not self.token:
            self.token = self._lay_token()

    def _lay_token(self):
        """Token 2-legged (client credentials). Đủ để đọc dữ liệu dự án khi
        ứng dụng đã được cấp quyền trong ACC Account Admin > Custom Integrations.
        Muốn thao tác dưới danh nghĩa người dùng thì dùng token 3-legged và
        đặt vào APS_TOKEN."""
        cid = bat_buoc_env("APS_CLIENT_ID")
        secret = bat_buoc_env("APS_CLIENT_SECRET")
        pham_vi = os.environ.get(
            "APS_SCOPE", "data:read data:write data:create account:read")
        r = goi("POST", f"{APS}/authentication/v2/token",
                auth=(cid, secret),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={"grant_type": "client_credentials", "scope": pham_vi})
        if r.status_code != 200:
            raise SystemExit(f"❌ Lấy token thất bại ({r.status_code}): {r.text[:300]}")
        return r.json()["access_token"]

    @property
    def dau(self):
        return {"Authorization": f"Bearer {self.token}"}

    def _get(self, duong_dan, **kw):
        url = duong_dan if duong_dan.startswith("http") else f"{APS}{duong_dan}"
        r = goi("GET", url, headers={**self.dau, **kw.pop("headers", {})}, **kw)
        if r.status_code >= 400:
            raise SystemExit(f"❌ GET {url}\n   {r.status_code}: {r.text[:400]}")
        return r.json()

    # -- duyệt dự án -------------------------------------------------------
    def hubs(self):
        return self._get("/project/v1/hubs")["data"]

    def du_an(self, hub_id):
        kq, url = [], f"/project/v1/hubs/{hub_id}/projects?page[limit]=200"
        while url:
            d = self._get(url)
            kq += d["data"]
            url = d.get("links", {}).get("next", {}).get("href")
        return kq

    def thu_muc_goc(self, hub_id, project_id):
        return self._get(
            f"/project/v1/hubs/{hub_id}/projects/{project_id}/topFolders")["data"]

    def noi_dung(self, project_id, folder_id):
        kq, url = [], (f"/data/v1/projects/{project_id}/folders/{folder_id}"
                       f"/contents?page[limit]=200")
        while url:
            d = self._get(url)
            kq += d["data"]
            url = d.get("links", {}).get("next", {}).get("href")
        return kq

    def duyet(self, project_id, folder_id, sau=0, toi_da=6, duong=""):
        """Duyệt đệ quy, trả về danh sách phẳng gồm thư mục và tài liệu."""
        kq = []
        for m in self.noi_dung(project_id, folder_id):
            ten = m["attributes"].get("displayName") or m["attributes"].get("name", "")
            duong_moi = f"{duong}/{ten}" if duong else ten
            if m["type"] == "folders":
                kq.append({"loai": "thư mục", "ten": ten, "duong_dan": duong_moi,
                           "id": m["id"], "sua_luc": m["attributes"].get("lastModifiedTime")})
                if sau < toi_da:
                    kq += self.duyet(project_id, m["id"], sau + 1, toi_da, duong_moi)
            else:
                tt = m["attributes"]
                kq.append({
                    "loai": "tài liệu", "ten": ten, "duong_dan": duong_moi,
                    "id": m["id"],
                    "phien_ban": tt.get("versionNumber") or
                                 (m.get("relationships", {}).get("tip", {})
                                  .get("data", {}) or {}).get("id", ""),
                    "sua_luc": tt.get("lastModifiedTime"),
                    "nguoi_sua": tt.get("lastModifiedUserName"),
                    "kich_thuoc": tt.get("storageSize"),
                })
        return kq

    def ban_moi_nhat(self, project_id, item_id):
        return self._get(f"/data/v1/projects/{project_id}/items/{item_id}/tip")["data"]

    def tai_ve(self, project_id, item_id, dich):
        ban = self.ban_moi_nhat(project_id, item_id)
        kho = (ban.get("relationships", {}).get("storage", {}).get("data") or {}).get("id")
        if not kho:
            return False, "không có bản lưu trữ (có thể là file liên kết)"
        # urn:adsk.objects:os.object:<bucket>/<object>
        phan = kho.split(":")[-1]
        bucket, obj = phan.split("/", 1)
        d = self._get(f"/oss/v2/buckets/{bucket}/objects/"
                      f"{requests.utils.quote(obj, safe='')}/signeds3download")
        url = d.get("url")
        if not url:
            return False, "không lấy được liên kết tải"
        r = goi("GET", url, stream=True)
        dich.parent.mkdir(parents=True, exist_ok=True)
        with open(dich, "wb") as fh:
            for khoi in r.iter_content(1 << 20):
                fh.write(khoi)
        return True, f"{dich.stat().st_size / 1e6:.2f} MB"

    def tai_len(self, project_id, folder_id, duong_dan_file):
        """Tải file lên theo luồng direct-to-S3 của Autodesk."""
        f = Path(duong_dan_file)
        # 1. xin chỗ lưu
        r = goi("POST", f"{APS}/data/v1/projects/{project_id}/storage",
                headers={**self.dau, "Content-Type": "application/vnd.api+json"},
                data=json.dumps({
                    "jsonapi": {"version": "1.0"},
                    "data": {"type": "objects",
                             "attributes": {"name": f.name},
                             "relationships": {"target": {"data": {
                                 "type": "folders", "id": folder_id}}}}}))
        if r.status_code >= 400:
            return False, f"tạo chỗ lưu thất bại: {r.status_code} {r.text[:200]}"
        kho = r.json()["data"]["id"]
        bucket, obj = kho.split(":")[-1].split("/", 1)
        obj_q = requests.utils.quote(obj, safe="")

        # 2. xin liên kết ký sẵn
        d = self._get(f"/oss/v2/buckets/{bucket}/objects/{obj_q}/signeds3upload?parts=1")
        # 3. đẩy dữ liệu thẳng lên S3 (không kèm token)
        with open(f, "rb") as fh:
            ru = goi("PUT", d["urls"][0], data=fh)
        if ru.status_code >= 400:
            return False, f"đẩy dữ liệu thất bại: {ru.status_code}"
        # 4. chốt
        rc = goi("POST", f"{APS}/oss/v2/buckets/{bucket}/objects/{obj_q}/signeds3upload",
                 headers={**self.dau, "Content-Type": "application/json"},
                 data=json.dumps({"uploadKey": d["uploadKey"]}))
        if rc.status_code >= 400:
            return False, f"chốt tải lên thất bại: {rc.status_code} {rc.text[:200]}"

        # 5. đăng ký thành tài liệu trong thư mục
        r2 = goi("POST", f"{APS}/data/v1/projects/{project_id}/items",
                 headers={**self.dau, "Content-Type": "application/vnd.api+json"},
                 data=json.dumps({
                     "jsonapi": {"version": "1.0"},
                     "data": {
                         "type": "items",
                         "attributes": {"displayName": f.name,
                                        "extension": {"type": "items:autodesk.bim360:File",
                                                      "version": "1.0"}},
                         "relationships": {
                             "tip": {"data": {"type": "versions", "id": "1"}},
                             "parent": {"data": {"type": "folders", "id": folder_id}}}},
                     "included": [{
                         "type": "versions", "id": "1",
                         "attributes": {"name": f.name,
                                        "extension": {"type": "versions:autodesk.bim360:File",
                                                      "version": "1.0"}},
                         "relationships": {"storage": {"data": {"type": "objects",
                                                                "id": kho}}}}]}))
        if r2.status_code >= 400:
            # file đã tồn tại → cần tạo version mới thay vì item mới
            return False, (f"đăng ký tài liệu thất bại: {r2.status_code} "
                           f"{r2.text[:200]} (nếu file đã có, dùng --ghi-de-ban-moi)")
        return True, "xong"

    def issues(self, project_id):
        pid = project_id[2:] if project_id.startswith("b.") else project_id
        kq, offset = [], 0
        while True:
            d = self._get(f"/construction/issues/v1/projects/{pid}/issues"
                          f"?limit=100&offset={offset}")
            kq += d.get("results", [])
            if len(d.get("results", [])) < 100:
                break
            offset += 100
        return kq


# ----------------------------------------------------------------------------
# Nguồn REST chung — cho CDE nội bộ
# ----------------------------------------------------------------------------

class RestChung:
    """Client cho CDE nội bộ, mô tả bằng file JSON. Xem mẫu đầy đủ trong
    references/cau-hinh-cde.md. Rất gọn:

    {
      "ten": "CDE nội bộ",
      "goc": "https://ten-mien/api",
      "dang_nhap": {"duong_dan": "/auth/login", "kieu": "json",
                    "truong": {"username": "$ENV:CDE_USER", "password": "$ENV:CDE_PASS"},
                    "duong_token": "data.token"},
      "danh_sach": {"duong_dan": "/documents", "duong_ket_qua": "data.items"},
      "tai_len":   {"duong_dan": "/documents/upload", "truong_file": "file"}
    }
    """

    def __init__(self, duong_dan_cau_hinh):
        nap_env()
        self.ch = json.loads(Path(duong_dan_cau_hinh).read_text(encoding="utf-8"))
        self.goc = self.ch["goc"].rstrip("/")
        self.token = None
        if "dang_nhap" in self.ch:
            self.dang_nhap()

    @staticmethod
    def _giai(v):
        if isinstance(v, str) and v.startswith("$ENV:"):
            return bat_buoc_env(v[5:])
        return v

    @staticmethod
    def _lay_sau(d, duong):
        for phan in duong.split("."):
            if d is None:
                return None
            d = d.get(phan) if isinstance(d, dict) else None
        return d

    def dang_nhap(self):
        c = self.ch["dang_nhap"]
        truong = {k: self._giai(v) for k, v in c.get("truong", {}).items()}
        url = self.goc + c["duong_dan"]
        if c.get("kieu", "json") == "json":
            r = goi("POST", url, json=truong)
        else:
            r = goi("POST", url, data=truong)
        if r.status_code >= 400:
            raise SystemExit(f"❌ Đăng nhập CDE thất bại ({r.status_code}): {r.text[:300]}")
        self.token = self._lay_sau(r.json(), c.get("duong_token", "token"))
        if not self.token:
            raise SystemExit(f"❌ Không tìm thấy token theo đường "
                             f"'{c.get('duong_token')}' trong phản hồi.")
        print(f"✅ Đã đăng nhập {self.ch.get('ten', self.goc)}")

    @property
    def dau(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def danh_sach(self, tham_so=None):
        c = self.ch["danh_sach"]
        r = goi("GET", self.goc + c["duong_dan"], headers=self.dau, params=tham_so or {})
        if r.status_code >= 400:
            raise SystemExit(f"❌ {r.status_code}: {r.text[:300]}")
        d = r.json()
        duong = c.get("duong_ket_qua")
        return self._lay_sau(d, duong) if duong else d

    def tai_len(self, duong_dan_file, tham_so=None):
        c = self.ch["tai_len"]
        f = Path(duong_dan_file)
        with open(f, "rb") as fh:
            r = goi("POST", self.goc + c["duong_dan"], headers=self.dau,
                    files={c.get("truong_file", "file"): (f.name, fh)},
                    data=tham_so or {})
        return r.status_code < 400, f"{r.status_code} {r.text[:150]}"


# ----------------------------------------------------------------------------
# Lệnh CLI
# ----------------------------------------------------------------------------

def ghi_excel(df, duong_dan, sheet="Dữ liệu"):
    p = Path(duong_dan)
    p.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(p, engine="openpyxl") as w:
        df.to_excel(w, sheet_name=sheet[:31], index=False)
        ws = w.sheets[sheet[:31]]
        for i, c in enumerate(df.columns, 1):
            rong = max([len(str(c))] + [len(str(v)) for v in df[c].head(200).fillna("")])
            ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = \
                min(max(rong + 2, 10), 60)
        ws.freeze_panes = "A2"
    return p


def lenh_du_an(a):
    acc = ACC()
    hang = []
    for h in acc.hubs():
        ten_hub = h["attributes"]["name"]
        for d in acc.du_an(h["id"]):
            hang.append({"Hub": ten_hub, "Mã hub": h["id"],
                         "Dự án": d["attributes"]["name"], "Mã dự án": d["id"]})
    df = pd.DataFrame(hang)
    print(df.to_string(index=False) if len(df) else "Không có dự án nào.")
    print("\nGhi chú: mã dự án dùng cho lệnh 'cay'/'tai-ve' là mã có tiền tố 'b.'")
    if a.ra:
        print(f"→ {ghi_excel(df, a.ra, 'Dự án')}")


def _lay_thu_muc_goc(acc, du_an):
    for h in acc.hubs():
        for d in acc.du_an(h["id"]):
            if d["id"] == du_an:
                return acc.thu_muc_goc(h["id"], du_an)
    raise SystemExit(f"❌ Không tìm thấy dự án {du_an}. Chạy lệnh 'du-an' để xem danh sách.")


def lenh_cay(a):
    acc = ACC()
    if not a.thu_muc:
        goc = _lay_thu_muc_goc(acc, a.du_an)
        print("Các thư mục gốc của dự án:\n")
        for g in goc:
            print(f"   {g['attributes']['displayName']}\n      {g['id']}")
        print("\nChạy lại lệnh với --thu-muc <mã ở trên> để xem bên trong.")
        return
    ds = acc.duyet(a.du_an, a.thu_muc, toi_da=a.sau)
    df = pd.DataFrame(ds)
    tl = df[df["loai"] == "tài liệu"] if len(df) else df
    print(f"✅ {len(df)} mục ({len(tl)} tài liệu)")
    if len(df):
        print(df[["loai", "duong_dan"]].head(30).to_string(index=False))
    if a.ra:
        print(f"→ {ghi_excel(df, a.ra, 'Cây thư mục')}")


def lenh_dang_ky(a):
    acc = ACC()
    ds = acc.duyet(a.du_an, a.thu_muc, toi_da=a.sau)
    tl = [m for m in ds if m["loai"] == "tài liệu"]
    df = pd.DataFrame(tl)
    if len(df):
        df = df.rename(columns={
            "ten": "Tên tài liệu", "duong_dan": "Đường dẫn", "phien_ban": "Phiên bản",
            "sua_luc": "Sửa lúc", "nguoi_sua": "Người sửa", "kich_thuoc": "Dung lượng (byte)",
            "id": "Mã tài liệu"})
        df.insert(0, "STT", range(1, len(df) + 1))
        df = df.drop(columns=["loai"], errors="ignore")
    print(f"✅ Bảng đăng ký {len(df)} tài liệu → {ghi_excel(df, a.ra, 'Đăng ký tài liệu')}")


def lenh_tai_ve(a):
    acc = ACC()
    ds = [m for m in acc.duyet(a.du_an, a.thu_muc, toi_da=a.sau)
          if m["loai"] == "tài liệu"]
    if a.loc:
        ds = [m for m in ds if fnmatch.fnmatch(m["ten"].lower(), a.loc.lower())]
    if not ds:
        raise SystemExit("❌ Không có tài liệu nào khớp.")
    print(f"Sẽ tải {len(ds)} tài liệu về {a.ra}")
    if a.thu:
        for m in ds[:40]:
            print(f"   {m['duong_dan']}")
        print("(chạy thử — bỏ --thu để tải thật)")
        return
    goc = Path(a.ra)
    ok = loi = 0
    for i, m in enumerate(ds, 1):
        dich = goc / m["duong_dan"] if a.giu_cay else goc / m["ten"]
        thanh_cong, tin = acc.tai_ve(a.du_an, m["id"], dich)
        print(f"   [{i}/{len(ds)}] {'✓' if thanh_cong else '✗'} {m['ten']} — {tin}")
        ok, loi = (ok + 1, loi) if thanh_cong else (ok, loi + 1)
    print(f"✅ Tải xong {ok} file, lỗi {loi}")


def lenh_tai_len(a):
    files = [p for p in (Path(a.vao).glob("*") if Path(a.vao).is_dir()
                         else Path().glob(a.vao)) if p.is_file()]
    if not files:
        raise SystemExit("❌ Không có file nào để tải lên.")
    print(f"Sẽ tải lên {len(files)} file:")
    for f in files[:20]:
        print(f"   {f.name}  ({f.stat().st_size / 1e6:.2f} MB)")
    if a.thu:
        print("(chạy thử — bỏ --thu để tải thật)")
        return
    if a.nguon == "acc":
        acc = ACC()
        for i, f in enumerate(files, 1):
            ok, tin = acc.tai_len(a.du_an, a.thu_muc, f)
            print(f"   [{i}/{len(files)}] {'✓' if ok else '✗'} {f.name} — {tin}")
    else:
        cl = RestChung(a.cau_hinh)
        for i, f in enumerate(files, 1):
            ok, tin = cl.tai_len(f)
            print(f"   [{i}/{len(files)}] {'✓' if ok else '✗'} {f.name} — {tin}")


def lenh_issue(a):
    acc = ACC()
    ds = acc.issues(a.du_an)
    if not ds:
        raise SystemExit("❌ Không lấy được issue nào (kiểm tra quyền của ứng dụng).")
    hang = [{
        "Mã": m.get("displayId"), "Tiêu đề": m.get("title"),
        "Trạng thái": m.get("status"), "Loại": m.get("issueTypeId"),
        "Mức độ": m.get("rootCauseId"),
        "Giao cho": m.get("assignedTo"),
        "Hạn xử lý": (m.get("dueDate") or "")[:10],
        "Tạo lúc": (m.get("createdAt") or "")[:10],
        "Đóng lúc": (m.get("closedAt") or "")[:10],
        "Vị trí": m.get("locationDetails"),
        "Mô tả": (m.get("description") or "")[:500],
    } for m in ds]
    df = pd.DataFrame(hang)
    ra = ghi_excel(df, a.ra, "Issue")
    print(f"✅ {len(df)} issue → {ra}")
    if "Trạng thái" in df:
        print("\nTheo trạng thái:")
        print(df["Trạng thái"].value_counts().to_string())
    qua_han = df[(df["Hạn xử lý"] != "") & (df["Trạng thái"].isin(["open", "in_progress"]))]
    if len(qua_han):
        print(f"\n⚠️  {len(qua_han)} issue còn mở có gắn hạn xử lý — soát lại trước họp giao ban.")


def main():
    p = argparse.ArgumentParser(
        description="cde — làm việc với CDE qua API",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = p.add_subparsers(dest="lenh", required=True)

    def chung(s, can_du_an=True):
        s.add_argument("--nguon", default="acc", choices=["acc", "rest"])
        s.add_argument("--cau-hinh", default="", help="File JSON khi --nguon rest")
        if can_du_an:
            s.add_argument("--du-an", default="", help="Mã dự án (có tiền tố b.)")

    s = sub.add_parser("du-an", help="Liệt kê hub và dự án")
    chung(s, False)
    s.add_argument("--ra", default="")
    s.set_defaults(func=lenh_du_an)

    s = sub.add_parser("cay", help="Xem cây thư mục")
    chung(s)
    s.add_argument("--thu-muc", default="")
    s.add_argument("--sau", type=int, default=4)
    s.add_argument("--ra", default="")
    s.set_defaults(func=lenh_cay)

    s = sub.add_parser("dang-ky", help="Xuất bảng đăng ký tài liệu")
    chung(s)
    s.add_argument("--thu-muc", required=True)
    s.add_argument("--sau", type=int, default=6)
    s.add_argument("--ra", required=True)
    s.set_defaults(func=lenh_dang_ky)

    s = sub.add_parser("tai-ve", help="Tải hàng loạt tài liệu")
    chung(s)
    s.add_argument("--thu-muc", required=True)
    s.add_argument("--ra", required=True)
    s.add_argument("--loc", default="", help='Lọc tên, ví dụ "*.pdf"')
    s.add_argument("--sau", type=int, default=6)
    s.add_argument("--giu-cay", action="store_true", help="Giữ nguyên cấu trúc thư mục")
    s.add_argument("--thu", action="store_true", help="Chạy thử, chưa tải")
    s.set_defaults(func=lenh_tai_ve)

    s = sub.add_parser("tai-len", help="Tải hàng loạt file lên")
    chung(s)
    s.add_argument("--vao", required=True)
    s.add_argument("--thu-muc", default="")
    s.add_argument("--thu", action="store_true")
    s.set_defaults(func=lenh_tai_len)

    s = sub.add_parser("issue", help="Xuất Issue/RFI ra Excel")
    chung(s)
    s.add_argument("--ra", required=True)
    s.set_defaults(func=lenh_issue)

    a = p.parse_args()
    if getattr(a, "nguon", "acc") == "rest" and not a.cau_hinh:
        raise SystemExit("❌ --nguon rest cần kèm --cau-hinh <file.json>")
    a.func(a)


if __name__ == "__main__":
    main()
