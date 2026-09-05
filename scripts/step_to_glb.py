#!/usr/bin/env python3
"""Convert STEP → GLB via cascadio (OpenCASCADE) for Blender import.

Stock Blender 5.2 has no STEP importer. Tessellate CAD to GLB for --glb.
Requires: pip install cascadio
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
try:
    import cascadio
except ImportError as exc:
    raise SystemExit(f"cascadio not installed. pip install cascadio\n{exc}") from exc

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("step", type=Path)
    p.add_argument("glb", type=Path)
    p.add_argument("--tol-linear", type=float, default=0.1)
    p.add_argument("--tol-angular", type=float, default=0.5)
    args = p.parse_args()
    if not args.step.exists():
        raise SystemExit(f"missing STEP: {args.step}")
    args.glb.parent.mkdir(parents=True, exist_ok=True)
    print(f"CONVERT {args.step} -> {args.glb}", flush=True)
    n = cascadio.step_to_glb(
        str(args.step), str(args.glb),
        tol_linear=args.tol_linear, tol_angular=args.tol_angular,
        merge_primitives=True, use_parallel=True,
    )
    print(f"OK faces~={n} -> {args.glb} ({args.glb.stat().st_size} bytes)", flush=True)

if __name__ == "__main__":
    main()
