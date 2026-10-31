---
name: "PM - Quản lý rủi ro"
description: "Sổ đăng ký rủi ro dự án: nhận diện, chấm điểm ma trận 5x5, giao người xử lý, giảm thiểu, leo thang, đóng rủi ro."
group: Xây dựng
source: ChineduNlem/claude-civil-pm-skills@b8d2a2a (MIT, đã duyệt và điều chỉnh 2026-10-09)
---

# PM Risk

## Khi nào dùng

Risk register management for large civil engineering projects. Triggers on any risk identification, risk update, risk materialisation, or request to review the risk register. Also triggers when pm-orchestrator routes a RISK-EVENT, or when any other skill (pm-investigate, pm-cost, pm-programme) identifies a risk implication. Manages the full risk lifecycle: identify, score, assign, mitigate, monitor, escalate, close.

> **Ghi chú điều chỉnh (2026-10-09):** skill gốc của ChineduNlem/claude-civil-pm-skills@b8d2a2a (MIT, xem `LICENSE`), viết cho dự án ở Nigeria. Đã bỏ tên công ty và tên tác giả. Các skill `pm-orchestrator`, `pm-state`, `pm-careful` KHÔNG được cài. Khi văn bản nhắc `pm-programme` thì dùng `tien-do-san-luong`; `pm-cost` dùng `qs-khoi-luong-du-toan`; `pm-quality` dùng `qc-nghiem-thu-ho-so`. Áp dụng theo pháp luật và tiêu chuẩn Việt Nam; viết đầu ra bằng tiếng Việt.

Risk register management for civil engineering projects. Full lifecycle:
identify → score → assign → mitigate → monitor → escalate → close.

---

## Risk Register Format

Each risk record:

```
RISK RECORD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID:               R-[NNN]
Category:         [TECHNICAL / COMMERCIAL / PROGRAMME / HSE / REGULATORY / EXTERNAL]
Description:      [what could happen and what the consequence would be]
Probability:      [1–5]  1=Rare  3=Possible  5=Almost certain
Impact:           [1–5]  1=Negligible  3=Significant  5=Critical
Risk Score:       [P × I = score]
Rating:           [LOW 1–6 / MEDIUM 7–12 / HIGH 13–19 / CRITICAL 20–25]
Owner:            [name / role]
Status:           [OPEN / MITIGATING / ESCALATED / CLOSED]
Identified:       [date]
Last reviewed:    [date]

Mitigation action: [what is being done to reduce probability or impact]
Residual score after mitigation: [P × I]
Contingency (if risk materialises): [pre-agreed response]
Early warning indicators: [what to watch for]
```

---

## Risk Scoring Matrix

| | **Impact 1** | **Impact 2** | **Impact 3** | **Impact 4** | **Impact 5** |
|---|---|---|---|---|---|
| **Prob 5** | 5 MED | 10 MED | 15 HIGH | 20 CRIT | 25 CRIT |
| **Prob 4** | 4 LOW | 8 MED | 12 MED | 16 HIGH | 20 CRIT |
| **Prob 3** | 3 LOW | 6 MED | 9 MED | 12 MED | 15 HIGH |
| **Prob 2** | 2 LOW | 4 LOW | 6 MED | 8 MED | 10 MED |
| **Prob 1** | 1 LOW | 2 LOW | 3 LOW | 4 LOW | 5 MED |

**Escalation thresholds:**
- CRITICAL (20–25): Escalate to [PM] immediately. Client notification required.
- HIGH (13–19): Mitigation plan required within 48 hours. Review weekly.
- MEDIUM (7–12): Mitigation plan required. Review monthly.
- LOW (1–6): Monitor. Review at milestone.

---

## Initial Risk Register (Civil Project Template)

Seed these risks at project start. Score and assign for each project:

| ID | Description | Category | Default Probability |
|---|---|---|---|
| R-001 | Ground conditions worse than anticipated | TECHNICAL | 3 |
| R-002 | Design changes during construction | TECHNICAL | 3 |
| R-003 | Contractor programme delay | PROGRAMME | 3 |
| R-004 | Material price escalation | COMMERCIAL | 2 |
| R-005 | Client payment delay | COMMERCIAL | 3 |
| R-006 | Regulatory approval delay | REGULATORY | 2 |
| R-007 | Scope increase not captured as variation | COMMERCIAL | 3 |
| R-008 | HSE incident on site | HSE | 2 |
| R-009 | Key personnel unavailability | PROGRAMME | 2 |
| R-010 | Third-party utility clash | TECHNICAL | 2 |

---

## Risk Review Protocol

At each reporting cycle:
1. Review all OPEN risks - update probability, impact, mitigation status
2. Check early warning indicators for HIGH and CRITICAL risks
3. Close any risks that are no longer applicable
4. Add any new risks identified this period
5. Flag any risk that has escalated in score since last review

Output a risk summary for inclusion in `pm-report`:
```
RISK SUMMARY FOR REPORT:
  Total open risks: [N]
  CRITICAL: [N]  HIGH: [N]  MEDIUM: [N]  LOW: [N]
  New this period: [N]
  Closed this period: [N]
  Top 3 risks: [R-ID, description, score, mitigation status]
```
