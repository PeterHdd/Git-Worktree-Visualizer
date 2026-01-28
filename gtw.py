#!/usr/bin/env python3
import os
import sys

LIBDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, LIBDIR)

from gtw.main import main


if __name__ == "__main__":
    raise SystemExit(main())
