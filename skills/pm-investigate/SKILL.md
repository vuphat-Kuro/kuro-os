---
name: "PM - Điều tra nguyên nhân sự cố"
description: "Điều tra nguyên nhân gốc của nứt, lún, khuyết tật, kết quả NDT bất thường trước khi đề xuất sửa chữa. Không sửa khi chưa rõ nguyên nhân."
group: Xây dựng
source: ChineduNlem/claude-civil-pm-skills@b8d2a2a (MIT, đã duyệt và điều chỉnh 2026-10-09)
---

# PM Investigate

## Khi nào dùng

Use this skill for ALL structural and NDT root cause investigations. Triggers on any report of anomaly, defect, failure, or unexpected finding - including cracking, settlement, corrosion mapping discrepancies, ultrasonic anomalies, load test deviations, weld defect patterns, tank calibration errors, or any situation where the phrase "why is this happening", "what caused this", "investigate this", or "root cause" appears. Also triggers when the user describes a structural or inspection finding without an explanation. NEVER proceed to a remediation recommendation without first completing this investigation protocol. The iron law: no remedy without root cause first.

> **Ghi chú điều chỉnh (2026-10-09):** skill gốc của ChineduNlem/claude-civil-pm-skills@b8d2a2a (MIT, xem `LICENSE`), viết cho dự án ở Nigeria. Đã bỏ tên công ty và tên tác giả. Các skill `pm-orchestrator`, `pm-state`, `pm-careful` KHÔNG được cài. Khi văn bản nhắc `pm-programme` thì dùng `tien-do-san-luong`; `pm-cost` dùng `qs-khoi-luong-du-toan`; `pm-quality` dùng `qc-nghiem-thu-ho-so`. Áp dụng theo pháp luật và tiêu chuẩn Việt Nam; viết đầu ra bằng tiếng Việt.

Systematic root cause investigation for structural anomalies, NDT findings,
and inspection defects. Adapted from the gstack `/investigate` methodology
for the project's engineering practice.

**IRON LAW: No remediation recommendation, no repair specification, no client
communication about fixes - until root cause is confirmed. Treating symptoms
creates cascading failures. Every unresolved root cause makes the next finding
harder to interpret.**

---

## Phase 1 - Symptom Gathering

Before forming any hypothesis, collect all available evidence.

### 1.1 Physical Observations
Ask for or extract:
- Location, distribution, and pattern of the defect (isolated vs. systematic)
- Dimensions: extent, depth (if measurable), orientation
- Visual characteristics: colour, texture, geometry (e.g. map cracking vs. diagonal
  shear crack, uniform corrosion vs. pitting)
- Age and progression: when first observed, any change since?
- Environmental context: exposure zone, drainage, loading history

### 1.2 Drawings and Records Review
Check:
- Original design drawings - specified materials, loadings, details
- As-built record (if available) - deviations from design
- Previous inspection reports - any prior findings at this location?
- Construction records - pour sequence, curing method, weld procedures, NDT certs
- Maintenance history - any prior repairs, coatings, interventions?

### 1.3 NDT Data Review
Compile available data:
- Rebound hammer readings (carbonation depth, surface hardness)
- Cover meter / rebar scan results
- UPV readings (velocity, signal quality)
- Half-cell potential maps (if corrosion investigation)
- Ultrasonic thickness readings (for steel / tank walls)
- Visual inspection photos

Flag any data gaps at this stage. Do not proceed to hypothesis if critical
data is missing - state what additional testing is needed first.

---

## Phase 2 - Prior Investigation Check

Before forming a new hypothesis, check:
- Has this location or element been investigated before?
- Are there recurring findings at this element type across the project or site?
- Recurring defects in the same area are an architectural / construction / design
  smell - note patterns.

If prior investigation records exist, document:
```
PRIOR INVESTIGATION NOTE:
  Location: [element/zone]
  Date of prior investigation: [date]
  Prior root cause finding: [summary]
  Prior remedy applied: [yes/no, description]
  Current status vs. prior: [same / worse / new location]
```

---

## Phase 3 - Hypothesis Formation

Generate **2–3 candidate hypotheses**, ranked by probability based on evidence.

For each hypothesis:

```
HYPOTHESIS [N]:
  Proposed root cause: [mechanism]
  Supporting evidence: [list observations that support this]
  Contradicting evidence: [list observations that conflict with this]
  Probability: [HIGH / MEDIUM / LOW]
  Distinguishing test: [what single test would confirm or rule this out]
```

### Common Root Cause Categories by Domain

**Reinforced Concrete - Cracking:**
- Structural overload (flexure, shear, torsion)
- Differential settlement
- Thermal/shrinkage during curing
- Corrosion-induced expansion (follow with half-cell potential)
- Alkali-silica reaction (map cracking, gel exudation)
- Carbonation-induced depassivation

**Reinforced Concrete - Delamination / Spalling:**
- Corrosion of rebar (insufficient cover, chloride ingress, carbonation)
- Freeze-thaw cycling
- Fire damage
- Impact / mechanical damage

**Steel Structures - Corrosion:**
- General atmospheric corrosion (coating failure)
- Galvanic corrosion (dissimilar metals in contact)
- Crevice corrosion (trapped moisture)
- Stress corrosion cracking (high-tensile members under sustained load)
- MIC (microbiologically influenced - offshore / subsea)

**Foundation - Settlement:**
- Consolidation of compressible layer (differential if variable soil)
- Loss of bearing capacity (scour, piping, erosion)
- Expansive / collapsible soils
- Vibration-induced densification
- Inadequate founding depth

**Welds - Defects:**
- Lack of fusion (wrong technique, dirty joint, wrong current)
- Porosity (moisture contamination, wrong shielding gas, wrong electrode)
- Undercut (excessive current, wrong angle)
- Hot cracking (high restraint, wrong preheat)
- Hydrogen-induced cracking (wrong preheat, high-strength steel)

**Tank / Vessel - Calibration Anomaly:**
- Strapping measurement error (check key dimensions)
- Shell deformation (dents, bulges outside tolerance)
- Floating roof seal displacement
- Product level gauge calibration drift

---

## Phase 4 - Test Protocol

For the highest-probability hypothesis, specify the **minimum test** needed
to confirm or refute it. Do not over-specify - one well-chosen test first.

```
PROPOSED INVESTIGATION TEST:
  Hypothesis being tested: [N]
  Test method: [specific NDT method, standard, equipment]
  Location: [exact element / grid / zone]
  Pass/fail criterion: [what result confirms the hypothesis]
  Estimated duration: [field time]
  Additional resource needed: [equipment, access, specialist]
```

If the test result **confirms** the hypothesis → proceed to Phase 5.
If the test result **refutes** the hypothesis → return to Phase 3, demote
this hypothesis, promote the next.

**THREE-STRIKE RULE:** If three consecutive hypotheses are tested and refuted,
STOP. Do not continue guessing. The anomaly requires a broader investigation
scope - escalate to:
- Specialist consultant (geotechnical, materials lab, structural analyst)
- Destructive investigation (core sample, trial pit, cut-out)
- Document the three failed hypotheses as evidence for the scope escalation

---

## Phase 5 - Root Cause Confirmation

When a hypothesis is confirmed by test evidence, document:

```
ROOT CAUSE CONFIRMED:
  Mechanism: [specific failure mechanism]
  Primary cause: [design deficiency / construction defect / material failure /
                  environmental / operational / maintenance gap]
  Contributing factors: [list secondary causes]
  Extent: [localised / systematic / progressive]
  Urgency: [IMMEDIATE / SHORT-TERM / MONITOR]
```

### Urgency Classification
| Class | Criteria | Action |
|---|---|---|
| IMMEDIATE | Structural capacity compromised, life safety risk | Restrict access, emergency prop/shore, notify client same day |
| SHORT-TERM | Defect is progressing, will reach structural threshold within one inspection cycle | Remediation within agreed programme |
| MONITOR | Defect is stable, no immediate risk | Inspect at defined interval, set trigger threshold |

---

## Phase 6 - Remediation Scoping (Post-Confirmation Only)

Only after root cause is confirmed:

1. Specify the remediation objective (restore capacity, arrest progression, seal,
   replace)
2. Reference applicable standard for the repair (ACI 224.1R, EN 1504, API 653
   Annex B, AWS D1.1 etc.)
3. Identify any design input required before repair specification
4. List any regulatory notification obligations ([National Regulator], client HSEMS, insurance)

---

## Output Format

Every investigation session concludes with a structured finding note:

```
PM INVESTIGATION NOTE
Ref: [MA-DU-AN]/INV/[YYYY]/[NNN]
Date: [date]
Project: [project name / client]
Element: [structural element / zone]

SYMPTOM SUMMARY:
[3–5 bullet observations]

HYPOTHESES CONSIDERED:
1. [hypothesis] - [CONFIRMED / REFUTED / UNTESTED]
2. [hypothesis] - [CONFIRMED / REFUTED / UNTESTED]

ROOT CAUSE:
[confirmed mechanism, or "INCONCLUSIVE - escalation required"]

URGENCY: [IMMEDIATE / SHORT-TERM / MONITOR]

RECOMMENDED NEXT STEP:
[single specific action - test, repair spec, monitor programme, or escalation]

Prepared by: [PM]
```

This note feeds directly into any subsequent project report or proposal.
