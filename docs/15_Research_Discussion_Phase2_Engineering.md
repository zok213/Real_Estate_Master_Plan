# **Research Discussion: Phase 2 Engineering Decisions**
## Constraint-Aware Generative Layouts for Industrial Estate Master Planning

**Date:** March 8, 2026  
**Purpose:** Critical engineering review of the Phase 2 research report. Use this document as a living prompt base — each section contains verifiable claims, open questions, and next research prompts.  
**Status:** Active — iterate and update as verification progresses.

---

## PART A: OVERALL VERDICT — IS THE APPROACH SOUND?

### Short Answer
**Mostly yes, but with two major domain-mismatch warnings that could derail the prototype if not caught early.**

### The Core Recommended Path (from research report)
```
LLM/heuristic JSON layout proposal
  → MILP/CP-SAT + Shapely/CGAL enforcement
  → DXF via ezdxf
  + image diffusion kept purely for visualization
```

### Engineering Verdict Table

| Component | Verdict | Confidence | Risk Level |
|---|---|---|---|
| JSON intermediate representation | ✅ Correct strategy | High | **Schema design is the hard part — not mentioned in report** |
| LLM as topology reasoner | ✅ Correct role | High | LLM must produce topology, NOT coordinates |
| CP-SAT for constraint enforcement | ✅ Well-suited | High | Irregular boundary requires careful discretization |
| Shapely/CGAL for geometry | ✅ Production-ready | High | Low risk |
| ezdxf for DXF output | ✅ Production-ready | High | Low risk |
| ResPlan-style JSON schema | ⚠️ Domain mismatch | High | Residential rooms ≠ industrial estate topology |
| HouseDiffusion / DiffPlanner | ❌ Wrong training domain | High | Thai industrial estates ≠ US floor plans |
| DiffVG / LIVE for raster-to-vector | ❌ Wrong use case | High | Designed for logos/illustrations, not zoning maps |
| Hard diffusion projectors | ⚠️ Experimental | Medium | Not proven for large irregular topologies |
| Scan2CAD / WiseImage for raster-to-vector | ⚠️ Limited applicability | Medium | Designed for mechanical drawings, not colour maps |

---

## PART B: COMPONENT-BY-COMPONENT ENGINEERING CRITIQUE

### B.1 — JSON Intermediate Representation

#### What the Report Says
Use a "ResPlan-style JSON" as an intermediate representation — LLM generates a JSON layout description, a solver enforces hard constraints, ezdxf compiles it to DXF.

#### Engineering Critique — STRONG STRATEGY, WRONG REFERENCE SCHEMA

The strategy is correct. The reference is wrong.

**ResPlan** (NeurIPS 2023, Ma et al.) is designed for:
- ~5–20 rectangular rooms inside a rectangular building footprint
- Room types: living room, bedroom, kitchen, bathroom
- Constraints: adjacency, door placement, room size ratios
- Scale: ~200 m² total footprint

**WHA industrial estate layout requires:**
- 100–400 irregular plots inside a non-rectangular 288 ha boundary
- Zone types: factoryplot_A, factoryplot_B, WWTP, retention_pond, substation, green, road
- Constraints: IEAT Clauses 6–36 (see §8.6 SOP), setbacks, flood berm continuity, road connectivity
- Scale: 2,880,000 m² — 14,400× larger than a residential plan

**Conclusion:** ResPlan's JSON schema cannot be reused. A WHA-specific schema must be designed from scratch.

#### Proposed WHA Industrial Estate JSON Schema (Draft)

```json
{
  "site_id": "WHA_RY36",
  "boundary_polygon": [[x1,y1], [x2,y2], "..."],
  "area_rai": 1800.0,
  "constraints_ref": "constraints.json",
  "road_network": {
    "spine_road": {
      "centerline": [[x,y], "..."],
      "right_of_way_m": 30,
      "surface_width_m": 14,
      "footpath_m": 2
    },
    "secondary_roads": [
      {"id": "R1", "centerline": [[x,y], "..."], "right_of_way_m": 16}
    ]
  },
  "plot_blocks": [
    {
      "block_id": "B1",
      "bounding_box": [x_min, y_min, x_max, y_max],
      "plots": [
        {"plot_id": "P001", "zone": "industrial_A", "area_sqm": 8000, "geometry": [[x,y], "..."]}
      ]
    }
  ],
  "utility_zones": {
    "wwtp": {"location": "southeast", "area_sqm": 30000},
    "retention_pond_1": {"area_sqm": 50000},
    "substation_primary": {"location": "north_access_road"}
  },
  "compliance_flags": {
    "clause_6_road_width": "pass",
    "clause_16_drainage_q_m3s": 36.1,
    "clause_21_flood_berm_level_m": 3.2
  }
}
```

#### Open Questions
- [ ] What is the minimum JSON field set for CP-SAT to solve the layout? (road topology + boundary only? or full geometry?)
- [ ] Should plot geometry be in the JSON, or computed entirely by solver from block bounding boxes?
- [ ] How does the LLM receive the boundary polygon from the DWG? (ezdxf.read → extract boundary vertices → pass as JSON coordinate list)

#### Research Prompt B.1
```
I am building a JSON intermediate representation for an AI system that generates 
industrial estate master plans (scale: ~288 hectares, 200-400 industrial plots, 
Thai IEAT regulatory framework). 

Compare how these papers define their layout JSON schemas and which aspects 
apply to large outdoor industrial context (NOT residential/indoor):
- LayoutGPT (ICML 2023)
- HouseTune/Tell2Design  
- ResPlan (NeurIPS 2023)
- StructDiffusion

Specifically: how do they encode road networks, irregular boundaries, and zone 
types with minimum JSON verbosity while preserving constraint-checkability?
What is the minimum schema that allows a CP-SAT solver to reconstruct all 
hard geometric constraints?
```

---

### B.2 — LLM as Spatial Reasoner

#### What the Report Says
LLM (GPT-4o / Qwen) generates a JSON layout proposal. MILP/CP-SAT then enforces hard constraints on that proposal.

#### Engineering Critique — CORRECT ROLE ASSIGNMENT, BUT WRONG EXPECTATION

**What LLMs are good at in this context:**
- Interpreting the site boundary description ("irregular trapezoid, hilly north side, highway access from west")
- Choosing zone distribution ("WWTP in the southeast corner away from prevailing wind from west, substation near main access road")
- Deciding road network topology ("grid with spine road north-south, three secondary E-W roads")
- Estimating rough plot counts per zone type based on area percentages

**What LLMs are BAD at (confirmed by 2023–2024 research):**
- Generating precise coordinates (CoT-spatial studies show LLMs have poor Euclidean distance reasoning)
- Computing areas from polygons without tool calls
- Ensuring non-overlap without external checker
- Generating topologically consistent road networks from scratch

**Critical Distinction — the research report implies LLM generates coordinates. It must NOT.**

Correct pattern:
```
LLM → topology JSON (which roads, how many blocks, zone assignments, rough sizes)
Solver → geometry JSON (computed coordinates from topology + boundary polygon)
ezdxf → DXF output
```

Incorrect pattern:
```
LLM → JSON with coordinates
Solver → validate/fix coordinates
ezdxf → DXF
```

The incorrect pattern causes LLM hallucination to propagate into the DXF. The solver becomes a debugger, not an optimizer.

#### Open Questions
- [ ] What few-shot prompt format gets Qwen3-VL to reliably output valid road topology (no coordinates)?
- [ ] How does LayoutGPT handle coordinate generation — does it use absolute coords or relative/parametric descriptions?
- [ ] What is the max JSON complexity an LLM can reliably generate in one shot without structural errors?

#### Research Prompt B.2
```
In LLM-based layout generation (LayoutGPT, StructDiffusion, Houseplan-as-code 
approaches), what is the established boundary between:
  (a) what the LLM generates (semantic / topological specification), and
  (b) what a downstream solver computes (geometric coordinates)?

Specifically: can an LLM reliably generate road network topology for a 288-hectare 
industrial estate as a graph (nodes + edges + attributes) without generating 
explicit polygon coordinates? What prompting techniques (chain-of-thought, tool-use, 
structured output) improve spatial topology reliability in practice?
Are there benchmarks (measured JSON parse success rate, spatial consistency metrics) 
for LLM-generated layout JSON?
```

---

### B.3 — CP-SAT and MILP for Constraint Enforcement

#### What the Report Says
Use OR-Tools CP-SAT + Shapely/CGAL for hard geometric constraint enforcement.

#### Engineering Critique — CORRECT TOOL, FORMULATION IS UNDERSPECIFIED

CP-SAT is the right solver. The formulation challenge is significant and not addressed in the report.

**The formulation problem:**

Industrial plot layout is a variant of 2D bin-packing with geometric constraints. For WHA:

| Decision Variable | Type | Count |
|---|---|---|
| Plot position (x,y) | Continuous | ~200–400 |
| Plot dimensions (w,h) | Continuous or discrete | ~200–400 |
| Road segment presence | Boolean | ~50–100 |
| Zone assignment per block | Integer | ~20 blocks |

CP-SAT handles **integer/boolean variables**. Continuous position (real-valued x,y coordinates) requires conversion.

**Three valid approaches:**

**Approach 1 — Grid Discretization (Recommended for 2-week POC)**
Discretize the boundary polygon to a grid (e.g., 10m × 10m cells = 288,000 cells for 288 ha).
Each plot occupies a rectangular region of cells. CP-SAT assigns plots to grid positions.
Shapely checks final geometry for constraint violations.

- Pro: CP-SAT handles naturally, fast for typical plot sizes
- Con: 10m grid gives ±10m positional error; need 1m grid for ±1m (28,800,000 cells — feasible but slower)
- For Phase 1 POC: 10m grid is fine; refine to 1m in Phase 2

**Approach 2 — Explicit MILP on Plot Rectangles (More Precise)**
For each pair of adjacent plots, add non-overlap constraints as linear inequalities.
For N plots: N×(N-1)/2 constraint pairs → ~40,000 constraints for 200 plots.
OR-Tools GLOP or SCIP handles this.

- Pro: Precise coordinates, no grid approximation
- Con: Slow for irregular boundaries; needs boundary-as-halfplanes, which is complex for non-convex polygons

**Approach 3 — Heuristic Road Grid + Shapely Pack (Fastest POC)**
1. Skeleton-ize the boundary polygon (compute medial axis via Shapely + skimage)
2. Generate road network from skeleton (snap to grid)
3. For each road block: pack plots greedily from top-left, skipping boundary violations
4. Shapely validates final layout

This is NOT CP-SAT at all — it's a heuristic. But it's completeable in 3 days, produces realistic output, and is closer to how human planners actually work.

**RECOMMENDATION for 2-week POC: Approach 3 + Shapely validator**
Build CP-SAT solver in Phase 2 when you have a working pipeline to plug it into.

#### The IEAT Constraints as Solver Rules
From `constraints.json` and IEAT Clauses 6–36:

```python
# These must be enforced by solver/Shapely:
CONSTRAINT_SET = {
    "boundary_setback": 15.0,           # m — from constraints.json
    "primary_road_width": 30.0,         # m — IEAT Clause 6 (>1000 rai estate)
    "secondary_road_width": 16.0,       # m
    "min_plot_area": 5000.0,            # sqm — constraints.json
    "max_plot_area": 15000.0,           # sqm
    "road_gradient_max": 0.04,          # 4:100 — IEAT Clause 7
    "plot_to_total_ratio": 0.70,        # 70% saleable
    "green_ratio": 0.05,                # 5%
    "pond_ratio": 0.05,                 # 5%
    "road_ratio": 0.20,                 # 20%
    "flood_berm_height_m": 0.5          # above 10-year flood level
}
```

3 IEAT clauses are not yet coded (see SOP Part 9). These must be identified and added before the constraint checker is production-grade.

#### Open Questions
- [ ] What are the 3 uncoded IEAT clauses? (Need to enumerate from IEAT Regulations B.E. 2555 full text)
- [ ] Is OR-Tools CP-SAT with 10m grid discretization fast enough for 200+ plots on a CPU? (Benchmark needed)
- [ ] Does Shapely's `polygon.contains(point)` handle floating-point edge cases for boundary coincidence?
- [ ] How does the skeleton-to-road heuristic behave on the actual RY36 boundary polygon?

#### Research Prompt B.3
```
I need to build a 2D industrial estate layout optimizer with the following constraints:
- Boundary: irregular polygon of ~288 hectares (non-convex, 20-40 vertices)
- Constraints: all plots inside boundary; setback 15m; primary road ROW 30m; 
  secondary road ROW 16m; plots 5000-15000 sqm; road area = 20%, green = 5%, 
  saleable = 70%
- Solver target: maximize total saleable area while satisfying all above

Compare these three approaches for a 2-week prototype timeline:
(a) OR-Tools CP-SAT with 10m grid discretization
(b) OR-Tools GLOP/SCIP with MILP non-overlap constraints  
(c) Heuristic skeleton road generation + greedy plot packing + Shapely validation

For each: estimate implementation time, output coordinate precision (target ±1m at real scale), 
and scalability to 400 plots. Which is best for a first working prototype? 
Include specific code patterns or algorithm pseudocode.
```

---

### B.4 — Raster-to-Vector Pipeline (Q2 Assessment)

#### What the Report Says
Use Scan2CAD, WiseImage, or DiffVG/LIVE for raster-to-vector conversion. Target ±0.5m at 1:1000 scale.

#### Engineering Critique — TOOL MISMATCH + UNREALISTIC ERROR BUDGET

**DiffVG / LIVE:** Designed for differentiable rendering of simple vector graphics (logos, icons, artistic paths). They optimize SVG parameters with gradient descent. They have never demonstrated reliable results on:
- Multi-layer colored zoning maps
- Text annotations with leaders
- Hatch-filled polygons (industrial zones)
- Overlapping geometry at >100 layers

**Scan2CAD (Shen et al., 2021):** Designed for mechanical CAD drawings (black-and-white line art with clean geometry). It works on scanned floorplans. It would struggle on:
- Full-color WHA master plans (color semantic segmentation is not its pipeline)
- Multi-layer DWG exports with hatching
- Thai text annotations

**WiseImage / Raster Design (Autodesk):** Best option from the list for WHA use case. WiseImage is specifically designed for raster-to-vector conversion of engineering drawings. Can handle color segmentation with manual layer assignment. Limitation: it's a commercial desktop tool, not a pipeline-embedable library.

**The real error budget problem:**

"±0.5m at 1:1000 scale" means ±0.5px at 1 pixel-per-metre rendering.
To achieve ±0.5m in practice, you need:
- Source image rendered at ≥ 200 DPI on A0 paper at 1:1000 scale → ~3000×4000 pixels minimum
- Zero JPEG compression artifacts (use PNG/TIFF only)
- Clean background (no scan noise, no grid lines)
- Sub-pixel accurate line detection

WHA's existing DWG files export cleanly at any resolution — this is actually achievable, but only if the DWG → PNG export pipeline uses high-resolution settings. 300 DPI on A0 = ~9900×7000 pixels.

**Better raster-to-vector path for WHA specifically:**

```
Option A (skip pure raster-to-vector):
  Skip raster entirely — go DWG → DXF (via ODA File Converter or AutoCAD SaveAs DXF)
  Then ezdxf reads the DXF directly — no raster→vector error introduced at all
  This is what the verification report in doc 12 tried to do
  STATUS: Works if AutoCAD or ODA Converter is installed

Option B (Color-aware segmentation before vectorization):
  PNG → semantic segmentation (U-Net or SAM2 to segment zones by color)
  → per-zone binary mask → skimage contour → Shapely polygon → ezdxf entity
  This handles the color layer problem Scan2CAD cannot
  
Option C (as last resort only):
  WiseImage or Autodesk Raster Design for commercial raster-to-vector
  Requires commercial license; not pipeline-embeddable
```

Option A is almost always the right answer for WHA — the DWG files exist. Use them.

#### Open Questions
- [ ] Is ODA File Converter installed on the WHA production environment? (Check doc 12 — answer is no)
- [ ] Does the host machine have any AutoCAD-compatible software for DWG → DXF export?
- [ ] What is the actual DPI setting when WHA staff currently export DWG to PNG?
- [ ] Can SAM2 reliably segment WHA color-coded zone polygons without fine-tuning?

#### Research Prompt B.4
```
For raster-to-vector conversion of a color-coded industrial estate master plan PNG 
(exported from AutoCAD at 300 DPI, A0 sheet, 1:1000 scale, PNG/TIFF, WHA Thailand):

The plan has:
- Color-coded zone polygons (industrial, road, green, retention pond, WWTP)
- Road network as white/grey polygons
- Hatch patterns inside industrial zones
- Thai text annotations with leaders
- Clean vector export quality (no scan noise)

Compare these approaches:
(a) Direct DWG→DXF via ezdxf (bypasses raster entirely)
(b) Color semantic segmentation (SAM2 or U-Net) → polygon contour → ezdxf
(c) Scan2CAD reconstruction pipeline
(d) DiffVG/LIVE optimization

For each: state the actual use case it was designed for, realistic error at 1:1000 scale,
and whether it handles multi-color zoning maps. Which is most appropriate here?
What are the minimum DPI/resolution requirements to achieve ±0.5m positional accuracy?
```

---

### B.5 — Vector-Native Shortcut: Is JSON+Solver Better Than DXF Tokens?

#### What the Report Says
JSON-intermediate approach (LLM → topology JSON → rule-based DXF compiler) is more realistic than full DXF token model. References: CADTransformer, DeepCAD, SkexGen.

#### Engineering Critique — CORRECT CONCLUSION, IMPORTANT CAVEATS

The research report is right that JSON+solver is more realistic than DXF tokens given WHA's 1-file dataset. But the comparison needs precision:

**DXF Token Models (CADTransformer, DeepCAD, SkexGen):**

| Model | Year | Training Data | Input/Output | Scale |
|---|---|---|---|---|
| DeepCAD | 2021 | 179,133 CAD models (ABC dataset) | Sketch sequences → 3D model | 3D mechanical parts |
| CADTransformer | 2022 | 80,000+ floorplan DXF | Image → DXF token sequence | 2D floorplans |
| SkexGen | 2022 | ShapeNet (3D) | 3D → sketch sequences | 3D industrial parts |

None of these handle 2D industrial estate master plans. CADTransformer is closest but covers residential floorplans at building scale (~200 sqm), not industrial estates at site scale (~2.88 km²).

**JSON+Solver Advantage:**

The JSON+solver approach does NOT need a trained neural model for the core layout computation. It uses:
1. A pre-trained LLM (zero-shot or few-shot) for topology reasoning
2. A deterministic solver for geometry
3. A deterministic ezdxf compiler for output

This means it can work today with 1 training example (RY36 Final as a reference in the few-shot prompt). It is the right approach for the current data situation.

**Critical Caveat — "LLM shortcut" is still a 4-step pipeline:**

```
Step 1: DWG/PNG → parse boundary polygon (ezdxf or DWG→PNG→SAM2)
Step 2: LLM → topology JSON (road graph + zone distribution)
Step 3: Solver/heuristic → geometry (coordinates from topology)
Step 4: ezdxf → DXF output with WHA layer standards
```

Each step can fail independently. Error propagation across steps is the main engineering challenge.

**What the JSON Schema Must Capture (WHA-specific):**

Unlike a floor plan where walls contain rooms, an industrial estate JSON must capture:
1. **Road network as graph** (not room adjacency)
2. **Flood berm as boundary component** (not just a line — it has structural requirements from IEAT Clause 21)
3. **Utility zone placement rules** (WWTP southeast, substation near main road per planning convention)
4. **Phase designation** (which plots are Phase 1 vs Phase 2 development)
5. **Topographic influence** (road gradients, cut-and-fill zones)

These are not captured in any residential JSON schema. They must be WHA-designed.

#### Open Questions
- [ ] What is the minimum JSON schema that allows ezdxf to reconstruct a legally valid DXF without human correction?
- [ ] Can a GP-4o class LLM generate consistent road network topology JSON across multiple runs given the same boundary description? (Test: run 5 times, measure variance)
- [ ] How does ezdxf handle curved boundary lines (splines in WHA DWG)? Does `ezdxf.entities.Spline` preserve arc accuracy?
- [ ] Is there a Thai industrial estate spatial dataset (IEAT, EEC, BOI industrial zones) that could supplement WHA data for LLM fine-tuning?

#### Research Prompt B.5
```
I am building a JSON-intermediate pipeline for industrial estate master plan generation:
  LLM topology JSON → heuristic/solver geometry → ezdxf DXF output → AutoCAD

The intermediate JSON must encode:
- Road network as a directed graph (spine + secondary roads with IEAT widths)  
- Plot block regions (bounding boxes, zone types, rough counts)
- Utility zone placements (WWTP, retention ponds, substation, green buffer)
- Compliance flags (IEAT clause pass/fail per zone)
- Boundary polygon reference

Compare these JSON layout representation approaches:
(a) Graph-based (nodes=intersections, edges=road segments + attributes)
(b) Block-based (rectangular blocks subdivided into plots)
(c) Zone-based (zone polygons first, then road network fills gaps)
(d) Instruction-based (natural language style descriptions compiled to geometry)

For industrial scale (~288 ha, ~200-400 plots, ~50 road segments):
- Which representation minimizes LLM hallucination of invalid geometry?
- Which allows fastest CP-SAT/MILP formulation?
- Which produces most reliable ezdxf compilation?
- Is there production code (GitHub) for any of these that covers polygon boundaries?
```

---

## PART C: WHAT TO BUILD IN 2 WEEKS — REVISED SPRINT PLAN

Based on the critique above, the recommended path is adjusted:

### Week 1 — Foundation

| Day | Task | Deliverable | Risk |
|---|---|---|---|
| 1 | Design WHA industrial JSON schema (v0.1) | `schema/wha_layout_v0.1.json` | Schema may need iteration |
| 1–2 | Write ezdxf compiler: JSON → DXF (with WHA layers) | `src/json_to_dxf.py` | Low — ezdxf is well-documented |
| 2 | Write Shapely constraint checker: all IEAT rules from `constraints.json` | `src/constraint_checker.py` | Medium — need to encode 3 missing clauses |
| 3 | Manually author layout JSON for RY36 (truth reference) | `reference/ry36_layout_v0_manual.json` | Low — humans can read the DWG |
| 3–4 | Test JSON → DXF → open in AutoCAD/LibreCAD, compare with RY36 Final | Baseline visual comparison screenshot | Medium — coordinate system |
| 4–5 | Write heuristic road generator: boundary polygon → road grid skeleton | `src/road_heuristic.py` | High — irregular boundary is tricky |

### Week 2 — LLM Integration

| Day | Task | Deliverable | Risk |
|---|---|---|---|
| 6 | Write few-shot prompt for Qwen/GPT-4o: topo image → topology JSON | `src/prompts.py` (add topology prompt) | Medium |
| 6–7 | Test LLM JSON generation: 5 runs, same RY36 input, measure variance | Variance report | High — LLM may drift |
| 7–8 | Greedy plot packer: road grid → pack 8000 sqm plots respecting setbacks | `src/plot_packer.py` | High |
| 8–9 | Connect pipeline: PNG input → LLM topology → heuristic roads → Shapely pack → DXF | End-to-end test | High |
| 9–10 | Constraint audit: run `constraint_checker.py` on output, report IEAT pass rate | Compliance report vs RY36 | Medium |

### Priority Stack

```
MUST BUILD (blocks all downstream work):
  1. WHA JSON schema v0.1
  2. ezdxf JSON→DXF compiler
  3. Shapely IEAT constraint checker

SHOULD BUILD (core POC capability):
  4. Heuristic road generator
  5. Greedy plot packer
  6. LLM topology JSON prompt

DEFER (Phase 2, not 2-week POC):
  7. CP-SAT plot optimizer (replace greedy packer)
  8. Automated DWG→PNG pipeline (manual export is fine for POC)
  9. Raster-to-vector (use DWG→DXF directly)
  10. LoRA fine-tuning (insufficient data)
```

### What to Skip Entirely (Save the engineering hours)
- **HouseDiffusion / DiffPlanner** — wrong training domain; would require minimum 500 WHA-domain examples to fine-tune meaningfully
- **DiffVG / LIVE** — wrong use case; designed for artistic SVG, not engineering drawing conversion
- **DXF token model** — data gap is 9,999 files; not viable in any near-term timeline
- **Hard diffusion projectors** — research-grade, no production implementation; constraint precision unpredictable

---

## PART D: OPEN RESEARCH QUESTIONS (Verification Prompts)

Use these exact prompts in Perplexity (for citations) or Claude/GPT-4o (for code and architecture).

---

### D.1 — Verify: OR-Tools CP-SAT scalability for 200-plot bin-packing
```
RESEARCH PROMPT D.1:
What is the practical upper bound on OR-Tools CP-SAT performance for a 2D bin-packing 
problem with:
- 200–400 variable-size rectangles (5000–15000 sqm each)
- 1 large irregular polygon container (~288 ha)
- 10m grid discretization (→ ~288,000 grid cells)
- Non-overlap + boundary-containment constraints

On what CPU hardware and time budget can this be solved to optimality or 
near-optimality (>95% of maximum packing density)?
Are there published benchmarks or GitHub implementations for CP-SAT applied to 
rectangular packing inside irregular polygons?
```

---

### D.2 — Verify: ODA File Converter for DWG→DXF automation
```
RESEARCH PROMPT D.2:
How do I install and use the ODA File Converter (Open Design Alliance) on Windows 
to batch-convert multiple .dwg files to .dxf R2018 format without an AutoCAD license?

Specifically:
- Is it free for commercial use? Any licensing restrictions for industrial applications?
- What is the CLI syntax for batch conversion?
- Does it preserve all entity types from AutoCAD 2022 DWG (hatches, leaders, 
  mtext, dimensions, splines)?
- Is there a Python subprocess wrapper that's production-tested?
- Alternative: does ezdxf's recover module partially handle DWG binary without ODA?
```

---

### D.3 — Verify: ezdxf layer structure for WHA CAD standards
```
RESEARCH PROMPT D.3:
Using Python ezdxf, how do I:
1. Create DXF R2018 output with named layers matching WHA CAD standard 
   (e.g., BOUNDARY, ROAD_PRIMARY, ROAD_SECONDARY, PLOT_INDUSTRIAL, 
   UTIL_DRAINAGE, UTIL_POWER, UTIL_WATER, ANNOTATION)
2. Draw filled hatch polygons in DXF (for zone color fills)
3. Add dimension annotations with Thai font support
4. Set plot/page layout so it prints correctly on A0 at 1:1000 scale
5. Export to DXF R2018 compatible with AutoCAD 2022

Include code examples for each step. Are there any known ezdxf limitations 
with complex hatch patterns or polyline accuracy at large coordinate values 
(coordinates in the range 0 to 3000 metres)?
```

---

### D.4 — Verify: Shapely polygon operations for WHA constraint checking
```
RESEARCH PROMPT D.4:
Using Python Shapely 2.x, I need to validate an industrial estate layout against 
these geometric constraints:

1. All plot polygons fully contained within boundary polygon (with 15m buffer inset)
2. No two plot polygons overlap (tolerance: 0.01 sqm)  
3. Each plot has at least 12m of frontage on a road polygon
4. All road polygon widths are ≥ 16m (secondary) or ≥ 30m (primary)
5. Total plot area / total site area ≥ 0.70
6. Road gradient between connected road centreline points ≤ 4% 
   (requires elevation at each point from topo data)

For each constraint: show the correct Shapely method(s), common pitfalls 
(floating point, coordinate precision, self-intersection), and expected 
performance for ~300 polygons. Are there any constraints that Shapely cannot 
handle and need a different library (CGAL, PyClipper, Trimesh)?
```

---

### D.5 — Verify: LLM JSON generation reliability for spatial layouts
```
RESEARCH PROMPT D.5:
What is the current state of research (2023–2025) on using LLMs to generate 
structured JSON for spatial layouts?

Specifically I need evidence for or against this claim:
"An LLM (GPT-4o / Qwen3-VL-72B) can reliably generate a road network topology JSON 
(graph of ~50 road segments + ~20 rectangular plot blocks) for a given irregular 
polygon description and zone area targets, with <5% structural parse error rate 
and <10% logically invalid topologies (disconnected roads, plots outside boundary 
in the topology description)."

Cite specific benchmarks from LayoutGPT, HouseTune, Tell2Design, or similar papers.
What prompting techniques improve spatial layout JSON reliability?
What is the typical JSON failure mode: parse error, topology error, or constraint 
violation? Is tool-calling (structured output mode) significantly better than 
free-form generation with JSON schema in system prompt?
```

---

### D.6 — Verify: SAM2 for color-zone semantic segmentation on CAD maps
```
RESEARCH PROMPT D.6:
Can Segment Anything Model 2 (SAM2, Meta 2024) reliably segment color-coded 
zone polygons in an industrial master plan PNG exported from AutoCAD?

The image has:
- Clean anti-aliased edges (not scanned)
- Distinct solid fill colors per zone type (6–8 distinct colors)
- Overlapping annotations (text, leaders, dimensions)
- Hatch patterns inside zone polygons that could confuse segmentation

Specifically:
1. Does SAM2 work well on promptable (click-to-segment) mode for clean CAD exports?
2. Can it reliably extract clean polygon boundaries (without simplification artifacts)?
3. What post-processing turns SAM2 mask outputs into Shapely polygons with ±1m accuracy?
4. Is fine-tuning needed, or does zero-shot SAM2 work for this color fidelity level?
5. Are there alternative semantic segmentation approaches better suited to 
   CAD color maps (e.g., color-threshold + contour vs SAM2)?
```

---

## PART E: VERIFICATION CHECKLIST

Use this checklist to track what has been verified vs assumed.

### Research Claims from Report

| Claim | Status | Notes |
|---|---|---|
| CP-SAT can solve 200-plot layout in reasonable time | ❓ Unverified | Need benchmark — see D.1 |
| DiffVG/LIVE can vectorize CAD plans | ❌ Likely false | Wrong use case — designed for artistic SVG |
| Scan2CAD handles color zoning maps | ❌ Likely false | Designed for monochrome mechanical drawings |
| ±0.5m at 1:1000 is achievable with raster-to-vector | ❓ Conditional | Only if DWG→DXF direct path; impossible from raster if <300 DPI |
| HouseDiffusion/DiffPlanner apply to industrial estates | ❌ False | Trained on residential floor plans, wrong domain |
| ResPlan JSON schema applies to WHA | ❌ False | Residential rooms ≠ industrial estate topology |
| JSON+solver is more realistic than DXF tokens | ✅ Confirmed | Correct conclusion for WHA data situation |
| ezdxf can output production DXF | ✅ Confirmed | Used in doc 12 verification; known limitation: DWG input requires ODA |
| LLM should generate topology, not coordinates | ✅ Confirmed | Best practice from LayoutGPT et al. |
| ODA File Converter solves DWG input parsing | ❓ Unverified | Need to test — see D.2 |

### Pipeline Components Status

| Component | Built? | Tested? | WHA-specific? |
|---|---|---|---|
| WHA JSON schema | ❌ No | ❌ No | Required |
| ezdxf JSON→DXF compiler | ❌ No | ❌ No | Required |
| Shapely IEAT constraint checker | ❌ No | ❌ No | Required |
| Heuristic road generator | ❌ No | ❌ No | Required |
| Greedy plot packer | ❌ No | ❌ No | Required |
| LLM topology prompt | Partial (in app.py) | ✅ Demo mode | Needs JSON output format |
| DWG→DXF parsing (ezdxf direct) | ❌ No (ODA not installed) | ❌ No | Blocked by ODA |
| Raster-to-vector (SAM2 path) | ❌ No | ❌ No | Deferred to Phase 2 |
| CP-SAT optimizer | ❌ No | ❌ No | Deferred to Phase 2 |

---

## PART F: DECISION MATRIX — WHAT TO PROTOTYPE IN 2 WEEKS

| Component | Build Now? | Reason | Effort (days) |
|---|---|---|---|
| WHA JSON schema | **YES — first** | Blocks everything downstream | 1 |
| ezdxf JSON→DXF compiler | **YES** | Core output format | 1.5 |
| Shapely IEAT checker | **YES** | Needed for compliance report | 1.5 |
| Heuristic road generator | **YES** | First working layout needed | 2 |
| Greedy plot packer | **YES** | Needed for end-to-end pipeline | 1.5 |
| LLM topology prompt | **YES** | Core AI contribution | 1.5 |
| ODA File Converter setup | **IF AVAILABLE** | Clean DWG→DXF input; manual export otherwise | 0.5 |
| CP-SAT optimizer | **NO — Phase 2** | Greedy packer sufficient for POC | — |
| SAM2 segmentation | **NO — Phase 2** | Direct DXF path preferred | — |
| HouseDiffusion / DiffPlanner | **NEVER** | Wrong domain | — |
| DiffVG / LIVE | **NEVER** | Wrong use case | — |
| DXF token model | **NO — Phase 3** | Data gap too large | — |

**Total estimated effort for YES items: 9.5 days (fits in 2 weeks with buffer)**

---

## PART G: NEXT STEPS (Action Items)

1. **Immediate (today):** Run Research Prompts D.1–D.6 in Perplexity or Claude — paste each prompt, annotate the results in this document under each D.x section
2. **Day 1 of sprint:** Define WHA JSON schema v0.1 — use the draft in B.1, confirm with the WHA planner
3. **Day 2 of sprint:** Try `ezdxf.readfile("WHA RY36_Master Plan_Final.dxf")` — ask WHA to export DXF from AutoCAD; test what entities load correctly
4. **End of Week 1:** Manual JSON for RY36 + DXF output validator working — screenshot comparison vs original
5. **End of Week 2:** LLM → JSON → DXF pipeline, end-to-end, with constraint report printed

---

## PART H: DOCUMENT VERSION LOG

| Version | Date | Changes |
|---|---|---|
| v0.1 | March 8, 2026 | Initial engineering analysis created |

---

*This document is the primary engineering discussion file for Phase 2 research. Update it with findings from each research prompt, verification results, and sprint outcomes.*
