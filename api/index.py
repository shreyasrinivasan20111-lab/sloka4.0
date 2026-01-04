import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from the root
sys.path.append(str(Path(__file__).parent.parent))

from main import app

# Vercel expects this to be the handler
def handler(request):
    return app
