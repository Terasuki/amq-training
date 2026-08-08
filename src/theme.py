"""
Central definition of the app's pastel design system.

Keep this in sync with the CSS custom properties defined in assets/styles.css --
the hex values here should always match the ones in :root there.
"""

import plotly.graph_objects as go
import plotly.io as pio

# --- Core palette ---
PETAL_FROST = "#ffd6ff"
MAUVE = "#e7c6ff"
MAUVE_2 = "#c8b6ff"
PERIWINKLE = "#b8c0ff"
PERIWINKLE_2 = "#bbd0ff"

PALETTE = [PETAL_FROST, MAUVE, MAUVE_2, PERIWINKLE, PERIWINKLE_2]

# --- Text ---
INK = "#3d3358"
INK_SOFT = "#6b5f8a"

# Primary/secondary text read directly against the pastel page and card
# backgrounds. Keep in sync with --text-primary / --text-secondary in
# assets/styles.css.
TEXT_PRIMARY = "#fffaff"
TEXT_SECONDARY = "rgba(255, 250, 255, 0.8)"

# --- Colors for correct / incorrect / spectated ---
SUCCESS = "#cdead9"
SUCCESS_TEXT = "#2f5d3a"
SUCCESS_CHART = "#a8d9bc"

DANGER = "#f8d6dd"
DANGER_TEXT = "#7a2e3d"
DANGER_CHART = "#f0b0bf"

NEUTRAL = "#e6e1f0"
NEUTRAL_TEXT = "#5c5570"
NEUTRAL_CHART = "#c3b9d9"

# --- Deepened core palette ---
CHART_COLORWAY = [
    "#8f9aff",  # periwinkle, deepened
    "#c79eea",  # mauve, deepened
    "#e8a3e8",  # petal-frost, deepened
    "#9c82e6",  # mauve-2, deepened
    "#86a8f0",  # periwinkle-2, deepened
]

FONT_FAMILY = "Montserrat, 'Helvetica Neue', Arial, sans-serif"


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
