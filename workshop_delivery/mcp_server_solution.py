"""Compatibility entry point. Reference: workshop/solutions/mcp_server_solution.py."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workshop.solutions.mcp_server_solution import *

if __name__ == "__main__":
    mcp.run()
