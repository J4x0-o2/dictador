from PIL import Image, ImageDraw

COLORS = {
    "loading": (245, 158, 11),
    "idle": (59, 130, 246),
    "recording": (239, 68, 68),
    "paused": (156, 163, 175),
}


def make_icon(state, size=64):
    """Draw a microphone glyph tinted with the color of the given state."""
    color = COLORS[state]
    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((22, 4, 42, 38), radius=10, fill=color)
    draw.arc((14, 18, 50, 48), start=0, end=180, fill=color, width=4)
    draw.line((32, 48, 32, 56), fill=color, width=4)
    draw.line((22, 58, 42, 58), fill=color, width=4)
    return image if size == 64 else image.resize((size, size), Image.LANCZOS)
