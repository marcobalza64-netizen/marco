#!/usr/bin/env python3
"""Wrapper retrocompatibile: usa stock_monitor (NVIDIA di default)."""

from stock_monitor import *  # noqa: F401,F403
from stock_monitor import main

if __name__ == "__main__":
    raise SystemExit(main())
