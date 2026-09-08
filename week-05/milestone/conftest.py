"""Let the milestone tests import the milestone module by name."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
