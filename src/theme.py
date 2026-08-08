"""
Single source of truth for the app's pastel design system.

Every color used by the app -- in Plotly charts and in the page CSS -- is
defined here. The CSS custom properties in assets/styles.css are generated
from CSS_VARIABLES by write_css_variables() (called on app startup in
app.py) into assets/_generated_colors.css, so colors never need to be
hand-copied into the stylesheet.
"""

from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio

# --- Core palette ---
PETAL_FROST = "#ffd6ff"
MAUVE = "#e7c6ff"
MAUVE_2 = "#c8b6ff"
PERIWINKLE = "#b8c0ff"
PERIWINKLE_2 = "#bbd0ff"

PALETTE = [PETAL_FROST, MAUVE, MAUVE_2, PERIWINKLE, PERIWINKLE_2]

# Deepened shades used for hover/active states in assets/styles.css.
PERIWINKLE_DEEP = "#7b86e8"
MAUVE_DEEP = "#9c82e6"

# --- Text ---
INK = "#3d3358"
INK_SOFT = "#6b5f8a"
SURFACE = "#fffaff"

# Primary/secondary text read directly against the pastel page and card
# backgrounds.
TEXT_PRIMARY = "#8356F5"
TEXT_SECONDARY = "rgba(255, 250, 255, 0.8)"

# --- Colors for correct / incorrect / spectated ---
SUCCESS = "#cdead9"
SUCCESS_TEXT = "#2f5d3a"
SUCCESS_TEXT_LIGHT = "#4f9169"
SUCCESS_CHART = "#a8d9bc"

DANGER = "#f8d6dd"
DANGER_TEXT = "#7a2e3d"
DANGER_TEXT_LIGHT = "#d1607f"
DANGER_CHART = "#f0b0bf"

NEUTRAL = "#e6e1f0"
NEUTRAL_TEXT = "#5c5570"
NEUTRAL_TEXT_LIGHT = "#8f84ab"
NEUTRAL_CHART = "#c3b9d9"

# --- Deepened core palette (Plotly chart colorway) ---
CHART_COLORWAY = [
    "#8f9aff",  # periwinkle, deepened
    "#c79eea",  # mauve, deepened
    "#e8a3e8",  # petal-frost, deepened
    "#9c82e6",  # mauve-2, deepened
    "#86a8f0",  # periwinkle-2, deepened
]

# --- Font ---
FONT_PRIMARY = "Montserrat"
FONT_FALLBACK = "'Helvetica Neue', Arial, sans-serif"
FONT_FAMILY = f"{FONT_PRIMARY}, {FONT_FALLBACK}"
FONT_WEIGHTS = "ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400"
GOOGLE_FONTS_URL = (
    f"https://fonts.googleapis.com/css2?family={FONT_PRIMARY}:{FONT_WEIGHTS}&display=swap"
)


def _hex_to_rgb_triplet(hex_color: str) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"{r}, {g}, {b}"


# CSS custom property name (without the leading --) -> value. This is what
# gets written into assets/_generated_colors.css; add new colors here rather
# than editing CSS directly.
CSS_VARIABLES = {
    "petal-frost": PETAL_FROST,
    "mauve": MAUVE,
    "mauve-2": MAUVE_2,
    "periwinkle": PERIWINKLE,
    "periwinkle-2": PERIWINKLE_2,
    "periwinkle-deep": PERIWINKLE_DEEP,
    "mauve-deep": MAUVE_DEEP,
    "ink": INK,
    "ink-soft": INK_SOFT,
    "surface": SURFACE,
    "text-primary": TEXT_PRIMARY,
    "text-secondary": TEXT_SECONDARY,
    "text-shadow": f"0 1px 3px rgba({_hex_to_rgb_triplet(INK)}, 0.3)",
    "success": SUCCESS,
    "success-text": SUCCESS_TEXT,
    "success-text-light": SUCCESS_TEXT_LIGHT,
    "danger": DANGER,
    "danger-text": DANGER_TEXT,
    "danger-text-light": DANGER_TEXT_LIGHT,
    "neutral": NEUTRAL,
    "neutral-text": NEUTRAL_TEXT,
    "neutral-text-light": NEUTRAL_TEXT_LIGHT,
    "bs-primary-rgb": _hex_to_rgb_triplet(PERIWINKLE),
    "bs-link-color-rgb": _hex_to_rgb_triplet(PETAL_FROST),
    "font-family": FONT_FAMILY,
}

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
GENERATED_CSS_PATH = ASSETS_DIR / "_generated_theme.css"


def write_css_variables(path: Path = GENERATED_CSS_PATH) -> None:
    """Write CSS_VARIABLES (colors + font) out for assets/styles.css to consume via var()."""
    declarations = "\n".join(f"  --{name}: {value};" for name, value in CSS_VARIABLES.items())
    css = (
        f'@import url("{GOOGLE_FONTS_URL}");\n'
        "/* Auto-generated from src/theme.py -- do not edit directly.\n"
        "   Regenerated on every app startup by write_css_variables(). */\n"
        f":root {{\n{declarations}\n}}\n"
    )
    path.write_text(css)


def get_pastel_template() -> go.layout.Template:
    template = go.layout.Template()
    template.layout = go.Layout(
        colorway=CHART_COLORWAY,
        font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY, size=13),
        title=dict(font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY, size=16)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(color=TEXT_PRIMARY)),
        xaxis=dict(
            gridcolor="rgba(255, 250, 255, 0.25)",
            linecolor="rgba(255, 250, 255, 0.4)",
            zerolinecolor="rgba(255, 250, 255, 0.4)",
            tickfont=dict(color=TEXT_SECONDARY),
            title=dict(font=dict(color=TEXT_SECONDARY), standoff=12),
            automargin=True,
        ),
        yaxis=dict(
            gridcolor="rgba(255, 250, 255, 0.25)",
            linecolor="rgba(255, 250, 255, 0.4)",
            zerolinecolor="rgba(255, 250, 255, 0.4)",
            tickfont=dict(color=TEXT_SECONDARY),
            title=dict(font=dict(color=TEXT_SECONDARY), standoff=12),
            automargin=True,
        ),
    )
    pio.templates["pastel_dream"] = template
    pio.templates.default = "pastel_dream"
    return template


def table_style_table() -> dict:
    return {
        "width": "100%",
        "overflowX": "auto",
        "overflowY": "auto",
        "border": "none",
        "borderRadius": "16px",
    }


def table_style_cell() -> dict:
    return {
        "textAlign": "center",
        "padding": "8px",
        "whiteSpace": "normal",
        "height": "auto",
        "fontFamily": FONT_FAMILY,
        "border": "1px solid rgba(61, 51, 88, 0.08)",
    }


def table_style_header() -> dict:
    return {
        "backgroundColor": PERIWINKLE_2,
        "color": INK,
        "fontWeight": "600",
        "border": "none",
    }


def table_style_data() -> dict:
    return {
        "backgroundColor": "#fffaff",
        "color": INK,
        "border": "none",
    }


def table_conditional_correct(correct_col: str = "correct") -> list:
    return [
        {
            "if": {"filter_query": f"{{{correct_col}}} = 1"},
            "backgroundColor": SUCCESS,
            "color": SUCCESS_TEXT,
        },
        {
            "if": {"filter_query": f"{{{correct_col}}} = 0"},
            "backgroundColor": DANGER,
            "color": DANGER_TEXT,
        },
        {
            "if": {"filter_query": f"{{{correct_col}}} is nil"},
            "backgroundColor": NEUTRAL,
            "color": NEUTRAL_TEXT,
        },
        {"if": {"column_id": correct_col}, "display": "None"},
    ]


def table_header_conditional_correct(correct_col: str = "correct") -> list:
    return [{"if": {"column_id": correct_col}, "display": "None"}]
