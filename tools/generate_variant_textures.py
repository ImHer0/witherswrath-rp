"""Generates the Wither's Wrath skeleton variant assets.

Run from the repo root:  py tools/generate_variant_textures.py [path/to/minecraft-client.jar]
The jar is needed for the Triskull's side heads (they reuse the Wither's own skull pixels)
and for the Withered Steed (a recolor of the vanilla skeleton horse). It is found
automatically in a Prism or vanilla launcher install.

Writes:
  assets/wither/models/item/variant/<variant>.json      3D hat / head model
  assets/wither/textures/item/variant/<variant>.png     its texture
  assets/minecraft/items/air.json                       picks the model by custom_model_data
  assets/wither/equipment/wither_steed.json + skeleton_horse_saddle texture (black horse)
  tools/preview/*.png                                   previews (not shipped)

The hats are worn on an item whose vanilla model is "air", so without this pack nothing
is drawn and the datapack still works on its own. The chestplates are vanilla trims.
Hand-painting over the PNGs is fine, but re-running this script overwrites them.
"""
import glob
import json
import os
import random
import sys
import zipfile
from io import BytesIO

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VARIANTS = ["bone_knight", "soul_archer", "triskull", "hexbinder", "shade_reaper", "death_rider"]


def hexc(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255)


def shade(c, f):
    return tuple(max(0, min(255, int(ch * f))) for ch in c[:3]) + (255,)


def edge(x, y, w, h):
    return x in (0, w - 1) or y in (0, h - 1)


def save(img, *parts):
    path = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def save_json(data, *parts):
    path = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")


def find_jar():
    if len(sys.argv) > 1:
        return sys.argv[1]
    hits = glob.glob(os.path.expandvars(r"%APPDATA%\PrismLauncher\libraries\com\mojang\minecraft\*\minecraft-*-client.jar"))
    hits += glob.glob(os.path.expanduser("~/.minecraft/versions/*/*.jar"))
    return sorted(hits)[-1] if hits else None


def vanilla_png(jar, path):
    return Image.open(BytesIO(zipfile.ZipFile(jar).read(path))).convert("RGBA")


# =============================================================== 3D head models
# Units are entity pixels: the head is the box 4..12 on every axis, the face is -Z.
# display.head scale 1.6 makes 1 model unit = 1 pixel on the mob.
TEX = 128  # painted models: each face gets its own texture region, 1 texel per pixel


def el(name, a, b, mat, faces_mat=None, rot=None):
    return {"name": name, "from": a, "to": b, "mat": mat, "faces_mat": faces_mat or {}, "rot": rot}


def mirror(e):
    a, b = e["from"], e["to"]
    m = dict(e, name=e["name"] + "_r", **{"from": [16 - b[0], a[1], a[2]], "to": [16 - a[0], b[1], b[2]]})
    if e["rot"]:
        r = dict(e["rot"])
        r["origin"] = [16 - r["origin"][0], r["origin"][1], r["origin"][2]]
        if r["axis"] != "x":
            r["angle"] = -r["angle"]
        m["rot"] = r
    return m


def head_bone_knight():
    return [
        el("helm", [3.5, 3.5, 3.5], [12.5, 12.5, 12.5], "steel", {"north": "visor"}),
        el("crest", [7.25, 12.5, 3], [8.75, 15.5, 13], "trim"),
        el("gorget", [2.5, 1, 2.5], [13.5, 4, 13.5], "steel_d"),
        el("spike", [12.5, 8.5, 7], [15, 9.5, 9], "trim"),
        mirror(el("spike", [12.5, 8.5, 7], [15, 9.5, 9], "trim")),
    ]


def head_soul_archer():
    # Robin Hood cap (bycocket): pointed beak in front, brim turned up at the back, long feather
    side = el("brim_side", [3, 11.5, 6], [3.6, 13.5, 12.4], "cap_d")
    return [
        el("crown", [3.6, 11.5, 4], [12.4, 13.5, 12.4], "cap",
           {"north": "cap_band", "south": "cap_band", "east": "cap_band", "west": "cap_band"}),
        el("crown_mid", [4.2, 13.5, 5], [11.8, 15, 12], "cap"),
        el("crown_top", [5.5, 15, 6.5], [10.5, 16, 11.5], "cap_d"),
        el("beak_1", [4.5, 11.5, 2], [11.5, 12.5, 4], "cap"),
        el("beak_2", [5.5, 11.3, 0.5], [10.5, 12.3, 2], "cap"),
        el("beak_3", [6.75, 11.1, -1], [9.25, 12.1, 0.5], "cap_d"),
        el("brim_back", [3.2, 11.5, 12.2], [12.8, 14.5, 13.4], "cap_d"),
        side,
        mirror(side),
        el("feather", [12.4, 12.2, 7], [13.1, 15.2, 15], "feather",
           rot={"angle": -22.5, "axis": "x", "origin": [12.75, 13, 8]}),
        el("feather_tip", [12.45, 12.9, 15], [13.05, 14.5, 17.5], "feather_tip",
           rot={"angle": -22.5, "axis": "x", "origin": [12.75, 13, 8]}),
    ]


def head_hexbinder():
    return [
        el("brim", [0, 11.5, 0], [16, 12.5, 16], "felt_d"),
        el("band", [3.5, 12.5, 3.5], [12.5, 14, 12.5], "gold"),
        el("cone1", [4, 14, 4], [12, 18, 12], "felt", {"north": "felt_star"}),
        el("cone2", [5, 18, 5], [11, 21, 11], "felt"),
        el("cone3", [6, 21, 6.5], [10, 24, 10.5], "felt"),
        el("cone4", [6.75, 24, 7.5], [9.25, 26, 10], "felt_d"),
        el("tip", [7.25, 25, 10], [8.75, 26.5, 13], "felt", rot={"angle": -22.5, "axis": "x", "origin": [8, 25.5, 10]}),
    ]


def head_shade_reaper():
    side = el("side", [12, 2.5, 1.5], [13, 12.5, 12], "robe")
    return [
        el("top", [3, 12.5, 1.5], [13, 13.5, 13], "robe"),
        el("back", [3, 2.5, 12], [13, 12.5, 13], "robe"),
        side,
        mirror(side),
        el("brow", [3, 10, 1.5], [13, 12.5, 3], "robe", {"down": "shadow"}),
        el("peak", [6.5, 12.5, 11], [9.5, 15, 13], "robe_d"),
    ]


def head_death_rider():
    corners = [
        el("spike_corner", [3.25, 13, 3.25], [4.75, 15, 4.75], "iron_l"),
        el("spike_corner_b", [3.25, 13, 11.25], [4.75, 15, 12.75], "iron_l"),
        el("spike_side", [3.25, 13, 7], [4.25, 14.5, 9], "iron_l"),
    ]
    return [
        el("ring", [3.25, 11, 3.25], [12.75, 13, 12.75], "iron", {"north": "iron_gem"}),
        el("spike_front", [7, 13, 3.25], [9, 16.5, 4.25], "iron_l"),
        el("spike_back", [7, 13, 11.75], [9, 16, 12.75], "iron_l"),
    ] + corners + [mirror(e) for e in corners]


def staff_magus():
    """Blaze staff for the Magus (shown on its "Super Cute Sword" stone sword).
    Built upright, then every part is tilted -45 degrees so it lies along the same diagonal
    as a vanilla handheld item and uses the same hand transforms."""
    tilt = {"angle": -45, "axis": "z", "origin": [8, 8, 8]}
    parts = [
        el("butt", [7.25, -2, 7.25], [8.75, -1, 8.75], "gold"),
        el("shaft", [7.5, -1, 7.5], [8.5, 15, 8.5], "shaft"),
        el("grip", [7.3, 2, 7.3], [8.7, 5, 8.7], "leather"),
        el("ring", [7.2, 14, 7.2], [8.8, 15, 8.8], "gold"),
        el("claw_w", [6.6, 15, 7.6], [7.4, 18.5, 8.4], "gold"),
        el("claw_e", [8.6, 15, 7.6], [9.4, 18.5, 8.4], "gold"),
        el("claw_n", [7.6, 15, 6.6], [8.4, 18.5, 7.4], "gold"),
        el("claw_s", [7.6, 15, 8.6], [8.4, 18.5, 9.4], "gold"),
        el("core", [7.1, 15.5, 7.1], [8.9, 18.5, 8.9], "blaze"),
        el("spark", [7.6, 18.5, 7.6], [8.4, 19.5, 8.4], "blaze_l"),
    ]
    for p in parts:
        p["rot"] = dict(tilt)
    return parts


# Same as vanilla item/handheld, so the staff sits in the hand like a sword or rod
HANDHELD_DISPLAY = {
    "thirdperson_righthand": {"rotation": [0, -90, 55], "translation": [0, 4.0, 0.5], "scale": [0.85, 0.85, 0.85]},
    "thirdperson_lefthand": {"rotation": [0, 90, -55], "translation": [0, 4.0, 0.5], "scale": [0.85, 0.85, 0.85]},
    "firstperson_righthand": {"rotation": [0, -90, 25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
    "firstperson_lefthand": {"rotation": [0, 90, -25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
    "gui": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]},
    "ground": {"rotation": [0, 0, 0], "translation": [0, 2, 0], "scale": [0.5, 0.5, 0.5]},
}


HEADS = {
    "bone_knight": head_bone_knight,
    "soul_archer": head_soul_archer,
    "hexbinder": head_hexbinder,
    "shade_reaper": head_shade_reaper,
    "death_rider": head_death_rider,
}

MATERIALS = {
    "steel": hexc("#34363b"), "steel_d": hexc("#1f2024"), "trim": hexc("#8a8478"),
    "cap": hexc("#1f4a48"), "cap_d": hexc("#153432"), "leather": hexc("#5a3b22"),
    "feather": hexc("#4fd8e8"), "feather_tip": hexc("#e8f8fa"),
    "felt": hexc("#3d1f52"), "felt_d": hexc("#26123a"), "gold": hexc("#e8c34f"),
    "robe": hexc("#24242c"), "robe_d": hexc("#16161b"), "shadow": hexc("#060608"),
    "iron": hexc("#26272b"), "iron_l": hexc("#3a3c42"), "soul": hexc("#4fd8e8"),
    "shaft": hexc("#2a1f1a"), "blaze": hexc("#ff9a1f"), "blaze_l": hexc("#ffe27a"),
}


def face_pixel(mat, x, y, w, h, rng):
    """Color of one texel of a face. A few materials draw details."""
    if mat == "visor":  # great helm front: T-shaped slit + breathing holes
        if y == 4 and 1 <= x <= w - 2 or x in (w // 2 - 1, w // 2) and 4 <= y <= 7:
            return hexc("#050505")
        if y >= 6 and x in (1, 2, w - 3, w - 2) and y % 2 == 0:
            return hexc("#141416")
        return MATERIALS["trim"] if y == 0 else MATERIALS["steel"]
    if mat == "cap_band":  # leather band around the bottom of the cap
        return MATERIALS["leather"] if y == h - 1 else shade(MATERIALS["cap"], 1 + rng.uniform(-0.07, 0.07))
    if mat == "feather":  # cyan vane with a pale quill down the middle
        return MATERIALS["feather_tip"] if h >= 3 and y == h // 2 else shade(MATERIALS["feather"], 1 + rng.uniform(-0.1, 0.1))
    if mat == "felt_star":
        if (x, y) in {(3, 1), (4, 1), (2, 2), (3, 2), (4, 2), (5, 2), (3, 3), (4, 3)}:
            return MATERIALS["gold"]
        mat = "felt"
    if mat == "iron_gem":
        if y in (0, h - 1):
            return MATERIALS["iron_l"]
        if x % 3 == 1 and y == 1:
            return MATERIALS["soul"]
        mat = "iron"
    c = MATERIALS[mat]
    if w > 2 and h > 2 and edge(x, y, w, h):
        c = shade(c, 0.82)
    return shade(c, 1 + rng.uniform(-0.07, 0.07))


FACE_DIMS = {"north": (0, 1), "south": (0, 1), "east": (2, 1), "west": (2, 1), "up": (0, 2), "down": (0, 2)}


def model_json(name, elements, display=None):
    return {
        "textures": {"0": f"wither:item/variant/{name}", "particle": f"wither:item/variant/{name}"},
        "elements": elements,
        "display": display or {"head": {"scale": [1.6, 1.6, 1.6]}},
    }


def build_head(name, elems, display=None):
    rng = random.Random(name)
    img = Image.new("RGBA", (TEX, TEX), (0, 0, 0, 0))
    cur_x = cur_y = row_h = 0
    out = []
    for e in elems:
        size = [e["to"][i] - e["from"][i] for i in range(3)]
        jfaces = {}
        for face, (ax_w, ax_h) in FACE_DIMS.items():
            w, h = max(1, round(size[ax_w])), max(1, round(size[ax_h]))
            if cur_x + w > TEX:
                cur_x, cur_y, row_h = 0, cur_y + row_h, 0
            if cur_y + h > TEX:
                sys.exit(f"{name}: head texture atlas full")
            mat = e["faces_mat"].get(face, e["mat"])
            for y in range(h):
                for x in range(w):
                    img.putpixel((cur_x + x, cur_y + y), face_pixel(mat, x, y, w, h, rng))
            k = 16 / TEX
            jfaces[face] = {"uv": [cur_x * k, cur_y * k, (cur_x + w) * k, (cur_y + h) * k], "texture": "#0"}
            cur_x += w
            row_h = max(row_h, h)
        je = {"name": e["name"], "from": e["from"], "to": e["to"], "faces": jfaces}
        if e["rot"]:
            je["rotation"] = e["rot"]
        out.append(je)
    return model_json(name, out, display), img


def box_faces(u, v, w, h, d, k=0.25):
    """Entity-style box UV (as used by the Wither model) -> item model faces. k = UV units per texel."""
    def r(x0, y0, x1, y1):
        return {"uv": [x0 * k, y0 * k, x1 * k, y1 * k], "texture": "#0"}
    return {
        "up": r(u + d, v, u + d + w, v + d),
        "down": r(u + d + w, v, u + d + 2 * w, v + d),
        "west": r(u, v + d, u + d, v + d + h),
        "north": r(u + d, v + d, u + d + w, v + d + h),
        "east": r(u + d + w, v + d, u + 2 * d + w, v + d + h),
        "south": r(u + 2 * d + w, v + d, u + 2 * d + 2 * w, v + d + h),
    }


def build_triskull(jar):
    """The Wither's two side heads and shoulder bar, placed exactly like on the Wither
    (side heads 9px out and 3px lower than the middle head), using the Wither's texture."""
    tex = vanilla_png(jar, "assets/minecraft/textures/entity/wither/wither.png")
    elements = [
        {"name": "shoulders", "from": [-2, 1.1, 7.5], "to": [18, 4.1, 10.5], "faces": box_faces(0, 16, 20, 3, 3)},
        {"name": "right_head", "from": [-4, 2, 5], "to": [2, 8, 11], "faces": box_faces(32, 0, 6, 6, 6)},
        {"name": "left_head", "from": [14, 2, 5], "to": [20, 8, 11], "faces": box_faces(32, 0, 6, 6, 6)},
    ]
    return model_json("triskull", elements), tex


# =============================================================== withered steed
def build_steed(jar):
    horse = vanilla_png(jar, "assets/minecraft/textures/entity/horse/horse_skeleton.png")
    saddle = vanilla_png(jar, "assets/minecraft/textures/entity/equipment/skeleton_horse_saddle/saddle.png")
    out = Image.new("RGBA", horse.size, (0, 0, 0, 0))
    for y in range(horse.height):
        for x in range(horse.width):
            r, g, b, a = horse.getpixel((x, y))
            if a:
                # Map the pale skeleton greys (13..227) onto the wither skeleton range (10..82)
                lum = (r + g + b) / 3
                v = int(10 + max(0, lum - 13) / 214 * 72)
                out.putpixel((x, y), (v, v, v, a))
            r, g, b, a = saddle.getpixel((x, y))
            if a:
                out.putpixel((x, y), (int(r * 0.35), int(g * 0.3), int(b * 0.3), a))
    return horse, out



# =============================================================== homing skull (animated)
VANILLA_PLAYER_HEAD = {
    "type": "minecraft:special", "base": "minecraft:item/template_skull", "model": {"type": "minecraft:player_head"},
    "transformation": {"left_rotation": [1.0, 0.0, 0.0, -0.0], "right_rotation": [0.0, 0.0, 0.0, 1.0],
                       "scale": [1.0, 1.0, 1.0], "translation": [0.5, 0.0, 0.5]},
}


def homing_skull_texture(jar):
    """The vanilla wither skeleton skull, with only the eyes recolored.
    32x64: two 32x32 frames (red eyes, white eyes), the head's box UV in the top 32x16 of each."""
    skull = vanilla_png(jar, "assets/minecraft/textures/entity/skeleton/wither_skeleton.png").crop((0, 0, 32, 16))
    img = Image.new("RGBA", (32, 64), (0, 0, 0, 0))
    eyes = [(1, 4), (2, 4), (5, 4), (6, 4)]  # the black eye pixels on the face (face starts at 8,8)
    # The vanilla texture leaves gaps in the bottom face; fill them so the skull's underside is solid
    for y in range(16):
        for x in range(32):
            on_face = 8 <= x < 24 if y < 8 else True
            if on_face and skull.getpixel((x, y))[3] == 0:
                skull.putpixel((x, y), hexc("#1a1a1a"))
    for frame, eye in enumerate([hexc("#ff1a1a"), hexc("#ffffff")]):
        img.alpha_composite(skull, (0, frame * 32))
        for x, y in eyes:
            img.putpixel((8 + x, 8 + y + frame * 32), eye)
    return img


def homing_skull_model():
    faces = box_faces(0, 0, 8, 8, 8, k=0.5)
    return {
        "textures": {"0": "wither:item/variant/homing_skull", "particle": "wither:item/variant/homing_skull"},
        "elements": [{"name": "skull", "from": [4, 4, 4], "to": [12, 12, 12], "faces": faces}],
        "display": {"fixed": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]},
                    "head": {"scale": [1.6, 1.6, 1.6]}},
    }


# =============================================================== Wither midpoint cracks
def wither_cracks():
    """Replaces the Wither's half-health overlay (vanilla: a blue energy swirl) with glowing soul-fire cracks.
    The game draws this layer additively and slowly drifts it, so black = nothing, bright = glowing fissure."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 255))
    rng = random.Random("cracks")
    core, mid, outer = (230, 255, 255), (80, 220, 235), (20, 90, 110)
    for _ in range(14):
        x, y = rng.randrange(64), rng.randrange(64)
        dx, dy = rng.choice([(1, 0), (0, 1), (1, 1), (1, -1)])
        for _ in range(rng.randrange(8, 20)):
            for (ox, oy), col in (((0, 0), core), ((1, 0), mid), ((0, 1), mid)):
                px, py = (x + ox) % 64, (y + oy) % 64
                r, g, b, _a = img.getpixel((px, py))
                img.putpixel((px, py), (max(r, col[0]), max(g, col[1]), max(b, col[2]), 255))
            for ox, oy in ((-1, 0), (0, -1), (2, 0), (0, 2)):
                px, py = (x + ox) % 64, (y + oy) % 64
                r, g, b, _a = img.getpixel((px, py))
                img.putpixel((px, py), (max(r, outer[0]), max(g, outer[1]), max(b, outer[2]), 255))
            if rng.random() < 0.3:  # jagged turns
                dx, dy = rng.choice([(1, 0), (0, 1), (1, 1), (1, -1), (-1, 1)])
            x, y = x + dx, y + dy
    return img

# =============================================================== previews
def head_front(model, tex, behind):
    """Rough front view of a head model (rotations ignored), 1px per unit.
    behind=True draws only the parts starting behind the face (drawn before the skull)."""
    canvas = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
    k = tex.width / 16
    for e in sorted(model["elements"], key=lambda e: -e["from"][2]):
        if (e["from"][2] >= 4) != behind:
            continue
        u0, v0, u1, v1 = (int(round(c * k)) for c in e["faces"]["north"]["uv"])
        face = tex.crop((u0, v0, max(u1, u0 + 1), max(v1, v0 + 1)))
        w = max(1, round(e["to"][0] - e["from"][0]))
        h = max(1, round(e["to"][1] - e["from"][1]))
        canvas.alpha_composite(face.resize((w, h), Image.NEAREST), (round(e["from"][0]) + 12, round(28 - e["to"][1])))
    return canvas


def preview(head_back, head_front_img):
    img = Image.new("RGBA", (40, 52), (0, 0, 0, 0))
    img.alpha_composite(head_back, (0, 4))
    bone, chest = (38, 38, 38, 255), (52, 46, 50, 255)
    ox, oy = 12, 20
    for (x, y, w, h, c) in [(4, 0, 8, 8, bone), (5, 8, 6, 12, bone), (2, 8, 2, 12, bone), (12, 8, 2, 12, bone),
                            (5, 20, 2, 12, bone), (9, 20, 2, 12, bone), (3, 8, 10, 7, chest)]:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                img.putpixel((ox + xx, oy + yy), c)
    for (ex, ey) in [(6, 4), (9, 4)]:
        img.putpixel((ox + ex, oy + ey), (5, 5, 5, 255))
    img.alpha_composite(head_front_img, (0, 4))
    return img.resize((img.width * 7, img.height * 7), Image.NEAREST)


# =============================================================== main
def main():
    jar = find_jar()
    if not jar:
        sys.exit("Minecraft client jar not found; pass its path as the first argument")
    previews, cases = [], []
    for name in VARIANTS:
        model, tex = build_triskull(jar) if name == "triskull" else build_head(name, HEADS[name]())
        save(tex, "assets", "wither", "textures", "item", "variant", f"{name}.png")
        save_json(model, "assets", "wither", "models", "item", "variant", f"{name}.json")
        cases.append({"when": f"wither:{name}", "model": {"type": "minecraft:model", "model": f"wither:item/variant/{name}"}})
        previews.append(preview(head_front(model, tex, True), head_front(model, tex, False)))
        print("generated", name)

    # Hats are worn on an item whose model is "air": vanilla draws nothing,
    # this pack draws the model matching the item's custom_model_data string.
    save_json({"model": {"type": "minecraft:select", "property": "minecraft:custom_model_data", "index": 0,
                         "cases": cases, "fallback": {"type": "minecraft:model", "model": "minecraft:item/air"}}},
              "assets", "minecraft", "items", "air.json")

    # The Magus's "Super Cute Sword" stone sword shows as a blaze staff; any other stone sword stays vanilla
    model, tex = build_head("magus_staff", staff_magus(), HANDHELD_DISPLAY)
    save(tex, "assets", "wither", "textures", "item", "variant", "magus_staff.png")
    save_json(model, "assets", "wither", "models", "item", "variant", "magus_staff.json")
    save_json({"model": {"type": "minecraft:select", "property": "minecraft:custom_model_data", "index": 0,
                         "cases": [{"when": "wither:magus_staff",
                                    "model": {"type": "minecraft:model", "model": "wither:item/variant/magus_staff"}}],
                         "fallback": {"type": "minecraft:model", "model": "minecraft:item/stone_sword"}}},
              "assets", "minecraft", "items", "stone_sword.json")
    print("generated magus_staff")

    # Homing skull: flashing red/white eyes on the homing missile only (other player heads stay vanilla)
    tex = homing_skull_texture(jar)
    save(tex, "assets", "wither", "textures", "item", "variant", "homing_skull.png")
    save_json({"animation": {"frametime": 3}}, "assets", "wither", "textures", "item", "variant", "homing_skull.png.mcmeta")
    save_json(homing_skull_model(), "assets", "wither", "models", "item", "variant", "homing_skull.json")
    save_json({"model": {"type": "minecraft:select", "property": "minecraft:custom_model_data", "index": 0,
                         "cases": [{"when": "wither:homing_skull",
                                    "model": {"type": "minecraft:model", "model": "wither:item/variant/homing_skull"}}],
                         "fallback": VANILLA_PLAYER_HEAD}},
              "assets", "minecraft", "items", "player_head.json")
    save(tex.resize((tex.width * 8, tex.height * 8), Image.NEAREST), "tools", "preview", "homing_skull.png")
    print("generated homing_skull")

    # Wither: glowing cracks once it drops to half health (replaces the blue swirl)
    cracks = wither_cracks()
    save(cracks, "assets", "minecraft", "textures", "entity", "wither", "wither_armor.png")
    save(cracks.resize((512, 512), Image.NEAREST), "tools", "preview", "wither_cracks.png")
    print("generated wither_armor (midpoint cracks)")

    vanilla, black = build_steed(jar)
    save(black, "assets", "wither", "textures", "entity", "equipment", "skeleton_horse_saddle", "wither_steed.png")
    save_json({"layers": {"skeleton_horse_saddle": [{"texture": "wither:wither_steed"}]}},
              "assets", "wither", "equipment", "wither_steed.json")
    cmp_img = Image.new("RGBA", (64 * 2 + 4, 64), (90, 140, 90, 255))
    cmp_img.alpha_composite(vanilla, (0, 0))
    cmp_img.alpha_composite(black, (68, 0))
    save(cmp_img.resize((cmp_img.width * 6, cmp_img.height * 6), Image.NEAREST), "tools", "preview", "wither_steed.png")
    print("generated wither_steed")

    for old in glob.glob(os.path.join(ROOT, "tools", "preview", "*.png")):
        if os.path.basename(old) not in ("all_variants.png", "wither_steed.png", "homing_skull.png", "wither_cracks.png"):
            os.remove(old)
    w = sum(p.width for p in previews) + 16 * (len(previews) + 1)
    sheet = Image.new("RGBA", (w, previews[0].height + 32), (120, 120, 130, 255))
    x = 16
    for p in previews:
        sheet.alpha_composite(p, (x, 16))
        x += p.width + 16
    save(sheet, "tools", "preview", "all_variants.png")


if __name__ == "__main__":
    main()
