"""Server-side SVG charts.

One line chart, drawn as inline SVG. A charting library would add a build step and a
runtime dependency for a single chart shape; the report template asks for charts only
where they make a change over time easier to see.

Colours come from CSS custom properties so the chart follows the page theme.
"""

from __future__ import annotations

from datetime import date
from html import escape

Point = tuple[date, float]


def line_chart(
    points: list[Point],
    *,
    label: str,
    unit: str,
    width: int = 720,
    height: int = 220,
) -> str:
    """Render a time series. Returns an empty string when there is nothing to draw."""
    if len(points) < 2:
        return ""

    points = sorted(points, key=lambda p: p[0])
    pad_l, pad_r, pad_t, pad_b = 44, 12, 16, 32
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b

    xs = [p[0].toordinal() for p in points]
    ys = [p[1] for p in points]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    if y_max == y_min:  # a flat series still deserves a readable band
        y_min, y_max = y_min - 1, y_max + 1
    x_span = (x_max - x_min) or 1
    y_span = y_max - y_min

    def sx(x: int) -> float:
        return pad_l + (x - x_min) / x_span * plot_w

    def sy(y: float) -> float:
        return pad_t + (1 - (y - y_min) / y_span) * plot_h

    coords = [(sx(x), sy(y)) for x, y in zip(xs, ys)]
    path = " ".join(
        f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(coords)
    )
    area = (
        f"M{coords[0][0]:.1f},{pad_t + plot_h:.1f} "
        + " ".join(f"L{x:.1f},{y:.1f}" for x, y in coords)
        + f" L{coords[-1][0]:.1f},{pad_t + plot_h:.1f} Z"
    )

    gridlines, y_labels = [], []
    for frac in (0.0, 0.5, 1.0):
        y_val = y_min + y_span * frac
        y_pos = sy(y_val)
        gridlines.append(
            f'<line x1="{pad_l}" y1="{y_pos:.1f}" x2="{width - pad_r}" '
            f'y2="{y_pos:.1f}" class="grid" />'
        )
        y_labels.append(
            f'<text x="{pad_l - 8}" y="{y_pos + 4:.1f}" class="axis" '
            f'text-anchor="end">{y_val:.0f}</text>'
        )

    first, last = points[0][0], points[-1][0]
    x_labels = (
        f'<text x="{pad_l}" y="{height - 10}" class="axis">{first.isoformat()}</text>'
        f'<text x="{width - pad_r}" y="{height - 10}" class="axis" '
        f'text-anchor="end">{last.isoformat()}</text>'
    )

    last_x, last_y = coords[-1]
    title = escape(f"{label}, {unit}, {first.isoformat()} to {last.isoformat()}")

    return f"""<svg viewBox="0 0 {width} {height}" class="chart" role="img"
     aria-label="{title}" preserveAspectRatio="xMidYMid meet">
  <title>{title}</title>
  {''.join(gridlines)}
  <path d="{area}" class="area" />
  <path d="{path}" class="line" />
  <circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="3.5" class="marker" />
  {''.join(y_labels)}
  {x_labels}
</svg>"""


def direction(points: list[Point]) -> str:
    """Rising, falling, or stable, by comparing the first and last thirds of the series.

    Endpoints alone are too noisy for a weekly report; a third at each end smooths that
    without pretending to be a trend model.
    """
    if len(points) < 2:
        return "not enough data"
    points = sorted(points, key=lambda p: p[0])
    third = max(1, len(points) // 3)
    head = sum(v for _, v in points[:third]) / third
    tail = sum(v for _, v in points[-third:]) / third
    if head == 0:
        return "stable"
    change = (tail - head) / abs(head)
    if change > 0.10:
        return "rising"
    if change < -0.10:
        return "falling"
    return "stable"
