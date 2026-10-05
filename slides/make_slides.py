"""Render a Markdown deck into a 16:9 PDF meant for a projector.

Run from the repository root:

    uv run python slides/make_slides.py slides/deck.md
    uv run python slides/make_slides.py slides/deck.md -o /tmp/talk.pdf --png

The page is 13.333 x 7.5 in -- PowerPoint's widescreen size, which is exactly
1920 x 1080 at 144 dpi, so the PDF fills a 1080p projector with no letterboxing.
Text stays vector; only bitmap images are rasterised.

The supported Markdown is deliberately small; see slides/README.md. Nothing is
invented: every slide shows exactly the blocks written in the source file, and
the only automatic decision is the layout (title / section / content), inferred
from what the slide contains.

Code, identifiers and comments are English, like the rest of the software.
Slide content is whatever the Markdown says.
"""

import argparse
import os
import re
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

# --------------------------------------------------------------------------
# Page geometry and style
# --------------------------------------------------------------------------

DPI = 144
PAGE_W_IN, PAGE_H_IN = 1920 / DPI, 1080 / DPI  # 16:9, PowerPoint's widescreen page
IN_PER_PT = 1.0 / 72.0

MARGIN_L = 0.068  # figure fractions
MARGIN_R = 0.068
MARGIN_T = 0.085
MARGIN_B = 0.090

THEMES = {
    "light": {
        "bg": "#FCFCFA",
        "ink": "#121A21",
        "body": "#333F4B",
        "muted": "#7C8894",
        "accent": "#0B6E8F",
        "accent2": "#C2592E",
        "rule": "#D7DDE3",
        "code_bg": "#EFF2F4",
        "img_bg": "#FFFFFF",
    },
    "dark": {
        "bg": "#0F1720",
        "ink": "#F3F6F8",
        "body": "#C8D3DC",
        "muted": "#7E8C99",
        "accent": "#4CC3E8",
        "accent2": "#F0905A",
        "rule": "#28343F",
        "code_bg": "#18222C",
        "img_bg": "#FFFFFF",
    },
}

FONT_TITLE = "Inter Display"
FONT_BODY = "Inter"
FONT_MONO = "Source Code Pro"

# Point sizes, chosen for a 7.5 in tall page (so they match PowerPoint's).
SIZES = {
    "deck_title": 58,
    "deck_subtitle": 27,
    "deck_meta": 18,
    "section": 50,
    "title": 40,
    "kicker": 23,
    "h3": 27,
    "body": 25,
    "bullet": 25,
    "bullet2": 21,
    "quote": 29,
    "code": 18,
    "caption": 15,
    "footer": 12,
}

LINE_SPACING = 1.33  # multiple of the font size
BLOCK_GAP = 0.030  # vertical gap between blocks, figure fractions
CAPTION_GAP = 0.014  # between an image and its caption
MIN_IMG_H = 0.22  # an image never gets squeezed below this, text shrinks instead


def pt_to_frac_h(points):
    """Convert a point size to a fraction of the page height."""
    return points * IN_PER_PT / PAGE_H_IN


def pt_to_frac_w(points):
    """Convert a point size to a fraction of the page width."""
    return points * IN_PER_PT / PAGE_W_IN


# --------------------------------------------------------------------------
# Markdown parsing
# --------------------------------------------------------------------------

SLIDE_SEP = re.compile(r"^-{3,}\s*$")
COMMENT = re.compile(r"<!--(.*?)-->", re.S)
DIRECTIVE = re.compile(r"^\s*(layout|notes?)\s*:\s*(.*?)\s*$", re.I)
IMAGE = re.compile(r"^!\[(?P<alt>.*?)\]\((?P<src>[^)]+)\)\s*$")
BULLET = re.compile(r"^(?P<indent>\s*)[-*+]\s+(?P<text>.*)$")
NUMBERED = re.compile(r"^(?P<indent>\s*)(?P<num>\d+)[.)]\s+(?P<text>.*)$")
QUOTE = re.compile(r"^>\s?(?P<text>.*)$")
FENCE = re.compile(r"^\s*```")


def parse_front_matter(lines):
    """Pull an optional YAML-ish header off the top of the file."""
    meta = {}
    if not lines or not SLIDE_SEP.match(lines[0]):
        return meta, lines
    for end in range(1, len(lines)):
        if SLIDE_SEP.match(lines[end]):
            break
    else:
        return meta, lines
    for line in lines[1:end]:
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip().lower()] = value.strip()
    return meta, lines[end + 1 :]


def split_slides(lines):
    """Split the body into slides on a bare `---` line (outside code fences)."""
    slides, current, in_code = [], [], False
    for line in lines:
        if FENCE.match(line):
            in_code = not in_code
        if not in_code and SLIDE_SEP.match(line):
            slides.append(current)
            current = []
        else:
            current.append(line)
    slides.append(current)
    return [s for s in slides if any(line.strip() for line in s)]


def parse_inline(text):
    """Split one line into styled spans.

    Styles: "" plain, "b" bold, "i" italic, "bi" both, "code", "math".
    `$...$` is handed to matplotlib's mathtext verbatim.
    """
    spans, pos = [], 0
    pattern = re.compile(
        r"(?P<code>`[^`]+`)"
        r"|(?P<math>\$[^$]+\$)"
        r"|(?P<bi>\*\*\*[^*]+\*\*\*)"
        r"|(?P<b>\*\*[^*]+\*\*)"
        r"|(?P<i>(?<!\*)\*(?!\*)[^*]+\*(?!\*)|_[^_]+_)"
    )
    for m in pattern.finditer(text):
        if m.start() > pos:
            spans.append((text[pos : m.start()], ""))
        kind = m.lastgroup
        raw = m.group()
        if kind == "code":
            spans.append((raw[1:-1], "code"))
        elif kind == "math":
            spans.append((raw, "math"))
        elif kind == "bi":
            spans.append((raw[3:-3], "bi"))
        elif kind == "b":
            spans.append((raw[2:-2], "b"))
        else:
            spans.append((raw[1:-1], "i"))
        pos = m.end()
    if pos < len(text):
        spans.append((text[pos:], ""))
    return [(t, s) for t, s in spans if t]


def parse_blocks(lines):
    """Turn one slide's lines into a list of blocks, plus its directives."""
    blocks, directives = [], {}

    # Directives and notes live in HTML comments; strip them out first.
    text = "\n".join(lines)
    for body in COMMENT.findall(text):
        for line in body.strip().splitlines():
            m = DIRECTIVE.match(line)
            if m:
                directives[m.group(1).lower().rstrip("s")] = m.group(2)
    lines = COMMENT.sub("", text).splitlines()

    para, quote, code, images = [], [], None, []

    def flush():
        nonlocal para, quote, images
        if para:
            blocks.append({"kind": "para", "spans": parse_inline(" ".join(para))})
            para = []
        if quote:
            blocks.append({"kind": "quote", "spans": parse_inline(" ".join(quote))})
            quote = []
        if images:
            blocks.append({"kind": "images", "items": images})
            images = []

    for line in lines:
        if code is not None:
            if FENCE.match(line):
                blocks.append({"kind": "code", "lines": code})
                code = None
            else:
                code.append(line.rstrip())
            continue
        if FENCE.match(line):
            flush()
            code = []
            continue

        stripped = line.strip()
        if not stripped:
            flush()
            continue

        m = IMAGE.match(stripped)
        if m:
            if para or quote:
                flush()
            images.append({"src": m.group("src"), "caption": m.group("alt")})
            continue

        if images:
            flush()

        if stripped.startswith("### "):
            flush()
            blocks.append({"kind": "h3", "spans": parse_inline(stripped[4:].strip())})
            continue
        if stripped.startswith("## "):
            flush()
            blocks.append({"kind": "h2", "spans": parse_inline(stripped[3:].strip())})
            continue
        if stripped.startswith("# "):
            flush()
            blocks.append({"kind": "h1", "spans": parse_inline(stripped[2:].strip())})
            continue

        m = QUOTE.match(stripped)
        if m:
            if para:
                flush()
            quote.append(m.group("text").strip())
            continue

        m = NUMBERED.match(line)
        if m:
            if para or quote:
                flush()
            level = len(m.group("indent")) // 2
            blocks.append(
                {
                    "kind": "item",
                    "level": level,
                    "marker": m.group("num") + ".",
                    "spans": parse_inline(m.group("text").strip()),
                }
            )
            continue

        m = BULLET.match(line)
        if m:
            if para or quote:
                flush()
            level = len(m.group("indent")) // 2
            blocks.append(
                {
                    "kind": "item",
                    "level": level,
                    "marker": None,
                    "spans": parse_inline(m.group("text").strip()),
                }
            )
            continue

        para.append(stripped)

    if code is not None:  # unterminated fence
        blocks.append({"kind": "code", "lines": code})
    flush()
    return blocks, directives


def infer_layout(blocks, directives, index):
    """Pick a layout when the slide does not ask for one."""
    if "layout" in directives:
        return directives["layout"].strip().lower()
    kinds = {b["kind"] for b in blocks}
    if kinds and kinds <= {"h1", "h2"}:
        return "title" if index == 0 else "section"
    if kinds == {"images"}:
        return "full"
    return "content"


# --------------------------------------------------------------------------
# Text measuring and rich-text drawing
# --------------------------------------------------------------------------


class Painter:
    """Measures and draws styled text on one figure, in figure fractions."""

    def __init__(self, fig, theme):
        self.fig = fig
        self.theme = theme
        self.renderer = fig.canvas.get_renderer()
        self.px_w = fig.get_figwidth() * fig.dpi
        self.px_h = fig.get_figheight() * fig.dpi
        self._cache = {}
        self._vcache = {}
        self.too_wide = False  # set by wrap() when an unbreakable token overflows

    def font(self, style, size, family=None, weight=None):
        kw = {
            "fontsize": size,
            "fontfamily": family or FONT_BODY,
            "fontweight": weight if weight is not None else 400,
            "fontstyle": "normal",
        }
        if style == "code":
            kw["fontfamily"] = FONT_MONO
            kw["fontsize"] = size * 0.92
        elif style in ("b", "bi"):
            kw["fontweight"] = 700
        if style in ("i", "bi"):
            kw["fontstyle"] = "italic"
        return kw

    def measure(self, text, style, size, family=None, weight=None):
        """Width of `text` as a fraction of the page width."""
        key = (text, style, round(size, 3), family, weight)
        if key not in self._cache:
            kw = self.font(style, size, family, weight)
            artist = self.fig.text(0, -1, text, **kw)
            box = artist.get_window_extent(renderer=self.renderer)
            artist.remove()
            self._cache[key] = box.width / self.px_w
        return self._cache[key]

    def measure_vertical(self, text, style, size, family=None, weight=None):
        """Ascent and descent about the baseline, as fractions of page height.

        A formula with a fraction and an exponent is two or three times taller
        than a line of text at the same point size, so the line box has to be
        measured, not assumed.
        """
        key = (text, style, round(size, 3), family, weight)
        if key not in self._vcache:
            kw = self.font(style, size, family, weight)
            artist = self.fig.text(0, 0.5, text, va="baseline", **kw)
            box = artist.get_window_extent(renderer=self.renderer)
            artist.remove()
            anchor = 0.5 * self.px_h
            self._vcache[key] = ((box.y1 - anchor) / self.px_h,
                                 (anchor - box.y0) / self.px_h)
        return self._vcache[key]

    def line_boxes(self, lines, size, family=None, weight=None):
        """Per line, (height above the baseline, advance to the next line)."""
        nominal = pt_to_frac_h(size)
        boxes = []
        for line in lines:
            ascent = descent = 0.0
            for word, style, _ in line:
                a, d = self.measure_vertical(word, style, size, family, weight)
                ascent, descent = max(ascent, a), max(descent, d)
            top = max(ascent + 0.10 * nominal, 0.78 * nominal)
            boxes.append((top, max(top + descent + 0.20 * nominal,
                                   LINE_SPACING * nominal)))
        return boxes

    def line_width(self, line, size, family=None, weight=None):
        if not line:
            return 0.0
        word, style, dx = line[-1]
        return dx + self.measure(word, style, size, family, weight)

    def space(self, size, family=None, weight=None):
        a = self.measure("x x", "", size, family, weight)
        b = self.measure("xx", "", size, family, weight)
        return max(a - b, pt_to_frac_w(size * 0.22))

    def tokenise(self, spans):
        """Flatten spans into (word, style, space_before) tokens."""
        tokens, pending_space = [], False
        for text, style in spans:
            if style == "math":
                tokens.append((text, style, pending_space))
                pending_space = False
                continue
            parts = re.split(r"(\s+)", text)
            for part in parts:
                if not part:
                    continue
                if part.isspace():
                    pending_space = True
                else:
                    tokens.append((part, style, pending_space))
                    pending_space = False
        return tokens

    def wrap(self, spans, max_w, size, family=None, weight=None):
        """Greedy word wrap. Returns a list of lines of (word, style, x) tuples."""
        space = self.space(size, family, weight)
        lines, line, x = [], [], 0.0
        for word, style, space_before in self.tokenise(spans):
            w = self.measure(word, style, size, family, weight)
            if w > max_w:
                # A single unbreakable token -- a long formula, a URL -- that no
                # amount of wrapping will fit. Report it so the caller shrinks.
                self.too_wide = True
            gap = space if (line and space_before) else 0.0
            if line and x + gap + w > max_w:
                lines.append(line)
                line, x = [], 0.0
                gap = 0.0
            line.append((word, style, x + gap))
            x += gap + w
        if line:
            lines.append(line)
        return lines

    def draw_lines(self, lines, x0, y_top, size, color, family=None, weight=None,
                   center_in=None):
        """Draw wrapped lines downward from `y_top`. Returns the height used.

        With `center_in` set to a width, each line is centred in a box of that
        width starting at x0, which is what a figure caption wants.
        """
        boxes = self.line_boxes(lines, size, family, weight)
        cursor = y_top
        for line, (top, advance) in zip(lines, boxes):
            baseline = cursor - top
            shift = 0.0
            if center_in is not None:
                shift = (center_in - self.line_width(line, size, family, weight)) / 2
            for word, style, dx in line:
                kw = self.font(style, size, family, weight)
                self.fig.text(
                    x0 + shift + dx,
                    baseline,
                    word,
                    color=self.theme["accent"] if style == "code" else color,
                    va="baseline",
                    ha="left",
                    **kw,
                )
            cursor -= advance
        return y_top - cursor

    def height_of(self, lines, size, family=None, weight=None):
        return sum(a for _, a in self.line_boxes(lines, size, family, weight))

    def first_baseline_drop(self, lines, size, family=None, weight=None):
        """How far below the block top the first baseline sits."""
        return self.line_boxes(lines, size, family, weight)[0][0]


# --------------------------------------------------------------------------
# Image helpers
# --------------------------------------------------------------------------


def load_image(src, base_dir):
    path = src if os.path.isabs(src) else os.path.join(base_dir, src)
    if not os.path.exists(path):
        raise FileNotFoundError(f"image not found: {src} (looked at {path})")
    data = plt.imread(path)
    return data, data.shape[1] / data.shape[0]


def place_image(fig, data, x, y, w, h, theme):
    """Draw an image in the box (x, y, w, h), preserving its aspect ratio."""
    ax = fig.add_axes([x, y, w, h], zorder=2)
    ax.imshow(data, interpolation="antialiased", aspect="auto")
    ax.set_axis_off()
    return ax


def caption_block(painter, caption, width):
    """Wrap a caption to `width`. Returns (lines, height); ([], 0) if there is none."""
    if not caption:
        return [], 0.0
    size = SIZES["caption"]
    lines = painter.wrap([(caption, "i")], width, size)
    return lines, painter.height_of(lines, size) + CAPTION_GAP


def columns_of(n, x0, total_w, gap):
    """Split a width into n equal columns, as (left edge, width) pairs."""
    width = (total_w - gap * (n - 1)) / n
    return [(x0 + i * (width + gap), width) for i in range(n)]


def draw_image_row(painter, theme, loaded, boxes, captions, columns, y_bottom, row_h):
    """One image per column, centred in it, with its caption centred underneath.

    Giving every image its own column is what keeps two captions from landing on
    top of each other: a caption is wrapped and centred in the column, never in
    the image, which may be much narrower than its column.
    """
    for ((data, _), _), (w, h), (lines, _), (x, col_w) in zip(
            loaded, boxes, captions, columns):
        y = y_bottom + (row_h - h) / 2
        place_image(painter.fig, data, x + (col_w - w) / 2, y, w, h, theme)
        if lines:
            painter.draw_lines(lines, x, y - CAPTION_GAP, SIZES["caption"],
                               theme["muted"], center_in=col_w)


def fit_box(aspect, max_w, max_h):
    """Largest (w, h) in figure fractions with the given pixel aspect ratio."""
    # w * PAGE_W_IN / (h * PAGE_H_IN) == aspect
    h = max_w * PAGE_W_IN / (aspect * PAGE_H_IN)
    if h <= max_h:
        return max_w, h
    w = max_h * aspect * PAGE_H_IN / PAGE_W_IN
    return w, max_h


# --------------------------------------------------------------------------
# Slide rendering
# --------------------------------------------------------------------------


def new_figure(theme):
    fig = plt.figure(figsize=(PAGE_W_IN, PAGE_H_IN), dpi=DPI)
    fig.patch.set_facecolor(theme["bg"])
    return fig


def draw_footer(painter, theme, footer, number, total, show_number=True):
    fig, size = painter.fig, SIZES["footer"]
    y = MARGIN_B * 0.46
    if footer:
        fig.text(
            MARGIN_L,
            y,
            footer,
            fontsize=size,
            fontfamily=FONT_BODY,
            color=theme["muted"],
            va="center",
            ha="left",
        )
    if show_number:
        fig.text(
            1 - MARGIN_R,
            y,
            f"{number} / {total}",
            fontsize=size,
            fontfamily=FONT_BODY,
            color=theme["muted"],
            va="center",
            ha="right",
        )


def render_title_slide(painter, theme, blocks, meta):
    fig = painter.fig
    content_w = 1 - MARGIN_L - MARGIN_R
    h1 = [b for b in blocks if b["kind"] == "h1"]
    h2 = [b for b in blocks if b["kind"] == "h2"]

    pieces = []
    for block in h1:
        size = SIZES["deck_title"]
        lines = painter.wrap(block["spans"], content_w, size, family=FONT_TITLE, weight=600)
        pieces.append((lines, size, theme["ink"], FONT_TITLE, 600, 0.040))
    for block in h2:
        size = SIZES["deck_subtitle"]
        lines = painter.wrap(block["spans"], content_w * 0.86, size, weight=400)
        pieces.append((lines, size, theme["body"], FONT_BODY, 400, 0.030))

    total_h = sum(painter.height_of(l, s, f, w) + gap
                  for l, s, _, f, w, gap in pieces)
    meta_line = " · ".join(v for v in (meta.get("author"), meta.get("date")) if v)
    if meta_line:
        total_h += 0.055 + pt_to_frac_h(SIZES["deck_meta"]) * LINE_SPACING

    y = 0.5 + total_h / 2
    for lines, size, color, family, weight, gap in pieces:
        used = painter.draw_lines(lines, MARGIN_L, y, size, color, family, weight)
        if family == FONT_TITLE:
            y -= used + gap * 0.45
            fig.add_artist(
                Rectangle(
                    (MARGIN_L, y + 0.012),
                    0.085,
                    0.0075,
                    facecolor=theme["accent"],
                    edgecolor="none",
                    transform=fig.transFigure,
                )
            )
            y -= gap * 0.55
        else:
            y -= used + gap
    if meta_line:
        fig.text(
            MARGIN_L,
            y - 0.030,
            meta_line,
            fontsize=SIZES["deck_meta"],
            fontfamily=FONT_BODY,
            color=theme["muted"],
            va="top",
            ha="left",
        )


def render_section_slide(painter, theme, blocks):
    fig = painter.fig
    content_w = 1 - MARGIN_L - MARGIN_R
    fig.add_artist(
        Rectangle(
            (0, 0),
            0.013,
            1,
            facecolor=theme["accent"],
            edgecolor="none",
            transform=fig.transFigure,
        )
    )
    pieces = []
    for block in blocks:
        if block["kind"] == "h1":
            size = SIZES["section"]
            pieces.append(
                (
                    painter.wrap(block["spans"], content_w * 0.9, size, FONT_TITLE, 600),
                    size,
                    theme["ink"],
                    FONT_TITLE,
                    600,
                )
            )
        elif block["kind"] == "h2":
            size = SIZES["kicker"]
            pieces.append(
                (painter.wrap(block["spans"], content_w * 0.8, size), size, theme["body"], FONT_BODY, 400)
            )
    total_h = sum(painter.height_of(l, s, f, w) for l, s, _, f, w in pieces) + 0.030 * (
        len(pieces) - 1)
    y = 0.5 + total_h / 2
    for lines, size, color, family, weight in pieces:
        y -= painter.draw_lines(lines, MARGIN_L + 0.012, y, size, color, family, weight) + 0.030


def render_full_slide(painter, theme, blocks, base_dir):
    """One or more images filling the slide, with optional captions."""
    fig = painter.fig
    items = [item for b in blocks if b["kind"] == "images" for item in b["items"]]
    loaded = [(load_image(it["src"], base_dir), it["caption"]) for it in items]
    n = len(loaded)
    gap = 0.025
    columns = columns_of(n, MARGIN_L, 1 - MARGIN_L - MARGIN_R, gap)
    col_w = columns[0][1]
    captions = [caption_block(painter, c, col_w) for _, c in loaded]
    cap = max((h for _, h in captions), default=0.0)
    avail_h = 1 - MARGIN_T * 0.55 - MARGIN_B - cap

    boxes = [fit_box(aspect, col_w, avail_h) for (_, aspect), _ in loaded]
    row_h = max(h for _, h in boxes)
    y_bottom = MARGIN_B + cap + (avail_h - row_h) / 2
    draw_image_row(painter, theme, loaded, boxes, captions, columns, y_bottom, row_h)


def layout_content(painter, theme, blocks, base_dir, scale):
    """Measure every block of a content slide; return a plan and its height.

    The plan is a list of callables-with-geometry, so the same measuring code
    decides the vertical centring and then the drawing.
    """
    fig = painter.fig
    content_w = 1 - MARGIN_L - MARGIN_R
    plan, total = [], 0.0

    for i, block in enumerate(blocks):
        kind = block["kind"]
        gap = BLOCK_GAP if plan else 0.0

        if kind == "h1":
            size = SIZES["title"] * scale
            lines = painter.wrap(block["spans"], content_w, size, FONT_TITLE, 600)
            h = painter.height_of(lines, size, FONT_TITLE, 600) + 0.034
            plan.append({"kind": "title", "lines": lines, "size": size, "h": h, "gap": 0.0})
            total += h
            continue

        if kind == "h2":
            size = SIZES["kicker"] * scale
            lines = painter.wrap(block["spans"], content_w, size, FONT_BODY, 500)
            h = painter.height_of(lines, size, FONT_BODY, 500)
            plan.append(
                {
                    "kind": "text",
                    "lines": lines,
                    "size": size,
                    "color": theme["accent"],
                    "family": FONT_BODY,
                    "weight": 500,
                    "x": MARGIN_L,
                    "h": h,
                    "gap": gap * 0.5,
                }
            )
            total += h + gap * 0.5
            continue

        if kind == "h3":
            size = SIZES["h3"] * scale
            lines = painter.wrap(block["spans"], content_w, size, FONT_BODY, 600)
            h = painter.height_of(lines, size, FONT_BODY, 600)
            plan.append(
                {
                    "kind": "text",
                    "lines": lines,
                    "size": size,
                    "color": theme["ink"],
                    "family": FONT_BODY,
                    "weight": 600,
                    "x": MARGIN_L,
                    "h": h,
                    "gap": gap,
                }
            )
            total += h + gap
            continue

        if kind == "para":
            size = SIZES["body"] * scale
            lines = painter.wrap(block["spans"], content_w, size)
            h = painter.height_of(lines, size)
            plan.append(
                {
                    "kind": "text",
                    "lines": lines,
                    "size": size,
                    "color": theme["body"],
                    "family": FONT_BODY,
                    "weight": 400,
                    "x": MARGIN_L,
                    "h": h,
                    "gap": gap,
                }
            )
            total += h + gap
            continue

        if kind == "item":
            level = min(block["level"], 2)
            size = (SIZES["bullet"] if level == 0 else SIZES["bullet2"]) * scale
            indent = MARGIN_L + 0.030 + level * 0.038
            text_x = indent + pt_to_frac_w(size) * 1.25
            lines = painter.wrap(block["spans"], 1 - MARGIN_R - text_x, size)
            h = painter.height_of(lines, size)
            # Tighter gap between consecutive items.
            prev_item = plan and plan[-1]["kind"] == "bullet"
            g = pt_to_frac_h(size) * 0.42 if prev_item else gap
            plan.append(
                {
                    "kind": "bullet",
                    "lines": lines,
                    "size": size,
                    "level": level,
                    "marker": block["marker"],
                    "mx": indent,
                    "x": text_x,
                    "h": h,
                    "gap": g,
                }
            )
            total += h + g
            continue

        if kind == "quote":
            size = SIZES["quote"] * scale
            x = MARGIN_L + 0.030
            lines = painter.wrap(block["spans"], 1 - MARGIN_R - x - 0.04, size, FONT_BODY, 400)
            h = painter.height_of(lines, size, FONT_BODY, 400)
            plan.append({"kind": "quote", "lines": lines, "size": size, "x": x, "h": h, "gap": gap})
            total += h + gap
            continue

        if kind == "code":
            size = SIZES["code"] * scale
            pad = 0.018
            step = pt_to_frac_h(size) * 1.30
            h = step * len(block["lines"]) + pad * 2
            plan.append(
                {"kind": "code", "lines": block["lines"], "size": size, "pad": pad, "h": h, "gap": gap}
            )
            total += h + gap
            continue

        if kind == "images":
            loaded = [(load_image(it["src"], base_dir), it["caption"]) for it in block["items"]]
            # Books a floor here; draw_content hands it whatever the text leaves
            # over. Booking it means the fit test below sees the image's cost.
            plan.append({"kind": "images", "loaded": loaded, "h": MIN_IMG_H, "gap": gap})
            total += MIN_IMG_H + gap
            continue

    return plan, total


def draw_content(painter, theme, plan, total_h, base_dir):
    fig = painter.fig
    content_w = 1 - MARGIN_L - MARGIN_R
    top = 1 - MARGIN_T
    bottom = MARGIN_B
    avail = top - bottom

    image_entries = [p for p in plan if p["kind"] == "images"]
    has_title = plan and plan[0]["kind"] == "title"

    if image_entries:
        # Images absorb the space the text does not use, on top of the floor
        # each one already booked in layout_content.
        spare = max(avail - total_h, 0.0)
        share = spare / len(image_entries)
        for entry in image_entries:
            n = len(entry["loaded"])
            gap = 0.022
            columns = columns_of(n, MARGIN_L, content_w, gap)
            box_w = columns[0][1]
            captions = [caption_block(painter, c, box_w) for _, c in entry["loaded"]]
            cap = max((h for _, h in captions), default=0.0)
            box_h = max(MIN_IMG_H + share - cap, 0.08)
            boxes = [fit_box(aspect, box_w, box_h) for (_, aspect), _ in entry["loaded"]]
            entry["boxes"] = boxes
            entry["columns"] = columns
            entry["cap"] = cap
            entry["captions"] = captions
            entry["h"] = max(h for _, h in boxes) + cap
        total_h = sum(p["h"] + p["gap"] for p in plan)

    # Vertical placement: titled slides hang from the top, untitled ones centre.
    if has_title or total_h > avail - 0.02:
        y = top
    else:
        y = top - max((avail - total_h) / 2 - 0.02, 0.0)

    for entry in plan:
        y -= entry["gap"]
        kind = entry["kind"]

        if kind == "title":
            used = painter.draw_lines(
                entry["lines"], MARGIN_L, y, entry["size"], theme["ink"], FONT_TITLE, 600
            )
            rule_y = y - used - 0.016
            fig.add_artist(
                Rectangle(
                    (MARGIN_L, rule_y),
                    0.072,
                    0.0070,
                    facecolor=theme["accent"],
                    edgecolor="none",
                    transform=fig.transFigure,
                )
            )
            y -= entry["h"]
            continue

        if kind == "text":
            painter.draw_lines(
                entry["lines"],
                entry["x"],
                y,
                entry["size"],
                entry["color"],
                entry["family"],
                entry["weight"],
            )
            y -= entry["h"]
            continue

        if kind == "bullet":
            size = entry["size"]
            baseline = y - painter.first_baseline_drop(entry["lines"], size)
            if entry["marker"]:
                fig.text(
                    entry["mx"],
                    baseline,
                    entry["marker"],
                    fontsize=size,
                    fontfamily=FONT_BODY,
                    fontweight=600,
                    color=theme["accent"],
                    va="baseline",
                    ha="left",
                )
            elif entry["level"] == 0:
                side = pt_to_frac_h(size) * 0.26
                fig.add_artist(
                    Rectangle(
                        (entry["mx"], baseline + pt_to_frac_h(size) * 0.22),
                        side * PAGE_H_IN / PAGE_W_IN,
                        side,
                        facecolor=theme["accent"],
                        edgecolor="none",
                        transform=fig.transFigure,
                    )
                )
            else:
                fig.add_artist(
                    Rectangle(
                        (entry["mx"], baseline + pt_to_frac_h(size) * 0.30),
                        pt_to_frac_w(size) * 0.42,
                        0.0035,
                        facecolor=theme["muted"],
                        edgecolor="none",
                        transform=fig.transFigure,
                    )
                )
            painter.draw_lines(entry["lines"], entry["x"], y, size, theme["body"])
            y -= entry["h"]
            continue

        if kind == "quote":
            fig.add_artist(
                Rectangle(
                    (MARGIN_L, y - entry["h"] + 0.004),
                    0.0055,
                    entry["h"] - 0.008,
                    facecolor=theme["accent2"],
                    edgecolor="none",
                    transform=fig.transFigure,
                )
            )
            painter.draw_lines(
                entry["lines"], entry["x"] + 0.012, y, entry["size"], theme["ink"], FONT_BODY, 400
            )
            y -= entry["h"]
            continue

        if kind == "code":
            pad = entry["pad"]
            fig.add_artist(
                FancyBboxPatch(
                    (MARGIN_L, y - entry["h"]),
                    content_w,
                    entry["h"],
                    boxstyle="round,pad=0,rounding_size=0.010",
                    facecolor=theme["code_bg"],
                    edgecolor="none",
                    transform=fig.transFigure,
                    zorder=0,
                )
            )
            size = entry["size"]
            step = pt_to_frac_h(size) * 1.30
            for i, line in enumerate(entry["lines"]):
                fig.text(
                    MARGIN_L + 0.018,
                    y - pad - step * i - pt_to_frac_h(size) * 0.78,
                    line,
                    fontsize=size,
                    fontfamily=FONT_MONO,
                    color=theme["ink"],
                    va="baseline",
                    ha="left",
                )
            y -= entry["h"]
            continue

        if kind == "images":
            boxes = entry["boxes"]
            row_h = max(h for _, h in boxes)
            img_bottom = y - entry["h"] + entry["cap"]
            draw_image_row(painter, theme, entry["loaded"], boxes, entry["captions"],
                           entry["columns"], img_bottom, row_h)
            y -= entry["h"]
            continue

    return y


def render_slide(blocks, directives, layout, theme, meta, base_dir, number, total):
    fig = new_figure(theme)
    painter = Painter(fig, theme)
    footer = meta.get("footer", "")

    if layout == "title":
        render_title_slide(painter, theme, blocks, meta)
        draw_footer(painter, theme, footer, number, total, show_number=False)
        return fig, False

    if layout == "section":
        render_section_slide(painter, theme, blocks)
        draw_footer(painter, theme, footer, number, total)
        return fig, False

    if layout == "full":
        render_full_slide(painter, theme, blocks, base_dir)
        draw_footer(painter, theme, footer, number, total)
        return fig, False

    # Content: shrink the type until everything fits the text area.
    avail = (1 - MARGIN_T) - MARGIN_B
    overflow = False
    for candidate in (1.0, 0.94, 0.88, 0.82, 0.76, 0.70, 0.64, 0.58):
        painter.too_wide = False
        plan, total_h = layout_content(painter, theme, blocks, base_dir, candidate)
        if total_h <= avail and not painter.too_wide:
            break
    else:
        overflow = True

    draw_content(painter, theme, plan, total_h, base_dir)
    draw_footer(painter, theme, footer, number, total)
    return fig, overflow


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------


def build(src, out_pdf, png_dir=None, theme_name=None):
    with open(src, encoding="utf-8") as handle:
        lines = handle.read().splitlines()

    meta, body = parse_front_matter(lines)
    theme = THEMES[(theme_name or meta.get("theme") or "light").strip().lower()]
    base_dir = os.path.dirname(os.path.abspath(src))

    raw_slides = split_slides(body)
    slides = []
    for i, slide_lines in enumerate(raw_slides):
        blocks, directives = parse_blocks(slide_lines)
        slides.append((blocks, directives, infer_layout(blocks, directives, i)))

    total = len(slides)
    os.makedirs(os.path.dirname(os.path.abspath(out_pdf)), exist_ok=True)
    with PdfPages(out_pdf) as pdf:
        for i, (blocks, directives, layout) in enumerate(slides, start=1):
            fig, overflow = render_slide(
                blocks, directives, layout, theme, meta, base_dir, i, total
            )
            if overflow:
                print(f"  slide {i}: content overflows even at the smallest size", file=sys.stderr)
            pdf.savefig(fig, facecolor=theme["bg"])
            if png_dir:
                os.makedirs(png_dir, exist_ok=True)
                fig.savefig(
                    os.path.join(png_dir, f"slide-{i:02d}.png"),
                    dpi=DPI,
                    facecolor=theme["bg"],
                )
            plt.close(fig)
        info = pdf.infodict()
        if meta.get("title"):
            info["Title"] = meta["title"]
        if meta.get("author"):
            info["Author"] = meta["author"]

    print(f"{out_pdf}  ({total} slides, {int(PAGE_W_IN * DPI)}x{int(PAGE_H_IN * DPI)})")
    if png_dir:
        print(f"{png_dir}/slide-NN.png  ({total} images)")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", help="Markdown deck")
    parser.add_argument("-o", "--output", help="output PDF (default: alongside the source)")
    parser.add_argument("--png", action="store_true", help="also write one PNG per slide")
    parser.add_argument("--theme", choices=sorted(THEMES), help="override the deck's theme")
    args = parser.parse_args(argv)

    out = args.output or os.path.splitext(args.source)[0] + ".pdf"
    png_dir = os.path.splitext(out)[0] + "-png" if args.png else None
    build(args.source, out, png_dir, args.theme)


if __name__ == "__main__":
    main()
