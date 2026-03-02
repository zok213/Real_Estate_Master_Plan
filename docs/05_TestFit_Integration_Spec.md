# 05_TestFit_Integration_Spec.md

# TESTFIT INTEGRATION SPECIFICATION

## 1. INTEGRATION STRATEGY: THE "REALITY FIRST" APPROACH

**Engineering Note:** While a direct API is ideal, proprietary generative design tools often limit full API access to enterprise partners. For a 2-week POC, we must implement a **Dual-Path Strategy** to ensure success regardless of API availability.

### **Path A: Direct API (Preferred)**

- **Method:** HTTPS REST calls.
- **Pros:** Fast, headless (no UI needed), robust error handling.
- **Cons:** May require specific enterprise license or API key provisioning (risk).

### **Path B: Desktop Automation (Fallback / "The Hack")**

- **Method:** "File Watcher" + Desktop Macros.
- **Workflow:** Script generates input file -> User loads in TestFit -> User exports DXF -> Script detects new DXF -> Script processes it.
- **Pros:** 100% guaranteed to work with the desktop software. No API key needed.
- **Cons:** Slower, requires "human in the loop" or brittle UI automation (Selenium/PyAutoGUI).

**Decision for POC:** We will build the **File Watcher** architecture as the baseline because it is *guaranteed* to work. We will attempt API integration as an optimization.

---

## 2. DATA SCHEMA SPECIFICATION (JSON)

To ensure different parts of the system speak the same language, we define strict schemas.

### **2.1. Site Constraints Schema (`constraints.json`)**

This is the "Source of Truth" for the Wrapper.

```json
{
  "project_metadata": {
    "id": "PROJ-001",
    "name": "WHA RY36 Pilot",
    "unit_system": "metric"
  },
  "constraints": {
    "setbacks": {
      "front": 15.0,
      "side": 10.0,
      "rear": 10.0,
      "notes": "Standard WHA Industrial setback"
    },
    "plots": {
      "min_area_sqm": 5000,
      "max_area_sqm": 15000,
      "target_aspect_ratio_min": 0.5,
      "target_aspect_ratio_max": 2.0
    },
    "roads": {
      "primary_width": 24.0,
      "secondary_width": 16.0,
      "turn_radius": 12.0
    }
  },
  "optimization_goals": {
    "target_saleable_area_percent": 65.0,
    "max_retention_pond_percent": 5.0
  }
}
```

---

## 3. PATH A: API SPECIFICATION (Hypothetical)

**Base URL:** `https://api.testfit.io/v1` (To be verified)
**Auth:** Header `Authorization: Bearer <API_KEY>`

### **3.1 Endpoints**

| Method | Endpoint | Description | Payload | Response |
|--------|----------|-------------|---------|----------|
| `POST` | `/geometry/site` | Upload site boundary | GeoJSON | `site_id` |
| `POST` | `/solve/industrial` | Trigger generation | `site_id`, `constraints` | `solution_id` |
| `GET` | `/solution/{id}/export` | Get DXF result | `format=dxf` | Binary Stream |

---

## 4. PATH B: FILE-WATCHER ARCHITECTURE (The "Must Work" Plan)

If API is unavailable, we use the file system as the API.

### **4.1 Workflow**

1. **Input:** Python script converts `WHA_Input.dwg` -> `TestFit_Input.dxf` (Clean polygon).
2. **Action:** User opens TestFit Desktop -> Drag & Drop `TestFit_Input.dxf`.
3. **Action:** User applies preset "WHA Industrial" schematic.
4. **Action:** User clicks "Export DXF" -> Saves to `C:\WHA_POC\input_buffer\`.
5. **Trigger:** Python `Watchdog` script detects new file in `input_buffer`.
6. **Process:** Script immediately grabs file, locks it, runs `OutputProcessor`, and saves `WHA_Final_Draft.dwg` to `output/`.

### **4.2 Directory Structure for File Watcher**

```
C:\WHA_POC\
├── input_buffer\    <-- Monitoring this folder for TestFit exports
├── processed\       <-- Raw files moved here after processing
└── output\          <-- Final WHA-compliant DWG
```

---

## 5. ERROR HANDLING PROTOCOLS

| Scenario | System Reaction | User Alert |
|----------|-----------------|------------|
| **Bad Geometry** | Input Adapter validates geometry closure before generation. | "Error: Site boundary is not a closed loop. Check CAD." |
| **API Timeout** | Retry 3x, then failover to manual mode instructions. | "API unavailable. Switching to Manual Mode." |
| **Parsing Failure** | Catch `DXFStructureError`. Log offending entity. | "Cannot read TestFit export. Ensure Version R2013 DXF." |
