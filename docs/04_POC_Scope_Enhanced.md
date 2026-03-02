# POC SCOPE DEFINITION: BUILD vs. FAKE vs. SKIP

**Critical Principle:** In 2 weeks, you CANNOT build everything. Be strategic about what to demonstrate vs. what to simulate.

---

## **TIER 1: MUST BUILD (Core Demo)**

These components are MANDATORY for credible POC:

### **1. Input Adapter (Python Script)**

**Status:** ✅ BUILD
**Why:** Shows you can parse WHA data automatically
**Effort:** 1 day
**Evidence Required:**

- Takes WHA DWG file as input
- Extracts site boundary polygon
- Outputs clean GeoJSON
- Visual verification (matplotlib plot)

**Code to Write:**

```python
# input_adapter.py
class InputAdapter:
    def parse_site_boundary(dwg_path, layer='BOUNDARY-SITE') → GeoJSON
    def validate_geometry(polygon) → bool
    def export_to_geojson(polygon, output_path) → file
```

**Demo Moment:**
*"Here's the RY36 site boundary DWG from your team. Watch as the script automatically extracts the boundary in 5 seconds..."*

---

### **2. Constraint Configuration (JSON Interface)**

**Status:** ✅ BUILD
**Why:** Shows system is configurable for different projects
**Effort:** 0.5 days
**Evidence Required:**

- Well-structured JSON schema
- Clear mapping to WHA planning rules
- Validation script (checks required fields)

**Files to Create:**

```
input/
  └── wha_constraints_template.json  (with comments explaining each field)
  └── ry36_constraints.json          (actual RY36 parameters)
  └── validate_constraints.py         (checks JSON is valid)
```

**Demo Moment:**
*"Each project has different requirements. Here's how we configure constraints—just edit this JSON file. No coding required for planners."*

---

### **3. Output Processor (DXF → DWG Converter)**

**Status:** ✅ BUILD
**Why:** Proves integration with WHA CAD workflow
**Effort:** 1 day
**Evidence Required:**

- Reads TestFit DXF
- Remaps to WHA layers (with correct names, colors)
- Adds plot labels with areas
- Exports valid DWG that opens in AutoCAD

**Code to Write:**

```python
# output_processor.py
class OutputProcessor:
    def remap_layers(testfit_dxf) → wha_layers
    def add_plot_labels(plots_layer) → labeled_plots
    def add_site_boundary(site_geojson) → boundary_layer
    def export_dwg(doc, output_path) → file
```

**Demo Moment:**
*"TestFit outputs a generic DXF. Our processor converts it to WHA's exact layer standards. Watch—I'll open this in AutoCAD right now..."* [Opens file, shows layers panel]

---

### **4. Validation Engine (Automated Checks)**

**Status:** ✅ BUILD
**Why:** Shows system has "intelligence" to catch errors
**Effort:** 1.5 days
**Evidence Required:**

- At least 3 working validators:
  1. Plot size range check
  2. Land-use ratio check
  3. Basic topology check (no overlaps)
- JSON report output
- Clear pass/fail indicators

**Code to Write:**

```python
# validator.py
class LayoutValidator:
    def validate_plot_sizes(dwg, constraints) → CheckResult
    def validate_landuse_ratios(dwg, constraints) → CheckResult
    def validate_topology(dwg) → CheckResult
    def generate_report(all_checks) → JSON + PDF
```

**Demo Moment:**
*"The system automatically validates against your rules. Here's the report—12 checks run in 30 seconds. Let me show you what happens when a plot violates the size constraint..."* [Shows red flag in report]

---

### **5. Metrics Dashboard (Visual Comparison)**

**Status:** ✅ BUILD
**Why:** Quantifies value proposition (replaces human judgment with data)
**Effort:** 1 day
**Evidence Required:**

- Comparison table: Target vs. Actual metrics
- 3-4 charts (bar, histogram, pie chart)
- PDF report generation
- Export to Excel for further analysis

**Code to Write:**

```python
# metrics_analyzer.py
class MetricsAnalyzer:
    def extract_metrics(dwg_path) → dict
    def compare_to_target(actual, constraints) → DataFrame
    def generate_charts(metrics) → matplotlib figures
    def export_report(charts, output_pdf) → file
```

**Demo Moment:**
*"Let's compare this to your targets. Saleable area: 64.8% actual vs. 65% target—within 0.2%. Plot count: 47 vs. estimated 45. Here's the distribution..."* [Shows charts]

---

## **TIER 2: MANUAL / SIMULATED (Good Enough for POC)**

These components are TOO COMPLEX for 2 weeks. Use manual steps or mock them:

### **6. TestFit API Integration**

**Status:** ⚠️ MANUAL (with automation planned)
**Why:** TestFit likely has no public API, or API access requires enterprise contract
**POC Approach:**

- Use TestFit web interface manually during demo
- Show automation PLAN with Selenium code (not working code)
- Explain: "For production, we'd automate this via their API or web automation"

**What to Prepare:**

- TestFit account pre-configured with RY36 site
- Parameters saved as preset
- One-click generate button ready
- Download folder set to `temp/`

**Demo Moment:**
*"Right now, this step uses TestFit's web interface—I click 'Generate' here. Takes 60 seconds. For production, we'd automate this via API or Selenium."* [Shows Selenium code on screen, doesn't run it]

---

### **7. Constraint Mapper (WHA → TestFit Translation)**

**Status:** ⚠️ HARDCODED (not dynamic)
**Why:** Full constraint mapping requires understanding ALL TestFit parameters
**POC Approach:**

- Hardcode mapping for RY36 parameters only
- Create mapping table document (shows concept)
- Explain: "We've mapped 15 key constraints. Full system would support 50+"

**What to Prepare:**

```python
# constraint_mapper.py (simplified)
def map_ry36_constraints_to_testfit(wha_json):
    """Hardcoded for RY36 demo only"""
    return {
        'building_width_range':,  # From WHA JSON
        'setback': 15,                       # From WHA JSON
        'road_width_primary': 24,            # From WHA JSON
        # ... (rest hardcoded)
    }
```

**Demo Moment:**
*"This mapper translates WHA constraints to TestFit parameters. For this demo, we've mapped the 15 most critical constraints for industrial estates. Full system would support 50+ parameters."*

---

### **8. Multi-Site Batch Processing**

**Status:** ❌ SKIP (out of scope)
**Why:** POC demonstrates single-site generation. Batch is nice-to-have.
**POC Approach:**

- Mention in "Future Roadmap" slide
- Show code structure that WOULD support it:

  ```python
  # Future: batch_processor.py
  def process_multiple_sites(site_list):
      for site in site_list:
          generate_master_plan(site)  # Reuse core function
  ```

**Demo Moment:**
*"For today's demo, we're showing single-site generation. The architecture supports batch processing—we'd just loop through a site list. That's Phase 2."*

---

### **9. Interactive Web UI**

**Status:** ❌ SKIP (out of scope)
**Why:** 2 weeks is too short for frontend development
**POC Approach:**

- Show mockup/wireframe (made in PowerPoint or Figma)
- Explain: "The backend works via command line today. For production, we'd add a web interface like this..."

**What to Prepare:**

- 3-5 wireframe slides showing ideal UI:
  - Upload page
  - Parameter configuration page
  - Generation progress page
  - Results comparison page
- Explain: "UI is 4-6 weeks of additional work. Core AI works now."

**Demo Moment:**
*"Here's what the production interface could look like..."* [Shows mockups] *"But the intelligence—the hard part—already works. UI is just packaging."*

---

### **10. Cost Estimation Module**

**Status:** ❌ SKIP (out of scope)
**Why:** Requires WHA's cost database integration
**POC Approach:**

- Acknowledge in limitations
- Show where it would plug in:

  ```python
  # Future: cost_estimator.py
  def estimate_project_cost(layout_metrics, cost_db):
      road_cost = metrics['road_area'] * cost_db['road_per_sqm']
      # ... etc
      return total_cost
  ```

**Demo Moment:**
*"Cost estimation isn't in this POC—it requires your cost database. But the hook is here. Once we have access to your cost data, we can add it in 2 weeks."*

---

## **TIER 3: ACKNOWLEDGE LIMITATIONS (Don't Hide Them)**

Be HONEST about what the POC cannot do:

### **Limitations to State Upfront:**

1. **"This POC uses TestFit as the core engine"**
   - Why: Full custom solution needs 12-16 weeks
   - Implication: We're constrained by TestFit's capabilities
   - Mitigation: Custom wrapper adds WHA-specific logic on top

2. **"Generation is semi-automated (manual TestFit step)"**
   - Why: TestFit API access uncertain in trial period
   - Implication: Cannot run 100 sites overnight yet
   - Mitigation: Automation roadmap ready for Phase 2

3. **"Validation checks are basic (not exhaustive)"**
   - Why: Full rule engine needs more time + WHA expert input
   - Implication: Human review still required
   - Mitigation: System catches 80% of obvious issues now

4. **"Output quality depends on TestFit algorithm"**
   - Why: TestFit is black box (we don't control its logic)
   - Implication: Some layouts may be suboptimal
   - Mitigation: Generate 3+ alternatives, human picks best

5. **"No support for complex constraints yet"**
   - Examples: Phasing requirements, existing utility conflicts, irregular topography
   - Mitigation: These are Phase 2 enhancements (feasibility proven first)

---

## **POC DEMO SCRIPT STRUCTURE**

### **Act 1: Setup (5 min)**

*"We had 2 weeks. Here's what we built..."*

- Show architecture diagram
- Explain TestFit + wrapper approach
- Set expectations: "Draft generation, not final design"

### **Act 2: Live Demo (10 min)**

*"Let me walk you through the workflow..."*

1. ✅ **Automated:** Input adapter (runs in 5 sec)
2. ⚠️ **Manual:** TestFit generation (click button, wait 60 sec)
3. ✅ **Automated:** Output processor (runs in 10 sec)
4. ✅ **Automated:** Validation (runs in 30 sec)
5. ✅ **Automated:** Metrics report (generates PDF in 5 sec)

**Total Time:** ~2 minutes of actual processing + 1 minute of human clicks

### **Act 3: Results (10 min)**

*"Here's what it generated..."*

- Open DWG in AutoCAD (show layers, plots)
- Show 3 alternative layouts side-by-side
- Show validation report (12 checks, 11 passed, 1 warning)
- Show metrics comparison (target vs. actual within 5%)

### **Act 4: Comparison (5 min)**

*"How does this compare to RY36 Final (human design)?"*

- Side-by-side screenshot
- Qualitative: "AI captured main layout logic"
- Quantitative: "Metrics within 10% of human design"
- Honest: "Human design is still better on X, Y aspects"

### **Act 5: Value Proposition (5 min)**

*"What does this enable?"*

- **Time savings:** 3-5 days → 1 day (60-80% reduction)
- **Consistency:** Same rules applied every time
- **Exploration:** Generate 10 alternatives in 1 hour
- **Iteration:** Client changes boundary? Regenerate in 5 minutes

### **Act 6: Roadmap (5 min)**

*"What's next if we proceed?"*

- **Option A:** Continue with TestFit ($15K/year subscription)
  - Pros: Fast deployment, proven tool
  - Cons: Licensing cost, limited customization
  
- **Option B:** Build custom solution (12-16 weeks, $150K-$300K)
  - Pros: Full control, WHA-specific algorithms
  - Cons: Development time, maintenance responsibility
  
- **Option C:** Hybrid (start with TestFit, migrate later)
  - Pros: Prove value quickly, plan long-term
  - Cons: Two integration efforts

**Recommendation:** Start with Option C

---

## **POC SUCCESS CRITERIA (REALISTIC)**

### **Must-Have (POC Approved):**

- [x] System generates valid DWG that opens in AutoCAD
- [x] Output meets ≥ 70% of validation checks
- [x] Processing time ≤ 5 minutes
- [x] Stakeholders understand approach and limitations

### **Nice-to-Have (POC Exceeded Expectations):**

- [x] Output meets ≥ 90% of validation checks
- [x] Metrics within 5% of targets
- [x] Designer feedback: "I'd use this"
- [x] Clear ROI justification

### **Stretch Goals (Bonus):**

- [ ] Full automation (no manual steps)
- [ ] Multiple site types demonstrated
- [ ] Cost estimation included
- [ ] Web UI prototype

---

## **RESOURCE REQUIREMENTS**

### **Software Licenses (2 weeks):**

- TestFit trial: $0 (14-day trial) or $299/month
- Python libraries: $0 (all open source)
- AutoCAD: $0 (assume WHA has licenses)
- Cloud compute: ~$50 (AWS EC2 if needed for Selenium)

**Total Budget: $50-$350**

### **Time Investment:**

- Your time: 110 hours (full-time for 2 weeks)
- Designer review: 4 hours (validate outputs)
- Stakeholder time: 2 hours (demo + Q&A)

**Total Effort: 116 person-hours**

### **ROI Calculation:**

If POC succeeds and system is deployed:

- **Annual time savings:** 50 projects/year × 3 days saved × $500/day = $75,000/year
- **POC cost:** $50-$350 + 116 hours
- **ROI:** 200:1 if successful

**Break-even:** After 1 project uses the system successfully

---

## **DECISION TREE**

```
POC Demo Complete
    │
    ├─ Stakeholders Impressed?
    │   ├─ YES → Approve Phase 2 (Pilot)
    │   │         │
    │   │         ├─ Deploy TestFit wrapper for 3 real projects
    │   │         ├─ Collect feedback from designers
    │   │         └─ Measure time savings
    │   │
    │   └─ NO → Understand Why?
    │             │
    │             ├─ "Quality not good enough"
    │             │   → PIVOT: Explore alternative tools
    │             │
    │             ├─ "Too expensive"
    │             │   → REFRAME: Show ROI calculation
    │             │
    │             ├─ "Not ready for our workflow"
    │             │   → DEFER: Revisit in 6-12 months
    │             │
    │             └─ "Interesting but not priority"
    │                 → ARCHIVE: Document learnings
```

---

## **WHAT TO SAY WHEN ASKED...**

**Q: "Can it handle irregular site boundaries?"**
A: "Yes—the input adapter works with any polygon. We tested with RY36's actual boundary. Complex boundaries just mean more computation time."

**Q: "What if we have existing buildings to work around?"**
A: "Good question. Current POC assumes greenfield sites. Adding obstacle avoidance is a Phase 2 enhancement—feasible, needs 2-4 weeks."

**Q: "Can it do phased development (build in stages)?"**
A: "Not in current POC. Phasing requires temporal logic—which plots to develop first. That's a custom algorithm we'd build in Phase 2."

**Q: "How accurate is the road design?"**
A: "TestFit generates basic road layouts (connectivity). Detailed road geometry—curves, superelevation—still needs civil engineer review. Think of this as 'schematic design,' not 'construction drawings.'"

**Q: "What about utility routing (water, sewer, power)?"**
A: "Out of scope for POC. Utilities require underground data + specialized routing algorithms. Feasible to add, but separate module (4-6 weeks)."

**Q: "Can we customize the algorithm?"**
A: "Limited with TestFit (black box). Our wrapper adds pre/post-processing customization. For full algorithm control, we'd need custom solution (12-16 weeks, higher cost)."

**Q: "What's the ongoing cost?"**
A: "TestFit approach: $300-500/month subscription. Custom solution: $0 license cost, but ~$50K/year maintenance (server, updates). Trade-off between flexibility and convenience."

**Q: "How long to production-ready?"**
A: "If we proceed: Phase 2 pilot (4 weeks) → Feedback incorporation (2 weeks) → Production deployment (2 weeks). Total: 8-10 weeks from today to production system."

---

## **POST-DEMO FOLLOW-UP EMAIL TEMPLATE**

```
Subject: WHA AI Master Plan POC - Demo Follow-up & Next Steps

Hi [Stakeholder Name],

Thank you for attending today's POC demonstration. As promised, here are the materials and next steps:

**Demo Materials:**
- Presentation slides (PDF): [link]
- Demo video recording: [link]
- Sample output files:
  - WHA_MasterPlan_OptionA.dwg
  - WHA_MasterPlan_OptionB.dwg
  - WHA_MasterPlan_OptionC.dwg
- Validation report: validation_report.pdf
- Metrics comparison: metrics_comparison.xlsx

**Key Takeaways:**
✓ Demonstrated automated master plan generation from site boundary + constraints
✓ Generated 3 alternative layouts in < 5 minutes each
✓ Output meets 11/12 validation checks (92% pass rate)
✓ Metrics within 5% of targets (saleable area, road area, plot sizes)
✓ Identified path forward: TestFit integration for quick deployment OR custom build for full control

**Open Questions from Q&A:**
1. [Question 1] - Answer: [...]
2. [Question 2] - Answer: [...]

**Proposed Next Steps:**
- [ ] Week 1: Decision meeting (GO / NO-GO / PIVOT)
- [ ] Week 2-3: If GO, start Phase 2 pilot (3 real projects)
- [ ] Week 4: Pilot results review
- [ ] Week 5-6: Refinements based on designer feedback
- [ ] Week 7-8: Production deployment

**Decision Required:**
Please confirm by [Date] whether to proceed to Phase 2 pilot.

**Estimated Investment (Phase 2):**
- Time: 4 weeks development + 4 weeks pilot
- Cost: $5K-15K (software licenses + infrastructure)
- Team: 1 AI engineer + 1 designer (part-time review)

**Expected Return:**
- Time savings: 60-80% reduction in master planning time (3-5 days → 1 day)
- Consistency: Automated compliance with WHA standards
- Flexibility: Generate multiple alternatives for client review

Let me know if you need any clarifications or additional information.

Best regards,
[Your Name]
```

---

## **SUMMARY: BUILD SMART, NOT HARD**

**2 weeks is SHORT. Be strategic:**

✅ **BUILD:** Core components that prove technical feasibility
⚠️ **MANUAL:** Complex integrations that can be simulated
❌ **SKIP:** Nice-to-haves that don't affect core value proposition

**Your POC must answer ONE question:**
*"Can AI generate a usable master plan draft faster than a human?"*

Everything else is secondary.

Focus 80% effort on:

1. Input adapter (proves data compatibility)
2. Output processor (proves workflow integration)
3. Validation engine (proves quality control)
4. Metrics dashboard (proves value quantification)

The other 20% is presentation polish and contingency planning.

**You've got this. 🚀**
