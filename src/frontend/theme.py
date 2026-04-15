"""UnCram productive UI palette (emerald / slate).

Uses shared head HTML instead of ``ui.colors()`` so importing ``app.py`` does not
enter NiceGUI script mode (which conflicts with ``@ui.page`` routes).
"""

from nicegui.functions.html import add_head_html

_BRAND_CSS = """
<style data-uncram-theme>
  :root {
    --q-primary: #059669;
    --q-secondary: #1e293b;
    --q-accent: #34d399;
    --q-positive: #059669;
    --q-negative: #dc2626;
    --q-info: #0284c7;
    --q-warning: #d97706;
  }
</style>
"""


def apply_productive_theme() -> None:
    add_head_html(_BRAND_CSS.strip(), shared=True)
