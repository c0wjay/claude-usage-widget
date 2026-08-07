"""Direction 6 — Brutalist Mono.

Swiss grid / newspaper. Off-white bg, pure black ink, one crimson accent.
Heavy 2px section rules, Space Mono for all text, everything ALL CAPS.

Nuances:
- Section break is a pair of horizontal lines: top at 2px black, bottom
  at 1px black, with section number + title between them.
- Section number uses the CRIMSON accent; the title is black.
- Progress bars are RECTANGULAR (no radius), with a hard 1px black
  border. Session bar fills red, weekly bar fills black. This is
  intentional asymmetry — session is the "hot" one.
- Live badge is a red rect with white text, 1px wide letters. No
  inner padding besides 4px.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFontMetrics, QPainter, QPen

from ._paint import draw_text, draw_ticker_marquee, hex_to_qcolor, mono_font


WANTS_TICKER = True


THEME = {
    "style":          "brutalist",
    '_mono_family'    : 'Space Mono',
    '_ui_family'      : 'Space Mono',
    'paper'           : '#ffffff',
    'accent2'         : '#d81f26',
    'border'          : '#0a0a0a',
    "bg":             "#eeece7",
    "panel":          "#ffffff",
    "bar_blue":       "#d81f26",
    "bar_track":      "#1f1f1f",
    "text_primary":   "#0a0a0a",
    "text_secondary": "#575757",
    "text_dim":       "#8b8b8b",
    "text_link":      "#d81f26",
    "separator":      "#0a0a0a",
    "warn":           "#d81f26",
    "crit":           "#d81f26",
    "error":          "#d81f26",
    "live_indicator": "#d81f26",
    "ink":            "#0a0a0a",
    "accent":         "#d81f26",
    "hair":           "#d4d2cc",
    "very_dim":       "#c8c6c0",
}

METRICS = {
    "osd_width": 360, "osd_height": 188, "osd_radius": 0, "osd_padding": 12,
    "border_width": 2, "ticker_h": 22,
    "osd_height_scoped": 236,
    "codex_rows_height": 96,
}

FONTS = {"family_mono": "Space Mono", "body_pt": 10, "title_pt": 11}


def _format_reset_min(total_mins: int) -> str:
    if total_mins <= 0:
        return "0M"
    if total_mins < 60:
        return f"{total_mins}M"
    hrs = total_mins // 60
    mins = total_mins % 60
    if hrs >= 24:
        days = hrs // 24
        rem_hrs = hrs % 24
        return f"{days}D {rem_hrs}H {mins}M" if mins > 0 else f"{days}D {rem_hrs}H"
    return f"{hrs}H {mins}M" if mins > 0 else f"{hrs}H"


def _format_reset_hrs_min(total_hrs: int, mins: int) -> str:
    if total_hrs <= 0 and mins <= 0:
        return "0M"
    if total_hrs >= 24:
        days = total_hrs // 24
        rem_hrs = total_hrs % 24
        if rem_hrs > 0 and mins > 0:
            return f"{days}D {rem_hrs}H {mins}M"
        elif rem_hrs > 0:
            return f"{days}D {rem_hrs}H"
        elif mins > 0:
            return f"{days}D {mins}M"
        else:
            return f"{days}D"
    if total_hrs > 0:
        return f"{total_hrs}H {mins}M" if mins > 0 else f"{total_hrs}H"
    return f"{mins}M"


def paint_osd(p: QPainter, rect: QRectF, data, scale: float = 1.0) -> None:
    """Brutalist OSD: white panel, heavy 2px black border, Swiss-grid rules
    between sections, crimson accent for the LIVE badge and session bar."""
    s = scale; t = THEME
    pad = METRICS["osd_padding"] * s

    # panel: white fill + heavy black 2px border
    p.setPen(Qt.NoPen); p.setBrush(hex_to_qcolor(t["panel"]))
    p.drawRect(rect)
    pen = QPen(hex_to_qcolor(t["ink"])); pen.setWidthF(METRICS["border_width"] * s)
    p.setPen(pen); p.setBrush(Qt.NoBrush)
    # Inset by half the pen width so the stroke falls entirely inside the
    # rect at any scale (Qt strokes are centred on the path).
    inset = METRICS["border_width"] / 2 * s
    p.drawRect(rect.adjusted(inset, inset, -inset, -inset))

    x = rect.x() + pad; y = rect.y() + pad
    w = rect.width() - pad * 2

    title_f = mono_font(FONTS["title_pt"] * s, bold=True, family=FONTS["family_mono"])
    body_f = mono_font(FONTS["body_pt"] * s, family=FONTS["family_mono"])
    big_f = mono_font(14 * s, bold=True, family=FONTS["family_mono"])
    small_f = mono_font(9 * s, family=FONTS["family_mono"])
    time_f = mono_font(11 * s, bold=True, family=FONTS["family_mono"])
    fm = QFontMetrics(title_f); fm_b = QFontMetrics(big_f); fm_s = QFontMetrics(small_f); fm_time = QFontMetrics(time_f)

    # top bar
    draw_text(p, x, y + fm.ascent(),
              "CLAUDE / USAGE",
              hex_to_qcolor(t["ink"]), title_f, letter_spacing_px=3 * s)

    if getattr(data, "is_live", False):
        label = "LIVE"
        lw = fm_s.horizontalAdvance(label)
        # red badge
        p.setPen(Qt.NoPen); p.setBrush(hex_to_qcolor(t["accent"]))
        badge = QRectF(rect.right() - pad - lw - 10 * s - 60 * s,
                       y + 2 * s, lw + 8 * s, fm.height() - 2 * s)
        p.drawRect(badge)
        draw_text(p, badge.x() + 4 * s, badge.y() + fm_s.ascent() + 2 * s,
                  label, QColor("#ffffff"), small_f, letter_spacing_px=2 * s)
        tm = f"{data.live_tok_per_min:.1f}K/MIN"
        draw_text(p, badge.right() + 6 * s, badge.y() + fm_s.ascent() + 2 * s,
                  tm, hex_to_qcolor(t["ink"]), small_f, letter_spacing_px=1.5 * s)

    # 2px rule under header
    y_rule = y + fm.height() + 4 * s
    pen = QPen(hex_to_qcolor(t["ink"])); pen.setWidthF(2 * s)
    p.setPen(pen)
    p.drawLine(QPointF(x, y_rule), QPointF(x + w, y_rule))

    def row(yy: float, label: str, pct: float, time_str: str, is_urgent: bool, fill_hex: str):
        # label left
        draw_text(p, x, yy + fm_s.ascent(),
                  label, hex_to_qcolor(t["ink"]), small_f, letter_spacing_px=2 * s)
        # reset time next to label, aligned at fixed X offset
        if time_str:
            reset_txt = f"{time_str}"
            t_color = hex_to_qcolor(t["accent"]) if is_urgent else hex_to_qcolor(t["ink"])
            draw_text(p, x + 65 * s, yy + fm_time.ascent() - 1 * s,
                      reset_txt, t_color, time_f, letter_spacing_px=1 * s)
        # % right
        pct_txt = f"{int(pct * 100)}%"
        pw = QFontMetrics(big_f).horizontalAdvance(pct_txt)
        draw_text(p, x + w - pw, yy + fm_b.ascent(),
                  pct_txt, hex_to_qcolor(t["ink"]), big_f)
        # rect bar below
        ybar = yy + fm_b.height() + 2 * s
        p.setPen(QPen(hex_to_qcolor(t["ink"]), 1 * s))
        p.setBrush(hex_to_qcolor(t["very_dim"]))
        p.drawRect(QRectF(x, ybar, w, 14 * s))
        p.setPen(Qt.NoPen); p.setBrush(hex_to_qcolor(fill_hex))
        p.drawRect(QRectF(x + 1, ybar + 1, (w - 2) * pct, 14 * s - 2))
        return ybar + 14 * s + 8 * s

    yy = y_rule + 10 * s
    sess_time = _format_reset_min(data.session_reset_min)
    sess_urgent = (data.session_reset_min < 60)
    yy = row(yy, "SESSION", data.session_pct, sess_time, sess_urgent, t["accent"])

    wk_time = _format_reset_hrs_min(data.weekly_reset_hrs, data.weekly_reset_min)
    wk_urgent = (data.weekly_reset_hrs < 24)
    yy = row(yy, "WEEKLY", data.weekly_pct, wk_time, wk_urgent, t["ink"])

    if data.scoped_pct is not None and data.scoped_label:
        scoped_time = _format_reset_hrs_min(data.scoped_reset_hrs, data.scoped_reset_min)
        scoped_urgent = (data.scoped_reset_hrs < 24)
        yy = row(yy, data.scoped_label.upper(), data.scoped_pct, scoped_time, scoped_urgent, t["ink"])

    if getattr(data, "codex_available", False):
        c5_time = _format_reset_min(data.codex_session_reset_min)
        c5_urgent = (data.codex_session_reset_min < 60)
        yy = row(yy, "CODEX 5H", data.codex_session_pct, c5_time, c5_urgent, t["accent"])

        c7_time = _format_reset_hrs_min(data.codex_weekly_reset_hrs, data.codex_weekly_reset_min)
        c7_urgent = (data.codex_weekly_reset_hrs < 24)
        yy = row(yy, "CODEX 7D", data.codex_weekly_pct, c7_time, c7_urgent, t["ink"])

    # 2px rule above the ticker strip — matches the Swiss-grid section
    # break at the top of the panel. Collapses the gap between the last content
    # row and ticker before hiding the ticker when the window height is reduced.
    y_tick_target = rect.bottom() - METRICS["ticker_h"] * s
    y_tick_rule = max(yy + 2 * s, y_tick_target)
    pen = QPen(hex_to_qcolor(t["ink"])); pen.setWidthF(2 * s)
    p.setPen(pen)
    p.drawLine(QPointF(x, y_tick_rule), QPointF(x + w, y_tick_rule))
    ticker_f = mono_font(9 * s, bold=True, family=FONTS["family_mono"])
    fm_tick = QFontMetrics(ticker_f)
    y_tick_base = y_tick_rule + 6 * s + fm_tick.ascent()
    # Brutalist palette — red hot, black warn, muted cool/dim.
    ticker_colors = (t["text_dim"], t["ink"], t["ink"], t["accent"])
    draw_ticker_marquee(
        p, x, y_tick_base, w,
        data.ticker_items, data.ticker_offset,
        ticker_colors, ticker_f, sep_gap_px=10 * s,
    )


# ---- POPUP ---------------------------------------------------------

def paint_popup(p, rect, data, scale: float = 1.0) -> float:
    """Brutalist popup: heavy 2px rules, § section marks, crimson accent.

    Nuance: section headers are \"§01 TITLE\" style with a 2px black top
    rule above. The generic painter's \"brutalist\" section style draws
    this correctly.
    """
    from . import _popup_generic
    return _popup_generic.paint_popup(p, rect, data, scale, THEME,
                                      section_style="brutalist",
                                      bar_style="rect_border",
                                      masthead_style="brutalist")


def measure_popup(data, scale: float = 1.0) -> int:
    from ._popup import dry_measure
    return dry_measure(paint_popup, data, scale, METRICS.get("popup_width", 540)) + int(20 * scale)


def paint_loading(p, rect, phase: float = 0.0, scale: float = 1.0) -> None:
    from ._popup import paint_loading as _pl
    _pl(p, rect, THEME, scale, style="brutalist", phase=phase)
