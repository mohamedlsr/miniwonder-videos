"""White Bunny in real 3D with Blender (bpy): characters rendered once per pose as transparent sprites,
sets rendered once as backgrounds. The 2D story engine then animates them quickly.
Usage:  python3 bunny3d.py sprites [who ...]   |   python3 bunny3d.py sets [name ...]"""
import math, os, sys, random
import bpy
from mathutils import Vector

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets3d")


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def hexrgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


_MATS = {}


def mat(name, color, rough=0.5, sheen=0.0, sss=0.0, emission=None, spec=0.3, strength=1.0):
    key = (name,)
    if key in _MATS:
        return _MATS[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*(hexrgb(color) if isinstance(color, str) else color), 1)
    b.inputs["Roughness"].default_value = rough
    if "Sheen Weight" in b.inputs:
        b.inputs["Sheen Weight"].default_value = sheen
    if "Subsurface Weight" in b.inputs and sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (0.2, 0.1, 0.1)
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = spec
    if emission:
        b.inputs["Emission Color"].default_value = (*(hexrgb(emission) if isinstance(emission, str) else emission), 1)
        b.inputs["Emission Strength"].default_value = strength
    _MATS[key] = m
    return m


def sphere(name, loc, scale, material, parent=None, rot=(0, 0, 0), seg=40):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    if parent:
        o.parent = parent
    return o


def box(name, loc, scale, material, parent=None, bevel=0.08, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    o.data.materials.append(material)
    if bevel:
        bpy.ops.object.transform_apply(scale=True)
        m = o.modifiers.new("bev", "BEVEL")
        m.width = bevel
        m.segments = 4
    bpy.ops.object.shade_smooth()
    if parent:
        o.parent = parent
    return o


def cyl(name, loc, r, depth, material, rot=(0, 0, 0), parent=None, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    if parent:
        o.parent = parent
    return o


# ------------------------------------------------------------------ characters
RABBITS = {
    #        fur        inner     outfit     outfit colour  accessory  size
    "bunny": ("#ffffff", "#ffb3c6", "scarf", "#4dabf7", None, 1.0),
    "maman": ("#fff3e6", "#ffb3c6", "dress", "#ff8fab", "flower", 1.12),
    "papa": ("#d2b48c", "#f0b8a8", "sweater", "#4caf6a", "glasses", 1.2),
    "noisette": ("#e3b98c", "#ffb3c6", "dress", "#ffd43b", "bow", 0.8),
}


def build_rabbit(who, mouth="smile", eyes="open", mood="happy", arms="down"):
    fur, inner, outfit, ocol, acc, size = RABBITS[who]
    bpy.ops.object.empty_add(location=(0, 0, 0))
    root = bpy.context.object
    root.scale = (size, size, size)
    F = mat(who + "fur", fur, 0.65, 0.7, 0.06)
    IN = mat(who + "in", inner, 0.6, 0.3)
    EYE = mat("eye", "#141420", 0.04, spec=0.9)
    HI = mat("hi", (1, 1, 1), 0.1, emission=(1, 1, 1), strength=2)
    NOSE = mat("nose", "#ff7a9c", 0.3)
    CHEEK = mat("cheek", "#ffa8bf", 0.8)
    MOUTH = mat("mouth", "#6b2333", 0.4)
    TONGUE = mat("tongue", "#ff8fa3", 0.4)
    O = mat(who + "outfit", ocol, 0.75, 0.4)
    # body
    sphere("body", (0, 0, 0.98), (0.76, 0.68, 0.86), O if outfit == "sweater" else F, root)
    if outfit != "sweater":
        sphere("belly", (0, -0.42, 0.92), (0.48, 0.3, 0.58), mat(who + "belly", "#f7f8fb" if who == "bunny" else fur, 0.7, 0.5), root)
    if outfit == "dress":
        bpy.ops.mesh.primitive_cone_add(radius1=0.95, radius2=0.55, depth=1.05, location=(0, 0, 0.78), vertices=48)
        d = bpy.context.object
        d.data.materials.append(O)
        bpy.ops.object.shade_smooth()
        d.parent = root
        dots = mat("dots", "#ffffff", 0.6)
        for i in range(10):
            a = -1.3 + i * 0.29
            sphere("dot", (0.78 * math.sin(a) * (1 - 0.0), -0.78 * math.cos(a) * 0.98, 0.55 + (i % 2) * 0.35), (0.06, 0.03, 0.06), dots, root, seg=12)
    for s in (-1, 1):
        sphere("foot", (0.36 * s, -0.22, 0.13), (0.3, 0.44, 0.16), F, root)
        up = arms == "up"
        sphere("arm", (0.74 * s, -0.12, 1.45 if up else 1.12), (0.18, 0.18, 0.42),
               O if outfit == "sweater" else F, root, rot=(0, (-0.9 if up else 0.32) * s, 0))
    sphere("tail", (0, 0.66, 0.55), (0.24, 0.24, 0.24), F, root)
    # head
    bpy.ops.object.empty_add(location=(0, 0, 2.08))
    head = bpy.context.object
    head.parent = root
    sphere("skull", (0, 0, 0), (0.9, 0.8, 0.8), F, head)
    droop = 0.75 if mood == "sad" else 0.0
    for s in (-1, 1):
        rx, ry = 0.05 + droop * 0.4, (-0.2 - droop) * s
        sphere("ear", (0.33 * s + droop * 0.25 * s, 0.05, 1.0 - droop * 0.35), (0.21, 0.1, 0.66), F, head, rot=(rx, ry, 0))
        sphere("earin", (0.33 * s + droop * 0.25 * s, -0.06, 1.0 - droop * 0.35), (0.12, 0.05, 0.5), IN, head, rot=(rx, ry, 0))
        if eyes == "closed":
            bpy.ops.mesh.primitive_torus_add(location=(0.32 * s, -0.7, 0.06), major_radius=0.12, minor_radius=0.025,
                                             rotation=(math.radians(90), 0, 0))
            e = bpy.context.object
            e.scale = (1, 0.6, 1)
            e.data.materials.append(EYE)
            e.parent = head
            # hide lower half of the ring by pushing it into the head: use a squashed sphere lid in fur colour
            sphere("lid", (0.32 * s, -0.66, 0.0), (0.16, 0.07, 0.07), F, head)
        else:
            sphere("eye", (0.32 * s, -0.66, 0.08), (0.15, 0.1, 0.18), EYE, head)
            sphere("hi", (0.32 * s - 0.05, -0.75, 0.16), (0.05, 0.03, 0.05), HI, head)
            sphere("hi2", (0.32 * s + 0.04, -0.75, 0.0), (0.022, 0.015, 0.022), HI, head)
        if mood == "sad":
            box("brow", (0.32 * s, -0.72, 0.33), (0.13, 0.025, 0.025), MOUTH, head, bevel=0.02, rot=(0, (0.35) * s, 0))
        sphere("cheek", (0.56 * s, -0.54, -0.2), (0.15, 0.06, 0.1), CHEEK, head)
        if acc == "glasses":
            bpy.ops.mesh.primitive_torus_add(location=(0.32 * s, -0.82, 0.08), major_radius=0.22, minor_radius=0.03,
                                             rotation=(math.radians(90), 0, 0))
            g = bpy.context.object
            g.data.materials.append(mat("glass", "#5c4033", 0.4))
            g.parent = head
    sphere("muzzle", (0, -0.66, -0.25), (0.28, 0.17, 0.17), F, head)
    sphere("nose", (0, -0.8, -0.13), (0.1, 0.06, 0.07), NOSE, head)
    if mouth == "open":
        sphere("mouth", (0, -0.78, -0.37), (0.12, 0.05, 0.11), MOUTH, head)
        sphere("tongue", (0, -0.81, -0.42), (0.07, 0.03, 0.04), TONGUE, head)
    elif mood == "sad":
        bpy.ops.mesh.primitive_torus_add(location=(0, -0.8, -0.44), major_radius=0.09, minor_radius=0.018,
                                         rotation=(math.radians(90), 0, 0))
        m = bpy.context.object
        m.data.materials.append(MOUTH)
        m.parent = head
        sphere("mcover", (0, -0.79, -0.5), (0.13, 0.05, 0.07), F, head)
    else:
        for s in (-1, 1):
            bpy.ops.mesh.primitive_torus_add(location=(0.06 * s, -0.8, -0.3), major_radius=0.06, minor_radius=0.016,
                                             rotation=(math.radians(90), 0, 0))
            m = bpy.context.object
            m.data.materials.append(MOUTH)
            m.parent = head
        sphere("mcover", (0, -0.8, -0.27), (0.18, 0.05, 0.06), F, head)
    # outfits & accessories
    if outfit == "scarf":
        bpy.ops.mesh.primitive_torus_add(location=(0, 0, 1.62), major_radius=0.58, minor_radius=0.14)
        sc = bpy.context.object
        sc.scale = (1, 0.92, 1)
        sc.data.materials.append(O)
        bpy.ops.object.shade_smooth()
        sc.parent = root
        sphere("scarfend", (0.32, -0.5, 1.36), (0.14, 0.06, 0.3), O, root, rot=(0.2, 0, 0.3))
    if acc == "flower":
        for i in range(6):
            a = 2 * math.pi * i / 6
            sphere("petal", (0.55 + 0.1 * math.cos(a), -0.35, 0.75 + 0.1 * math.sin(a)), (0.08, 0.04, 0.08),
                   mat("petal", "#ff6b9a", 0.5), head)
        sphere("fc", (0.55, -0.38, 0.75), (0.06, 0.04, 0.06), mat("fc", "#ffd43b", 0.5), head)
    if acc == "bow":
        for s in (-1, 1):
            sphere("bow", (0.45 + 0.13 * s, -0.3, 0.8), (0.14, 0.06, 0.1), mat("bow", "#ff4d7a", 0.5), head, rot=(0, 0, 0.3 * s))
        sphere("bowc", (0.45, -0.34, 0.8), (0.06, 0.05, 0.06), mat("bowc", "#e03163", 0.5), head)
    return root


def build_squirrel(mouth="smile", eyes="open", mood="happy", arms="down"):
    bpy.ops.object.empty_add(location=(0, 0, 0))
    root = bpy.context.object
    root.scale = (0.95, 0.95, 0.95)
    O = mat("sq", "#ef8a3b", 0.65, 0.6)
    C = mat("sqc", "#ffe0bd", 0.7, 0.4)
    EYE, HI = mat("eye", "#141420", 0.04, spec=0.9), mat("hi", (1, 1, 1), 0.1, emission=(1, 1, 1), strength=2)
    CAP = mat("cap", "#e03131", 0.6)
    sphere("body", (0, 0, 0.95), (0.7, 0.62, 0.85), O, root)
    sphere("belly", (0, -0.4, 0.9), (0.42, 0.28, 0.55), C, root)
    # big tail: chain of spheres
    for i in range(10):
        t = i / 9
        sphere("tail", (0.35 + 0.55 * math.sin(t * 2.0), 0.55 + 0.2 * t, 0.45 + 2.5 * t - 0.5 * t * t), (0.42 - 0.06 * t,) * 3, O, root, seg=32)
    sphere("tailtip", (0.95, 0.75, 2.6), (0.4, 0.4, 0.35), O, root, seg=32)
    for s in (-1, 1):
        sphere("foot", (0.32 * s, -0.2, 0.12), (0.26, 0.4, 0.14), O, root)
        sphere("arm", (0.66 * s, -0.15, 1.15 if arms == "down" else 1.45), (0.16, 0.16, 0.38), O, root,
               rot=(0, (0.3 if arms == "down" else -0.9) * s, 0))
    bpy.ops.object.empty_add(location=(0, 0, 2.0))
    head = bpy.context.object
    head.parent = root
    sphere("skull", (0, 0, 0), (0.82, 0.74, 0.74), O, head)
    sphere("face", (0, -0.45, -0.15), (0.55, 0.32, 0.42), C, head)
    for s in (-1, 1):
        bpy.ops.mesh.primitive_cone_add(radius1=0.22, depth=0.55, location=(0.48 * s, 0.05, 0.78), rotation=(0, -0.35 * s, 0))
        e = bpy.context.object
        e.data.materials.append(O)
        e.parent = head
        if eyes == "closed":
            sphere("lid", (0.3 * s, -0.66, 0.06), (0.15, 0.06, 0.03), mat("mouth", "#6b2333", 0.4), head)
        else:
            sphere("eye", (0.3 * s, -0.64, 0.08), (0.14, 0.1, 0.17), EYE, head)
            sphere("hi", (0.3 * s - 0.05, -0.73, 0.16), (0.045, 0.03, 0.045), HI, head)
        sphere("cheek", (0.5 * s, -0.55, -0.22), (0.13, 0.05, 0.09), mat("cheek", "#ffa8bf", 0.8), head)
        if mood == "sad":
            box("brow", (0.3 * s, -0.7, 0.32), (0.12, 0.025, 0.025), mat("mouth", "#6b2333", 0.4), head, bevel=0.02, rot=(0, 0.35 * s, 0))
    sphere("nose", (0, -0.8, -0.12), (0.09, 0.06, 0.06), mat("snose", "#4a2a17", 0.3), head)
    if mouth == "open":
        sphere("mouth", (0, -0.75, -0.33), (0.11, 0.05, 0.1), mat("mouth", "#6b2333", 0.4), head)
    else:
        sphere("mouth", (0, -0.76, -0.3), (0.08, 0.03, 0.02), mat("mouth", "#6b2333", 0.4), head)
    # cap
    sphere("cap", (0, 0.0, 0.58), (0.8, 0.74, 0.4), CAP, head)
    box("visor", (0, -0.68, 0.5), (0.42, 0.28, 0.03), CAP, head, bevel=0.03, rot=(0.2, 0, 0))
    return root


def build_turtle(mouth="smile", eyes="open", mood="happy", arms="down"):
    bpy.ops.object.empty_add(location=(0, 0, 0))
    root = bpy.context.object
    G = mat("tg", "#8fd18a", 0.6, 0.3)
    SH = mat("shell", "#a8743f", 0.5)
    SP = mat("spot", "#c99a5e", 0.5)
    EYE, HI = mat("eye", "#141420", 0.04, spec=0.9), mat("hi", (1, 1, 1), 0.1, emission=(1, 1, 1), strength=2)
    sphere("shell", (0, 0.2, 0.75), (1.25, 1.1, 0.8), SH, root)
    for (x, z) in ((-0.5, 1.15), (0.5, 1.15), (0, 1.45), (-0.85, 0.75), (0.85, 0.75), (0, 0.95)):
        sphere("spot", (x, -0.55 if z < 1.3 else -0.25, z), (0.25, 0.12, 0.2), SP, root)
    cyl("rim", (0, 0.2, 0.35), 1.22, 0.18, mat("rim", "#d9b06b", 0.5))
    bpy.context.object.parent = root
    for s in (-1, 1):
        sphere("leg", (0.75 * s, -0.45, 0.2), (0.3, 0.3, 0.22), G, root)
    bpy.ops.object.empty_add(location=(0, -1.15, 1.05))
    head = bpy.context.object
    head.parent = root
    sphere("neck", (0, -0.9, 0.75), (0.3, 0.35, 0.35), G, root)
    sphere("skull", (0, 0, 0), (0.62, 0.55, 0.55), G, head)
    for s in (-1, 1):
        if eyes == "closed":
            sphere("lid", (0.22 * s, -0.5, 0.08), (0.12, 0.05, 0.025), mat("mouth", "#6b2333", 0.4), head)
        else:
            sphere("eye", (0.22 * s, -0.47, 0.1), (0.12, 0.08, 0.14), EYE, head)
            sphere("hi", (0.22 * s - 0.04, -0.55, 0.16), (0.04, 0.025, 0.04), HI, head)
        sphere("cheek", (0.38 * s, -0.4, -0.12), (0.1, 0.04, 0.07), mat("cheek", "#ffa8bf", 0.8), head)
        if mood == "sad":
            box("brow", (0.22 * s, -0.52, 0.32), (0.1, 0.02, 0.02), mat("mouth", "#6b2333", 0.4), head, bevel=0.015, rot=(0, 0.35 * s, 0))
    if mouth == "open":
        sphere("mouth", (0, -0.53, -0.2), (0.1, 0.04, 0.08), mat("mouth", "#6b2333", 0.4), head)
    else:
        sphere("mouth", (0, -0.54, -0.18), (0.08, 0.025, 0.018), mat("mouth", "#6b2333", 0.4), head)
    bpy.ops.mesh.primitive_torus_add(location=(0, -0.95, 0.68), major_radius=0.32, minor_radius=0.07)
    sc = bpy.context.object
    sc.data.materials.append(mat("lscarf", "#9775fa", 0.7, 0.4))
    sc.parent = root
    return root


BUILDERS = {"pipo": build_squirrel, "lila": build_turtle}


def sprite_camera(height=4.2, yaw=18, tz=1.65):
    """Perspective camera looking at a character standing at the origin, slightly from the side."""
    d = 13.0
    a = math.radians(yaw)
    loc = Vector((d * math.sin(a), -d * math.cos(a), 2.0))
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.data.type = "PERSP"
    cam.data.lens = 85
    t = Vector((0, 0, tz))
    cam.rotation_euler = (t - loc).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    return cam


def studio_lights(sky="#bfe6ff", strength=0.9):
    bpy.ops.object.light_add(type="SUN", location=(4, -4, 8))
    sun = bpy.context.object
    sun.data.energy = 3.2
    sun.rotation_euler = (math.radians(48), math.radians(8), math.radians(32))
    sun.data.angle = math.radians(10)
    bpy.ops.object.light_add(type="AREA", location=(-5, -6, 4))
    fill = bpy.context.object
    fill.data.energy = 600
    fill.data.size = 6
    fill.rotation_euler = (math.radians(60), 0, math.radians(-40))
    bpy.ops.object.light_add(type="AREA", location=(0, 6, 5))
    rim = bpy.context.object
    rim.data.energy = 400
    rim.data.size = 4
    rim.rotation_euler = (math.radians(-55), 0, 0)
    w = bpy.data.worlds.new("w")
    bpy.context.scene.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (*hexrgb(sky), 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = strength


def setup_render(res, samples, transparent=False):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = transparent
    names = [i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items]
    sc.view_settings.view_transform = "AgX" if "AgX" in names else "Filmic"
    for look in (("AgX - Punchy", "Punchy") if not transparent else ()):
        try:
            sc.view_settings.look = look
            break
        except Exception:
            pass
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA" if transparent else "RGB"


POSES = [  # (tag, mouth, eyes, mood, arms)
    ("idle", "smile", "open", "happy", "down"),
    ("talk", "open", "open", "happy", "down"),
    ("blink", "smile", "closed", "happy", "down"),
    ("sad", "smile", "open", "sad", "down"),
    ("sadtalk", "open", "open", "sad", "down"),
    ("cheer", "open", "open", "happy", "up"),
]


def render_sprites(who_list):
    os.makedirs(OUT, exist_ok=True)
    for who in who_list:
        for tag, mouth, eyes, mood, arms in POSES:
            path = os.path.join(OUT, f"{who}_{tag}.png")
            if os.path.exists(path):
                continue
            reset()
            _MATS.clear()
            if who in RABBITS:
                build_rabbit(who, mouth, eyes, mood, arms)
            else:
                BUILDERS[who](mouth, eyes, mood, arms)
            studio_lights()
            sprite_camera(tz={"papa": 2.35, "maman": 2.1}.get(who, 1.65))
            setup_render((800, 1100), 20, transparent=True)
            bpy.context.scene.render.filepath = path
            bpy.ops.render.render(write_still=True)
            print("SPRITE", path, flush=True)


# ------------------------------------------------------------------ sets
def ground(color="#6cc24a"):
    bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, 0))
    bpy.context.object.data.materials.append(mat("ground" + color, color, 0.9))


def flowers(n=90, area=(-9, 9, -2, 10), seed=3, avoid=None):
    rnd = random.Random(seed)
    cols = ["#ff8fab", "#ffd43b", "#ffffff", "#b197fc"]
    for i in range(n):
        x, y = rnd.uniform(area[0], area[1]), rnd.uniform(area[2], area[3])
        c = cols[i % 4]
        for k in range(5):
            a = 2 * math.pi * k / 5
            sphere("p", (x + 0.07 * math.cos(a), y + 0.07 * math.sin(a), 0.07), (0.055, 0.055, 0.03), mat("fl" + c, c, 0.6), seg=10)
        sphere("c", (x, y, 0.08), (0.035, 0.035, 0.03), mat("flc", "#f59f00", 0.5), seg=10)


def tree(x, y, s=1.0):
    cyl("trunk", (x, y, 1.6 * s), 0.28 * s, 3.2 * s, mat("trunk", "#8b5a2b", 0.8))
    for dx, dz, r, c in ((0, 3.8, 1.7, "#4f9e3a"), (-1.0, 3.2, 1.2, "#5cb247"), (1.0, 3.3, 1.2, "#5cb247"), (0.2, 4.6, 1.1, "#69c055")):
        sphere("leaf", (x + dx * s, y, dz * s), (r * s, r * s, r * s * 0.9), mat("leaf" + c, c, 0.8), seg=32)


def hills():
    for i, (x, y, r, c) in enumerate(((-12, 24, 10, "#9ad97a"), (10, 28, 13, "#8bd06b"), (0, 38, 18, "#a8de8c"))):
        sphere("hill", (x, y, -r * 0.5), (r, r * 0.8, r * 0.62), mat("hill" + c, c, 0.9), seg=32)


def set_camera(loc=(0, -11, 2.3), target=(0, 0, 1.4), lens=35):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.data.lens = lens
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = (Vector(target) - Vector(loc)).length
    cam.data.dof.aperture_fstop = 4.0
    bpy.context.scene.camera = cam


def set_meadow():
    ground()
    hills()
    # burrow: green mound with a round wooden door and window
    sphere("mound", (-4.2, 3.0, -0.3), (3.4, 2.6, 2.4), mat("mound", "#7cc35a", 0.85), seg=48)
    cyl("door", (-3.6, 0.55, 1.05), 0.85, 0.2, mat("door", "#b7793f", 0.6), rot=(math.radians(90), 0, 0.25))
    bpy.ops.mesh.primitive_torus_add(location=(-3.62, 0.45, 1.05), major_radius=0.88, minor_radius=0.1, rotation=(math.radians(90), 0, 0.25))
    bpy.context.object.data.materials.append(mat("doorframe", "#7a4b2a", 0.6))
    for dx in (-0.3, 0.3):
        box("plank", (-3.6 + dx * 0.97, 0.43 + dx * 0.25, 1.05), (0.02, 0.02, 0.7), mat("doorframe", "#7a4b2a", 0.6), bevel=0, rot=(0, 0, 0.25))
    sphere("knob", (-3.05, 0.35, 1.0), (0.08, 0.08, 0.08), mat("knob", "#ffd43b", 0.3))
    cyl("window", (-5.6, 1.3, 1.6), 0.4, 0.15, mat("win", "#fff3bf", 0.3, emission="#fff3bf", strength=0.6), rot=(math.radians(90), 0, 0.5))
    tree(5.2, 4.0)
    flowers()


def set_picnic():
    ground()
    hills()
    tree(-6, 5, 1.1)
    tree(-2.5, 7, 0.9)
    cyl("pond", (5.5, 5, 0.02), 3.2, 0.05, mat("pond", "#4dabf7", 0.08, spec=0.8))
    bpy.context.object.scale = (1.3, 0.7, 1)
    for x, y in ((4.8, 4.6), (6.3, 5.4)):
        cyl("lily", (x, y, 0.07), 0.35, 0.03, mat("lily", "#51cf66", 0.6))
    # checked blanket
    for i in range(6):
        for j in range(3):
            c = "#ff6b6b" if (i + j) % 2 == 0 else "#ffe3e3"
            box("blk", (-1.5 + i * 0.6, -0.6 + j * 0.6, 0.02), (0.3, 0.3, 0.015), mat("blk" + c, c, 0.9), bevel=0)
    flowers(70, seed=5)


def set_kitchen():
    floor = mat("floor", "#d9a066", 0.6)
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
    bpy.context.object.data.materials.append(floor)
    box("wall", (0, 4.5, 4), (20, 0.2, 4), mat("wall", "#ffe8cc", 0.9), bevel=0)
    for x in range(-12, 13, 2):
        box("stripe", (x, 4.28, 4), (0.25, 0.02, 4), mat("stripe", "#fff4e6", 0.9), bevel=0)
    box("winframe", (2.5, 4.25, 3.6), (1.6, 0.1, 1.3), mat("wframe", "#5c4033", 0.6), bevel=0.05)
    box("winglass", (2.5, 4.18, 3.6), (1.45, 0.05, 1.15), mat("glass2", "#a5d8ff", 0.2, emission="#d0ebff", strength=0.8), bevel=0)
    box("sill", (2.5, 4.0, 2.25), (1.8, 0.3, 0.08), mat("sill", "#f08c00", 0.5))
    box("shelf", (-4.5, 4.1, 3.4), (1.8, 0.3, 0.08), mat("shelf", "#a0703c", 0.6))
    for i, c in enumerate(("#ff8787", "#ffd43b", "#69db7c")):
        cyl("jar", (-5.6 + i * 1.1, 4.0, 3.85), 0.3, 0.8, mat("jar" + c, c, 0.3))
        cyl("lid", (-5.6 + i * 1.1, 4.0, 4.3), 0.32, 0.12, mat("lidm", "#868e96", 0.4))
    cyl("table", (4.5, 1.5, 1.55), 1.8, 0.15, mat("tabletop", "#c98d54", 0.5))
    cyl("leg", (4.5, 1.5, 0.75), 0.18, 1.5, mat("tableleg", "#a8703a", 0.6))
    cyl("plate", (4.5, 1.3, 1.66), 0.7, 0.05, mat("plate", "#ffffff", 0.3))
    for i in range(4):
        bpy.ops.mesh.primitive_cone_add(radius1=0.09, depth=0.7, location=(4.2 + i * 0.2, 1.3, 1.78), rotation=(0, math.radians(90), 0.3))
        bpy.context.object.data.materials.append(mat("carrot", "#ff922b", 0.5))
    w = bpy.data.worlds.new("w")
    bpy.context.scene.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (*hexrgb("#fff1e0"), 1)


def set_bedroom():
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
    bpy.context.object.data.materials.append(mat("rug", "#7c5cbf", 0.9))
    box("wall", (0, 4.5, 4), (20, 0.2, 4), mat("nwall", "#3b3f8f", 0.9), bevel=0)
    box("win", (3.5, 4.25, 3.6), (1.5, 0.1, 1.2), mat("nframe", "#1c1f4a", 0.6), bevel=0.05)
    sphere("moon", (3.9, 4.1, 4.0), (0.35, 0.05, 0.35), mat("moon", "#fff3bf", 0.3, emission="#fff3bf", strength=3))
    rnd = random.Random(2)
    for _ in range(14):
        sphere("star", (rnd.uniform(2.2, 4.8), 4.12, rnd.uniform(2.6, 4.6)), (0.04, 0.02, 0.04),
               mat("star", "#ffffff", 0.3, emission="#ffffff", strength=4), seg=8)
    box("bed", (-4.2, 1.5, 0.6), (2.2, 1.3, 0.45), mat("bed", "#ffa8a8", 0.8))
    box("head", (-6.3, 1.5, 1.2), (0.15, 1.3, 1.1), mat("wood", "#a0703c", 0.6))
    sphere("pillow", (-5.6, 1.5, 1.2), (0.6, 0.9, 0.25), mat("pillow", "#ffffff", 0.7))
    box("night", (0.2, 3.3, 0.6), (0.5, 0.5, 0.6), mat("wood", "#a0703c", 0.6))
    cyl("lampst", (0.2, 3.3, 1.6), 0.05, 1.2, mat("metal", "#868e96", 0.3))
    bpy.ops.mesh.primitive_cone_add(radius1=0.55, radius2=0.3, depth=0.6, location=(0.2, 3.3, 2.3))
    bpy.context.object.data.materials.append(mat("shade", "#ffd43b", 0.6, emission="#ffd43b", strength=1.5))
    bpy.ops.object.light_add(type="POINT", location=(0.2, 3.0, 2.2))
    bpy.context.object.data.energy = 250
    bpy.context.object.data.color = (1, 0.85, 0.55)
    w = bpy.data.worlds.new("w")
    bpy.context.scene.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (*hexrgb("#2b2f6b"), 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.4


def prop_carrot():
    bpy.ops.mesh.primitive_cone_add(radius1=0.16, depth=1.1, location=(0, 0, 0.55), rotation=(math.radians(180), 0, 0), vertices=32)
    o = bpy.context.object
    o.data.materials.append(mat("carrot", "#ff922b", 0.5))
    bpy.ops.object.shade_smooth()
    for i, a in enumerate((-0.35, 0, 0.35)):
        sphere("leaf", (0.08 * math.sin(a * 3), 0, 1.25), (0.05, 0.05, 0.25), mat("cleaf", "#51cf66", 0.6), rot=(0, a, 0), seg=16)


def prop_basket():
    cyl("bk", (0, 0, 0.35), 0.75, 0.7, mat("wick", "#d9a066", 0.8))
    bpy.ops.mesh.primitive_torus_add(location=(0, 0, 0.72), major_radius=0.76, minor_radius=0.06)
    bpy.context.object.data.materials.append(mat("wick2", "#a0703c", 0.8))
    bpy.ops.mesh.primitive_torus_add(location=(0, 0, 0.75), major_radius=0.6, minor_radius=0.05, rotation=(math.radians(90), 0, 0))
    o = bpy.context.object
    o.scale = (1, 1.4, 1)
    o.data.materials.append(mat("wick2", "#a0703c", 0.8))
    for i in range(4):
        bpy.ops.mesh.primitive_cone_add(radius1=0.12, depth=0.8, location=(-0.3 + i * 0.2, 0, 0.95), rotation=(math.radians(180) - 0.2 + i * 0.13, 0, 0), vertices=24)
        bpy.context.object.data.materials.append(mat("carrot", "#ff922b", 0.5))
        sphere("leaf", (-0.3 + i * 0.2, 0, 1.4), (0.05, 0.05, 0.16), mat("cleaf", "#51cf66", 0.6), seg=12)


def prop_basket_empty():
    cyl("bk", (0, 0, 0.35), 0.75, 0.7, mat("wick", "#d9a066", 0.8))
    bpy.ops.mesh.primitive_torus_add(location=(0, 0, 0.72), major_radius=0.76, minor_radius=0.06)
    bpy.context.object.data.materials.append(mat("wick2", "#a0703c", 0.8))
    bpy.ops.mesh.primitive_torus_add(location=(0, 0, 0.75), major_radius=0.6, minor_radius=0.05, rotation=(math.radians(90), 0, 0))
    o = bpy.context.object
    o.scale = (1, 1.4, 1)
    o.data.materials.append(mat("wick2", "#a0703c", 0.8))


def prop_nut():
    sphere("nut", (0, 0, 0.35), (0.3, 0.3, 0.36), mat("nutm", "#b5651d", 0.4))
    sphere("cap", (0, 0, 0.62), (0.33, 0.33, 0.16), mat("nutc", "#7a4a1c", 0.7))


PROPS = {"carrot": prop_carrot, "basket": prop_basket, "basket_empty": prop_basket_empty, "nut": prop_nut}


def render_props():
    os.makedirs(OUT, exist_ok=True)
    for n, fn in PROPS.items():
        path = os.path.join(OUT, f"prop_{n}.png")
        if os.path.exists(path):
            continue
        reset()
        _MATS.clear()
        fn()
        studio_lights()
        bpy.ops.object.camera_add(location=(0, -6, 2.2))
        cam = bpy.context.object
        cam.data.lens = 60
        cam.rotation_euler = (Vector((0, 0, 0.6)) - cam.location).to_track_quat("-Z", "Y").to_euler()
        bpy.context.scene.camera = cam
        setup_render((500, 500), 16, transparent=True)
        bpy.context.scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print("PROP", path, flush=True)


SETS = {"meadow": set_meadow, "picnic": set_picnic, "kitchen": set_kitchen, "bedroom": set_bedroom}


def render_sets(names):
    os.makedirs(OUT, exist_ok=True)
    for n in names:
        path = os.path.join(OUT, f"set_{n}.png")
        if os.path.exists(path):
            continue
        reset()
        _MATS.clear()
        SETS[n]()
        if n in ("meadow", "picnic"):
            studio_lights("#6ec0ff", 1.1)
        else:
            bpy.ops.object.light_add(type="AREA", location=(0, -6, 6))
            l = bpy.context.object
            l.data.energy = 1500 if n == "kitchen" else 250
            l.data.size = 10
            l.rotation_euler = (math.radians(40), 0, 0)
        set_camera()
        setup_render((1920, 1080), 32)
        bpy.context.scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print("SET", path, flush=True)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "sprites":
        render_sprites(sys.argv[2:] or ["bunny", "maman", "papa", "noisette", "pipo", "lila"])
    elif mode == "props":
        render_props()
    elif mode == "sets":
        render_sets(sys.argv[2:] or list(SETS))
