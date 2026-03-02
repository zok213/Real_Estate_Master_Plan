# 06_Custom_Wrapper_Code_Structure.md

# CUSTOM WRAPPER CODE STRUCTURE & ARCHITECTURE

## 1. ARCHITECTURAL PATTERN

We will use a **Modular Pipeline Architecture**.
Data flows sequentially: `Input` -> `Adapter` -> `Processor` -> `Validator` -> `Output`.
State is managed via **Pydantic Models** to enforce data integrity (Type Safety).

## 2. TECHNOLOGY STACK (FROZEN)

* **Language:** Python 3.10+
* **CAD I/O:** `ezdxf` (Best for DXF manipulation)
* **Geometry Engine:** `shapely` (Robust geometric operations)
* **Data Validation:** `pydantic` (Strict schema enforcement)
* **File Monitoring:** `watchdog` (For "File Watcher" workflow)
* **Testing:** `pytest`

---

## 3. CORE CLASS DIAGRAM (Python definitions)

### **3.1. Data Models (`models.py`)**

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Tuple

class SiteConstraint(BaseModel):
    min_plot_size: float = Field(..., gt=0, description="Min area in sqm")
    road_width_primary: float = 24.0
    setback_dist: float = 15.0

class PlotEntity(BaseModel):
    id: str
    geometry: object # Shapely Polygon
    area_sqm: float
    layer: str

    @field_validator('area_sqm')
    def check_area(cls, v):
        if v < 0: raise ValueError("Area cannot be negative")
        return v
```

### **3.2. Input Adapter (`adapters/input_adapter.py`)**

```python
import ezdxf
from shapely.geometry import Polygon

class InputAdapter:
    def __init__(self, filepath: str):
        self.doc = ezdxf.readfile(filepath)
    
    def extract_boundary(self, layer_name: str) -> Polygon:
        """
        Scans specific layer for closed polylines.
        Returns Shapely Polygon for the site.
        Raises: ValueError if boundary is open or self-intersecting.
        """
        msp = self.doc.modelspace()
        # ... logic to find polyline -> convert to generic points ...
        return polygon
```

### **3.3. Output Processor (`processors/dxf_processor.py`)**

```python
class OutputProcessor:
    def __init__(self, template_path: str):
        self.template = ezdxf.readfile(template_path)
    
    def remap_layers(self, source_doc, mapping_rules: dict):
        """
        Reads entities from TestFit source_doc.
        Clones them into self.template.
        Changes properties (Layer, Color, Linetype) based on WHA standards.
        """
        pass
        
    def add_labels(self, plots: List[PlotEntity]):
        """
        Calculates centroid of each plot.
        Adds MTEXT entity with Area ID and SQM.
        """
        pass
```

### **3.4. Validator Engine (`logic/validator.py`)**

```python
class ValidationResult:
    status: bool
    issues: List[str]

class DesignValidator:
    def __init__(self, constraints: SiteConstraint):
        self.rules = constraints
        
    def validate_plot_sizes(self, plots: List[PlotEntity]) -> ValidationResult:
        issues = []
        for p in plots:
             if p.area_sqm < self.rules.min_plot_size:
                 issues.append(f"Plot {p.id} too small: {p.area_sqm}")
        return ValidationResult(status=(len(issues)==0), issues=issues)
```

---

## 4. ENTRY POINT: `main.py`

```python
import sys
from loguru import logger

def main(input_dwg, constraint_json):
    logger.info("Starting WHA Master Plan Wrapper...")
    
    # 1. Parse Constraints
    config = load_config(constraint_json)
    
    # 2. Load CAD
    try:
        adapter = InputAdapter(input_dwg)
        site_poly = adapter.extract_boundary("BOUNDARY-SITE")
    except Exception as e:
        logger.critical(f"Failed to read site boundary: {e}")
        sys.exit(1)

    # 3. [Manual Step or API Call to TestFit here]
    # For POC, we assume we pick up the 'testfit_export.dxf'
    
    # 4. Process Output
    processor = OutputProcessor(template="wha_standard_template.dxf")
    processor.process("testfit_export.dxf")
    
    # 5. Validate
    validator = DesignValidator(config)
    report = validator.run_all_checks()
    
    if report.has_critical_errors:
        logger.warning(f"Design invalid: {report.summary}")
    else:
        logger.success("Design verified automatically.")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
```

## 5. DEVELOPMENT ENVIRONMENT

- **Virtual Env:** `python -m venv venv`
* **Dependencies:** `requirements.txt`
  * `ezdxf==1.1.0`
  * `shapely==2.0.1`
  * `pydantic==2.5.0`
  * `loguru==0.7.2`
  * `watchdog==3.0.0`
