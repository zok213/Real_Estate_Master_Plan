# WHA AI Master Plan POC (Implementation)

This repository contains the **production-ready source code** for the WHA AI Master Plan Proof of Concept. The system uses a **Custom Python Wrapper** to orchestrate data flow between WHA's AutoCAD files and the **TestFit** AI engine.

## 📂 Project Structure

```
d:\newrealestate\WHA_AI_MasterPlan_POC\
├── docs/                # Project Documentation (The 10-Document Package)
├── src/                 # Source Code
│   ├── adapters/        # Input/Output Handlers (DWG <-> TestFit)
│   ├── logic/           # Core Logic & Validators
│   ├── models.py        # Pydantic Data Models (Type Safety)
│   ├── main.py          # CLI Entry Point
│   ├── testfit_client.py# File Watcher Integration
│   ├── output_processor.py # Layer Remapping
│   └── inspect_layers.py # Helper Tool
├── input/               # Drop your input .dwg files here
├── output/              # Generated results appear here
└── requirements.txt     # Python Dependencies
```

## 📂 Client Data References

The project validates against real client data located in `d:\newrealestate\client doument`.

- **Primary Input:** `WHA RY36_Master Plan_Original (1).dwg`

## 🚀 How to Run

### 1. Setup

```bash
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
```

## 🚀 User Guide (Verified Workflow)

**Prerequisite:** Convert your `.dwg` input to `.dxf` (AutoCAD 2018 format) to ensure maximum compatibility without external binary dependencies.

### 1. Run the Pipeline (Production Mode)

```bash
# Process a real site using the OR-Tools engine
python -m src.main "path/to/your_site.dxf" ortools
```

### 2. Output

* **Design:** `output/ry36_v2_result.dxf` (Open in AutoCAD)
- **Report:** `output/ry36_v2_result.json` (Metrics & Compliance)

### 3. Troubleshooting

If you see `ODA File Converter not found`:

1. **Option A:** Install [ODA File Converter](https://www.opendesign.com/guestfiles/oda_file_converter).
2. **Option B (Recommended):** Manually save your DWG as DXF before running.

### 4. Run TestFit Watcher (Real Integration)

Starts the background service that listens for TestFit exports.

```bash
python src/testfit_client.py
```

## 📜 Documentation Index

- [Executive Summary](docs/01_Executive_Summary.md)
- [Technical Architecture](docs/02_Technical_Architecture.md)
- [Implementation Guide](docs/03_Implementation_Guide_2Weeks.md)
- [Demo Script](docs/08_Demo_Script.md)
