import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
src_path = root_dir / "src"
sys.path.append(str(root_dir))
sys.path.append(str(src_path))
