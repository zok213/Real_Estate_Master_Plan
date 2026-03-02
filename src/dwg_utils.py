"""
dwg_utils.py — DWG / CAD file → PNG conversion using ConvertAPI cloud service.

Why ConvertAPI instead of local aspose-cad?
  • Accurate rendering of all DWG entities (hatches, colours, linetypes).
  • No local CAD engine needed — just an HTTP call.
  • Tested and confirmed working for WHA boundary / topo DWG files.
"""
import os
import tempfile

import convertapi
from config import CONVERTAPI_SECRET

# Configure once at import time.
convertapi.api_credentials = CONVERTAPI_SECRET


def convert_dwg_to_png(dwg_bytes: bytes) -> str | None:
    """
    Convert raw DWG bytes to a PNG file via ConvertAPI.

    Returns the absolute path of the output PNG, or None on failure.
    The caller is responsible for cleaning up the file when done.

    Args:
        dwg_bytes: Raw bytes of the .dwg file.

    Returns:
        Absolute path to the generated PNG, or None on error.
    """
    # Write DWG bytes to a temp file so ConvertAPI can read it.
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".dwg"
    ) as tmp:
        tmp.write(dwg_bytes)
        tmp_path = tmp.name

    out_dir = tempfile.mkdtemp()

    try:
        convertapi.convert(
            "png",
            {"File": tmp_path},
            from_format="dwg",
        ).save_files(out_dir)

        pngs = [
            f for f in os.listdir(out_dir)
            if f.lower().endswith(".png")
        ]
        if pngs:
            return os.path.join(out_dir, pngs[0])

        return None  # conversion produced no output

    except Exception:
        raise  # let the caller handle / display the error

    finally:
        # Clean up the temp DWG input; leave the PNG for the caller.
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
