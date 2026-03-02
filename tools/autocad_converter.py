"""
Utility script to convert DWG to DXF using installed AutoCAD/TrueView via COM.
Real Engineering Standard: Automate the tool you have.
"""
import sys
import os
from pathlib import Path
from loguru import logger

try:
    import win32com.client
except ImportError:
    logger.error("pypiwin32 not installed. Run 'pip install pypiwin32'")
    sys.exit(1)

def convert_dwg_to_dxf(dwg_path: str):
    dwg_file = Path(dwg_path).resolve()
    if not dwg_file.exists():
        logger.error(f"File not found: {dwg_file}")
        return

    dxf_file = dwg_file.with_suffix(".dxf")
    
    try:
        logger.info("Connecting to AutoCAD Application...")
        acad = win32com.client.Dispatch("AutoCAD.Application")
        acad.Visible = False # Run in background
        
        logger.info(f"Opening {dwg_file.name}...")
        doc = acad.Documents.Open(str(dwg_file))
        
        logger.info(f"Saving as {dxf_file.name}...")
        # ac2018_dxf = 64 (Enum value for DXF 2018)
        # ac2013_dxf = 60
        doc.SaveAs(str(dxf_file), 60) 
        
        doc.Close()
        logger.success("Conversion Complete.")
        
    except Exception as e:
        logger.critical(f"AutoCAD Automation Failed: {e}")
        logger.info("Ensure AutoCAD is installed and no dialogs are blocking.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python autocad_converter.py <file.dwg>")
        sys.exit(1)
    
    convert_dwg_to_dxf(sys.argv[1])
