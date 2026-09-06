#!/usr/bin/env python3
"""Bake Demo · open CAD viewer GLBs from the stills pipeline (dark-premium mats).

Reuses hide-supports + headband join + Watchy knife-3 extras + product-mats,
then writes a Pages-friendly GLB (hidden CAD/jig meshes stripped). Mix-shader
earcups are flattened to vertex colors so glTF / <model-viewer> can show them.
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import bpy

_SCRIPTS_DIR = Path(__file__).resolve().parent if "__file__" in dir() else Path("/workspace/scripts")
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from render_stills_pipeline import (  # noqa: E402
    add_ploopy_headband_proxy,
    assign_product_materials,
    hide_print_supports,
    import_model,
    _mesh_key,
)

try:
    from watchy_assemble_extras import add_watchy_screen_and_strap
except Exception as exc:  # pragma: no cover
    add_watchy_screen_and_strap = None
    print(f"WATCHY_EXTRAS_IMPORT_FAIL {exc}", flush=True)

REPO = _SCRIPTS_DIR.parent
TARGETS = {
    "ploopy": {
        "glb": REPO / "media/demo-ploopy/source/PloopyHeadphones-RevA.glb",
        "out": REPO / "media/demo-ploopy/source/Ploopy_Viewer.glb",
        "extras": False,
        "headband": True,
        "supports": True,
    },
    "watchy": {
        "glb": REPO / "media/demo-watchy/source/Party_Model.glb",
        "out": REPO / "media/demo-watchy/source/Party_Viewer.glb",
        "extras": True,
        "headband": False,
        "supports": True,
    },
}


def parse_targets() -> list[str]:
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    wanted = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--target" and i + 1 < len(args):
            i += 1
            wanted.extend(x.strip() for x in args[i].split(",") if x.strip())
        elif a in TARGETS or a == "all":
            wanted.append(a)
        i += 1
    if not wanted or "all" in wanted:
        return ["ploopy", "watchy"]
    unknown = [t for t in wanted if t not in TARGETS]
    if unknown:
        raise SystemExit(f"unknown target(s): {unknown}")
    return wanted


def flatten_earcup_mix_to_vertex_color():
    """glTF cannot keep the Mix-shader pad/shell graph — bake the same falloff to COLOR_0."""
    shell = (0.048, 0.050, 0.056)
    pad = (0.032, 0.022, 0.016)
    converted = 0
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        if _mesh_key(obj) not in ("HPH-013", "HPH-018"):
            continue
        mesh = obj.data
        if "Col" in mesh.color_attributes:
            attr = mesh.color_attributes["Col"]
        else:
            attr = mesh.color_attributes.new(name="Col", type="FLOAT_COLOR", domain="POINT")
        for i, v in enumerate(mesh.vertices):
            x, y, z = v.co.x, v.co.y, v.co.z
            if x <= -0.018:
                med = 1.0
            elif x >= 0.014:
                med = 0.0
            else:
                med = 1.0 - (x + 0.018) / 0.032
            r = math.sqrt(y * y + z * z)
            rin = 0.0 if r <= 0.020 else (1.0 if r >= 0.028 else (r - 0.020) / 0.008)
            rout = 1.0 if r <= 0.052 else (0.0 if r >= 0.066 else 1.0 - (r - 0.052) / 0.014)
            if r <= 0.018:
                r_gate = 0.0
            elif r >= 0.026:
                r_gate = 0.75
            else:
                r_gate = 0.75 * (r - 0.018) / 0.008
            fac = max(0.0, min(1.0, max(med * rin * rout, med * r_gate)))
            attr.data[i].color = (
                shell[0] * (1.0 - fac) + pad[0] * fac,
                shell[1] * (1.0 - fac) + pad[1] * fac,
                shell[2] * (1.0 - fac) + pad[2] * fac,
                1.0,
            )
        mat = bpy.data.materials.new(f"Prod_EarcupViewer_{obj.name}")
        mat.use_nodes = True
        nt = mat.node_tree
        bsdf = nt.nodes.get("Principled BSDF")
        attr_n = nt.nodes.new("ShaderNodeVertexColor")
        if "layer_name" in attr_n.inputs:
            pass
        try:
            attr_n.layer_name = "Col"
        except Exception:
            try:
                attr_n.inputs["Layer"].default_value = "Col"
            except Exception:
                pass
        if bsdf:
            nt.links.new(attr_n.outputs["Color"], bsdf.inputs["Base Color"])
            bsdf.inputs["Roughness"].default_value = 0.42
            if "Metallic" in bsdf.inputs:
                bsdf.inputs["Metallic"].default_value = 0.0
            if "Specular IOR Level" in bsdf.inputs:
                bsdf.inputs["Specular IOR Level"].default_value = 0.48
            if "Coat Weight" in bsdf.inputs:
                bsdf.inputs["Coat Weight"].default_value = 0.18
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = 0.0
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        converted += 1
    print(f"VIEWER_FLATTEN earcups={converted}", flush=True)


def strip_non_product():
    """Drop hidden supports / clip plates, plus cameras / lights / empties."""
    removed = []
    for obj in list(bpy.data.objects):
        drop = False
        if obj.type in {"CAMERA", "LIGHT", "EMPTY"}:
            drop = True
        elif obj.name == "CycloramaFloor":
            drop = True
        elif getattr(obj, "hide_render", False) or getattr(obj, "hide_viewport", False):
            drop = True
        if drop:
            removed.append(f"{obj.name}/{obj.type}")
            mesh = obj.data if obj.type == "MESH" else None
            bpy.data.objects.remove(obj, do_unlink=True)
            if mesh and getattr(mesh, "users", 1) == 0:
                bpy.data.meshes.remove(mesh)
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    print(f"VIEWER_STRIP {len(removed)}: {removed}", flush=True)


def _export_glb(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    kwargs = dict(
        filepath=str(path),
        export_format="GLB",
        use_selection=False,
        export_cameras=False,
        export_extras=False,
        export_apply=True,
    )
    # Blender 4/5 flag names drift; try the richer set, then fall back.
    optional = {
        "export_yup": True,
        "export_lights": False,
        "export_materials": "EXPORT",
        "export_image_format": "AUTO",
        "export_vertex_color": "MATERIAL",
        "export_attributes": True,
        "export_texcoords": True,
        "export_normals": True,
        "export_animations": False,
    }
    try:
        bpy.ops.export_scene.gltf(**kwargs, **optional)
    except TypeError:
        bpy.ops.export_scene.gltf(**kwargs)
    print(f"VIEWER_WROTE {path} ({path.stat().st_size} bytes)", flush=True)


def bake_one(name: str):
    spec = TARGETS[name]
    src = spec["glb"]
    if not src.is_file():
        raise FileNotFoundError(src)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import_model({"glb": src, "obj": None, "stl": None, "step": None})
    print(f"VIEWER_IMPORT {name} {src}", flush=True)
    hide_print_supports(enabled=bool(spec["supports"]))
    if spec["headband"]:
        add_ploopy_headband_proxy(enabled=True)
    if spec["extras"]:
        if add_watchy_screen_and_strap is None:
            raise RuntimeError("watchy extras unavailable")
        add_watchy_screen_and_strap(enabled=True)
    kind = assign_product_materials(kind="auto", dark_premium=True)
    print(f"VIEWER_MATS {name} kind={kind}", flush=True)
    flatten_earcup_mix_to_vertex_color()
    strip_non_product()
    meshes = [o.name for o in bpy.data.objects if o.type == "MESH"]
    print(f"VIEWER_MESHES {name} {meshes}", flush=True)
    if not meshes:
        raise RuntimeError(f"{name}: no meshes left to export")
    _export_glb(spec["out"])


def main():
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    try:
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except Exception:
        pass
    for name in parse_targets():
        bake_one(name)
    print("VIEWER_DONE", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", flush=True)
        raise
