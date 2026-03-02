# WHA AI Master Plan: Technical RFP Specification & POC Scope

**Document ID:** 11_Consolidated_RFP_Spec
**Version:** 1.0 (Bulletproof Edition)
**Status:** **APPROVED FOR VENDOR DISTRIBUTION**

---

## 1. Executive Overview

This document defines the technical specifications, evaluation criteria, and "Rules of Engagement" for vendors participating in the WHA AI Master Plan Proof of Concept (POC).

**Strategic Intent:** WHA is seeking a **production-grade partnership**, not just a demonstration. This POC validates technical reality, filtering out "vaporware" and marketing hype.

---

## 2. Technical Scope & Requirements

### 2.1 Input Data Specifications (Mandatory)

Vendors must demonstrate the ability to ingest WHA-standard data without manual cleaning.

* **A. Land Boundary Data:**
  * **Format:** AutoCAD DWG (R2018 or later) OR ESRI Shapefile.
  * **Coordinate System:** **EPSG:32648 (WGS84 / UTM Zone 48N)**.
  * **Required Attributes:** Closed polyline for Site Boundary.
  * **Context:** Existing topography contours (if available) and protected Environmental Zones.

* **B. Planning Constraints (Hard Rules):**
  * **Setbacks:** Min [X] meters from boundary.
  * **Fire Access:** Mandatory [Z] meter lanes for all plots.
  * **Building Coverage:** Max [Y]% Plot Coverage Ratio (PCR).

* **C. Planning Preferences (Optimization Goals):**
  * **Plot Size Distribution:** Target mix (e.g., 20% Small, 50% Medium, 30% Large).
  * **Saleable Efficiency:** Maximize Saleable Area % (Target: >[E]%).
  * **Road Hierarchy:** Distinct profiles for Primary ([W1]m) vs. Secondary ([W2]m) roads.

### 2.2 AI Functionality: The "Real Intelligence" Test

The solution must demonstrate genuine spatial reasoning, not just random generation.

**PHASE 1: Site Analysis**

* Parse boundary geometry and identify buildable vs. unbuildable zones (wetlands, slopes).
* **Fail Condition:** System ignores exclusion zones.

**PHASE 2: Network Generation**

* Generate a fully connected road network respecting turning radii for industrial trucks.
* **Fail Condition:** Dead-ends longer than [L] meters or isolated plots.

**PHASE 3: Plot Subdivision**

* Subdivide blocks into saleable plots respecting target aspect ratios (rectangularity).
* **Fail Condition:** "Sliver" plots or unusable irregular shapes.

**PHASE 4: Infrastructure Allocation**

* Auto-allocate green buffers and utility corridors (drainage/power) based on % requirements.

### 2.3 Output Requirements (The "Usability" Test)

Outputs must be immediately usable by WHA designers in their native workflow.

* **A. File Format:** Native AutoCAD DWG (R2018+). **NO BLOCKS/XREFS**.
* **B. Layer Standards (Strict Compliance):**
  * `BOUNDARY-SITE` (White, Continuous)
  * `ROAD-PRIMARY-ROW` (Yellow, Continuous)
  * `PLOTS-BOUNDARY` (Green, Continuous) – *Must be closed polylines*
  * `PLOTS-LABELS` (Green, Text) – *Must contain Plot ID + Area*
  * `CONSTRAINTS-VIOLATION` (Red, Hidden) – *Highlighting errors*
* **C. Editability:**
  * Geometry must be topologically clean (no overlaps).
  * Designers must be able to stretch/move plot lines using standard CAD tools.

---

## 3. Technical Transparency (Anti-Vaporware Clause)

To ensure genuine capability, vendors must disclose:

* **A. AI Approach:**
  * Is this Rule-Based, Evolutionary Optimization, or Deep Learning?
  * *Note: WHA prefers Hybrid (Rules + Optimization) for auditability.*

* **B. "Black Box" Transparency:**
  * If using ML, what data was it trained on? (Relevance to SE Asian Industrial Estates?)
  * If Rule-Based, are rules editable by WHA staff without coding?

* **C. Reproducibility:**
  * Given identical inputs + seed, does the system produce identical outputs?

---

## 4. Evaluation Criteria (Scoring Rubric)

**Total Score: 100 Points** (Passing = 75)

### 4.1 Technical Capability (40%)

* **Spatial Quality (15 pts):** Plot regularity > 0.75, No dead ends.
* **Constraint Compliance (10 pts):** Zero setback violations.
* **CAD Usability (10 pts):** Files open in AutoCAD 2018+ with correct layers.
* **Adaptability (5 pts):** Live demo of parameter change (e.g., "Change Min Plot Size").

### 4.2 Practical Usability (30%)

* **Designer Workflow (15 pts):** Can a human modify the AI output in <5 steps?
* **Interpretability (10 pts):** Does the system explain *why* it placed a road there?
* **Learning Curve (5 pts):** Can a planner learn it in <4 hours?

### 4.3 Scalability & Future Readiness (20%)

* **Portfolio Scale:** Can it handle 50+ hectare sites?
* **Extensibility:** Can we add new rules (e.g., EIA buffers) later?

### 4.4 Vendor/Team Capability (10%)

* **Support:** Response time SLA.
* **Data Security:** On-premise / Local-cloud capability (Data Residency).

---

## 5. POC Execution Plan (Tiered)

To manage risk, the POC will be executed in stages:

* **Tier 1: Mandatory Foundation (Week 1-3)**
  * Test Site: Simple rectangular 50ha plot.
  * Goal: Valid CAD output, Basic Constraints met.
  * *Result: Pass/Fail for Tier 2.*

* **Tier 2: Complex Scenario (Week 4-5)**
  * Test Site: Irregular 120ha plot with obstacles.
  * Goal: Demonstrate adaptability and handling of "messy" reality.

---

## 6. Business & Legal Framework

### 6.1 ROI Validation (Business Case)

* **Current State:** 3-5 days per iteration.
* **Target State:** <1 day per iteration (AI Draft + Human Polish).
* **Break-Even:** System pays for itself within [X] months based on [Z] projects/year.

### 6.2 Legal & IP

* **Ownership:** WHA owns all *generated* layouts and *WHA-specific* rules configurations.
* **Licensing:** Vendor retains core algorithm IP.
* **Exit Strategy:** Data exportability guaranteed; no vendor lock-in on generated assets.

### 6.3 Automatic Disqualification

Vendors are **disqualified** if:

* Outputs are raster images or non-editable blocks.
* System requires data transmission to public cloud (Security Violation).
* Vendor cannot demonstrate live regeneration during demo (evidence of "faked" demo).

---

## 7. Decision Framework

Post-POC, the committee will vote:

1. **GO (Full Scale):** >75 Points. Proceed to Pilot.
2. **GO (Modified):** 60-74 Points. Proceed with reduced scope (e.g., Road generation only).
3. **NO-GO:** <60 Points. Technology immature; revisit in 12 months.

---

**Prepared By:** WHA AI Engineering Team
**Approved By:** [Stakeholder Name]
**Date:** [Date]
