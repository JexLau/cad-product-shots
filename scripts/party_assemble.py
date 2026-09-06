"""Assemble SQFMI Party case parts into a pipeline-ready GLB.

Imports Case_Top/Bottom + Button (x4), drops Plug, rotates so face → -Y / thin = Y
(matching Yatari extras heuristics). Writes media/demo-watchy/source/Party_Model.glb.
"""
from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Euler, Vector

ROOT = Path("/workspace/cad-product-shots/media/demo-watchy/source/party")
OUT = Path("/workspace/cad-product-shots/media/demo-watchy/source/Party_Model.glb")


def _import_glb(path: Path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return [o for o in bpy.data.objects if o not in before]


def _world_bbox(objects):
    mins = Vector((1e9, 1e9, 1e9))
    maxs = Vector((-1e9, -1e9, -1e9))
    for obj in objects:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            w = obj.matrix_world @ Vector(corner)
            mins = Vector(tuple(min(mins[i], w[i]) for i in range(3)))
            maxs = Vector(tuple(max(maxs[i], w[i]) for i in range(3)))
    return mins, maxs


def _mesh_centroid_local(mesh):
    verts = mesh.vertices
    if not verts:
        return Vector((0, 0, 0))
    acc = Vector((0, 0, 0))
    for v in verts:
        acc += v.co
    return acc / len(verts)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)

    bot = _import_glb(ROOT / "Case_Bottom.glb")[0]
    top = _import_glb(ROOT / "Case_Top.glb")[0]
    btn_src = _import_glb(ROOT / "Button.glb")[0]
    bot.name = "PartyBottom"
    top.name = "PartyTop"
    bot.data.name = "PartyBottom"
    top.data.name = "PartyTop"

    mesh = btn_src.data
    coords = [btn_src.matrix_world @ v.co for v in mesh.vertices]
    cx = sum(c.x for c in coords) / len(coords)
    cy = sum(c.y for c in coords) / len(coords)
    cz = sum(c.z for c in coords) / len(coords)
    print(f"PARTY_ASSEMBLE btn_template center=({cx:.5f},{cy:.5f},{cz:.5f})", flush=True)

    bpy.data.objects.remove(btn_src, do_unlink=True)
    positions = [(cx, cy), (cx, -cy), (-cx, cy), (-cx, -cy)]
    buttons = []
    for i, (px, py) in enumerate(positions):
        m = mesh.copy()
        m.name = f"PartyButtonMesh.{i}"
        o = bpy.data.objects.new(f"PartyButton.{i}", m)
        bpy.context.collection.objects.link(o)
        lc = _mesh_centroid_local(m)
        if px > 0:
            # Mirror across YZ so the long axis still hugs the +X wall.
            o.scale = (-1.0, 1.0, 1.0)
            o.location = Vector((px - (-lc.x), py - lc.y, cz - lc.z))
        else:
            o.location = Vector((px - lc.x, py - lc.y, cz - lc.z))
        buttons.append(o)

    meshes = [bot, top, *buttons]
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root_empty = bpy.context.object
    root_empty.name = "PartyRoot"
    for o in meshes:
        o.parent = root_empty
    # Face authored toward -Z → -Y for Watchy extras / camera.
    root_empty.rotation_euler = Euler((-math.pi / 2.0, 0.0, 0.0), "XYZ")
    bpy.context.view_layer.update()

    for o in meshes:
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = mw
    bpy.data.objects.remove(root_empty, do_unlink=True)

    for o in meshes:
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    mins, maxs = _world_bbox(meshes)
    size = maxs - mins
    print(
        f"PARTY_ASSEMBLE size=({size.x:.5f},{size.y:.5f},{size.z:.5f}) "
        f"center={tuple(round(v, 5) for v in ((mins + maxs) / 2))} "
        f"objs={[o.name for o in meshes]}",
        flush=True,
    )
    assert size.y < size.x and size.y < size.z, "expected thin axis Y after rotate"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(OUT), export_format="GLB", use_selection=False)
    print(f"PARTY_ASSEMBLE wrote {OUT} ({OUT.stat().st_size} bytes)", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", flush=True)
        raise
