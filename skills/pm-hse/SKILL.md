---
name: "PM - An toàn lao động (HSE)"
description: "Quản lý an toàn, môi trường công trường: kế hoạch HSE, biện pháp và đánh giá rủi ro công việc nguy hiểm, sự cố, near-miss."
group: Xây dựng
source: ChineduNlem/claude-civil-pm-skills@b8d2a2a (MIT, đã duyệt và điều chỉnh 2026-10-09)
---

# PM HSE

## Khi nào dùng

Health, safety, and environment management for large civil engineering projects. Triggers on any HSE event: incident, near-miss, unsafe condition, environmental release, safety observation, or method statement review. Also triggers when pm-orchestrator routes an HSE-EVENT. Manages the safety plan, incident register, method statement review, toolbox talk records, and statutory reporting obligations.

> **Ghi chú điều chỉnh (2026-10-09):** skill gốc của ChineduNlem/claude-civil-pm-skills@b8d2a2a (MIT, xem `LICENSE`), viết cho dự án ở Nigeria. Đã bỏ tên công ty và tên tác giả. Các skill `pm-orchestrator`, `pm-state`, `pm-careful` KHÔNG được cài. Khi văn bản nhắc `pm-programme` thì dùng `tien-do-san-luong`; `pm-cost` dùng `qs-khoi-luong-du-toan`; `pm-quality` dùng `qc-nghiem-thu-ho-so`. Áp dụng theo pháp luật và tiêu chuẩn Việt Nam; viết đầu ra bằng tiếng Việt.

Health, safety, and environment management for civil engineering projects.
Safety plan → method statement review → incident management → statutory
reporting.

**RULE: Any incident with injury, fatality, or environmental release is an
IMMEDIATE escalation to [PM]. No communication to regulators or client
before [PM] has reviewed the facts.**

---

## HSE Plan Essentials

Set up at project start. Minimum required elements:

| Element | Status |
|---|---|
| Project HSE Plan (site-specific) | [ ] Prepared / [ ] Client approved |
| Emergency Response Plan | [ ] Prepared |
| Site-specific risk assessment | [ ] Prepared |
| First Aid provisions confirmed | [ ] |
| PPE requirements defined | [ ] |
| Site induction programme | [ ] Prepared |
| Method statements for high-risk activities | [ ] Identified / [ ] Prepared |
| Environmental controls (waste, water, noise) | [ ] Identified |
| Regulatory notifications (if applicable) | [ ] Filed |

---

## High-Risk Activity Method Statements

These activities require a written Method Statement and Risk Assessment
(MSRA) before work commences. Flag any that apply to this project:

- Excavation > 1.2m depth
- Formwork and falsework
- Working at height (> 2m)
- Crane and lifting operations
- Confined space entry
- Demolition works
- Electrical isolation (LV or HV)
- Hot work (welding, cutting, grinding)
- Hazardous materials handling (asbestos, lead paint, fuel)
- Piling operations

For each applicable activity:
```
MSRA RECORD
  Activity: [description]
  MSRA prepared: [yes/no - date]
  MSRA reviewed by PM: [yes/no - date]
  MSRA approved by client: [yes/no - date, if required]
  Toolbox talk conducted: [yes/no - date, attendees]
  Permit to work required: [yes/no - permit type]
```

---

## Incident Classification

| Class | Description | Immediate action |
|---|---|---|
| FATALITY | Death on site or caused by site activity | STOP ALL WORK. [PM] + client within 1 hour. Regulator within 24 hours. Preserve scene. |
| SERIOUS INJURY | Lost time injury, hospitalisation, permanent disability | STOP affected work. [PM] + client same day. Regulator as required. |
| MINOR INJURY | First aid treatment, no lost time | First aid administered, logged, reported to site manager |
| NEAR-MISS | Potential for injury but no injury occurred | Investigate within 24 hours - near-misses predict future incidents |
| UNSAFE CONDITION | Hazard identified before incident | Correct immediately or isolate. Log and report. |
| ENVIRONMENTAL | Spill, discharge, noise/dust exceedance | Contain, report to PM, notify client and regulator as required |

---

## Incident Record

```
INCIDENT RECORD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID:               INC-[NNN]
Date/time:        [date and time]
Location:         [WBS ref + physical description]
Class:            [FATALITY / SERIOUS INJURY / MINOR INJURY / NEAR-MISS /
                   UNSAFE CONDITION / ENVIRONMENTAL]
Persons involved: [name, role, contractor - anonymise for external reports]
Description:      [what happened - factual, no blame language]
Immediate action taken: [first aid, area isolated, equipment stopped, etc.]

Root cause investigation:
  Route to pm-investigate for all SERIOUS INJURY, FATALITY, and NEAR-MISS

Contributing factors: [after investigation]
Corrective action: [specific, owner, date]
Preventive action: [systemic change to prevent recurrence]

Statutory reporting required: [yes/no - which body - deadline]
Client notification required: [yes/no - deadline]
Reported by: [name]
Report date: [date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Statutory Reporting (Việt Nam)

Bảng khai báo gốc theo luật nước ngoài đã được gỡ. Ở Việt Nam, khai báo và điều tra tai nạn lao động
theo Luật An toàn, vệ sinh lao động 2015 và các văn bản hướng dẫn; sự cố công trình theo quy định về
quản lý chất lượng thi công hiện hành (Nghị định 207/2026/NĐ-CP từ 01/7/2026). Cơ quan nhận khai báo và
thời hạn: tra lại văn bản đang có hiệu lực trước khi dùng (cần xác minh), không tự điền.

Mọi khai báo ra cơ quan nhà nước phải được [PM] duyệt trước khi gửi.

---

## Toolbox Talk Register

Weekly minimum. Log:

| Date | Topic | Conducted by | Attendees (N) | Sign-off sheet filed |
|---|---|---|---|---|

---

## HSE Summary (for pm-report)

```
HSE SUMMARY FOR REPORT:
  Incidents this period:      FATALITY [N]  SERIOUS [N]  MINOR [N]
  Near-misses this period:    [N]
  Unsafe conditions reported: [N resolved / N open]
  Lost Time Injury (LTI):     [N]
  LTI Frequency Rate (LTIFR): [if tracked - (LTIs × 200,000) / man-hours]
  Toolbox talks conducted:    [N]
  Method statements approved: [N]
  Open HSE actions:           [N]
```
