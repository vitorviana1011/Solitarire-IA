import io
import os
import sys

import pygame
from cairosvg import svg2png

import card

card_svgs = None
icon_svgs = None
back_svg = None
empty_svg = None

card_surfaces: dict[str, pygame.Surface] = None
icon_surfaces: dict[str, pygame.Surface] = None
back_surface: pygame.Surface = None
empty_surface: pygame.Surface = None


def get_icon():
    return render_svg(load_svg("icon.svg"), 1, False)


def load_svgs():
    global card_svgs, icon_svgs, back_svg, empty_svg
    card_svgs = {(suit, symbol): load_svg(f"{suit.value}_{symbol.value}.svg") for suit in card.Suit for symbol in card.Symbol}
    icon_svgs = {file.removesuffix(".svg"): load_svg(os.path.join("icons", file)) for file in os.listdir(normalize_path("icons")) if file.endswith(".svg")}
    back_svg = load_svg("back.svg")
    empty_svg = load_svg("empty.svg")


def render_svgs(scale):
    global card_surfaces, icon_surfaces, back_surface, empty_surface
    card_surfaces = {k: render_svg(v, scale) for k, v in card_svgs.items()}
    icon_surfaces = {k: render_svg(v, scale) for k, v in icon_svgs.items()}
    back_surface = render_svg(back_svg, scale)
    empty_surface = render_svg(empty_svg, scale)


def normalize_path(file):
    dir = getattr(sys, "_MEIPASS", "")
    return os.path.join(dir, "assets", file)


def load_svg(file_path):
    with open(normalize_path(file_path), "rb") as f:
        return f.read()  # raw SVG bytes


def render_svg(svg_bytes, scale=1.0, convert=True):
    """
    Render SVG bytes to a Pygame surface.

    Parameters:
    - svg_bytes: bytes object containing SVG
    - scale: float, scaling factor
    - convert: whether to call convert_alpha() on the surface

    Returns:
    - pygame.Surface
    """
    # Render SVG to PNG bytes in memory
    png_bytes = svg2png(bytestring=svg_bytes, scale=scale, dpi=96)

    # Load PNG bytes into Pygame
    buffer = io.BytesIO(png_bytes)
    surface = pygame.image.load(buffer, "image.png")
    if convert:
        surface = surface.convert_alpha()
    return surface
