# 10_Risk_Mitigation_Plan.md

# RISK MITIGATION PLAN & CONTINGENCY STRATEGY

## 1. EXECUTIVE SUMMARY ON RISK

This project introduces **Probabilistic Technology** (Generative AI) into a **Deterministic Workflow** (Civil Engineering). The primary risks are not just software bugs, but "mismatched expectations" where the AI result is "technically correct but useless" due to nuance.

## 2. DETAILED RISK MATRIX

| ID | Risk Category | Risk Description | Probability | Impact | Mitigation Strategy | Owner |
|----|---|---|---|---|---|---|
| **T01** | **Technical** | **Coordinate System Mismatch**<br>TestFit usually works in local coordinates or Lat/Long. WHA uses UTM/Thai Grid. Export comes in "floating in space" or wrong scale. | High | Critical | **Coordinate Transformer Module**: Implement a dedicated step in `InputAdapter` that records the insertion point (0,0) of the WHA DWG and translates the TestFit output back to exactly that point. | Developer |
| **T02** | **Technical** | **Layer Name Drift**<br>TestFit changes their default layer names (e.g., update from v2.0 to v2.1 aliases `Roads` to `Streets`). | Medium | High | **Dynamic Mapping Config**: Do not hardcode layer names. Use a `layer_map.json` file that can be updated without touching code. | Developer |
| **O01** | **Operational** | **"The Black Box" Problem**<br>Planners reject the tool because they can't see *why* it placed a road there. | High | High | **Explainability via Validation**: The `ValidationReport.pdf` helps. It doesn't explain *why* the road is there, but proves *that* it works. Position strictly as "Drafting Assistant" not "Designer". | Project Lead |
| **O02** | **Operational** | **Learning Curve / UI Fatigue**<br>Planners refuse to use Command Line Interface (CLI). | Medium | Medium | **"Zero UI" File Watcher**: Planners don't type commands. They just save file to `Input` folder, magic happens, result appears in `Output`. | Developer |
| **B01** | **Business** | **Vendor Lock-in**<br>We build workflow around TestFit, they raise price 10x next year. | Low | High | **Modular Wrapper**: Ensure the `InputAdapter` and `OutputProcessor` are tool-agnostic. If we switch to Autodesk Forma later, we only swap the middle engine. The wrapper investment is safe. | CTO |

## 3. CONTINGENCY SCENARIOS (The "What Ifs")

### **Scenario A: TestFit Output is "Garbage" for complex polygons.**

* *Cause:* Complex polygon with acute angles confuses the packing algorithm.
* *Response:* Manual Subdivision.
* *Action:* Planner manually splits the large complex site into 2-3 simpler rectangular "zones" in CAD. Feed each zone to TestFit separately. Wrapper merges them back.

### **Scenario B: Python Dependency Hell on WHA Machines.**

* *Cause:* Corporate IT prevents installing Python/Pip or restricts libraries.
* *Response:* PyInstaller Executable.
* *Action:* Compile the Python scripts into a single standalone `.exe` file (`WHA_Generator.exe`) that requires no installation.

### **Scenario C: Demo Day "The Wi-Fi is Dead"**

* *Cause:* Connectivity failure prevents TestFit login.
* *Response:* License Caching & Offline Mode.
* *Action:* Ensure TestFit "Offline Mode" is active/verified 24h prior. Have `OutputProcessor` ready to run on pre-existing DXF files (Mock Demo Mode).

## 4. GO/NO-GO CRITERIA FOR PHASE 2 (PILOT)

We only proceed to Pilot if:

1. [ ] **Accuracy:** System creates closed, valid plot boundaries for >80% of generated plots.
2. [ ] **Speed:** Total cycle time (Input -> DWG) is < 10 minutes.
3. [ ] **Usability:** A planner can run the script with < 1 hour training.
4. [ ] **Value:** The result is editable (standard polylines), not block references or proxy objects.

## 5. SECURITY & DATA PRIVACY

* **Data Handling:** Site boundaries are uploaded to TestFit servers (US-based).
* **Mitigation:**
  * Strip all text/metadata from DWG before upload.
  * Only upload the boundary polygon. No client names, no title blocks.
  * *Note:* TestFit is SOC 2 compliant, but data stripping is best practice.
