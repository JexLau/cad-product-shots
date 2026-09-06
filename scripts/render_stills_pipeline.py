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

# Local extras (same directory as this script when launched via Blender --python)
_SCRIPTS_DIR = Path(__file__).resolve().parent if "__file__" in dir() else Path("/workspace/cad-product-shots/scripts")
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
try:
    from watchy_assemble_extras import add_watchy_screen_and_strap, detect_watchy_family
except Exception as _watchy_imp_exc:  # pragma: no cover
    add_watchy_screen_and_strap = None
    detect_watchy_family = lambda: False
    print(f"WATCHY_EXTRAS_IMPORT_FAIL {_watchy_imp_exc}", flush=True)

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
        "headband_proxy": True,
        "watchy_extras": True,
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
        elif a == "--headband-proxy":
            out["headband_proxy"] = True
            explicit.add("headband_proxy")
        elif a == "--no-headband-proxy":
            out["headband_proxy"] = False
            explicit.add("headband_proxy")
        elif a == "--watchy-extras":
            out["watchy_extras"] = True
            explicit.add("watchy_extras")
        elif a == "--no-watchy-extras":
            out["watchy_extras"] = False
            explicit.add("watchy_extras")
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


def mesh_bbox(exclude_prefixes=None):
    """World AABB of visible meshes. Optionally skip helper prefixes (strap tails)."""
    mins = Vector((1e9, 1e9, 1e9))
    maxs = Vector((-1e9, -1e9, -1e9))
    found = False
    excl = tuple(exclude_prefixes or ())
    for obj in bpy.data.objects:
        if obj.type != "MESH" or obj.hide_render:
            continue
        if excl and any(obj.name.startswith(p) for p in excl):
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
        # DJI-track: high rim/kicker vs fill so charcoal satin shells keep a readable edge.
        add_area("Key", target + Vector((-0.70 * s, -0.95 * s, 0.90 * s)), target, 20.0 * e, 0.68 * s, (1.0, 0.97, 0.92))
        add_area("Fill", target + Vector((1.10 * s, -0.30 * s, 0.35 * s)), target, 1.8 * e, 1.40 * s, (0.72, 0.82, 1.0))
        add_area("Rim", target + Vector((0.20 * s, 1.15 * s, 0.70 * s)), target, 36.0 * e, 0.46 * s, (1.0, 0.93, 0.86))
        add_area("Kicker", target + Vector((-0.85 * s, 0.75 * s, 0.45 * s)), target, 16.0 * e, 0.40 * s, (0.95, 0.98, 1.0))
        add_area("Top", target + Vector((0.0, -0.10 * s, 1.70 * s)), target, 2.4 * e, 1.20 * s, (0.95, 0.97, 1.0))
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
# Wearable silhouette restored via add_ploopy_headband_proxy() (quiet Bezier fabric arc).
PLOOPY_HIDE_MESH_PREFIXES = ("HPH-039", "HPH-038", "HPH-036", "HPH-035")
# One-sided slider stubs (no left twin in this GLB) — hidden only when headband proxy
# replaces the wearable bridge so featured stills are not right-yoke-only.
PLOOPY_HIDE_WITH_PROXY = ("HPH-037", "HPH-033")
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


def _world_bbox(obj):
    mins = Vector((1e9, 1e9, 1e9))
    maxs = Vector((-1e9, -1e9, -1e9))
    for corner in obj.bound_box:
        w = obj.matrix_world @ Vector(corner)
        mins = Vector(tuple(min(mins[i], w[i]) for i in range(3)))
        maxs = Vector(tuple(max(maxs[i], w[i]) for i in range(3)))
    return mins, maxs


def _tube_along_path(path, tube_r, n_side=14, oval=(1.08, 0.72)):
    """Build a smooth oval tube mesh along a list of Vectors."""
    if len(path) < 2:
        return None
    tangents = []
    for i in range(len(path)):
        if i == 0:
            tangents.append((path[1] - path[0]).normalized())
        elif i == len(path) - 1:
            tangents.append((path[i] - path[i - 1]).normalized())
        else:
            tangents.append((path[i + 1] - path[i - 1]).normalized())

    verts = []
    faces = []
    up = Vector((0.0, 1.0, 0.0))
    rx, ry = tube_r * oval[0], tube_r * oval[1]
    n_path = len(path) - 1
    for i, (p, tang) in enumerate(zip(path, tangents)):
        side = tang.cross(up)
        if side.length < 1e-6:
            side = tang.cross(Vector((1.0, 0.0, 0.0)))
        side.normalize()
        normal = side.cross(tang).normalized()
        for s in range(n_side):
            ang = (2.0 * math.pi * s) / n_side
            offset = side * (math.cos(ang) * rx) + normal * (math.sin(ang) * ry)
            verts.append(p + offset)
        if i > 0:
            base = i * n_side
            prev = (i - 1) * n_side
            for s in range(n_side):
                s2 = (s + 1) % n_side
                faces.append((prev + s, prev + s2, base + s2, base + s))

    for end_i, rev in ((0, False), (n_path, True)):
        center_idx = len(verts)
        verts.append(Vector(path[end_i]))
        ring = end_i * n_side
        for s in range(n_side):
            s2 = (s + 1) % n_side
            if rev:
                faces.append((center_idx, ring + s2, ring + s))
            else:
                faces.append((center_idx, ring + s, ring + s2))

    mesh = bpy.data.meshes.new("PloopyHeadbandProxyMesh")
    mesh.from_pydata([(v.x, v.y, v.z) for v in verts], [], faces)
    mesh.update()
    for poly in mesh.polygons:
        poly.use_smooth = True
    return mesh


def _cup_outer_top_pad(obj, side_sign):
    """Outer-third top pad on an earcup (solid shell, not ear cavity)."""
    mw = obj.matrix_world
    verts = [mw @ v.co for v in obj.data.vertices]
    if not verts:
        mins, maxs = _world_bbox(obj)
        x = mins.x + 0.28 * (maxs.x - mins.x) if side_sign < 0 else maxs.x - 0.28 * (maxs.x - mins.x)
        return Vector((x, mins.y + 0.25 * (maxs.y - mins.y), maxs.z))
    xs = [v.x for v in verts]
    x_lo, x_hi = min(xs), max(xs)
    if side_sign < 0:
        pool = [v for v in verts if v.x <= x_lo + 0.34 * (x_hi - x_lo)]
    else:
        pool = [v for v in verts if v.x >= x_hi - 0.34 * (x_hi - x_lo)]
    z_hi = max(v.z for v in pool)
    top = [v for v in pool if v.z >= z_hi - 0.010]
    y_lo = min(v.y for v in top)
    y_span = max(1e-9, max(v.y for v in top) - y_lo)
    front = [v for v in top if v.y <= y_lo + 0.40 * y_span]
    cluster = front if len(front) >= 6 else top
    return sum(cluster, Vector((0.0, 0.0, 0.0))) / float(len(cluster))


def add_ploopy_headband_proxy(enabled=True):
    """Quiet fabric C-band into both earcup outer-top pads + joint plugs.

    Hides one-sided HPH-037/033. Measures outer-third top pads on HPH-013/018,
    builds vertical yokes + crown, and adds small joint spheres so ends read as
    joined (not floating) even when the tube centerline sits near hollow shell.
    """
    if not enabled:
        print("HEADBAND_PROXY off", flush=True)
        return None
    cups = {}
    for obj in bpy.data.objects:
        if obj.type != "MESH" or obj.hide_render or obj.name in ("CycloramaFloor", "PloopyHeadbandProxy"):
            continue
        key = _mesh_key(obj)
        if key in ("HPH-013", "HPH-018"):
            cups[key] = obj
    if "HPH-013" not in cups or "HPH-018" not in cups:
        print("HEADBAND_PROXY skip (no earcups)", flush=True)
        return None

    for obj in list(bpy.data.objects):
        if obj.type != "MESH":
            continue
        if _mesh_key(obj) in ("HPH-037", "HPH-033"):
            obj.hide_render = True
            obj.hide_viewport = True

    left = _cup_outer_top_pad(cups["HPH-013"], -1)
    right = _cup_outer_top_pad(cups["HPH-018"], +1)
    lm, lM = _world_bbox(cups["HPH-013"])
    rm, rM = _world_bbox(cups["HPH-018"])
    cup_h = max(lM.z - lm.z, rM.z - rm.z)

    tube_r = max(0.0155, 0.5 * abs(right.x - left.x) * 0.140)
    # Path on the measured pads; tiny camera bias only (too much Y float reads as a gap).
    x_L = left.x - 0.15 * tube_r
    x_R = right.x + 0.15 * tube_r
    y_L = left.y - 0.15 * tube_r
    y_R = right.y - 0.15 * tube_r
    y0 = 0.5 * (y_L + y_R)

    z_pad_L, z_pad_R = left.z, right.z
    z_pad = 0.5 * (z_pad_L + z_pad_R)
    # Path starts at dug-in plug centers.
    z_bury = z_pad - 0.85 * (tube_r * 1.45)
    z_rise = z_pad + 1.25 * tube_r
    half = 0.5 * abs(x_R - x_L)
    z_shoulder = z_pad + max(0.062, half * 0.70)
    crown_z = z_pad + max(0.110, half * 1.25)

    def yoke(x, y, n_vert=18, n_bend=11):
        pts = []
        for i in range(n_vert):
            u = i / (n_vert - 1)
            u2 = u * u * (3.0 - 2.0 * u)
            pts.append(Vector((x, y, z_bury + (z_rise - z_bury) * u2)))
        start = pts[-1]
        end = Vector((x + (0.0 - x) * 0.10, 0.40 * y0 + 0.60 * y, z_shoulder))
        mid = Vector((0.70 * start.x + 0.30 * end.x, 0.5 * (start.y + end.y), 0.25 * start.z + 0.75 * end.z))
        for i in range(1, n_bend):
            u = i / (n_bend - 1)
            pts.append((1 - u) ** 2 * start + 2 * (1 - u) * u * mid + u ** 2 * end)
        return pts

    left_yoke = yoke(x_L, y_L)
    right_yoke = yoke(x_R, y_R)
    pL, pR = left_yoke[-1], right_yoke[-1]
    a = 0.5 * (pR.x - pL.x)
    cx = 0.5 * (pL.x + pR.x)
    z0 = 0.5 * (pL.z + pR.z)
    b = max(0.001, crown_z - z0)
    arc = [Vector((cx + a * math.cos(t), y0 + 0.012 * math.sin(t), z0 + b * math.sin(t)))
           for t in (math.pi * (1.0 - i / 39.0) for i in range(40))]
    full = left_yoke[:-1] + arc + list(reversed(right_yoke))[1:]

    mesh = _tube_along_path(full, tube_r, n_side=18, oval=(1.10, 0.82))
    if mesh is None:
        print("HEADBAND_PROXY mesh fail", flush=True)
        return None

    mat = _make_principled("Prod_HeadbandProxy", (0.09, 0.095, 0.11), 0.90, 0.0, 0.07)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf and "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = 0.40
        if "Sheen Roughness" in bsdf.inputs:
            bsdf.inputs["Sheen Roughness"].default_value = 0.55

    band = bpy.data.objects.new("PloopyHeadbandProxy", mesh)
    bpy.context.collection.objects.link(band)
    band.data.materials.append(mat)

    # Joint plugs: fill the cup-to-yoke interface so ends never read as floating caps.
    plug_r = tube_r * 1.45
    # Dig plugs deep into the pad so AO does not read as an air gap.
    for i, (x, y, z) in enumerate((
        (left.x, left.y, left.z - 0.85 * plug_r),
        (right.x, right.y, right.z - 0.85 * plug_r),
    )):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=plug_r, location=(x, y, z), segments=20, ring_count=12)
        plug = bpy.context.active_object
        plug.name = f"PloopyHeadbandJoint{i}"
        plug.data.materials.append(mat)
        for poly in plug.data.polygons:
            poly.use_smooth = True

    print(
        f"HEADBAND_PROXY ok pads L=({left.x:.3f},{left.y:.3f},{left.z:.3f}) "
        f"R=({right.x:.3f},{right.y:.3f},{right.z:.3f}) "
        f"yoke_x=({x_L:.3f},{x_R:.3f}) bury_z={z_bury:.3f} rise_z={z_rise:.3f} "
        f"crown_z={crown_z:.3f} tube_r={tube_r:.4f} plug_r={plug_r:.4f} pts={len(full)}",
        flush=True,
    )
    return band



def _make_principled(name, color, roughness, metallic=0.0, specular=0.45, sheen=0.0, coat=0.0):
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
        # Blender 5 / AgX: kill leftover emission so CAD flats do not blow white.
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = 0.0
        if "Coat Weight" in bsdf.inputs:
            bsdf.inputs["Coat Weight"].default_value = float(coat)
        if "Sheen Weight" in bsdf.inputs:
            bsdf.inputs["Sheen Weight"].default_value = float(sheen)
        if sheen > 0 and "Sheen Roughness" in bsdf.inputs:
            bsdf.inputs["Sheen Roughness"].default_value = 0.45
    return mat


def _add_micro_bump(mat, strength=0.045, scale=48.0):
    """Subtle Noise→Bump so soft pads read cushion, not hard CAD flats."""
    if not mat or not mat.use_nodes:
        return
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if not bsdf:
        return
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = float(scale)
    noise.inputs["Detail"].default_value = 8.0
    noise.inputs["Roughness"].default_value = 0.55
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = float(strength)
    bump.inputs["Distance"].default_value = 0.08
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def _assign_single(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    if obj.material_slots:
        obj.material_slots[0].material = mat


def _earcup_shell_pad_material(name="Prod_EarcupShellPad", dark_premium=False):
    """Satin shell mixed → soft warm pad by object-space medial ring (smooth falloff).

    Both L/R cups: local −X is medial (toward head); disc lies in local YZ.
    GLB has no UVs — procedural Mix avoids jagged per-face tessellation.
    dark_premium: charcoal satin shell + stronger coat for DJI-bar deep studio.
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (1100, 0)

    shell = nt.nodes.new("ShaderNodeBsdfPrincipled")
    shell.location = (700, 220)
    if dark_premium:
        # Charcoal injection-mold satin (DJI-bar): dark base, coat catches rim.
        shell.inputs["Base Color"].default_value = (0.048, 0.050, 0.056, 1.0)
        shell.inputs["Roughness"].default_value = 0.28
        coat_w, spec = 0.26, 0.58
    else:
        shell.inputs["Base Color"].default_value = (0.18, 0.19, 0.22, 1.0)
        shell.inputs["Roughness"].default_value = 0.34
        coat_w, spec = 0.12, 0.48
    if "Specular IOR Level" in shell.inputs:
        shell.inputs["Specular IOR Level"].default_value = float(spec)
    if "Coat Weight" in shell.inputs:
        shell.inputs["Coat Weight"].default_value = float(coat_w)
    if "Metallic" in shell.inputs:
        shell.inputs["Metallic"].default_value = 0.0
    if "Emission Strength" in shell.inputs:
        shell.inputs["Emission Strength"].default_value = 0.0

    pad = nt.nodes.new("ShaderNodeBsdfPrincipled")
    pad.location = (700, -260)
    if dark_premium:
        pad.inputs["Base Color"].default_value = (0.032, 0.022, 0.016, 1.0)
    else:
        pad.inputs["Base Color"].default_value = (0.040, 0.028, 0.022, 1.0)
    pad.inputs["Roughness"].default_value = 0.95
    if "Specular IOR Level" in pad.inputs:
        pad.inputs["Specular IOR Level"].default_value = 0.03
    if "Sheen Weight" in pad.inputs:
        pad.inputs["Sheen Weight"].default_value = 0.70
        if "Sheen Roughness" in pad.inputs:
            pad.inputs["Sheen Roughness"].default_value = 0.48
    if "Coat Weight" in pad.inputs:
        pad.inputs["Coat Weight"].default_value = 0.0
    if "Emission Strength" in pad.inputs:
        pad.inputs["Emission Strength"].default_value = 0.0

    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (420, -460)
    noise.inputs["Scale"].default_value = 36.0
    noise.inputs["Detail"].default_value = 12.0
    noise.inputs["Roughness"].default_value = 0.6
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (560, -420)
    bump.inputs["Strength"].default_value = 0.07
    bump.inputs["Distance"].default_value = 0.06
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], pad.inputs["Normal"])

    texcoord = nt.nodes.new("ShaderNodeTexCoord")
    texcoord.location = (-800, 0)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    sep.location = (-600, 0)
    nt.links.new(texcoord.outputs["Object"], sep.inputs["Vector"])

    # Medial = low local X (both cups). Soft: 1 at x<=-0.016, 0 at x>=0.004
    map_med = nt.nodes.new("ShaderNodeMapRange")
    map_med.location = (-360, 160)
    map_med.clamp = True
    map_med.inputs["From Min"].default_value = -0.018
    map_med.inputs["From Max"].default_value = 0.014
    map_med.inputs["To Min"].default_value = 1.0
    map_med.inputs["To Max"].default_value = 0.0
    nt.links.new(sep.outputs["X"], map_med.inputs["Value"])

    # r = sqrt(y^2+z^2) in object space (cup disc)
    my = nt.nodes.new("ShaderNodeMath")
    my.operation = "MULTIPLY"
    my.location = (-360, -40)
    nt.links.new(sep.outputs["Y"], my.inputs[0])
    nt.links.new(sep.outputs["Y"], my.inputs[1])
    mz = nt.nodes.new("ShaderNodeMath")
    mz.operation = "MULTIPLY"
    mz.location = (-360, -160)
    nt.links.new(sep.outputs["Z"], mz.inputs[0])
    nt.links.new(sep.outputs["Z"], mz.inputs[1])
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    add.location = (-180, -90)
    nt.links.new(my.outputs["Value"], add.inputs[0])
    nt.links.new(mz.outputs["Value"], add.inputs[1])
    sqr = nt.nodes.new("ShaderNodeMath")
    sqr.operation = "SQRT"
    sqr.location = (0, -90)
    nt.links.new(add.outputs["Value"], sqr.inputs[0])

    # Cushion torus band ~28–55mm from cup axis
    rin = nt.nodes.new("ShaderNodeMapRange")
    rin.location = (200, -20)
    rin.clamp = True
    rin.inputs["From Min"].default_value = 0.020
    rin.inputs["From Max"].default_value = 0.028
    rin.inputs["To Min"].default_value = 0.0
    rin.inputs["To Max"].default_value = 1.0
    nt.links.new(sqr.outputs["Value"], rin.inputs["Value"])
    rout = nt.nodes.new("ShaderNodeMapRange")
    rout.location = (200, -200)
    rout.clamp = True
    rout.inputs["From Min"].default_value = 0.052
    rout.inputs["From Max"].default_value = 0.066
    rout.inputs["To Min"].default_value = 1.0
    rout.inputs["To Max"].default_value = 0.0
    nt.links.new(sqr.outputs["Value"], rout.inputs["Value"])
    ring = nt.nodes.new("ShaderNodeMath")
    ring.operation = "MULTIPLY"
    ring.location = (420, -90)
    nt.links.new(rin.outputs["Result"], ring.inputs[0])
    nt.links.new(rout.outputs["Result"], ring.inputs[1])

    fac_ring = nt.nodes.new("ShaderNodeMath")
    fac_ring.operation = "MULTIPLY"
    fac_ring.location = (560, 80)
    nt.links.new(map_med.outputs["Result"], fac_ring.inputs[0])
    nt.links.new(ring.outputs["Value"], fac_ring.inputs[1])

    # Soft fill: medial half of cup disc (cushion walls) even outside strict torus band.
    med_half = nt.nodes.new("ShaderNodeMath")
    med_half.operation = "MULTIPLY"
    med_half.location = (560, -40)
    # reuse map_med; require r > ~0.022 so cup axis cavity stays shell/mesh-adjacent
    r_gate = nt.nodes.new("ShaderNodeMapRange")
    r_gate.location = (380, -40)
    r_gate.clamp = True
    r_gate.inputs["From Min"].default_value = 0.018
    r_gate.inputs["From Max"].default_value = 0.026
    r_gate.inputs["To Min"].default_value = 0.0
    r_gate.inputs["To Max"].default_value = 0.75
    nt.links.new(sqr.outputs["Value"], r_gate.inputs["Value"])
    nt.links.new(map_med.outputs["Result"], med_half.inputs[0])
    nt.links.new(r_gate.outputs["Result"], med_half.inputs[1])

    fac = nt.nodes.new("ShaderNodeMath")
    fac.operation = "MAXIMUM"
    fac.location = (720, 20)
    nt.links.new(fac_ring.outputs["Value"], fac.inputs[0])
    nt.links.new(med_half.outputs["Value"], fac.inputs[1])

    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.location = (900, 0)
    nt.links.new(fac.outputs["Value"], mix.inputs["Fac"])
    nt.links.new(shell.outputs["BSDF"], mix.inputs[1])
    nt.links.new(pad.outputs["BSDF"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return mat



def assign_product_materials(kind="auto", dark_premium=False):
    """Assignable product plastics — not white/lavender clay (Rams surface DoD).

    dark_premium: charcoal satin palette for studio-dark / DJI-bar featured stills.
    """
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.name != "CycloramaFloor" and not o.hide_render]
    if not meshes:
        return "none"
    keys = {_mesh_key(o) for o in meshes}
    names = {o.name.lower() for o in meshes}
    data_names = {(getattr(o.data, "name", "") or "").lower() for o in meshes}

    if kind == "auto":
        if any(k.startswith("HPH-") for k in keys):
            kind = "ploopy"
        elif any(
            "button" in n
            or n.startswith("top")
            or n.startswith("bottom")
            or "pole02" in n
            or "yatari" in n
            or "watchyscreen" in n
            or "watchystrap" in n
            for n in names | data_names
        ):
            kind = "watchy"
        else:
            kind = "generic"

    if kind == "ploopy":
        mat_earcup = _earcup_shell_pad_material(dark_premium=bool(dark_premium))
        if dark_premium:
            mat_mesh = _make_principled(
                "Prod_DriverMesh", (0.022, 0.024, 0.028), 0.22, 0.78, 0.42, sheen=0.0, coat=0.18
            )
            mat_metal = _make_principled(
                "Prod_MetalAccent", (0.28, 0.29, 0.32), 0.24, 0.82, 0.48, sheen=0.0, coat=0.16
            )
            mat_band = _make_principled(
                "Prod_Headband", (0.014, 0.015, 0.018), 0.90, 0.0, 0.05, sheen=0.55, coat=0.0
            )
            mat_shell = _make_principled(
                "Prod_PlasticShell", (0.048, 0.050, 0.056), 0.28, 0.0, 0.58, sheen=0.0, coat=0.26
            )
        else:
            mat_mesh = _make_principled(
                "Prod_DriverMesh", (0.035, 0.038, 0.045), 0.26, 0.68, 0.38, sheen=0.0, coat=0.14
            )
            mat_metal = _make_principled(
                "Prod_MetalAccent", (0.38, 0.39, 0.42), 0.28, 0.75, 0.42, sheen=0.0, coat=0.12
            )
            # Headband fabric: clearly darker than shell so crown reads as another material.
            mat_band = _make_principled(
                "Prod_Headband", (0.022, 0.024, 0.030), 0.93, 0.0, 0.04, sheen=0.60, coat=0.0
            )
            mat_shell = _make_principled(
                "Prod_PlasticShell", (0.22, 0.23, 0.26), 0.34, 0.0, 0.48, sheen=0.0, coat=0.12
            )
        _add_micro_bump(mat_band, strength=0.04, scale=26.0)

        for obj in meshes:
            key = _mesh_key(obj)
            if key in ("HPH-013", "HPH-018"):
                _assign_single(obj, mat_earcup)
            elif key == "HPH-032":
                _assign_single(obj, mat_mesh)
            elif key in ("HPH-033", "HPH-037"):
                _assign_single(obj, mat_metal)
            elif key == "HPH-035" or obj.name.startswith("PloopyHeadband"):
                _assign_single(obj, mat_band)
            else:
                _assign_single(obj, mat_shell)
        print("PRODUCT_MATS ploopy earcup(mix pad/shell)/mesh/band", flush=True)
        return "ploopy"

    if kind == "watchy":
        # Yatari2 remodel: dark satin case, light e-ink insert plane, light-grey buttons,
        # soft dark strap — geometry extras named WatchyScreen* / WatchyStrap*.
        mat_case = _make_principled(
            "Prod_CasePlastic", (0.022, 0.024, 0.028), 0.42, 0.0, 0.38, sheen=0.0, coat=0.14
        )
        mat_insert = _make_principled(
            "Prod_InsertScreen", (0.82, 0.84, 0.78), 0.62, 0.0, 0.10, sheen=0.04, coat=0.0
        )
        # Tiny emission so e-ink stays readable under product softgrey underexposure.
        try:
            nt = mat_insert.node_tree
            bsdf = nt.nodes.get("Principled BSDF")
            if bsdf and "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (0.75, 0.77, 0.70, 1.0)
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = 0.18
        except Exception:
            pass
        mat_btn = _make_principled(
            "Prod_Button", (0.42, 0.43, 0.45), 0.34, 0.12, 0.42, sheen=0.0, coat=0.16
        )
        mat_strap = _make_principled(
            "Prod_Strap", (0.018, 0.018, 0.020), 0.88, 0.0, 0.06, sheen=0.45, coat=0.0
        )
        _add_micro_bump(mat_strap, strength=0.03, scale=18.0)
        mat_buckle = _make_principled(
            "Prod_Buckle", (0.12, 0.12, 0.13), 0.40, 0.35, 0.35, sheen=0.0, coat=0.12
        )
        for obj in meshes:
            key = _mesh_key(obj).lower()
            nl = obj.name.lower()
            if "watchyscreen" in nl or "screeninsert" in nl:
                mat = mat_insert
            elif "watchystrapbuckle" in nl:
                mat = mat_buckle
            elif "watchystrap" in nl:
                mat = mat_strap
            elif "button" in key or "button" in nl:
                mat = mat_btn
            elif key.startswith("top") or nl.startswith("top"):
                mat = mat_case
            elif key.startswith("bottom") or nl.startswith("bottom") or "pole02" in nl:
                mat = mat_case
            else:
                mat = mat_case
            _assign_single(obj, mat)
        print("PRODUCT_MATS watchy case/screen/button/strap", flush=True)
        return "watchy"

    mat = _make_principled("Prod_Neutral", (0.30, 0.31, 0.33), 0.46, 0.03, 0.40)
    for obj in meshes:
        _assign_single(obj, mat)
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

    # Quiet fabric headband proxy for Ploopy (HPH-035 stays hidden — no serpentine).
    if bool(opts.get("headband_proxy", True)):
        add_ploopy_headband_proxy(enabled=True)

    # Watchy Rams remodel: recessed screen insert + demo strap (geometry, not paint).
    if bool(opts.get("watchy_extras", True)) and add_watchy_screen_and_strap is not None:
        add_watchy_screen_and_strap(enabled=True)

    use_clay = bool(opts["clay"]) and not bool(opts.get("no_clay"))
    use_product = bool(opts.get("product_mats", False)) and not use_clay
    if use_clay:
        apply_simple_material_if_needed(force=True)
    elif use_product:
        # Prefer readable product plastics over white clay / lavender CAD placeholders.
        # Dark studio featured: charcoal satin palette (DJI-bar), not soft-grey lab clay.
        assign_product_materials(
            kind="auto",
            dark_premium=(opts.get("lighting") or "softgrey") == "dark",
        )
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

    # Frame on case+screen; ignore long strap overhang so watch fills the still.
    mins, maxs = mesh_bbox(exclude_prefixes=("WatchyStrap",))
    center = (mins + maxs) / 2.0
    size = maxs - mins
    extent = max(size.x, size.y, size.z)
    radius = extent * float(opts["radius_scale"])
    print(f"CENTER {tuple(round(v, 4) for v in center)} SIZE {tuple(round(v, 4) for v in size)} R={radius:.3f}", flush=True)

    lighting = opts.get("lighting") or "softgrey"
    # Product-mat demos: pull world/lights down so tinted plastics stay readable (not chalk).
    if use_product and lighting != "dark":
        # Keep satin readable without chalking mid-greys to clay white (Rams surface gate 1/4).
        opts["world_strength"] = min(float(opts.get("world_strength", 0.65)), 0.28)
        opts["light_scale"] = min(float(opts.get("light_scale", 0.40)), 0.18)
        opts["exposure"] = min(float(opts.get("exposure", -0.70)), -1.05)
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
        mins_f, maxs_f = mesh_bbox(exclude_prefixes=("WatchyStrap",))
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
