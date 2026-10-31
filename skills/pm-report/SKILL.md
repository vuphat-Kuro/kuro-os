---
name: "PM - Báo cáo & biên bản họp"
description: "Báo cáo tiến độ tuần/tháng cho chủ đầu tư, biên bản họp, sổ theo dõi việc cần làm và nhật ký công văn đi đến."
group: Xây dựng
source: ChineduNlem/claude-civil-pm-skills@b8d2a2a (MIT, đã duyệt và điều chỉnh 2026-10-09)
---

# PM Report

## Khi nào dùng

Stakeholder reporting and communications management for large civil engineering projects. Triggers on any reporting request, client communication, meeting that needs minutes, or action that needs logging. Also triggers when pm-orchestrator routes CLIENT-COMMS, CONTRACTOR-COMMS, or REPORTING events. Produces weekly and monthly progress reports by pulling summaries from pm-programme, pm-cost, pm-risk, pm-quality, and pm-hse. Manages the action register and communication log.

> **Ghi chú điều chỉnh (2026-10-09):** skill gốc của ChineduNlem/claude-civil-pm-skills@b8d2a2a (MIT, xem `LICENSE`), viết cho dự án ở Nigeria. Đã bỏ tên công ty và tên tác giả. Các skill `pm-orchestrator`, `pm-state`, `pm-careful` KHÔNG được cài. Khi văn bản nhắc `pm-programme` thì dùng `tien-do-san-luong`; `pm-cost` dùng `qs-khoi-luong-du-toan`; `pm-quality` dùng `qc-nghiem-thu-ho-so`. Áp dụng theo pháp luật và tiêu chuẩn Việt Nam; viết đầu ra bằng tiếng Việt.

Stakeholder reporting and communications management. Pulls data from all
other PM skills. Produces progress reports, meeting minutes, and formal
correspondence.

---

## Report Types

| Type | Frequency | Audience | Sections |
|---|---|---|---|
| Weekly Progress Report | Weekly | Client PM + site team | Progress, programme, issues, next week plan |
| Monthly Progress Report | Monthly | Client management | Full: progress, programme, cost, risk, quality, HSE |
| Site Instruction Log | Ongoing | Site team | All client and PM instructions issued |
| Meeting Minutes | Per meeting | All attendees | Agenda, discussions, decisions, actions |
| Formal Correspondence | As required | Client, contractors, regulators | Letter format, project ref number |

---

## Monthly Progress Report Structure

Pull from each skill using their summary outputs:

```
[PROJECT NAME]
MONTHLY PROGRESS REPORT
Report No: [N]
Period: [month/year]
Date: [issue date]
Ref: [MA-DU-AN]/RPT/YYYY/NNN

1. EXECUTIVE SUMMARY
   [3–5 sentences: overall project status, key achievement this period,
   key issue or risk, outlook for next period]
   Overall status: [GREEN - on track / AMBER - at risk / RED - delayed or over budget]

2. PROGRESS THIS PERIOD
   [from pm-programme: % complete, activities completed, milestones achieved]

3. PROGRAMME STATUS
   [from pm-programme: milestone table, critical path status, SPI, delay summary]
   Forecast completion: [date]
   Variance from baseline: [+/− N days]

4. COST STATUS
   [from pm-cost: contract sum, variations, forecast final account, invoices]
   Budget status: [GREEN / AMBER / RED]

5. RISK REGISTER SUMMARY
   [from pm-risk: top 3 risks, new risks, closed risks]

6. QUALITY
   [from pm-quality: hold points, NCRs, material submittals]

7. HEALTH, SAFETY AND ENVIRONMENT
   [from pm-hse: incidents, near-misses, LTI status, toolbox talks]

8. ISSUES AND DECISIONS REQUIRED
   [items requiring client decision or action - numbered, with deadline]

9. PROGRAMME FOR NEXT PERIOD
   [key activities planned for the next reporting period]

10. ATTACHMENTS
    [ ] Updated programme (Gantt)
    [ ] Photograph record
    [ ] Site instruction log
    [ ] NCR register
    [ ] Risk register
```

---

## Communication Log

Every formal communication in or out is logged:

| Com-ID | Date | Direction | From | To | Subject | Ref | Response required by | Response received |
|---|---|---|---|---|---|---|---|---|
| COM-001 | | IN | Client | [PM] | | | | |
| COM-002 | | OUT | [PM] | Client | | [MA-DU-AN]/LTR/YYYY/001 | | |

**Rule:** Every communication that carries an instruction, a claim, a
notice, or a decision must be logged. Verbal instructions must be confirmed
in writing within 24 hours.

---

## Action Register

Every meeting, site visit, or communication generates actions:

| Act-ID | Source | Description | Owner | Due date | Status | Closed date |
|---|---|---|---|---|---|---|
| ACT-001 | Meeting 001 | | [PM] | | OPEN | |

Surface all overdue actions in the orchestrator's proactive alerts.

---

## Meeting Minutes Format

```
MEETING MINUTES
Project: [name]
Meeting: [type - site meeting / progress meeting / design meeting]
Date: [date]
Location: [venue]
Ref: [MA-DU-AN]/MOM/YYYY/NNN

ATTENDEES:
  [Name - Organisation - Role]

AGENDA ITEMS:
  1. [item] - [discussion summary] - [decision if any]
  2. ...

ACTIONS ARISING:
  [ACT-ID] - [description] - [Owner] - [Due date]

NEXT MEETING: [date / TBD]

Prepared by: [PM]
Issued to: [distribution list]
```

---

## Status Colour Codes

Apply to every report:

| Colour | Meaning |
|---|---|
| 🟢 GREEN | On track - no significant issues |
| 🟡 AMBER | At risk - issues identified, mitigation in place, monitoring required |
| 🔴 RED | Off track - client notification required, recovery plan needed |

Apply GREEN/AMBER/RED to: overall project, programme, cost, quality, HSE
independently. A project can be GREEN on cost and RED on programme.
