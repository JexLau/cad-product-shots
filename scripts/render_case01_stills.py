#!/usr/bin/env python3
"""Case #1 one-click multi-angle stills (Blender EEVEE, headless).

Imports the Catellect product-story GLB, applies a white-bg studio lighting
preset, and writes ≥6 marketing stills into MEDIA.md-style names (07+ / orbit).

Run:

  bash /workspace/cad-product-shots/scripts/run_case01_stills.sh

See docs/RENDER.md.
"""

from __future__ import annotations

import math
import os
import shutil
import sys
import traceback
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


def argv_after_sep():
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1 :]
    return []


def parse_args():
    args = argv_after_sep()
    out = {"out": DEFAULT_OUT, "res": 1080, "force": False, "copy_repo": True, "glb": None}
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
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()


def setup_world_white(scene):
    world = bpy.data.worlds.new("Case01White")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg is None:
        nt = world.node_tree
        bg = nt.nodes.new("ShaderNodeBackground")
        out = nt.nodes.get("World Output") or nt.nodes.new("ShaderNodeOutputWorld")
        nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    bg.inputs["Color"].default_value = (0.96, 0.96, 0.96, 1.0)
    bg.inputs["Strength"].default_value = 1.0


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
    s = max(scale, 0.15)
    add_area("Key", target + Vector((-0.55 * s, -0.75 * s, 0.95 * s)), target, 70.0, 0.85 * s, (1.0, 0.97, 0.93))
    add_area("Fill", target + Vector((0.85 * s, -0.35 * s, 0.55 * s)), target, 32.0, 1.0 * s, (0.85, 0.90, 1.0))
    add_area("Rim", target + Vector((0.15 * s, 0.95 * s, 0.75 * s)), target, 45.0, 0.65 * s, (1.0, 0.92, 0.85))


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


def setup_camera(scene, res):
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.name = "Case01Cam"
    cam.data.lens = 70
    cam.data.clip_start = 0.01
    cam.data.clip_end = 100.0
    scene.camera = cam
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.quality = 92
    scene.render.film_transparent = False
    eevee = getattr(scene, "eevee", None)
    if eevee is not None:
        for attr, val in (("taa_render_samples", 24), ("use_raytracing", False), ("use_shadows", True)):
            if hasattr(eevee, attr):
                try:
                    setattr(eevee, attr, val)
                except Exception as exc:
                    print(f"EEVEE skip {attr}: {exc}", flush=True)
    if hasattr(scene, "view_settings"):
        try:
            scene.view_settings.exposure = -0.35
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
    bpy.ops.render.render(write_still=True)
    size = path.stat().st_size if path.exists() else 0
    print(f"WROTE {path} bytes={size}", flush=True)
    if size < 1000:
        raise RuntimeError(f"Render too small / missing: {path}")


def resolve_glb(explicit):
    if explicit is not None:
        if not explicit.exists():
            raise FileNotFoundError(explicit)
        return explicit
    for p in DEFAULT_GLBS:
        if p.exists():
            return p
    raise FileNotFoundError("No GLB found among defaults")


def main():
    try:
        opts = parse_args()
        glb = resolve_glb(opts["glb"])
        out_dir = opts["out"]
        out_dir.mkdir(parents=True, exist_ok=True)

        bpy.ops.wm.read_factory_settings(use_empty=True)
        print(f"IMPORT {glb}", flush=True)
        bpy.ops.import_scene.gltf(filepath=str(glb))
        print("IMPORTED", flush=True)

        scene = bpy.context.scene
        if "ProductStory" in bpy.data.actions:
            action = bpy.data.actions["ProductStory"]
            print(f"ACTION ProductStory {action.frame_range[0]}-{action.frame_range[1]}", flush=True)

        hide_prefix(CLOSED_LID_NAMES, True)
        set_frame(FRAME_CLOSED)
        mins, maxs = mesh_bbox()
        center = (mins + maxs) / 2.0
        size = maxs - mins
        radius = max(size.x, size.y, size.z) * 1.85
        print(f"CENTER {tuple(round(v, 4) for v in center)} SIZE {tuple(round(v, 4) for v in size)} R={radius:.3f}", flush=True)

        setup_world_white(scene)
        print("WORLD ok", flush=True)
        setup_floor(mins.z, max(size.x, size.y) * 6.0)
        print("FLOOR ok", flush=True)
        setup_studio(center, max(size.x, size.y, size.z))
        print("LIGHTS ok", flush=True)
        cam = setup_camera(scene, opts["res"])
        print(f"CAMERA ok engine={scene.render.engine} res={opts['res']}", flush=True)

        shots = [
            ("07-front.jpg", FRAME_CLOSED, 0, 12, 70, 0.0, 1.0),
            ("08-three-quarter.jpg", FRAME_CLOSED, 38, 16, 70, 0.0, 1.0),
            ("09-top.jpg", FRAME_CLOSED, 15, 72, 55, 0.0, 1.15),
            ("10-orbit-a.jpg", FRAME_CLOSED, 90, 14, 70, 0.0, 1.0),
            ("11-orbit-b.jpg", FRAME_CLOSED, 155, 18, 70, 0.0, 1.0),
            ("12-detail.jpg", FRAME_CLOSED, 25, 8, 95, -0.02, 0.62),
            ("13-open-three-quarter.jpg", FRAME_OPEN, 42, 18, 70, 0.01, 1.05),
            ("14-open-front.jpg", FRAME_OPEN, 5, 14, 70, 0.01, 1.0),
        ]

        written = []
        for name, frame, az, el, lens, z_bias, r_scale in shots:
            path = safe_write_path(out_dir, name, opts["force"])
            set_frame(frame)
            mins_f, maxs_f = mesh_bbox()
            center_f = (mins_f + maxs_f) / 2.0
            center_f = Vector((center_f.x, center_f.y, center_f.z + z_bias))
            place_camera(cam, center_f, radius * r_scale, az, el, lens)
            print(f"RENDER {name} frame={frame} az={az} el={el}", flush=True)
            render_still(scene, path)
            written.append(path)

        if opts["copy_repo"]:
            REPO_STILLS.mkdir(parents=True, exist_ok=True)
            for src in written:
                dst = REPO_STILLS / src.name
                shutil.copy2(src, dst)
                print(f"COPIED {dst}", flush=True)

        print("DONE", len(written), "stills", flush=True)
        for p in written:
            print("OUT", p, flush=True)
    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
