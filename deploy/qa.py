#!/usr/bin/env python3
"""Deploy the reviewed QA infrastructure, service and browser application."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:]=[entry for entry in sys.path if Path(entry).resolve()!=ROOT/'deploy']
sys.path.insert(0,str(ROOT))
from deploy.orchestrate import entrypoint
if __name__=='__main__':raise SystemExit(entrypoint('qa'))
