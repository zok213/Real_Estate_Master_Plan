# POC EVALUATION CRITERIA: HOW TO ASSESS SUCCESS

**Purpose:** Objective scorecard to determine if POC meets requirements.

---

## **EVALUATION FRAMEWORK**

### **Scoring System:**

- **Critical (Must-Pass):** Binary—if any fails, POC is not viable
- **Important (Weighted):** Scored 0-10, weighted by importance
- **Nice-to-Have (Bonus):** Extra points, not required for approval

**Pass Threshold:** ≥ 70/100 points + all Critical criteria met

---

## **SECTION 1: TECHNICAL FEASIBILITY (40 points)**

### **1.1 Input Data Handling (Critical)**

**Question:** Can the system parse WHA CAD files reliably?

**Test:**

- [ ] Load WHA-RY36_Original.dwg
- [ ] Extract site boundary polygon
- [ ] Output GeoJSON with correct coordinates
- [ ] Visual verification (boundary looks correct)

**Scoring:**

- ✅ PASS: Boundary extracted correctly
- ❌ FAIL: Boundary missing, distorted, or wrong coordinates

**Weight:** CRITICAL (must pass)

---

### **1.2 Generation Capability (Critical)**

**Question:** Can the system generate a layout?

**Test:**

- [ ] Input: Site boundary + constraints
- [ ] Process: Generate via TestFit
- [ ] Output: DXF/DWG file produced

**Scoring:**

- ✅ PASS: Layout generated successfully
- ❌ FAIL: System crashes, no output, or corrupt file

**Weight:** CRITICAL (must pass)

---

### **1.3 Output Quality (10 points)**

**Question:** Is the generated layout reasonable?

**Evaluation Criteria:**

| Criterion | Points | Evaluation |
|-----------|--------|------------|
| **Layout Structure** | 0-3 | Plots arranged logically (not random) |
| **Road Connectivity** | 0-3 | All plots have road access |
| **Geometry Validity** | 0-2 | No overlapping plots, no gaps |
| **Visual Appeal** | 0-2 | Looks professional (not chaotic) |

**Scoring:**

- 8-10 points: Excellent—layout comparable to human
- 5-7 points: Good—layout usable with minor edits
- 2-4 points: Fair—layout needs significant rework
- 0-1 points: Poor—layout unusable

---

### **1.4 Validation Accuracy (10 points)**

**Question:** Does validation engine catch constraint violations correctly?

**Test Cases:**

| Test | Expected Result | Points |
|------|----------------|--------|
| All plots within size range | PASS validation | 2 |
| One plot too small (deliberate test) | FAIL validation (flag it) | 2 |
| Land-use ratios within ±5% | PASS validation | 2 |
| Saleable area 50% (below 65% target) | FAIL validation (flag it) | 2 |
| All plots have road frontage | PASS validation | 2 |

**Scoring:**

- 10 points: All 5 tests correct
- 8 points: 4/5 tests correct
- 6 points: 3/5 tests correct
- <6 points: Validation unreliable

---

### **1.5 Processing Time (10 points)**

**Question:** How fast is generation?

**Measurement:**

- Start: Upload site boundary
- End: Download final DWG

**Scoring:**

| Time | Points | Assessment |
|------|--------|------------|
| < 2 minutes | 10 | Excellent (interactive) |
| 2-5 minutes | 8 | Good (acceptable for iteration) |
| 5-10 minutes | 6 | Fair (acceptable for batch) |
| 10-20 minutes | 4 | Poor (too slow for frequent use) |
| > 20 minutes | 2 | Unacceptable |

---

### **1.6 File Compatibility (10 points)**

**Question:** Does output integrate with WHA workflow?

**Test:**

| Check | Points | Test Procedure |
|-------|--------|----------------|
| Opens in AutoCAD without errors | 3 | Double-click DWG file |
| Layers match WHA standards | 3 | Check layer names & colors |
| Geometry is editable | 2 | Try moving a plot boundary |
| Labels are readable & correct | 2 | Zoom in on plot labels |

**Scoring:**

- 10 points: Perfect compatibility
- 7-9 points: Minor issues (fixable)
- 4-6 points: Significant issues (needs work)
- <4 points: Incompatible (blocker)

---

## **SECTION 2: ACCURACY & QUALITY (30 points)**

### **2.1 Constraint Adherence (Critical)**

**Question:** Does output follow WHA planning rules?

**Evaluation:**

| Constraint | Target | Actual | Pass? |
|------------|--------|--------|-------|
| Min plot size | 5,000 sqm | [measure] | Y/N |
| Max plot size | 15,000 sqm | [measure] | Y/N |
| Saleable area % | 65% (±5%) | [calculate] | Y/N |
| Road area % | 20% (±3%) | [calculate] | Y/N |
| Green buffer | 15m setback | [measure] | Y/N |
| Retention pond | Present & sized | [verify] | Y/N |

**Scoring:**

- ✅ PASS: ≥ 5/6 constraints met (83%)
- ❌ FAIL: < 5/6 constraints met

**Weight:** CRITICAL (must pass)

---

### **2.2 Metrics Comparison (15 points)**

**Question:** How close to targets?

**Formula:**

```
Score = 15 × (1 - avg_deviation)

where avg_deviation = average of |actual - target| / target for key metrics
```

**Key Metrics:**

1. Total saleable area (sqm)
2. Number of plots
3. Average plot size (sqm)
4. Road area percentage
5. Saleable area percentage

**Example Calculation:**

| Metric | Target | Actual | Deviation |
|--------|--------|--------|-----------|
| Saleable area | 325,000 | 310,000 | 4.6% |
| Plot count | 45 | 47 | 4.4% |
| Avg plot size | 7,222 | 6,596 | 8.7% |
| Road % | 20% | 21% | 5.0% |
| Saleable % | 65% | 62% | 4.6% |

Avg deviation = (4.6 + 4.4 + 8.7 + 5.0 + 4.6) / 5 = **5.5%**

Score = 15 × (1 - 0.055) = **14.2 points**

**Scoring:**

- 13-15 points: Excellent (< 10% deviation)
- 10-12 points: Good (10-20% deviation)
- 7-9 points: Fair (20-30% deviation)
- <7 points: Poor (> 30% deviation)

---

### **2.3 Comparison to Human Design (15 points)**

**Question:** How does AI layout compare to RY36 Final (human)?

**Evaluation by Designer:**

| Aspect | Score (0-3) | Comments |
|--------|-------------|----------|
| **Overall Layout Logic** | | Does it "make sense"? |
| **Plot Arrangement** | | Sizes/positions reasonable? |
| **Road Network** | | Efficient connectivity? |
| **Land Use Efficiency** | | Maximizes saleable area? |
| **Practicality** | | Buildable & operable? |

**Scoring:**

- 13-15 points: AI layout comparable to human
- 10-12 points: AI layout acceptable with minor tweaks
- 7-9 points: AI layout needs significant redesign
- <7 points: AI layout not usable

---

## **SECTION 3: USABILITY & WORKFLOW (20 points)**

### **3.1 Ease of Use (10 points)**

**Question:** Can a non-technical planner use this?

**Test User:** WHA designer (not developer)

**Tasks:**

1. Prepare input file (site boundary DWG)
2. Edit constraints JSON
3. Run generation script
4. Review output in AutoCAD
5. Interpret validation report

**Scoring:**

| Task | Points | Criteria |
|------|--------|----------|
| Task 1 | 2 | Completed without help |
| Task 2 | 2 | JSON fields clearly labeled |
| Task 3 | 2 | Script runs without errors |
| Task 4 | 2 | Output opens & is understandable |
| Task 5 | 2 | Report is clear (not technical jargon) |

**Scoring:**

- 9-10 points: Designer can use independently
- 6-8 points: Designer needs minimal training
- 3-5 points: Designer needs significant support
- <3 points: Too technical for designers

---

### **3.2 Iteration Speed (10 points)**

**Question:** How fast can user iterate on designs?

**Scenario:** Client asks to increase saleable area from 60% to 70%

**Test:**

1. Edit constraints JSON (change target_saleable_percentage)
2. Regenerate layout
3. Review new output

**Scoring:**

| Iteration Time | Points | Assessment |
|----------------|--------|------------|
| < 3 minutes | 10 | Enables rapid iteration |
| 3-5 minutes | 8 | Acceptable for exploration |
| 5-10 minutes | 6 | Acceptable for major changes |
| 10-20 minutes | 4 | Too slow for iteration |
| > 20 minutes | 2 | Not practical for iteration |

---

## **SECTION 4: BUSINESS VALUE (10 points)**

### **4.1 Time Savings (Critical)**

**Question:** Does this save time vs. manual process?

**Measurement:**

| Process Step | Manual | AI-Assisted | Savings |
|--------------|--------|-------------|---------|
| Site analysis | 4 hours | 0.5 hours | 88% |
| Initial layout | 16 hours | 0.1 hours | 99% |
| Road design | 8 hours | 0.1 hours | 99% |
| Plot sizing | 8 hours | 0 hours | 100% |
| Iteration (3 rounds) | 12 hours | 0.3 hours | 98% |
| **TOTAL** | **48 hours** | **1 hour** | **98%** |

**Realistic Savings:** 60-80% (accounting for human review/refinement time)

**Scoring:**

- ✅ PASS: ≥ 50% time savings
- ❌ FAIL: < 50% time savings

**Weight:** CRITICAL (must pass)

---

### **4.2 Cost-Benefit Analysis (10 points)**

**Question:** What's the ROI?

**Calculation:**

**Investment:**

- POC development: 110 hours × $50/hour = $5,500
- Software licenses: $500/month × 12 = $6,000/year
- Maintenance: $10,000/year
- **Total Year 1 Cost:** $21,500

**Return:**

- Projects per year: 50
- Time saved per project: 3 days (24 hours)
- Designer rate: $50/hour
- **Annual savings:** 50 × 24 × $50 = **$60,000/year**

**ROI:** ($60,000 - $21,500) / $21,500 = **179%** in Year 1

**Scoring:**

- 9-10 points: ROI > 150% (compelling business case)
- 7-8 points: ROI 100-150% (good business case)
- 5-6 points: ROI 50-100% (marginal business case)
- <5 points: ROI < 50% (not worth it)

---

## **SECTION 5: BONUS POINTS (up to +10)**

### **5.1 Alternative Options (+5 points)**

**Did system generate multiple layout alternatives?**

- +5 points: 3+ alternatives generated
- +3 points: 2 alternatives generated
- +0 points: Single layout only

### **5.2 Visual Quality (+3 points)**

**Does output look professional?**

- +3 points: Looks like human-made drawing
- +2 points: Looks computer-generated but clean
- +1 point: Looks rough but understandable
- +0 points: Looks messy/unprofessional

### **5.3 Documentation (+2 points)**

**Is system well-documented?**

- +2 points: Complete user guide + technical docs
- +1 point: Basic instructions only
- +0 points: No documentation

---

## **FINAL SCORE CALCULATION**

```
SCORE BREAKDOWN:
├─ Technical Feasibility:    ___ / 40 points
├─ Accuracy & Quality:        ___ / 30 points
├─ Usability & Workflow:      ___ / 20 points
├─ Business Value:            ___ / 10 points
└─ Bonus Points:              ___ / +10 points

TOTAL SCORE:                   ___ / 100 points

CRITICAL CHECKS:
☐ Input data handling           (PASS / FAIL)
☐ Generation capability         (PASS / FAIL)
☐ Constraint adherence          (PASS / FAIL)
☐ Time savings ≥ 50%            (PASS / FAIL)

POC RESULT:
☐ APPROVED     (Score ≥ 70 AND all Critical checks PASS)
☐ CONDITIONAL  (Score 60-69 OR 1 Critical check FAIL)
☐ REJECTED     (Score < 60 OR 2+ Critical checks FAIL)
```

---

## **EVALUATION REPORT TEMPLATE**

```markdown
# WHA AI MASTER PLAN POC - EVALUATION REPORT
Date: [Date]
Evaluator: [Name]
System Version: POC v0.1

## EXECUTIVE SUMMARY
[1-2 paragraph summary of overall assessment]

Overall Score: ___ / 100
Critical Checks: ___ / 4 passed
Recommendation: ☐ APPROVED  ☐ CONDITIONAL  ☐ REJECTED

## DETAILED SCORES

### 1. Technical Feasibility (40 points)
- Input Data Handling: PASS / FAIL
- Generation Capability: PASS / FAIL
- Output Quality: ___ / 10
- Validation Accuracy: ___ / 10
- Processing Time: ___ / 10
- File Compatibility: ___ / 10

**Subtotal: ___ / 40**

**Comments:**
[Detailed observations]

### 2. Accuracy & Quality (30 points)
- Constraint Adherence: PASS / FAIL
- Metrics Comparison: ___ / 15
- Comparison to Human Design: ___ / 15

**Subtotal: ___ / 30**

**Comments:**
[Detailed observations]

### 3. Usability & Workflow (20 points)
- Ease of Use: ___ / 10
- Iteration Speed: ___ / 10

**Subtotal: ___ / 20**

**Comments:**
[Detailed observations]

### 4. Business Value (10 points)
- Time Savings: PASS / FAIL
- Cost-Benefit Analysis: ___ / 10

**Subtotal: ___ / 10**

**Comments:**
[ROI calculation details]

### 5. Bonus Points (+10)
- Alternative Options: ___ / +5
- Visual Quality: ___ / +3
- Documentation: ___ / +2

**Subtotal: ___ / +10**

## STRENGTHS
1. [Strength 1]
2. [Strength 2]
3. [Strength 3]

## WEAKNESSES
1. [Weakness 1] - Severity: High / Medium / Low
2. [Weakness 2] - Severity: High / Medium / Low
3. [Weakness 3] - Severity: High / Medium / Low

## RECOMMENDATIONS

### If APPROVED:
- [ ] Proceed to Phase 2 Pilot (3 real projects)
- [ ] Address [specific weakness] before pilot
- [ ] Allocate budget: $[amount]
- [ ] Target pilot completion: [date]

### If CONDITIONAL:
- [ ] Fix [critical issue]
- [ ] Re-evaluate after fixes
- [ ] Decision timeline: [date]

### If REJECTED:
- [ ] Reason: [primary reason for rejection]
- [ ] Alternative path: [if any]
- [ ] Revisit timeline: [if applicable]

## SIGNATURES
Evaluator: ________________________  Date: __________
Approver: ________________________   Date: __________
```

---

## **DECISION MATRIX**

Use this to make GO/NO-GO decision:

| Score Range | Critical Pass | Business Decision |
|-------------|---------------|-------------------|
| 80-100 | 4/4 | **STRONG GO** - Deploy to pilot immediately |
| 70-79 | 4/4 | **GO** - Proceed to pilot with minor improvements |
| 70-79 | 3/4 | **CONDITIONAL** - Fix critical issue, then pilot |
| 60-69 | 4/4 | **CONDITIONAL** - Improve quality, then re-evaluate |
| 60-69 | <3/4 | **NO-GO** - Too many blockers, not viable |
| <60 | Any | **NO-GO** - Does not meet minimum requirements |

---

## **POST-EVALUATION ACTIONS**

### **If Score ≥ 70 + All Critical Pass:**

✅ Schedule Phase 2 pilot kickoff
✅ Allocate budget for pilot
✅ Select 3 pilot projects (varying complexity)
✅ Set success metrics for pilot
✅ Plan production deployment timeline

### **If Conditional:**

⚠️ Document specific issues to fix
⚠️ Set re-evaluation date (2-4 weeks)
⚠️ Allocate time to address blockers
⚠️ Re-test with same criteria

### **If Rejected:**

❌ Archive POC code for future reference
❌ Document lessons learned
❌ Explore alternative approaches (if any)
❌ Set timeline for potential revisit (6-12 months)

---

**This scorecard ensures objective, data-driven decision-making. No "gut feel"—just facts and numbers.**
