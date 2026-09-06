"""Watchy demo extras: e-ink insert (+ glass) + pass-through strap.

Primary: SQFMI Party (Case_Top/Bottom). Yatari2 fallback still supported.
Party face is flush through Top window — cut a shallow pocket into Bottom.
"""
from __future__ import annotations

import bpy
from mathutils import Vector

HELPER_NAMES = (
    "WatchyScreenInsert",
    "WatchyScreenGlass",
    "WatchyStrap",
    "WatchyStrapNorth",
    "WatchyStrapSouth",
    "WatchyStrapLugNorth",
    "WatchyStrapLugSouth",
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


def _name_blob():
    parts = []
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        parts.append((o.name or "").lower())
        parts.append((getattr(o.data, "name", "") or "").lower())
    return " ".join(parts)


def detect_watchy_family() -> bool:
    blob = _name_blob()
    keys = ("button", "pole02", "yatari", "armadillonium", "party", "case_top", "case_bottom", "watchy")
    hit = sum(1 for k in keys if k in blob)
    has_btn = "button" in blob
    return ("party" in blob or "case_top" in blob) or (has_btn and hit >= 2)


def is_party_assembly() -> bool:
    blob = _name_blob()
    if "party" in blob:
        return True
    return ("case_top" in blob and "case_bottom" in blob)


def _clear_helpers():
    for name in HELPER_NAMES:
        obj = bpy.data.objects.get(name)
        if not obj:
            continue
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh and mesh.users == 0:
            bpy.data.meshes.remove(mesh)


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
        area = obj.dimensions.x * obj.dimensions.z
        score = y_min - 0.0001 * area
        if score < best_y:
            best_y = score
            best = obj
    return best


def cut_watchy_dial_window(mins=None, maxs=None):
    if mins is None or maxs is None:
        mins, maxs = _mesh_bbox_world()
    size = maxs - mins
    front = _front_case_object(mins, maxs)
    if front is None:
        return None
    cx = 0.5 * (mins.x + maxs.x)
    cz = 0.5 * (mins.z + maxs.z)
    sx = 0.72 * size.x
    sz = 0.62 * size.z
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
        print(f"WATCHY_EXTRAS boolean apply failed ({exc})", flush=True)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return {
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


def _party_dial_from_window():
    """Party Top window is flush with Bottom — pocket Bottom, seat e-ink."""
    mins, maxs = _mesh_bbox_world()
    size = maxs - mins
    scene = bpy.context.scene
    deps = bpy.context.evaluated_depsgraph_get()
    bot_hits = []
    x0, x1 = mins.x + 0.04 * size.x, maxs.x - 0.04 * size.x
    z0, z1 = mins.z + 0.06 * size.z, maxs.z - 0.06 * size.z
    origin_y = mins.y - max(2.0 * size.y, 0.02)
    for ix in range(40):
        for iz in range(36):
            x = x0 + (x1 - x0) * (ix + 0.5) / 40
            z = z0 + (z1 - z0) * (iz + 0.5) / 36
            ok, loc, _n, _i, obj, _m = scene.ray_cast(
                deps, Vector((x, origin_y, z)), Vector((0.0, 1.0, 0.0))
            )
            if not ok or not obj:
                continue
            nl = (obj.name + " " + (getattr(obj.data, "name", "") or "")).lower()
            if "button" in nl or "top" in nl:
                continue
            if "bottom" in nl or "party" in nl:
                bot_hits.append(loc)
    if len(bot_hits) < 20:
        print(f"WATCHY_EXTRAS party window hits low bot={len(bot_hits)}", flush=True)
        return None
    rx0, rx1 = min(h.x for h in bot_hits), max(h.x for h in bot_hits)
    rz0, rz1 = min(h.z for h in bot_hits), max(h.z for h in bot_hits)
    pad_x = 0.05 * (rx1 - rx0)
    pad_z = 0.05 * (rz1 - rz0)
    cx = 0.5 * (rx0 + rx1)
    cz = 0.5 * (rz0 + rz1)
    sx = max(0.024, (rx1 - rx0) - 2 * pad_x)
    sz = max(0.020, (rz1 - rz0) - 2 * pad_z)
    bot = None
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        nl = (o.name + " " + (getattr(o.data, "name", "") or "")).lower()
        if "bottom" in nl:
            bot = o
            break
    if bot is None:
        bot = _front_case_object(mins, maxs)
    y_face = mins.y
    depth = max(0.0014, 0.50 * size.y)
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    cutter = bpy.context.object
    cutter.name = "WatchyDialCutter"
    cutter.scale = (sx, depth * 1.7, sz)
    cutter.location = (cx, y_face + 0.40 * depth, cz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = bot.modifiers.new(name="WatchyDialWindow", type="BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    bpy.context.view_layer.objects.active = bot
    bot.select_set(True)
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
        print(f"WATCHY_EXTRAS party boolean pocket on {bot.name} {sx:.4f}x{sz:.4f} d={depth:.4f}", flush=True)
    except Exception as exc:
        print(f"WATCHY_EXTRAS party boolean failed ({exc})", flush=True)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return {
        "x0": cx - 0.5 * sx * 0.95,
        "x1": cx + 0.5 * sx * 0.95,
        "z0": cz - 0.5 * sz * 0.95,
        "z1": cz + 0.5 * sz * 0.95,
        "y": y_face + 0.42 * depth,
        "y_bezel": y_face,
        "mins": mins,
        "maxs": maxs,
        "front": bot.name,
    }


def add_watchy_screen_insert(pocket):
    sx = max(1e-4, pocket["x1"] - pocket["x0"])
    sz = max(1e-4, pocket["z1"] - pocket["z0"])
    case_y = max(1e-4, pocket["maxs"].y - pocket["mins"].y)
    thickness = max(0.00028, 0.040 * case_y)
    # Knife-2: thinner cover glass so Fresnel reads as a sheet, not a slab.
    glass_t = max(0.00006, 0.007 * case_y)
    cx = 0.5 * (pocket["x0"] + pocket["x1"])
    cz = 0.5 * (pocket["z0"] + pocket["z1"])
    y_insert = pocket["y"]
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = bpy.context.object
    obj.name = "WatchyScreenInsert"
    obj.scale = (sx * 0.97, thickness, sz * 0.97)
    obj.location = (cx, y_insert, cz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # UV: project so Face.png covers the camera (-Y) face.
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.cube_project(cube_size=1.0, correct_aspect=True, scale_to_bounds=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    glass = bpy.context.object
    glass.name = "WatchyScreenGlass"
    glass.scale = (sx * 1.005, glass_t, sz * 1.005)
    glass.location = (cx, y_insert - 0.55 * thickness - 0.55 * glass_t, cz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    print(
        f"WATCHY_EXTRAS screen {obj.name} size=({sx:.4f},{thickness:.4f},{sz:.4f}) y={y_insert:.4f} + glass_t={glass_t:.5f}",
        flush=True,
    )
    return obj



def _bevel_light(obj, width=0.00018, segments=2):
    """Soft silicone edge — cubes alone read as fixture rails."""
    try:
        mod = obj.modifiers.new(name="StrapBevel", type="BEVEL")
        mod.width = float(width)
        mod.segments = int(segments)
        mod.limit_method = "ANGLE"
        mod.angle_limit = 0.5
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except Exception as exc:
        print(f"WATCHY_EXTRAS bevel skip {obj.name}: {exc}", flush=True)


def add_watchy_strap(pocket):
    """Consumer silicone strap — not an industrial rail / work-fixture band."""
    mins, maxs = pocket["mins"], pocket["maxs"]
    size = maxs - mins
    cx = 0.5 * (mins.x + maxs.x)
    # Knife-2: slightly wider + thinner = wrist strap, not fixture bar.
    strap_w = max(0.012, min(0.022, 0.52 * size.x))
    strap_t = max(0.00055, 0.095 * size.y)
    y_strap = mins.y + 0.38 * size.y
    overhang = max(0.026, 0.78 * size.z)
    dial_z0 = pocket["z0"] - 0.015 * size.z
    dial_z1 = pocket["z1"] + 0.015 * size.z

    def _band(name, z0, z1, y=None, w_scale=1.0, t_scale=1.0):
        length = max(1e-4, z1 - z0)
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        obj = bpy.context.object
        obj.name = name
        obj.scale = (strap_w * w_scale, strap_t * t_scale, length)
        obj.location = (cx, y if y is not None else y_strap, 0.5 * (z0 + z1))
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        return obj

    _band("WatchyStrapSouth", mins.z - overhang, dial_z0)
    north = _band("WatchyStrapNorth", dial_z1, maxs.z + overhang)
    # Quiet rear pass-through (hidden-ish under case) — keep thinner.
    _band(
        "WatchyStrap",
        mins.z + 0.04 * size.z,
        maxs.z - 0.04 * size.z,
        y=maxs.y - 0.22 * size.y,
        w_scale=0.82,
        t_scale=0.58,
    )
    # Local cold-metal lug accents (short, flush) — not long rails.
    _band(
        "WatchyStrapLugNorth",
        dial_z1 - 0.012 * size.z,
        dial_z1 + 0.018 * size.z,
        y=y_strap + 0.02 * size.y,
        w_scale=1.02,
        t_scale=1.05,
    )
    _band(
        "WatchyStrapLugSouth",
        dial_z0 - 0.018 * size.z,
        dial_z0 + 0.012 * size.z,
        y=y_strap + 0.02 * size.y,
        w_scale=1.02,
        t_scale=1.05,
    )
    # Single soft silicone keeper (drop second fixture ring).
    keeper_z = maxs.z + 0.22 * overhang
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    k = bpy.context.object
    k.name = "WatchyStrapKeeperA"
    k.scale = (strap_w * 1.04, strap_t * 1.35, strap_t * 0.95)
    k.location = (cx, y_strap, keeper_z)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Tip loop: same silicone family as strap (not a bright metal buckle plate).
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    buckle = bpy.context.object
    buckle.name = "WatchyStrapBuckle"
    buckle.scale = (strap_w * 0.78, strap_t * 0.95, strap_t * 2.2)
    buckle.location = (cx, y_strap, maxs.z + 0.48 * overhang)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for nm in (
        "WatchyStrapSouth",
        "WatchyStrapNorth",
        "WatchyStrapKeeperA",
        "WatchyStrapBuckle",
        "WatchyStrapLugNorth",
        "WatchyStrapLugSouth",
    ):
        o = bpy.data.objects.get(nm)
        if o:
            _bevel_light(o, width=max(0.00012, 0.22 * strap_t), segments=3)
    print(f"WATCHY_EXTRAS strap w={strap_w:.4f} t={strap_t:.4f} overhang={overhang:.4f} (silicone knife-2)", flush=True)
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
    if is_party_assembly():
        pocket = _party_dial_from_window()
        if pocket is None:
            pocket = cut_watchy_dial_window(mins, maxs) or _dial_fallback(mins, maxs)
        print("WATCHY_EXTRAS party path", flush=True)
    else:
        pocket = cut_watchy_dial_window(mins, maxs) or _dial_fallback(mins, maxs)
        print("WATCHY_EXTRAS yatari-like path", flush=True)
    screen = add_watchy_screen_insert(pocket)
    strap = add_watchy_strap(pocket)
    return {"screen": screen, "strap": strap, "pocket": pocket}
