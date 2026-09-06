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
        "clay": False,
        "no_clay": False,
        "radius_scale": 2.35,
        "bg": 0.22,
        "exposure": -0.70,
        "light_scale": 0.40,
        "dampen": 0.46,
        "preset": "softgrey",
        "lighting": "softgrey",
        "world_strength": 0.65,
        "hide_supports": False,
        "product_mats": False,
        "hide_names": None,
    }
    explicit = set()
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
        elif a == "--radius-scale" and i + 1 < len(args):
            i += 1
            out["radius_scale"] = float(args[i])
            explicit.add("radius_scale")
        elif a == "--bg" and i + 1 < len(args):
            i += 1
            out["bg"] = float(args[i])
            explicit.add("bg")
        elif a == "--exposure" and i + 1 < len(args):
            i += 1
            out["exposure"] = float(args[i])
            explicit.add("exposure")
        elif a == "--light-scale" and i + 1 < len(args):
            i += 1
            out["light_scale"] = float(args[i])
            explicit.add("light_scale")
        elif a == "--dampen" and i + 1 < len(args):
            i += 1
            out["dampen"] = float(args[i])
            explicit.add("dampen")
        elif a == "--preset" and i + 1 < len(args):
            i += 1
            out["preset"] = args[i].strip().lower()
        elif a == "--clay":
            out["clay"] = True
            explicit.add("clay")
        elif a == "--no-clay":
            out["no_clay"] = True
            out["clay"] = False
            explicit.add("clay")
        elif a == "--hide-supports":
            out["hide_supports"] = True
            explicit.add("hide_supports")
        elif a == "--no-hide-supports":
            out["hide_supports"] = False
            explicit.add("hide_supports")
        elif a == "--product-mats":
            out["product_mats"] = True
            explicit.add("product_mats")
        elif a == "--no-product-mats":
            out["product_mats"] = False
            explicit.add("product_mats")
        elif a == "--hide-names" and i + 1 < len(args):
            i += 1
            out["hide_names"] = {x.strip() for x in args[i].split(",") if x.strip()}
        elif a == "--force":
            out["force"] = True
        elif a == "--no-copy-repo":
            out["copy_repo"] = False
        i += 1
    apply_preset(out, explicit)
    return out


def apply_preset(out, explicit):
    """Apply studio presets. Explicit CLI knobs always win over preset defaults."""
    name = (out.get("preset") or "softgrey").lower().replace("_", "-")
    if name in ("dark", "studio-dark", "dark-premium"):
        defaults = {
            "bg": 0.03,
            "exposure": -0.65,
            "light_scale": 0.34,
            "radius_scale": 2.95,
            "dampen": 0.90,
            "clay": False,
            "lighting": "dark",
            "world_strength": 0.22,
        }
        for key, val in defaults.items():
            if key == "clay":
                if "clay" not in explicit:
                    out["clay"] = False
                    out["no_clay"] = True
                continue
            if key not in explicit:
                out[key] = val
        out["preset"] = "studio-dark"
    else:
        out["preset"] = "softgrey"
        out.setdefault("lighting", "softgrey")
        out.setdefault("world_strength", 0.65)


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


def setup_world_studio(scene, level=0.22, strength=0.65, name="StudioSoftGrey"):
    """Studio backdrop — soft-grey (default) or near-black for studio-dark."""
    world = bpy.data.worlds.new(name)
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    bg = nt.nodes.new("ShaderNodeBackground")
    c = float(level)
    bg.inputs["Color"].default_value = (c * 0.98, c, c * 1.03, 1.0)
    bg.inputs["Strength"].default_value = float(strength)
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


def setup_studio(target, scale, light_scale=0.28, style="softgrey"):
    # Size-scale area power ~ distance^2, then * light_scale for contrast control.
    # softgrey: readable CAD demo. dark: high key:rim, low fill (DJI-track).
    s = max(scale, 0.05)
    e = max(0.18, min((s / 0.25) ** 2, 1.10)) * float(light_scale)
    if style == "dark":
        add_area("Key", target + Vector((-0.70 * s, -0.95 * s, 0.90 * s)), target, 18.0 * e, 0.70 * s, (1.0, 0.97, 0.92))
        add_area("Fill", target + Vector((1.10 * s, -0.30 * s, 0.35 * s)), target, 2.4 * e, 1.40 * s, (0.72, 0.82, 1.0))
        add_area("Rim", target + Vector((0.20 * s, 1.15 * s, 0.70 * s)), target, 28.0 * e, 0.50 * s, (1.0, 0.93, 0.86))
        add_area("Kicker", target + Vector((-0.85 * s, 0.75 * s, 0.45 * s)), target, 12.0 * e, 0.42 * s, (0.95, 0.98, 1.0))
        add_area("Top", target + Vector((0.0, -0.10 * s, 1.70 * s)), target, 3.0 * e, 1.20 * s, (0.95, 0.97, 1.0))
    else:
        add_area("Key", target + Vector((-0.65 * s, -0.90 * s, 0.85 * s)), target, 34.0 * e, 0.85 * s, (1.0, 0.96, 0.90))
        add_area("Fill", target + Vector((1.05 * s, -0.35 * s, 0.40 * s)), target, 7.0 * e, 1.35 * s, (0.78, 0.86, 1.0))
        add_area("Rim", target + Vector((0.25 * s, 1.10 * s, 0.65 * s)), target, 16.0 * e, 0.70 * s, (1.0, 0.90, 0.82))
        add_area("Top", target + Vector((0.0, -0.15 * s, 1.65 * s)), target, 3.5 * e, 1.50 * s, (0.95, 0.97, 1.0))


def setup_floor(
    z,
    size,
    tone=(0.20, 0.22, 0.25, 1.0),
    roughness=0.72,
    specular=0.15,
    mat_name="SoftGreyFloor",
    shadow_catcher=False,
):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0.0, 0.0, z - 0.001))
    floor = bpy.context.object
    floor.name = "CycloramaFloor"
    mat = bpy.data.materials.new(mat_name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = tone
        bsdf.inputs["Roughness"].default_value = float(roughness)
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = float(specular)
    floor.data.materials.append(mat)
    if shadow_catcher:
        # Cycles: contact shadow on dark world without a blown lit slab.
        try:
            floor.is_shadow_catcher = True
        except Exception:
            pass
        try:
            floor.visible_glossy = False
        except Exception:
            pass



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
                ("use_raytracing", True),
                ("use_shadows", True),
                ("use_gtao", True),
                ("gtao_distance", 0.2),
                ("gtao_factor", 1.0),
                ("gtao_quality", 0.5),
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
            for look in ("AgX - Medium High Contrast", "AgX - High Contrast", "None"):
                try:
                    scene.view_settings.look = look
                    break
                except Exception:
                    continue
        except Exception:
            pass
    return cam


def apply_exposure(scene, exposure=-0.90):
    if hasattr(scene, "view_settings"):
        try:
            scene.view_settings.exposure = float(exposure)
        except Exception:
            pass


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


def apply_simple_material_if_needed(force=False, tone=(0.22, 0.24, 0.27, 1.0)):
    mat = bpy.data.materials.new("NeutralPlastic")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = tone
        bsdf.inputs["Roughness"].default_value = 0.48
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.05
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.42
    for obj in bpy.data.objects:
        if obj.type != "MESH" or obj.name == "CycloramaFloor":
            continue
        if obj.data.materials and not force:
            continue
        obj.data.materials.clear()
        obj.data.materials.append(mat)


def dampen_existing_materials(factor=0.48):
    """Pull bright GLB materials down; use a higher factor (~0.90) for studio-dark."""
    for mat in bpy.data.materials:
        if mat.name in ("SoftGreyFloor", "DarkStudioFloor", "PaperWhite", "NeutralPlastic") or not mat.use_nodes:
            continue
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if not bsdf or "Base Color" not in bsdf.inputs:
            continue
        col = list(bsdf.inputs["Base Color"].default_value)
        rgb = [max(0.06, min(0.72, c * factor)) for c in col[:3]]
        bsdf.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], col[3])
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = max(0.38, min(0.72, bsdf.inputs["Roughness"].default_value))
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = min(
                0.45, max(0.2, bsdf.inputs["Specular IOR Level"].default_value)
            )



def satinize_overmetallic(max_metallic=0.12):
    """Pull mis-authored full-metal GLB plastics toward satin; preserve true metals lightly."""
    for mat in bpy.data.materials:
        if mat.name in ("SoftGreyFloor", "DarkStudioFloor", "PaperWhite", "NeutralPlastic") or not mat.use_nodes:
            continue
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if not bsdf or "Metallic" not in bsdf.inputs:
            continue
        metal = float(bsdf.inputs["Metallic"].default_value)
        rough = float(bsdf.inputs["Roughness"].default_value) if "Roughness" in bsdf.inputs else 0.5
        # Rough + fully metallic is usually CAD placeholder plastic, not chrome.
        if metal > 0.45 and rough >= 0.35:
            bsdf.inputs["Metallic"].default_value = float(max_metallic)
            if "Roughness" in bsdf.inputs:
                bsdf.inputs["Roughness"].default_value = max(0.42, min(0.62, rough))
            if "Specular IOR Level" in bsdf.inputs:
                bsdf.inputs["Specular IOR Level"].default_value = 0.38


# --- Demo assembly cleanup + product materials (Ploopy / Watchy) ---
# Documented hide list (prefer hide_render; do not delete CAD source):
# Ploopy mesh data names from STEP→GLB:
#   HPH-039 (obj NAUO6): lattice headphone stand + base — print-support aesthetic
#   HPH-038 (obj NAUO11): floating duplicate serpentine flexbars — ghost/explode
#   HPH-036 (obj NAUO9): tripod/jig lattice — assembly jig, not wearable product
# Kept as product: HPH-013/018 earcups, HPH-032 driver rings, HPH-033/037 sliders.
# HPH-035 bare serpentine flexbars hidden for Rams DoD (fabric-covered band not in CAD;
#   otherwise reads as print-support serpentine in featured stills).
PLOOPY_HIDE_MESH_PREFIXES = ("HPH-039", "HPH-038", "HPH-036", "HPH-035")
SUPPORT_NAME_HINTS = (
    "support", "scaffold", "lattice", "stand", "jig", "brim", "raft", "helper",
)


def _mesh_key(obj) -> str:
    data = getattr(obj, "data", None)
    return (getattr(data, "name", "") or obj.name or "").split(".")[0]


def hide_print_supports(extra_names=None, enabled=True):
    """Hide print-support / jig / ghost meshes from render (source CAD untouched)."""
    if not enabled:
        print("HIDE_SUPPORTS off", flush=True)
        return []
    hidden = []
    extras = {n.lower() for n in (extra_names or set())}
    for obj in bpy.data.objects:
        if obj.type != "MESH" or obj.name == "CycloramaFloor":
            continue
        key = _mesh_key(obj)
        name_l = (obj.name or "").lower()
        data_l = (getattr(obj.data, "name", "") or "").lower()
        reason = None
        if any(key == p or key.startswith(p + ".") or data_l.startswith(p.lower()) for p in PLOOPY_HIDE_MESH_PREFIXES):
            reason = f"ploopy-support:{key}"
        elif any(h in name_l or h in data_l for h in SUPPORT_NAME_HINTS):
            reason = f"name-hint:{key}"
        elif obj.name in (extra_names or set()) or name_l in extras or key.lower() in extras:
            reason = f"cli:{obj.name}"
        if reason:
            obj.hide_render = True
            obj.hide_viewport = True
            hidden.append(f"{obj.name}/{key} ({reason})")
    print(f"HIDE_SUPPORTS {len(hidden)}: {hidden}", flush=True)
    return hidden


def _make_principled(name, color, roughness, metallic=0.0, specular=0.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = float(roughness)
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = float(metallic)
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = float(specular)
        # Blender 5 / AgX: kill leftover emission and coat so CAD flats do not blow white.
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = 0.0
        if "Coat Weight" in bsdf.inputs:
            bsdf.inputs["Coat Weight"].default_value = 0.0
        if "Sheen Weight" in bsdf.inputs:
            bsdf.inputs["Sheen Weight"].default_value = 0.0
    return mat


def assign_product_materials(kind="auto"):
    """Assign readable industrial plastics (not white/lavender clay)."""
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.name != "CycloramaFloor" and not o.hide_render]
    if not meshes:
        return "none"
    keys = {_mesh_key(o) for o in meshes}
    names = {o.name.lower() for o in meshes}
    data_names = {(getattr(o.data, "name", "") or "").lower() for o in meshes}

    # Detect pack
    if kind == "auto":
        if any(k.startswith("HPH-") for k in keys):
            kind = "ploopy"
        elif any("button" in n or n.startswith("top") or n.startswith("bottom") for n in names | data_names):
            kind = "watchy"
        else:
            kind = "generic"

    if kind == "ploopy":
        # Tinted industrial plastics (neutral grey chalks white under softgrey+AgX).
        mat_shell = _make_principled("Prod_PlasticShell", (0.16, 0.17, 0.19), 0.68, 0.0, 0.18)
        mat_pad = _make_principled("Prod_PadFoam", (0.05, 0.05, 0.055), 0.92, 0.0, 0.06)
        mat_mesh = _make_principled("Prod_DriverMesh", (0.08, 0.085, 0.09), 0.36, 0.50, 0.30)
        mat_metal = _make_principled("Prod_MetalAccent", (0.40, 0.41, 0.44), 0.34, 0.70, 0.38)
        mat_band = _make_principled("Prod_Headband", (0.12, 0.13, 0.145), 0.72, 0.0, 0.16)
        for obj in meshes:
            key = _mesh_key(obj)
            if key in ("HPH-013", "HPH-018"):
                # Earcup assemblies — shell plastic (pad foam not a separate mesh in this GLB)
                mat = mat_shell
            elif key == "HPH-032":
                mat = mat_mesh
            elif key in ("HPH-033", "HPH-037"):
                mat = mat_metal
            elif key == "HPH-035":
                mat = mat_band
            else:
                mat = mat_shell
            obj.data.materials.clear()
            obj.data.materials.append(mat)
            if obj.material_slots:
                obj.material_slots[0].material = mat
        print("PRODUCT_MATS ploopy shell/mesh/metal/band", flush=True)
        return "ploopy"

    if kind == "watchy":
        # Cool charcoal case vs warm insert vs near-black buttons (chroma keeps parts readable).
        mat_case = _make_principled("Prod_CasePlastic", (0.11, 0.125, 0.15), 0.78, 0.0, 0.12)
        mat_insert = _make_principled("Prod_InsertScreen", (0.34, 0.32, 0.27), 0.85, 0.0, 0.08)
        mat_btn = _make_principled("Prod_Button", (0.03, 0.03, 0.035), 0.58, 0.10, 0.18)
        for obj in meshes:
            key = _mesh_key(obj).lower()
            nl = obj.name.lower()
            if "button" in key or "button" in nl:
                mat = mat_btn
            elif key.startswith("top") or nl.startswith("top"):
                # top half reads as insert / screen-adjacent face
                mat = mat_insert
            elif key.startswith("bottom") or nl.startswith("bottom"):
                mat = mat_case
            else:
                mat = mat_case
            obj.data.materials.clear()
            obj.data.materials.append(mat)
            if obj.material_slots:
                obj.material_slots[0].material = mat
        print("PRODUCT_MATS watchy case/insert/button", flush=True)
        return "watchy"

    # generic: quiet mid-grey plastic, not chalk white
    mat = _make_principled("Prod_Neutral", (0.36, 0.37, 0.39), 0.50, 0.03, 0.40)
    for obj in meshes:
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    print("PRODUCT_MATS generic", flush=True)
    return "generic"


def shot_list(mode):
    if mode == "simple":
        return [
            ("07-front.jpg", 1, 0, 14, 65, 0.0, 1.0),
            ("08-three-quarter.jpg", 1, 40, 18, 65, 0.0, 1.0),
            ("09-top.jpg", 1, 28, 52, 50, 0.0, 0.98),
            ("10-orbit-a.jpg", 1, 95, 16, 65, 0.0, 1.0),
            ("11-orbit-b.jpg", 1, 150, 20, 65, 0.0, 1.0),
            ("12-detail.jpg", 1, 30, 16, 75, 0.02, 0.95),
            ("13-rear-three-quarter.jpg", 1, 215, 18, 65, 0.0, 1.05),
            ("14-low-angle.jpg", 1, 48, 8, 60, 0.0, 1.12),
        ]
    return [
        ("07-front.jpg", FRAME_CLOSED, 0, 12, 70, 0.0, 1.0),
        ("08-three-quarter.jpg", FRAME_CLOSED, 38, 16, 70, 0.0, 1.0),
        ("09-top.jpg", FRAME_CLOSED, 22, 48, 55, 0.0, 1.12),
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

    # Hide print-support / jig / ghost meshes before bbox + materials.
    hide_print_supports(extra_names=opts.get("hide_names"), enabled=bool(opts.get("hide_supports", False)))

    use_clay = bool(opts["clay"]) and not bool(opts.get("no_clay"))
    use_product = bool(opts.get("product_mats", False)) and not use_clay
    if use_clay:
        apply_simple_material_if_needed(force=True)
    elif use_product:
        # Prefer readable product plastics over white clay / lavender CAD placeholders.
        assign_product_materials(kind="auto")
    elif kind in ("stl", "step", "obj"):
        # Assign NeutralPlastic only when meshes have no materials (never force-clay on dark).
        apply_simple_material_if_needed(force=False)
    elif kind == "glb":
        damp = float(opts.get("dampen", 0.46))
        if damp > 0:
            dampen_existing_materials(damp)
        if (opts.get("lighting") or "softgrey") == "dark":
            # GLB often marks plastics Metallic=1; keep satin character, not chrome/clay.
            satinize_overmetallic(max_metallic=0.12)

    mins, maxs = mesh_bbox()
    center = (mins + maxs) / 2.0
    size = maxs - mins
    extent = max(size.x, size.y, size.z)
    radius = extent * float(opts["radius_scale"])
    print(f"CENTER {tuple(round(v, 4) for v in center)} SIZE {tuple(round(v, 4) for v in size)} R={radius:.3f}", flush=True)

    lighting = opts.get("lighting") or "softgrey"
    # Product-mat demos: pull world/lights down so tinted plastics stay readable (not chalk).
    if use_product and lighting != "dark":
        opts["world_strength"] = min(float(opts.get("world_strength", 0.65)), 0.42)
        opts["light_scale"] = min(float(opts.get("light_scale", 0.40)), 0.26)
        opts["exposure"] = min(float(opts.get("exposure", -0.70)), -0.55)
        print(
            f"PRODUCT_LIGHTING world_strength={opts['world_strength']} "
            f"light_scale={opts['light_scale']} exposure={opts['exposure']}",
            flush=True,
        )
    world_name = "StudioDark" if lighting == "dark" else "StudioSoftGrey"
    setup_world_studio(scene, opts["bg"], strength=opts.get("world_strength", 0.65), name=world_name)
    if lighting == "dark":
        g = max(0.008, float(opts["bg"]) * 0.40)
        floor_tone = (g, g * 1.02, g * 1.05, 1.0)
        setup_floor(
            mins.z,
            max(size.x, size.y) * 6.0,
            tone=floor_tone,
            roughness=0.95,
            specular=0.02,
            mat_name="DarkStudioFloor",
            shadow_catcher=True,
        )
    else:
        g = max(0.16, float(opts["bg"]) * 0.62)
        floor_tone = (g, g * 1.01, g * 1.04, 1.0)
        setup_floor(mins.z, max(size.x, size.y) * 6.0, tone=floor_tone)
    setup_studio(center, extent, light_scale=opts["light_scale"], style=lighting)
    cam = setup_camera(scene, opts["res"], opts["engine"], opts["samples"])
    apply_exposure(scene, opts["exposure"])
    print(
        f"ENGINE {scene.render.engine} samples={opts['samples']} res={opts['res']} "
        f"preset={opts.get('preset')} lighting={lighting} bg={opts['bg']} "
        f"exposure={opts['exposure']} light_scale={opts['light_scale']} dampen={opts.get('dampen')}",
        flush=True,
    )

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
