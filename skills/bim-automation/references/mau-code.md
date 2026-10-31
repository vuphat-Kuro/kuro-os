# Mẫu code khởi điểm

Các khung code dưới đây là điểm xuất phát, không phải giải pháp hoàn chỉnh. Kiểm tra lại tên API theo phiên bản phần mềm người dùng đang chạy - API Revit và Tekla thay đổi giữa các đời, và một số lớp bị đổi tên hoặc bỏ đi.

## Python node trong Dynamo (CPython3)

```python
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

doc = DocumentManager.Instance.CurrentDBDocument

# ==== Cấu hình ====
TEN_THAM_SO = "Ma_cong_tac"
CHAY_THU = True          # True: chỉ liệt kê, không ghi vào mô hình

# ==== Đầu vào từ node ====
elements = UnwrapElement(IN[0]) if isinstance(IN[0], list) else [UnwrapElement(IN[0])]

ok, bo_qua, loi = [], [], []

if not CHAY_THU:
    TransactionManager.Instance.EnsureInTransaction(doc)

for el in elements:
    try:
        p = el.LookupParameter(TEN_THAM_SO)
        if p is None or p.IsReadOnly:
            bo_qua.append(el.Id.IntegerValue)
            continue
        if CHAY_THU:
            ok.append((el.Id.IntegerValue, p.AsString()))
        else:
            p.Set("...")           # giá trị cần ghi
            ok.append(el.Id.IntegerValue)
    except Exception as e:
        loi.append((el.Id.IntegerValue, str(e)))

if not CHAY_THU:
    TransactionManager.Instance.TransactionTaskDone()

OUT = {"thanh_cong": len(ok), "bo_qua": bo_qua, "loi": loi, "chi_tiet": ok}
```

Điểm cần giữ: chế độ chạy thử, bắt lỗi theo từng phần tử, và trả về thống kê thay vì trả về danh sách thô.

## Thu thập phần tử hiệu quả (Revit API)

```python
# Đúng: lọc ngay ở collector
collector = (FilteredElementCollector(doc)
             .OfCategory(BuiltInCategory.OST_StructuralFraming)
             .WhereElementIsNotElementType())

# Lọc theo view hiện hành
collector_view = (FilteredElementCollector(doc, doc.ActiveView.Id)
                  .OfCategory(BuiltInCategory.OST_Walls)
                  .WhereElementIsNotElementType())

# Lọc theo giá trị tham số (nhanh hơn nhiều so với lặp Python)
rule = ParameterFilterRuleFactory.CreateEqualsRule(
    ElementId(BuiltInParameter.ALL_MODEL_MARK), "TRU-P4", False)
collector_param = (FilteredElementCollector(doc)
                   .WherePasses(ElementParameterFilter(rule))
                   .WhereElementIsNotElementType())
```

## Chuyển đổi đơn vị

```python
from Autodesk.Revit.DB import UnitUtils, UnitTypeId

mm  = UnitUtils.ConvertFromInternalUnits(gia_tri_noi_bo, UnitTypeId.Millimeters)
m3  = UnitUtils.ConvertFromInternalUnits(the_tich_noi_bo, UnitTypeId.CubicMeters)
noi_bo = UnitUtils.ConvertToInternalUnits(1500, UnitTypeId.Millimeters)
```

Không nhân hệ số 304.8 thủ công. Hệ số cứng sống sót qua nhiều lần copy-paste rồi sai ở chỗ không ai ngờ.

## Một transaction cho cả lô (C#)

```csharp
using (Transaction t = new Transaction(doc, "Cap nhat tham so hang loat"))
{
    t.Start();
    foreach (Element el in elements)
    {
        try
        {
            Parameter p = el.LookupParameter("Ma_cong_tac");
            if (p != null && !p.IsReadOnly) p.Set(giaTri);
        }
        catch (Exception ex)
        {
            log.Add($"{el.Id}: {ex.Message}");   // ghi log, không dừng vòng lặp
        }
    }
    t.Commit();
}
```

## Tekla Open API - khung cơ bản (C#)

```csharp
using Tekla.Structures.Model;
using Tekla.Structures.Geometry3d;

Model model = new Model();
if (!model.GetConnectionStatus())
    throw new Exception("Khong ket noi duoc toi Tekla. Kiem tra model dang mo.");

Beam dam = new Beam
{
    StartPoint = new Point(0, 0, 0),
    EndPoint   = new Point(12000, 0, 0),   // Tekla dung mm
    Profile    = { ProfileString = "..." },
    Material   = { MaterialString = "..." },
    Class      = "..."
};

if (dam.Insert())
    model.CommitChanges();     // thieu dong nay thi thay doi khong duoc luu
```

Sau khi tạo hàng loạt cấu kiện, chạy lại numbering trước khi xuất bản vẽ chế tạo.

## Đọc Excel để dựng cấu kiện

Luồng nên theo:

1. Đọc toàn bộ vùng dữ liệu một lần thành mảng hai chiều.
2. Kiểm tra dữ liệu **trước khi** tạo bất cứ thứ gì: đủ cột bắt buộc, kiểu dữ liệu đúng, không có ô trống ở cột bắt buộc, giá trị nằm trong dải hợp lý.
3. In ra bảng tóm tắt số dòng hợp lệ / lỗi và dừng lại nếu có lỗi.
4. Chỉ khi dữ liệu sạch mới mở transaction và tạo cấu kiện.
5. Ghi ngược ElementId vào một cột kết quả để lần chạy sau biết dòng nào đã tạo rồi.

Bước 2 và 5 là thứ phân biệt script dùng được lâu dài với script chạy một lần rồi bỏ.

## Kiểm tra chất lượng dữ liệu mô hình - khung báo cáo

```python
# ==== Cấu hình ====
THAM_SO_BAT_BUOC = ["Ma_cong_tac", "Hang_muc", "Mac_be_tong"]
GIA_TRI_HOP_LE = {"Mac_be_tong": ["...", "..."]}

bao_cao = []
for el in elements:
    for ten in THAM_SO_BAT_BUOC:
        p = el.LookupParameter(ten)
        gt = p.AsString() if p else None
        if not gt:
            bao_cao.append((el.Id.IntegerValue, ten, "TRONG"))
        elif ten in GIA_TRI_HOP_LE and gt not in GIA_TRI_HOP_LE[ten]:
            bao_cao.append((el.Id.IntegerValue, ten, f"KHONG HOP LE: {gt}"))

OUT = bao_cao   # xuat ra Excel de nhay toi tung ElementId
```
