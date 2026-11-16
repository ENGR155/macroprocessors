"""Run the independent exported-file audit inside Autodesk Fusion."""
from pathlib import Path
import sys,importlib
def run(context):
    folder=str(Path(__file__).resolve().parent)
    if folder not in sys.path:sys.path.insert(0,folder)
    import native_audit
    importlib.reload(native_audit)
    native_audit.run()
