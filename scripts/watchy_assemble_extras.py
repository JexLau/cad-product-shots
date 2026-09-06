"""Watchy demo extras for Rams remodel DoD: screen insert + pass-through strap.

Used by render_stills_pipeline.py after GLB/STL import. Geometry-first (not paint):
adds a recessed e-ink plane in the dial pocket and a soft flat strap along 12–6.
Tuned for SQFMI Yatari / Yatari2 (thickness on Y, face toward -Y) but falls back
to bbox heuristics for similar assemblies.
"""
from __future__ import annotations

import math
from collections import Counter

import bpy
from mathutils import Vector


HELPER_NAMES = (
    "WatchyScreenInsert",
    "WatchyStrap",
    "WatchyStrapNorth",
    "WatchyStrapSouth",
    "WatchyStrapKeeperA",
    "WatchyStrapKeeperB",
    "WatchyStrapBuckle",
)


def _mesh_bbox_world(objects=None):
    mins = Vector((1e9, 1e9, 1e9))
    maxs = Vector((-1e9, -1e9, -1e9))
    found = False
    for obj in objects or bpy.data.objects:
        if obj.type != "MESH" or obj.hide_render or obj.name == "CycloramaFloor":
            continue
        if obj.name in HELPER_NAMES:
            continue
        found = True
        for corner in obj.bound_box:
            w = obj.matrix_world @ Vector(corner)
            mins = Vector(tuple(min(mins[i], w[i]) for i in range(3)))
            maxs = Vector(tuple(max(maxs[i], w[i]) for i in range(3)))
    if not found:
        raise RuntimeError("watchy extras: no mesh objects")
    return mins, maxs


def detect_watchy_family() -> bool:
    names = []
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        names.append((o.name or "").lower())
        names.append((getattr(o.data, "name", "") or "").lower())
    blob = " ".join(names)
    keys = ("button", "pole02", "yatari", "armadillonium", "top", "bottom", "watchy")
    hit = sum(1 for k in keys if k in blob)
    has_btn = any("button" in n for n in names)
    return has_btn and hit >= 2


def _clear_helpers():
    for name in HELPER_NAMES:
        obj = bpy.data.objects.get(name)
        if obj:
            mesh = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if mesh and mesh.users == 0:
                bpy.data.meshes.remove(mesh)


def _find_dial_pocket():
    """Raycast from -Y (camera/face side for Yatari family) to find recess vs bezel."""
    mins, maxs = _mesh_bbox_world()
    size = maxs - mins
    # Prefer thin axis as face normal; Yatari/Armadillonium → Y.
    axes = [(0, size.x), (1, size.y), (2, size.z)]
    axes.sort(key=lambda t: t[1])
    thin = axes[0][0]
    # We hard-assume Yatari orientation (thin=Y, face=-Y) when Y is thinnest.
    if thin != 1:
        print(f"WATCHY_EXTRAS thin_axis={thin} (expected Y=1); using Y-face heuristic anyway", flush=True)

    scene = bpy.context.scene
    deps = bpy.context.evaluated_depsgraph_get()
    cx = 0.5 * (mins.x + maxs.x)
    cz = 0.5 * (mins.z + maxs.z)
    # Sample grid in XZ on face
    hits = []
    x0, x1 = mins.x + 0.05 * size.x, maxs.x - 0.05 * size.x
    z0, z1 = mins.z + 0.08 * size.z, maxs.z - 0.08 * size.z
    nx, nz = 36, 40
    origin_y = mins.y - max(2.0 * size.y, 0.02)
    for ix in range(nx):
        for iz in range(nz):
            x = x0 + (x1 - x0) * (ix + 0.5) / nx
            z = z0 + (z1 - z0) * (iz + 0.5) / nz
            ok, loc, _n, _i, obj, _m = scene.ray_cast(
                deps, Vector((x, origin_y, z)), Vector((0.0, 1.0, 0.0))
            )
            if ok and obj and obj.name != "CycloramaFloor":
                hits.append(loc)
    if len(hits) < 30:
        print(f"WATCHY_EXTRAS dial ray hits low ({len(hits)}); bbox fallback", flush=True)
        return _dial_fallback(mins, maxs)

    ys = sorted(h.y for h in hits)
    y_outer = ys[int(0.08 * len(ys))]
    # Recess = first hit deeper into +Y than outer bezel
    recess = [h for h in hits if h.y >= y_outer + 0.15 * size.y]
    if len(recess) < 12:
        recess = [h for h in hits if h.y >= y_outer + 0.08 * size.y]
    if len(recess) < 8:
        print("WATCHY_EXTRAS no clear recess; bbox fallback", flush=True)
        return _dial_fallback(mins, maxs)

    rx0 = min(h.x for h in recess)
    rx1 = max(h.x for h in recess)
    rz0 = min(h.z for h in recess)
    rz1 = max(h.z for h in recess)
    ry = sum(h.y for h in recess) / len(recess)
    # Shrink slightly so plane sits inside bezel frame
    pad_x = 0.06 * (rx1 - rx0)
    pad_z = 0.06 * (rz1 - rz0)
    # Float in pocket toward camera (-Y): ~35% from bezel toward recess floor
    y_screen = y_outer + 0.35 * (ry - y_outer)
    pocket = {
        "x0": rx0 + pad_x,
        "x1": rx1 - pad_x,
        "z0": rz0 + pad_z,
        "z1": rz1 - pad_z,
        "y": y_screen,
        "y_bezel": y_outer,
        "mins": mins,
        "maxs": maxs,
    }
    print(
        f"WATCHY_EXTRAS dial pocket x={pocket['x0']:.4f}:{pocket['x1']:.4f} "
        f"z={pocket['z0']:.4f}:{pocket['z1']:.4f} y={pocket['y']:.4f} bezel_y={y_outer:.4f}",
        flush=True,
    )
    return pocket


def _dial_fallback(mins, maxs):
    size = maxs - mins
    cx = 0.5 * (mins.x + maxs.x)
    cz = 0.5 * (mins.z + maxs.z)
    w = 0.62 * size.x
    h = 0.55 * size.z
    y = mins.y + 0.38 * size.y
    return {
        "x0": cx - 0.5 * w,
        "x1": cx + 0.5 * w,
        "z0": cz - 0.5 * h,
        "z1": cz + 0.5 * h,
        "y": y,
        "y_bezel": mins.y,
        "mins": mins,
        "maxs": maxs,
    }


def _front_case_object(mins, maxs):
    """Mesh whose face sits at the camera side (min Y for Yatari family)."""
    best = None
    best_y = 1e9
    for obj in bpy.data.objects:
        if obj.type != "MESH" or obj.hide_render or obj.name in HELPER_NAMES:
            continue
        if obj.name == "CycloramaFloor":
            continue
        nl = obj.name.lower()
        if "button" in nl:
            continue
        ys = [(obj.matrix_world @ Vector(c)).y for c in obj.bound_box]
        y_min = min(ys)
        # Prefer larger plates near the front
        area = obj.dimensions.x * obj.dimensions.z
        score = y_min - 0.0001 * area
        if score < best_y:
            best_y = score
            best = obj
    return best


def cut_watchy_dial_window(mins=None, maxs=None):
    """Boolean-cut a rectangular dial window into the front case (geometry, not paint)."""
    if mins is None or maxs is None:
        mins, maxs = _mesh_bbox_world()
    size = maxs - mins
    front = _front_case_object(mins, maxs)
    if front is None:
        print("WATCHY_EXTRAS no front case for boolean", flush=True)
        return None
    cx = 0.5 * (mins.x + maxs.x)
    cz = 0.5 * (mins.z + maxs.z)
    # Dial covers most of the face; leave a bezel frame (~12% margin).
    sx = 0.72 * size.x
    sz = 0.62 * size.z
    # Cutter thicker than case so boolean cleanly punches through the face shell.
    sy = max(size.y * 1.35, 0.008)
    y_face = mins.y
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    cutter = bpy.context.object
    cutter.name = "WatchyDialCutter"
    cutter.scale = (sx, sy, sz)
    cutter.location = (cx, y_face + 0.35 * size.y, cz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    mod = front.modifiers.new(name="WatchyDialWindow", type="BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    bpy.context.view_layer.objects.active = front
    front.select_set(True)
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
        print(f"WATCHY_EXTRAS boolean dial on {front.name} cut={sx:.4f}x{sz:.4f}", flush=True)
    except Exception as exc:
        print(f"WATCHY_EXTRAS boolean apply failed ({exc}); leaving modifier", flush=True)
    # Remove cutter from render
    cutter.hide_render = True
    cutter.hide_viewport = True
    bpy.data.objects.remove(cutter, do_unlink=True)

    pocket = {
        "x0": cx - 0.5 * sx * 0.96,
        "x1": cx + 0.5 * sx * 0.96,
        "z0": cz - 0.5 * sz * 0.96,
        "z1": cz + 0.5 * sz * 0.96,
        "y": y_face + 0.22 * size.y,
        "y_bezel": y_face,
        "mins": mins,
        "maxs": maxs,
        "front": front.name,
    }
    return pocket


def add_watchy_screen_insert(pocket=None):
    if pocket is None:
        mins, maxs = _mesh_bbox_world()
        pocket = cut_watchy_dial_window(mins, maxs) or _dial_fallback(mins, maxs)
    sx = max(1e-4, pocket["x1"] - pocket["x0"])
    sz = max(1e-4, pocket["z1"] - pocket["z0"])
    thickness = max(0.00035, 0.035 * (pocket["maxs"].y - pocket["mins"].y))
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = bpy.context.object
    obj.name = "WatchyScreenInsert"
    obj.scale = (sx, thickness, sz)
    obj.location = (
        0.5 * (pocket["x0"] + pocket["x1"]),
        pocket["y"],
        0.5 * (pocket["z0"] + pocket["z1"]),
    )
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    print(f"WATCHY_EXTRAS screen {obj.name} size=({sx:.4f},{thickness:.4f},{sz:.4f}) y={pocket['y']:.4f}", flush=True)
    return obj


def add_watchy_strap(pocket=None):
    """Two-ended demo strap through 12/6 lug slots (does not cross dial window)."""
    pocket = pocket or _find_dial_pocket()
    mins, maxs = pocket["mins"], pocket["maxs"]
    size = maxs - mins
    cx = 0.5 * (mins.x + maxs.x)
    strap_w = max(0.012, min(0.022, 0.52 * size.x))
    strap_t = max(0.0012, 0.10 * size.y)
    # Through front lug depth so 07/08 read strap entering the case.
    y_strap = mins.y + 0.30 * size.y
    overhang = max(0.024, 0.58 * size.z)
    # Leave the dial clear: only build outside the screen z-range (+ margin).
    dial_z0 = pocket["z0"] - 0.02 * size.z
    dial_z1 = pocket["z1"] + 0.02 * size.z

    def _band(name, z0, z1):
        length = max(1e-4, z1 - z0)
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        obj = bpy.context.object
        obj.name = name
        obj.scale = (strap_w, strap_t, length)
        obj.location = (cx, y_strap, 0.5 * (z0 + z1))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        return obj

    south = _band("WatchyStrapSouth", mins.z - overhang, dial_z0)
    north = _band("WatchyStrapNorth", dial_z1, maxs.z + overhang)
    # Quiet under-case bridge (back) so silhouette stays continuous.
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    bridge = bpy.context.object
    bridge.name = "WatchyStrap"
    bridge.scale = (strap_w * 0.92, strap_t * 0.85, (maxs.z - mins.z) * 0.92)
    bridge.location = (cx, maxs.y - 0.18 * size.y, 0.5 * (mins.z + maxs.z))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    keeper_z = maxs.z + 0.28 * overhang
    for i, name in enumerate(("WatchyStrapKeeperA", "WatchyStrapKeeperB")):
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        k = bpy.context.object
        k.name = name
        k.scale = (strap_w * 1.12, strap_t * 2.2, strap_t * 1.6)
        k.location = (cx, y_strap, keeper_z + i * strap_t * 3.2)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    bpy.ops.mesh.primitive_cube_add(size=1.0)
    buckle = bpy.context.object
    buckle.name = "WatchyStrapBuckle"
    buckle.scale = (strap_w * 0.95, strap_t * 1.6, strap_t * 3.8)
    buckle.location = (cx, y_strap, maxs.z + 0.55 * overhang)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    print(
        f"WATCHY_EXTRAS strap split N/S w={strap_w:.4f} t={strap_t:.4f} y={y_strap:.4f} overhang={overhang:.4f}",
        flush=True,
    )
    return north

def add_watchy_screen_and_strap(enabled=True):
    if not enabled:
        print("WATCHY_EXTRAS off", flush=True)
        return None
    if not detect_watchy_family():
        print("WATCHY_EXTRAS skip (not watchy-like)", flush=True)
        return None
    _clear_helpers()
    mins, maxs = _mesh_bbox_world()
    # Yatari2 STEP face is a solid plate — cut a real dial window, then seat e-ink insert.
    pocket = cut_watchy_dial_window(mins, maxs)
    if pocket is None:
        pocket = _find_dial_pocket()
    screen = add_watchy_screen_insert(pocket)
    strap = add_watchy_strap(pocket)
    return {"screen": screen, "strap": strap, "pocket": pocket}
