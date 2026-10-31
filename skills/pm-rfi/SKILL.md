---
name: "PM - RFI & sổ bản vẽ"
description: "Sổ RFI, hồ sơ trình duyệt, sổ đăng ký bản vẽ; theo dõi hạn trả lời, nhắc và leo thang khi RFI quá hạn."
group: Xây dựng
source: ChineduNlem/claude-civil-pm-skills@b8d2a2a (MIT, đã duyệt và điều chỉnh 2026-10-09)
---

# PM RFI

## Khi nào dùng

RFI and submittal management for large civil engineering projects. Triggers on any request for information, design query, drawing discrepancy, or document submittal requiring review and approval. Also triggers when pm-orchestrator routes a DESIGN-EVENT, or when pm-investigate or pm-quality identifies a design input requirement. Manages the RFI register, tracks response times, escalates overdue items, and flags contractual implications of late design responses.

> **Ghi chú điều chỉnh (2026-10-09):** skill gốc của ChineduNlem/claude-civil-pm-skills@b8d2a2a (MIT, xem `LICENSE`), viết cho dự án ở Nigeria. Đã bỏ tên công ty và tên tác giả. Các skill `pm-orchestrator`, `pm-state`, `pm-careful` KHÔNG được cài. Khi văn bản nhắc `pm-programme` thì dùng `tien-do-san-luong`; `pm-cost` dùng `qs-khoi-luong-du-toan`; `pm-quality` dùng `qc-nghiem-thu-ho-so`. Áp dụng theo pháp luật và tiêu chuẩn Việt Nam; viết đầu ra bằng tiếng Việt.

Request for Information and submittal management. Open → route → track →
escalate → close.

---

## When to Raise an RFI

Raise an RFI when:
- A drawing is missing information required for construction
- Two drawings or specifications conflict
- Site conditions differ from design assumptions
- Contractor needs clarification before proceeding
- A design change is required due to site finding or client instruction
- An NCR has a potential design cause (route from `pm-quality`)
- A site anomaly requires design input (route from `pm-investigate`)

**Rule:** Never instruct a contractor to proceed on the basis of a verbal
design clarification. Open an RFI first. The RFI creates the paper trail.

---

## RFI Record

```
RFI RECORD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID:               RFI-[NNN]
Date raised:      [date]
Raised by:        [contractor / PM / [PM]]
Priority:         [URGENT - work stopped / NORMAL / LOW]
  Urgent: response required within [N] days - state contractual deadline
  Normal: response required within [N] days per contract

Description:
  Drawing / spec ref: [document number and revision]
  Location: [WBS ref + physical location]
  Question: [specific, one question per RFI - split multi-questions]

Attachments:
  [ ] Sketch / photo
  [ ] Extract from drawing
  [ ] Contractor's proposed solution (if any)

Routed to:        [designer / structural engineer / client / specialist]
Date routed:      [date]
Response due:     [date - per contract or agreed]

Response received: [date]
Response ref:      [document number]
Response summary:  [what was decided]

Contractual implication:
  [ ] No impact
  [ ] Variation likely - route to pm-cost
  [ ] Extension of time likely - route to pm-programme
  [ ] Design change - update drawing register

Closed by: [name]
Close date: [date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## RFI Register

Track all RFIs in a register. Surface overdue items to orchestrator:

| RFI-ID | Date raised | Priority | Routed to | Response due | Days outstanding | Status |
|---|---|---|---|---|---|---|
| RFI-001 | | URGENT | Designer | | | OPEN |

**Overdue thresholds (flag to orchestrator):**
- URGENT: overdue by 1 day → 🔴 IMMEDIATE alert
- NORMAL: overdue by 3 days → 🟡 THIS WEEK alert
- LOW: overdue by 7 days → 🔵 LOG alert

---

## Late Response - Contractual Implications

When a designer or client response is late:

1. **Day 1 overdue:** Issue a reminder (route via `pm-report` COM log)
2. **Day 3 overdue (NORMAL) / Day 1 (URGENT):** Formal notice of delay to
   the responding party - this creates the paper trail for any EOT claim
3. **Day 7 overdue:** Notify [PM] - consider whether the contractor is
   entitled to claim extension of time or additional cost due to late
   information
4. **Work stopped due to late RFI:** Immediately notify client and route
   to `pm-programme` for delay analysis

```
LATE RFI NOTICE
Ref: [COM-ID]
To: [designer / client]
Re: RFI-[NNN] - [description]

This RFI was issued on [date] with a required response date of [date].
As at [today's date], no response has been received. The contractor
[is / is not] currently stopped pending this response.

Please provide your response urgently. Continued delay may result in
an extension of time claim and/or additional cost claim by the contractor,
for which [client / employer] may be liable.

Prepared by: [PM]
```

---

## Drawing Register

Maintain a live register of current drawing revisions:

| Drawing No | Title | Current Rev | Date | Status | Superseded Rev |
|---|---|---|---|---|---|
| S-001 | Foundation Plan | Rev C | | AFC | Rev B |

**AFC = Approved for Construction.** Only AFC drawings may be used on site.
When a revised drawing is issued, immediately notify site and confirm old
revision is withdrawn. Any NCR caused by use of a superseded drawing is a
site management failure - log in `pm-quality`.

---

## RFI Summary (for pm-report)

```
RFI SUMMARY FOR REPORT:
  RFIs raised this period:    [N]
  RFIs closed this period:    [N]
  Total open RFIs:            [N]
  Overdue RFIs:               [N] - oldest [N days]
  RFIs with EOT implication:  [N]
  RFIs with cost implication: [N]
```
