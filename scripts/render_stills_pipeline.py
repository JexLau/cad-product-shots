#!/usr/bin/env python3
"""Multi-input CAD -> marketing stills (Blender headless).

Accepts --glb / --obj / --stl / --step. STEP requires a Blender CAD importer
addon; otherwise exits with a clear error. Writes >=6 stills as 07+ names and
never overwrites protected 01-06.

Default engine: Cycles CPU (reliable headless). Optional --engine EEVEE.
"""

from __future__ import annotations

import math
import os
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Vector

os.environ.setdefault("PYTHONUNBUFFERED", "1")
try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except Exception:
    pass

DEFAULT_GLBS = (
    Path("/workspace/previews/generated-story/catellect-product-story-v2-uncompressed.glb"),
    Path("/workspace/soulgard-web/public/preorder/product-demo/model/catellect-product-story.glb"),
    Path("/workspace/soulgard-web/public/preorder/product-demo/model/catellect-product-story-v2.glb"),
)
DEFAULT_OUT = Path("/workspace/catellect-ops/media/case-01/stills")
REPO_STILLS = Path("/workspace/cad-product-shots/media/case-01/stills")
PROTECTED_PREFIXES = ("01-", "02-", "03-", "04-", "05-", "06-")
CLOSED_LID_NAMES = ("_X2_593476D69AA8_X0_",)
FRAME_CLOSED = 10
FRAME_OPEN = 28


def argv_after_sep() -> list[str]:
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1 :]
    return []


def parse_args():
    args = argv_after_sep()
    out = {
        "out": DEFAULT_OUT,
        "res": 1080,
        "force": False,
        "copy_repo": True,
        "glb": None,
        "obj": None,
        "stl": None,
        "step": None,
        "engine": "CYCLES",
        "samples": 32,
        "shots": "case01",
        "repo_stills": None,
        "only": None,
    }
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--out" and i + 1 < len(args):
            i += 1
            out["out"] = Path(args[i])
        elif a == "--res" and i + 1 < len(args):
            i += 1
            out["res"] = int(args[i])
        elif a == "--glb" and i + 1 < len(args):
            i += 1
            out["glb"] = Path(args[i])
        elif a == "--obj" and i + 1 < len(args):
            i += 1
            out["obj"] = Path(args[i])
        elif a == "--stl" and i + 1 < len(args):
            i += 1
            out["stl"] = Path(args[i])
        elif a == "--step" and i + 1 < len(args):
            i += 1
            out["step"] = Path(args[i])
        elif a == "--engine" and i + 1 < len(args):
            i += 1
            out["engine"] = args[i].upper()
        elif a == "--samples" and i + 1 < len(args):
            i += 1
            out["samples"] = int(args[i])
        elif a == "--shots" and i + 1 < len(args):
            i += 1
            out["shots"] = args[i]
        elif a == "--repo-stills" and i + 1 < len(args):
            i += 1
            out["repo_stills"] = Path(args[i])
        elif a == "--only" and i + 1 < len(args):
            i += 1
            out["only"] = {x.strip() for x in args[i].split(",") if x.strip()}
        elif a == "--force":
            out["force"] = True
        elif a == "--no-copy-repo":
            out["copy_repo"] = False
        i += 1
    return out


def look_at(obj, target):
    direction = target - obj.location
    if direction.length < 1e-9:
        return
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def mesh_bbox():
    mins = Vector((1e9, 1e9, 1e9))
    maxs = Vector((-1e9, -1e9, -1e9))
    found = False
    for obj in bpy.data.objects:
        if obj.type != "MESH" or obj.hide_render:
            continue
        found = True
        for corner in obj.bound_box:
            w = obj.matrix_world @ Vector(corner)
            mins = Vector(tuple(min(mins[i], w[i]) for i in range(3)))
            maxs = Vector(tuple(max(maxs[i], w[i]) for i in range(3)))
    if not found:
        raise RuntimeError("No mesh objects after import")
    return mins, maxs


def hide_prefix(prefixes, hide):
    for obj in bpy.data.objects:
        if any(obj.name == p or obj.name.startswith(p + ".") for p in prefixes):
            obj.hide_render = hide
            obj.hide_viewport = hide


def set_frame(frame):
    scene = bpy.context.scene
    scene.frame_set(frame)
    bpy.context.view_layer.update()


def setup_world_white(scene):
    world = bpy.data.worlds.new("Case01White")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.96, 0.96, 0.96, 1.0)
    bg.inputs["Strength"].default_value = 1.0
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])


def add_area(name, location, target, energy, size, color):
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.shape = "DISK"
    light.data.size = size
    light.data.color = color
    look_at(light, target)


def setup_studio(target, scale):
    # Scale area-light power ~ distance^2 so tiny CAD (watch cases) is not blown out.
    s = max(scale, 0.05)
    e = (s / 0.25) ** 2
    add_area("Key", target + Vector((-0.55 * s, -0.75 * s, 0.95 * s)), target, 120.0 * e, 0.7 * s, (1.0, 0.97, 0.93))
    add_area("Fill", target + Vector((0.85 * s, -0.35 * s, 0.55 * s)), target, 55.0 * e, 0.9 * s, (0.85, 0.90, 1.0))
    add_area("Rim", target + Vector((0.15 * s, 0.95 * s, 0.75 * s)), target, 80.0 * e, 0.55 * s, (1.0, 0.92, 0.85))
    add_area("Top", target + Vector((0.0, -0.1 * s, 1.4 * s)), target, 40.0 * e, 1.1 * s, (1.0, 1.0, 1.0))


def setup_floor(z, size):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0.0, 0.0, z - 0.001))
    floor = bpy.context.object
    floor.name = "CycloramaFloor"
    mat = bpy.data.materials.new("PaperWhite")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.95, 0.95, 0.95, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.55
    floor.data.materials.append(mat)


def setup_camera(scene, res, engine, samples):
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.name = "Case01Cam"
    cam.data.lens = 70
    cam.data.clip_start = 0.01
    cam.data.clip_end = 1000.0
    scene.camera = cam
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.quality = 92
    scene.render.film_transparent = False

    eng = engine.upper()
    if eng in ("EEVEE", "BLENDER_EEVEE"):
        scene.render.engine = "BLENDER_EEVEE"
        eevee = getattr(scene, "eevee", None)
        if eevee is not None:
            for attr, val in (
                ("taa_render_samples", max(16, min(samples, 64))),
                ("use_raytracing", False),
                ("use_shadows", True),
            ):
                if hasattr(eevee, attr):
                    setattr(eevee, attr, val)
    else:
        scene.render.engine = "CYCLES"
        scene.cycles.device = "CPU"
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
        try:
            scene.cycles.denoiser = "OPENIMAGEDENOISE"
        except Exception:
            pass

    if hasattr(scene, "view_settings"):
        try:
            scene.view_settings.view_transform = "AgX"
            scene.view_settings.look = "AgX - Medium High Contrast"
        except Exception:
            pass
    return cam


def place_camera(cam, center, radius, az_deg, el_deg, lens=70.0):
    az = math.radians(az_deg)
    el = math.radians(el_deg)
    x = center.x + radius * math.cos(el) * math.sin(az)
    y = center.y - radius * math.cos(el) * math.cos(az)
    z = center.z + radius * math.sin(el)
    cam.location = Vector((x, y, z))
    cam.data.lens = lens
    look_at(cam, center)


def safe_write_path(out_dir, name, force):
    path = out_dir / name
    if path.exists() and not force and name.startswith(PROTECTED_PREFIXES):
        raise RuntimeError(f"Refusing to overwrite protected still {path}")
    return path


def render_still(scene, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(path)
    print(f"RENDER {path.name}...", flush=True)
    bpy.ops.render.render(write_still=True)
    print(f"WROTE {path}", flush=True)


def _has_step_operator():
    for group_name in ("import_scene", "import_mesh", "wm", "bim"):
        group = getattr(bpy.ops, group_name, None)
        if group is None:
            continue
        for attr in dir(group):
            al = attr.lower()
            if "step" in al or al in ("iges", "import_product"):
                return True
    return False


def try_enable_cad_importer():
    import addon_utils

    candidates = ("io_scene_cad", "io_import_cad", "blenderbim", "ifcopenshell", "import_step")
    for mod in addon_utils.modules():
        name = getattr(mod, "__name__", "") or ""
        lname = name.lower()
        if any(c.lower() in lname for c in candidates) or ("step" in lname and "smooth" not in lname):
            try:
                addon_utils.enable(name, default_set=True)
                print(f"ENABLED_ADDON {name}", flush=True)
            except Exception as exc:
                print(f"ADDON_ENABLE_FAIL {name}: {exc}", flush=True)
    return _has_step_operator()


def import_step(path):
    if not path.exists():
        raise FileNotFoundError(path)
    has_importer = try_enable_cad_importer()
    attempts = []
    for call in (
        lambda: bpy.ops.import_scene.step(filepath=str(path)),
        lambda: bpy.ops.wm.step_import(filepath=str(path)),
        lambda: bpy.ops.import_mesh.step(filepath=str(path)),
        lambda: bpy.ops.import_scene.iges(filepath=str(path)),
    ):
        try:
            call()
            print(f"IMPORT_STEP_OK {path}", flush=True)
            return
        except Exception as exc:
            attempts.append(str(exc))
    raise RuntimeError(
        "STEP import failed: no usable Blender CAD/STEP importer is available "
        f"in this build (tried built-in + common addons). File: {path}\n"
        "Install a STEP CAD importer addon, or export the assembly to GLB/OBJ/STL "
        "and pass --glb / --obj / --stl instead.\n"
        f"has_step_operator={has_importer}; errors={attempts[:3]}"
    )


def import_model(opts):
    explicit = [("step", opts["step"]), ("glb", opts["glb"]), ("obj", opts["obj"]), ("stl", opts["stl"])]
    chosen = [(k, p) for k, p in explicit if p is not None]
    if len(chosen) > 1:
        raise RuntimeError(f"Pass only one of --glb/--obj/--stl/--step; got {[k for k, _ in chosen]}")
    if len(chosen) == 1:
        kind, path = chosen[0]
        if not path.exists():
            raise FileNotFoundError(path)
        if kind == "glb":
            bpy.ops.import_scene.gltf(filepath=str(path))
        elif kind == "obj":
            if hasattr(bpy.ops.wm, "obj_import"):
                bpy.ops.wm.obj_import(filepath=str(path))
            else:
                bpy.ops.import_scene.obj(filepath=str(path))
        elif kind == "stl":
            bpy.ops.wm.stl_import(filepath=str(path))
        elif kind == "step":
            import_step(path)
        return kind, path
    for p in DEFAULT_GLBS:
        if p.exists():
            bpy.ops.import_scene.gltf(filepath=str(p))
            return "glb", p
    raise FileNotFoundError("No model input. Pass --glb / --obj / --stl / --step, or place a default GLB.")


def apply_simple_material_if_needed():
    mat = bpy.data.materials.new("NeutralPlastic")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.82, 0.84, 0.86, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.35
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.05
    for obj in bpy.data.objects:
        if obj.type != "MESH" or obj.name == "CycloramaFloor":
            continue
        if obj.data.materials:
            continue
        obj.data.materials.append(mat)


def shot_list(mode):
    if mode == "simple":
        return [
            ("07-front.jpg", 1, 0, 12, 70, 0.0, 1.0),
            ("08-three-quarter.jpg", 1, 38, 16, 70, 0.0, 1.0),
            ("09-top.jpg", 1, 15, 72, 55, 0.0, 1.15),
            ("10-orbit-a.jpg", 1, 90, 14, 70, 0.0, 1.0),
            ("11-orbit-b.jpg", 1, 155, 18, 70, 0.0, 1.0),
            ("12-detail.jpg", 1, 25, 8, 95, -0.02, 0.62),
            ("13-rear-three-quarter.jpg", 1, 210, 16, 70, 0.0, 1.05),
            ("14-low-angle.jpg", 1, 45, 6, 70, 0.0, 1.1),
        ]
    return [
        ("07-front.jpg", FRAME_CLOSED, 0, 12, 70, 0.0, 1.0),
        ("08-three-quarter.jpg", FRAME_CLOSED, 38, 16, 70, 0.0, 1.0),
        ("09-top.jpg", FRAME_CLOSED, 15, 72, 55, 0.0, 1.15),
        ("10-orbit-a.jpg", FRAME_CLOSED, 90, 14, 70, 0.0, 1.0),
        ("11-orbit-b.jpg", FRAME_CLOSED, 155, 18, 70, 0.0, 1.0),
        ("12-detail.jpg", FRAME_CLOSED, 25, 8, 95, -0.02, 0.62),
        ("13-open-three-quarter.jpg", FRAME_OPEN, 42, 18, 70, 0.01, 1.05),
        ("14-open-front.jpg", FRAME_OPEN, 5, 14, 70, 0.01, 1.0),
    ]


def main():
    opts = parse_args()
    out_dir = opts["out"]
    out_dir.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    kind, model_path = import_model(opts)
    print(f"IMPORT {kind} {model_path}", flush=True)

    scene = bpy.context.scene
    if "ProductStory" in bpy.data.actions:
        action = bpy.data.actions["ProductStory"]
        print(f"ACTION ProductStory frames {action.frame_range[0]}-{action.frame_range[1]}", flush=True)

    shots_mode = opts["shots"]
    if kind != "glb" and shots_mode == "case01":
        shots_mode = "simple"

    if shots_mode == "case01":
        hide_prefix(CLOSED_LID_NAMES, True)
        set_frame(FRAME_CLOSED)
    else:
        set_frame(1)

    if kind in ("stl", "step", "obj"):
        apply_simple_material_if_needed()

    mins, maxs = mesh_bbox()
    center = (mins + maxs) / 2.0
    size = maxs - mins
    extent = max(size.x, size.y, size.z)
    radius = extent * 1.55
    print(f"CENTER {tuple(round(v, 4) for v in center)} SIZE {tuple(round(v, 4) for v in size)} R={radius:.3f}", flush=True)

    setup_world_white(scene)
    setup_floor(mins.z, max(size.x, size.y) * 6.0)
    setup_studio(center, extent)
    cam = setup_camera(scene, opts["res"], opts["engine"], opts["samples"])
    print(f"ENGINE {scene.render.engine} samples={opts['samples']} res={opts['res']}", flush=True)

    shots = shot_list(shots_mode)
    if opts["only"]:
        shots = [s for s in shots if s[0] in opts["only"]]
        if not shots:
            raise RuntimeError(f"--only matched no shots: {opts['only']}")

    written = []
    for name, frame, az, el, lens, z_bias, r_scale in shots:
        path = safe_write_path(out_dir, name, opts["force"])
        set_frame(frame)
        mins_f, maxs_f = mesh_bbox()
        center_f = (mins_f + maxs_f) / 2.0
        center_f = Vector((center_f.x, center_f.y, center_f.z + z_bias * extent))
        place_camera(cam, center_f, radius * r_scale, az, el, lens)
        render_still(scene, path)
        written.append(path)

    repo_stills = opts["repo_stills"] or REPO_STILLS
    if opts["copy_repo"]:
        repo_stills.mkdir(parents=True, exist_ok=True)
        for src in written:
            dst = repo_stills / src.name
            if dst.resolve() == src.resolve():
                print(f"SKIP_COPY same-file {dst}", flush=True)
                continue
            shutil.copy2(src, dst)
            print(f"COPIED {dst}", flush=True)

    print(f"DONE {len(written)} stills", flush=True)
    for p in written:
        print(f"OUT {p}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1) from exc
