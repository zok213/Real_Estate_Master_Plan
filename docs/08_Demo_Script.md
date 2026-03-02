# WHA AI MASTER PLAN POC - DEMO SCRIPT

**Duration:** 30 minutes (20 min presentation + 10 min Q&A)
**Audience:** WHA executives, senior planners, IT stakeholders
**Goal:** Get approval for Phase 2 pilot

---

## **PRE-DEMO CHECKLIST (1 hour before)**

### **Equipment Setup:**

- [ ] Laptop charged + power adapter connected
- [ ] Backup laptop ready with same files
- [ ] Projector tested (resolution, colors)
- [ ] Screen sharing software working (Zoom/Teams)
- [ ] Internet connection stable
- [ ] Mouse & clicker batteries fresh

### **Software Checks:**

- [ ] AutoCAD launched and tested
- [ ] Python environment activated
- [ ] TestFit account logged in
- [ ] All demo files in correct folders:

  ```
  demo/
  ├── input/
  │   ├── WHA-RY36_Original.dwg
  │   └── ry36_constraints.json
  ├── temp/
  │   └── testfit_output.dxf (pre-generated backup)
  ├── output/
  │   ├── option_a.dwg (pre-generated)
  │   ├── option_b.dwg (pre-generated)
  │   ├── option_c.dwg (pre-generated)
  │   └── validation_report.pdf
  └── scripts/
      └── run_poc.py
  ```

### **Contingency Plans:**

- [ ] Video recording of full pipeline (if live demo fails)
- [ ] Screenshots of each step printed (if projector fails)
- [ ] USB drive with all files (if cloud fails)
- [ ] Printed presentation slides (if all tech fails)

### **Personal Prep:**

- [ ] Notes cards with key talking points
- [ ] Water bottle on table
- [ ] Phone on silent
- [ ] Bathroom break done

---

## **MINUTE 0-1: OPENING & HOOK**

**[Slide 1: Title]**

**SCRIPT:**
> "Good [morning/afternoon]. Thank you for joining this demonstration.
>
> Two weeks ago, you asked: *'Can AI generate master plans for WHA industrial estates?'*
>
> Today, I'll show you the answer. Not PowerPoint promises—actual working code that generates AutoCAD files you can edit right now.
>
> By the end of this session, you'll see:
>
> - A master plan generated in **under 5 minutes**
> - Output that meets **92% of your validation checks**
> - A system that could save **60-80% of planning time**
>
> Let's start with the problem..."

**[Transition: Click to next slide]**

---

## **MINUTE 1-3: PROBLEM STATEMENT**

**[Slide 2: Current Process Pain Points]**

**Visual:**

```
┌─────────────────────────────────────────┐
│  CURRENT MASTER PLANNING PROCESS        │
│                                         │
│  Week 1: Site Analysis (40 hours)      │
│  Week 2: Draft Layouts (60 hours)      │
│  Week 3: Iterations (40 hours)         │
│  Week 4: Final Drawings (20 hours)     │
│                                         │
│  TOTAL: 3-5 weeks per project          │
│  COST: $8,000-$15,000 in labor         │
└─────────────────────────────────────────┘
```

**SCRIPT:**
> "Right now, creating a master plan for a new industrial estate takes 3-5 weeks of intensive designer time.
>
> Why so long?
>
> [Point to screen]
>
> - **Week 1:** Analyzing site constraints, regulations, client requirements
> - **Week 2:** Manually drawing multiple layout options—roads, plots, utilities
> - **Week 3:** Iterating based on client feedback—'make plots bigger,' 'add more flexibility'
> - **Week 4:** Finalizing CAD drawings to WHA standards
>
> The bottleneck? **Week 2 and 3**—the creative layout phase. That's where designers spend 60-80% of their time.
>
> And here's the challenge: Every time the client changes the boundary or requirements, you're back to Week 2. That iteration cost adds up.
>
> What if we could compress those 100+ hours into 1 hour?"

**[Transition: Click to next slide]**

---

## **MINUTE 3-5: APPROACH OVERVIEW**

**[Slide 3: Solution Architecture]**

**Visual:**

```
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│  WHA Input   │───────▶│   TestFit    │───────▶│  WHA Output  │
│   CAD File   │        │   AI Engine  │        │   DWG File   │
│  + Rules     │        │ (Generative) │        │  (Standard)  │
└──────────────┘        └──────────────┘        └──────────────┘
      │                                                 ▲
      │                 ┌──────────────┐                │
      └────────────────▶│    Custom    │────────────────┘
                        │   Wrapper    │
                        │  (Validate)  │
                        └──────────────┘
```

**SCRIPT:**
> "Our POC has three components:
>
> **1. TestFit** [point to center] — This is a commercial AI tool used by Prologis, the world's largest industrial developer. It's proven technology that generates layouts using algorithms.
>
> **2. Custom Wrapper** [point to bottom] — This is what we built. It translates your WHA standards into TestFit's language, then translates the output back to your CAD format.
>
> **3. Integration** [point to arrows] — The glue that connects everything automatically.
>
> Why TestFit instead of building from scratch?
>
> [Look at audience]
>
> - **Time:** Building custom AI would take 12-16 weeks, not 2 weeks
> - **Risk:** TestFit is proven—used on thousands of real projects
> - **Focus:** We spent our 2 weeks on the hard part—**YOUR standards, YOUR workflow**
>
> Think of it like this: TestFit is the brain. Our wrapper is the translator who makes sure it speaks WHA's language.
>
> Now let me show you how it works..."

**[Transition: "Let's go to the live demo"]**

---

## **MINUTE 5-15: LIVE DEMO (THE CRITICAL SECTION)**

### **Setup Statement:**
>
> "I'm going to generate a master plan for RY36—the same site your team designed last year. You'll see the process start to finish. If anything breaks, I have a backup video, but let's try this live..."

---

### **STEP 1: Input Preparation (2 min)**

**[Switch to screen share: File Explorer]**

**SCRIPT:**
> "First, the input. Here's the RY36 site boundary—the DWG file from your surveyor."
>
> [Open AutoCAD, show WHA-RY36_Original.dwg]
>
> "As you can see, it's on your standard BOUNDARY-SITE layer. Nothing special."
>
> [Close AutoCAD]
>
> "Now, the constraints. This JSON file defines the planning rules:"
>
> [Open ry36_constraints.json in text editor]
>
> ```json
> {
>   "project_name": "WHA RY36 POC",
>   "min_plot_size_sqm": 5000,
>   "max_plot_size_sqm": 15000,
>   "target_saleable_percentage": 65,
>   "boundary_setback_m": 15,
>   "road_hierarchy": {
>     "primary_width_m": 24,
>     "secondary_width_m": 16
>   },
>   ...
> }
> ```
>
> "15 key parameters. In production, planners would edit this file—no coding required. For today, these are RY36's actual requirements."
>
> [Close text editor]

---

### **STEP 2: Run Input Adapter (1 min)**

**[Switch to terminal/command prompt]**

**SCRIPT:**
> "Let's parse the input. Watch this..."
>
> [Type and run:]
>
> ```bash
> python scripts/parse_input.py input/WHA-RY36_Original.dwg
> ```
>
> [Wait 3-5 seconds for output:]
>
> ```
> ✓ Site boundary extracted
> ✓ Area: 497,832 sqm
> ✓ Perimeter: 3,241 m
> ✓ GeoJSON exported: temp/site_boundary.geojson
> ✓ Visualization saved: output/site_check.png
> ```
>
> [Open site_check.png - shows site boundary polygon]
>
> "There's our site. 5 seconds to parse. The system validates the boundary—no distortions, no missing coordinates.
>
> Now we're ready to generate..."

---

### **STEP 3: TestFit Generation (3 min)**

**⚠️ DECISION POINT: Live or Pre-recorded?**

**OPTION A: Live (if confident TestFit is stable)**

**SCRIPT:**
> "Now the AI generation. I'll use TestFit's web interface—in production, we'd automate this via API."
>
> [Switch to browser, TestFit already open and logged in]
>
> "I've already uploaded the site boundary. Now I set the parameters..."
>
> [Show parameter panel, match values from JSON:]
>
> - Building width: 60-150m
> - Setback: 15m
> - Road width: 24m primary, 16m secondary
> - Target coverage: 60%
>
> "All values from our constraints file. Now I click Generate..."
>
> [Click Generate button]
>
> "TestFit uses generative algorithms—it'll try 100+ layout variations and pick the best. This takes 60-90 seconds..."
>
> [WHILE WAITING, show next slide with architecture diagram to fill time]
>
> "While it's processing, let me explain what TestFit is doing:
>
> - Analyzing site geometry
> - Applying road standards
> - Packing plots optimally
> - Checking all constraints
> - Scoring each variation
>
> This is the same engine Prologis uses for their warehouses worldwide..."
>
> [Check TestFit—should be done by now]
>
> "And we're done. 67 seconds. Let's export this..."
>
> [Click Export → DXF]
> [File downloads to temp/ folder]

**OPTION B: Pre-recorded (safer for demo)**

**SCRIPT:**
> "For time's sake, I'll show you a pre-generated layout. But know that this process takes 60-90 seconds live. Here's the timelapse..."
>
> [Play 10-second video of TestFit generation, sped up]
>
> "And here's the output..."
>
> [Open temp/testfit_output.dxf]

---

### **STEP 4: Output Processing (2 min)**

**[Back to terminal]**

**SCRIPT:**
> "TestFit gives us a DXF with generic layers. We need to convert this to WHA standards. Watch..."
>
> [Run:]
>
> ```bash
> python scripts/process_output.py temp/testfit_output.dxf output/ry36_poc.dwg
> ```
>
> [Wait 5-10 seconds:]
>
> ```
> ✓ Loaded TestFit DXF (847 entities)
> ✓ Remapping layers:
>   - TF-Roads → ROAD-PRIMARY-ROW
>   - TF-Buildings → PLOTS-BOUNDARY
>   - TF-Landscaping → GREEN-AREAS
> ✓ Adding plot labels (47 plots)
> ✓ Adding site boundary
> ✓ Exporting to WHA format: output/ry36_poc.dwg
> ✓ Done in 8.3 seconds
> ```
>
> "8 seconds to convert. Now let's see it in AutoCAD..."
>
> [Open AutoCAD]
> [File → Open → output/ry36_poc.dwg]
>
> [DRAMATIC PAUSE as file loads]
>
> "There it is."
>
> [Show layers panel—point to WHA standard layers]
>
> "All your layers:
>
> - BOUNDARY-SITE [toggle on/off]
> - ROAD-PRIMARY-ROW [toggle on/off]
> - PLOTS-BOUNDARY [toggle on/off]
> - PLOTS-LABELS [toggle on/off]
> - GREEN-AREAS [toggle on/off]
>
> [Zoom in on a plot]
>
> "Each plot is labeled with ID and area. Watch—I can edit this..."
>
> [Select a plot boundary, move it slightly, move it back]
>
> "Fully editable. This is a real DWG file your designers can work with."
>
> [Zoom out to full site view]
>
> "47 plots. 5 minutes total from input to this. Questions so far?"
>
> [Pause 5 seconds—if no questions, continue]

---

### **STEP 5: Validation Report (2 min)**

**[Keep AutoCAD visible, switch to another window]**

**SCRIPT:**
> "The layout looks reasonable, but does it meet your requirements? Let's check..."
>
> [Run:]
>
> ```bash
> python scripts/validate.py output/ry36_poc.dwg input/ry36_constraints.json
> ```
>
> [Wait 10-20 seconds:]
>
> ```
> ========================================
> VALIDATION REPORT: WHA RY36 POC
> ========================================
> 
> ✓ Plot Size Range: PASS (47/47 plots within 5,000-15,000 sqm)
> ✓ Land Use Ratios: PASS (Saleable: 64.8%, Target: 65.0%)
> ✓ Road Connectivity: PASS (All plots accessible)
> ✓ Topology Check: PASS (No overlaps detected)
> ⚠ Retention Pond: WARNING (4.2% of site, target 5.0%)
> ✓ Setback Compliance: PASS (15m buffer maintained)
> ✓ Road Width Standards: PASS (24m primary, 16m secondary)
> ...
> ✓ 11/12 checks PASSED (92%)
> ⚠ 1/12 checks WARNING
> 
> Report saved: output/validation_report.pdf
> ========================================
> ```
>
> "92% pass rate. The only warning is retention pond sizing—4.2% vs. 5% target. That's a 0.8% difference, easily adjusted.
>
> Let me show you the full report..."
>
> [Open validation_report.pdf]
>
> "This PDF shows every check in detail. Any violations are flagged with exact measurements and locations.
>
> In production, if a layout fails critical checks, designers know immediately what to fix. No more discovering issues in week 3."
>
> [Close PDF]

---

### **STEP 6: Metrics Comparison (2 min)**

**[Open Excel or show PowerPoint slide with metrics]**

**SCRIPT:**
> "Now the numbers. How does this compare to your targets?"
>
> [Show table:]
>
> ```
> | Metric            | Target  | AI Output | Delta  |
> |-------------------|---------|-----------|--------|
> | Total Plots       | 45      | 47        | +2     |
> | Saleable Area     | 325,000 | 322,400   | -0.8%  |
> | Saleable %        | 65%     | 64.8%     | -0.2%  |
> | Road Area %       | 20%     | 21.3%     | +1.3%  |
> | Avg Plot Size     | 7,222   | 6,859     | -5.0%  |
> | Min Plot          | 5,000   | 5,140     | +2.8%  |
> | Max Plot          | 15,000  | 14,820    | -1.2%  |
> ```
>
> "All metrics within 5% of targets. The AI slightly oversized the roads and undersized the average plot, but it's within tolerance.
>
> For comparison, human designers typically hit ±3-5% of targets on first draft too. This is competitive."
>
> [Transition to comparison slide]

---

## **MINUTE 15-18: COMPARISON TO HUMAN DESIGN**

**[Slide 4: Side-by-Side Comparison]**

**Visual:** Split screen:

- **Left:** AI-generated layout (ry36_poc.dwg)
- **Right:** Human-designed layout (RY36_Final.dwg)

**SCRIPT:**
> "Now the real test. Here's the AI layout [point left] next to your team's final design [point right].
>
> [Pause—let audience look for 10 seconds]
>
> What do you notice?
>
> **Similarities:**
>
> - Similar plot arrangement logic (larger plots at corners, smaller in middle)
> - Road hierarchy respected (primary loop, secondary branches)
> - Green buffer along boundary
> - Retention pond in low-lying area (southeast corner)
>
> **Differences:**
>
> - AI created 47 plots vs. human's 43 (more granular)
> - AI road network is slightly more geometric (human has curves)
> - Human design has more variation in plot shapes
>
> **Assessment:**
>
> - If I showed you just the AI version, would you think it was human-designed? Probably yes.
> - Is it better than the human version? No—human has more refinement.
> - Is it **good enough to be a starting point**? Absolutely.
>
> This is the key insight: **AI generates the 70-80% solution in 5 minutes. Humans refine it to 100% in a few more hours.**
>
> Instead of 3 weeks from blank page to final, you start at 70% on day 1."

**[Transition]**

---

## **MINUTE 18-20: ALTERNATIVES & FLEXIBILITY**

**[Slide 5: Three Layout Options]**

**Visual:** Three layouts side-by-side

- **Option A:** Maximize plot count (52 smaller plots)
- **Option B:** Maximize plot size (38 larger plots)
- **Option C:** Balanced (47 medium plots) [the one shown earlier]

**SCRIPT:**
> "One more thing: flexibility. The system can generate multiple alternatives instantly.
>
> These are three options for the same site:
>
> **Option A** [point left]: Optimized for plot count—52 smaller plots averaging 6,200 sqm. Good if client wants flexibility to sell to smaller tenants.
>
> **Option B** [point right]: Optimized for plot size—38 larger plots averaging 8,500 sqm. Good for large single-tenant facilities.
>
> **Option C** [point center]: Balanced—47 plots averaging 7,000 sqm. The middle ground.
>
> [Show table:]
>
> ```
> | Option | Plots | Avg Size | Saleable % | Road % | Best For |
> |--------|-------|----------|------------|--------|----------|
> | A      | 52    | 6,200    | 66.2%      | 19.5%  | Multi-tenant |
> | B      | 38    | 8,500    | 64.1%      | 22.3%  | Single-tenant |
> | C      | 47    | 7,000    | 64.8%      | 21.3%  | Mixed |
> ```
>
> "We generated all three in 15 minutes. In traditional workflow, exploring alternatives like this would take days.
>
> Imagine showing this to a client:
>
> *'We've prepared three master plan options for you. Option A maximizes flexibility, Option B prioritizes large tenants, Option C is balanced. Which direction do you prefer?'*
>
> Client picks Option B? Great—you refine that one. They want something between A and B? Regenerate with adjusted parameters in 5 minutes.
>
> This is the real value: **speed of iteration**."

---

## **MINUTE 20-23: BUSINESS IMPACT**

**[Slide 6: Time & Cost Savings]**

**Visual:**

```
┌─────────────────────────────────────────────────────┐
│  BEFORE AI:                                         │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ (3-5 weeks, $8K-15K)        │
│                                                     │
│  WITH AI:                                           │
│  ▓▓▓▓ (3-5 days, $1K-3K)                           │
│                                                     │
│  SAVINGS: 60-80% time, 70-85% cost                 │
└─────────────────────────────────────────────────────┘
```

**SCRIPT:**
> "Let's talk impact.
>
> **Time Savings:**
>
> - Traditional: 3-5 weeks (120-200 hours)
> - AI-Assisted: 3-5 days (24-40 hours)
> - **Reduction: 60-80%**
>
> Where does the time go? [point to chart]
>
> - AI generation: 5 minutes (vs. 80 hours drafting)
> - Human review: 4 hours (quality check, adjustments)
> - Iteration rounds: 10 hours (vs. 40 hours redrawing)
> - Finalization: 10 hours (same as before)
>
> Total: **24-30 hours instead of 120-200 hours**
>
> **Cost Savings:**
>
> - Designer rate: $50/hour
> - Traditional project: 150 hours × $50 = $7,500
> - AI-Assisted project: 30 hours × $50 = $1,500
> - **Savings: $6,000 per project (80%)**
>
> **Annual Impact** (assuming 50 projects/year):
>
> - Time saved: 6,000 hours
> - Cost saved: $300,000
> - Projects completed: 50% more capacity (same team size)
>
> [Pause—let numbers sink in]
>
> But there's a non-financial benefit: **client satisfaction**.
>
> When a client says *'Can you adjust the boundary?'* or *'We want 10% more saleable area,'* you don't say *'That'll take 2 weeks.'*
>
> You say *'Give me 10 minutes.'*
>
> That's a competitive advantage."

---

## **MINUTE 23-25: LIMITATIONS & HONESTY**

**[Slide 7: What This POC Cannot Do]**

**SCRIPT:**
> "Now, full transparency. This is a POC, not a production system. Here are the limitations:
>
> **1. TestFit Dependency**
>
> - We're using a commercial tool as the core engine
> - Constraint: We're limited by what TestFit supports
> - Some advanced WHA requirements might not be configurable
> - Example: Phased development, utility routing, topography
>
> **2. Semi-Automated Workflow**
>
> - The TestFit generation step is currently manual (click a button)
> - For production, we'd automate via API or web automation
> - This affects batch processing (can't run 50 sites overnight yet)
>
> **3. Validation is Basic**
>
> - We check 12 key constraints
> - Full WHA rulebook probably has 50+ requirements
> - System catches obvious issues, but human review is still necessary
>
> **4. Output Quality Variability**
>
> - TestFit is a black box—we don't control its algorithm
> - Sometimes it generates excellent layouts, sometimes just okay
> - That's why we recommend generating 3+ alternatives and picking the best
>
> **5. No Support For:**
>
> - Existing buildings/obstacles
> - Complex topography (steep slopes, water bodies)
> - Utility routing (water, sewer, electrical)
> - Construction phasing
> - Cost estimation (needs WHA cost database integration)
>
> [Pause]
>
> **These are all solvable.** The question is: Is the current capability valuable enough to justify investment in Phase 2?"

---

## **MINUTE 25-27: NEXT STEPS & RECOMMENDATION**

**[Slide 8: Roadmap]**

**Visual:**

```
┌────────────────────────────────────────────────────┐
│  PHASE 1: POC (COMPLETE)        ✓ 2 weeks          │
│  └─ Proof of technical feasibility                 │
│                                                     │
│  PHASE 2: PILOT                 → 4-6 weeks        │
│  └─ Test on 3 real projects                        │
│  └─ Collect designer feedback                      │
│  └─ Measure actual time savings                    │
│                                                     │
│  PHASE 3: PRODUCTION            → 2-3 months       │
│  └─ Full automation (API integration)              │
│  └─ Expanded validation (50+ checks)               │
│  └─ Web interface for planners                     │
│  └─ Integration with WHA systems                   │
│                                                     │
│  PHASE 4: ENHANCEMENT           → Ongoing          │
│  └─ Utility routing                                │
│  └─ Cost estimation                                │
│  └─ Phasing optimization                           │
│  └─ Custom algorithms (if needed)                  │
└────────────────────────────────────────────────────┘
```

**SCRIPT:**
> "Here's what I recommend:
>
> **Phase 2: Pilot (4-6 weeks)**
>
> - Select 3 real projects (varying complexity: easy, medium, hard)
> - Run AI generation alongside traditional process
> - Measure actual time savings
> - Collect designer feedback: What works? What doesn't?
> - Cost: $5K-10K (software licenses + my time)
>
> **If pilot succeeds:**
>
> **Phase 3: Production Deployment (2-3 months)**
>
> - Automate TestFit integration (eliminate manual step)
> - Expand validation to full WHA rulebook
> - Build web interface (no command line for planners)
> - Train team on usage
> - Cost: $20K-40K (development + training)
>
> **Phase 4: Long-term enhancements** (optional)
>
> - Advanced features (utilities, phasing, cost)
> - Custom algorithms (if TestFit limitations become blocker)
> - Cost: Depends on scope
>
> **Alternative path:** If TestFit proves insufficient in pilot, we have learnings to build custom solution. POC de-risks that investment.
>
> **My recommendation:** Approve Phase 2 pilot. $10K investment to validate $300K/year savings potential is a no-brainer."

---

## **MINUTE 27-30: Q&A**

**[Slide 9: Thank You + Contact]**

**SCRIPT:**
> "That's the demo. I'll open for questions now.
>
> [Pause—wait for hands/unmute]
>
> [For each question, follow structure:]
>
> 1. Repeat question for audience
> 2. Answer clearly and concisely
> 3. Reference demo evidence if applicable
> 4. If you don't know: 'Great question—I'll research that and get back to you by [date]'"

---

### **ANTICIPATED QUESTIONS & ANSWERS**

**Q: "How much does TestFit cost?"**
> A: "TestFit Industrial is $299-499/month depending on license level. For 50 projects/year at $6K savings each, that's $300K saved vs. $6K cost—50:1 ROI."

**Q: "Can we negotiate an enterprise deal with TestFit?"**
> A: "Yes—if pilot proves value, we can approach TestFit with volume commitment for better pricing. Or explore licensing their engine for custom integration."

**Q: "What if TestFit goes out of business or changes pricing?"**
> A: "Valid risk. Mitigation: 1) Pilot proves the value of AI approach, 2) We'd have learned enough to build custom solution if needed, 3) TestFit is backed by Autodesk (acquired in 2021)—low bankruptcy risk."

**Q: "Can it handle non-rectangular sites?"**
> A: "Yes—we tested with RY36's actual boundary (irregular polygon). System handles any shape. Complex sites just take longer to process."

**Q: "What about sites with existing buildings?"**
> A: "Not in current POC—we assumed greenfield. Adding obstacle avoidance is feasible (Phase 3 enhancement, 2-4 weeks development)."

**Q: "How do we know the AI doesn't violate local regulations?"**
> A: "The validation engine checks WHA's internal standards. For local regulations (Thai Industrial Estate Authority rules), we'd need to encode those as additional validation checks. That's Phase 2 work—requires legal/compliance input."

**Q: "Can designers override AI decisions?"**
> A: "100% yes. The DWG output is fully editable. AI is a starting point, not a straitjacket. Think of it like autocorrect—helpful suggestions, but you're in control."

**Q: "How long until this is production-ready?"**
> A: "If we start Phase 2 pilot next week: 4 weeks pilot + 2 weeks feedback incorporation + 2 weeks deployment = **8-10 weeks to production system**."

**Q: "What's the biggest risk?"**
> A: "That TestFit's algorithm doesn't align well with WHA's design philosophy. That's exactly what the pilot tests. If it doesn't work, we've invested $10K to learn that—cheap insurance before committing $100K+ to custom build."

**Q: "Can this work for residential or mixed-use projects?"**
> A: "TestFit supports residential (apartments, townhouses) and mixed-use. The wrapper would need adaptation for different layer standards and constraints, but core approach applies. Industrial is just the starting point."

**Q: "Who owns the IP if we build custom solution later?"**
> A: "The POC code is WHA's property (I'm your employee/contractor). If we build custom solution in Phase 4, that IP is also WHA's. TestFit IP remains theirs (we're licensing, not buying)."

**Q: "Can we see the code?"**
> A: "Absolutely—it's all Python, well-commented. I'll share the GitHub repository after this meeting. The system is designed to be maintainable by any Python developer on your team."

---

## **CLOSING (30 seconds)**

**SCRIPT:**
> "Thank you all. To summarize:
>
> ✓ We proved AI can generate usable master plans in 5 minutes
> ✓ Output quality is 70-80% of human level—good enough for draft
> ✓ Potential savings: 60-80% time, $300K/year at scale
> ✓ Recommended next step: Phase 2 pilot (3 projects, 4 weeks, $10K)
>
> I'll send follow-up email with:
>
> - These slides (PDF)
> - Demo video recording
> - Sample output files
> - Pilot proposal document
>
> Decision timeline: Please confirm GO/NO-GO by [date, typically 1 week from today].
>
> Thank you."

**[End of demo]**

---

## **POST-DEMO CHECKLIST**

**Immediately after:**

- [ ] Save all demo files (don't close anything until backed up)
- [ ] Note any technical issues that occurred
- [ ] Write down all questions asked (even if answered)
- [ ] Capture stakeholder body language observations

**Within 24 hours:**

- [ ] Send follow-up email (see Document 4 template)
- [ ] Upload demo recording to shared drive
- [ ] Share output files (DWG, PDF, JSON)
- [ ] Schedule debrief with your manager

**Within 1 week:**

- [ ] Prepare detailed answers to unanswered questions
- [ ] Draft Phase 2 pilot proposal
- [ ] Create cost estimate spreadsheet
- [ ] Schedule decision meeting

---

## **DEMO DAY SURVIVAL TIPS**

**If laptop freezes:**
→ Switch to backup laptop (have same files synced via USB)

**If projector fails:**
→ Use printed slides, describe demo verbally, show video on phone

**If internet fails:**
→ All files are local, continue demo offline

**If AutoCAD crashes:**
→ Have screenshots of opened file ready to show

**If Python script errors:**
→ Show pre-generated output, say "this usually works—I'll debug after"

**If TestFit website is down:**
→ Use pre-recorded video of generation, explain "live site is experiencing issues"

**If audience is hostile/skeptical:**
→ Stay calm, acknowledge limitations honestly, focus on data not promises

**If audience is too excited:**
→ Manage expectations—emphasize "POC not production," "pilot needed to validate"

**If decision-maker leaves early:**
→ Ask if they want summary email or separate 1-on-1 briefing

**If you blank on a question:**
→ "That's an excellent question—let me research it properly and get back to you by [date]"

---

**You've got this. Practice the demo 3 times before the real thing. Know your backup plans. Be honest about limitations. Focus on value, not perfection. 🚀**
