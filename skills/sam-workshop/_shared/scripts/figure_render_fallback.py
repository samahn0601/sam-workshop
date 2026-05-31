"""figure_render_fallback.py — sam-workshop / figure-prompt-eng 보조 도구 (v1.2 NEW)

Free-tier 이미지 생성기(Gemini Nano Banana 2 / GPT-image-2 등)가 워크숍 시간 내
가용하지 않거나 한국어/영어 텍스트 렌더링이 깨질 때, matplotlib으로 schematic
figure를 직접 렌더링하기 위한 fallback 템플릿.

Auto-Pilot 모드(reference run, H1)에서는 이미지 생성 단계를 무인 수행할 수 있어야
하므로 본 스크립트가 figure-prompt-eng skill의 default 산출 경로를 보장한다.

사용 예 (paper_home/07_figures/build_figures.py로 복사 후 본인 figure 추가):
    cp ~/.claude/skills/sam-workshop/_shared/scripts/figure_render_fallback.py \\
       paper_home/07_figures/build_figures.py
    # 본인 figure 함수 추가 후
    python paper_home/07_figures/build_figures.py

산출 위치:
    paper_home/07_figures/final/figure_<n>_<slug>.png  (300 dpi)

본 스크립트는 두 가지 *예시* figure를 포함한다:
- example_pipeline_horizontal: 좌→우 step 흐름 + Self-Gate diamond + 하단 band
- example_circular_dial: 원형 dial + halo ring

본인 figure를 추가할 때는 example_*를 복사·수정하거나, _draw_box / _draw_arrow
등 헬퍼만 사용해 새 figure를 그린다.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Wedge, Circle, Rectangle, FancyBboxPatch
import numpy as np


# ───────────────────────────────────────────────────────────────
# Helper primitives — small, composable, hand-tuned
# ───────────────────────────────────────────────────────────────

def _ensure_outdir(paper_home: Path) -> Path:
    out = paper_home / "07_figures" / "final"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _draw_box(ax, x: float, y: float, w: float, h: float,
              label: str, sub: str = "", *, face: str = "#e7ecef",
              edge: str = "#1f2933") -> None:
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.04,rounding_size=0.12",
        facecolor=face, edgecolor=edge, linewidth=1.4,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h * 0.62, label,
            ha="center", va="center", fontsize=10, fontweight="bold",
            color="#1f2933")
    if sub:
        ax.text(x + w / 2, y + h * 0.20, sub,
                ha="center", va="center", fontsize=7.5, color="#3a4a55")


def _draw_arrow(ax, x0: float, y0: float, x1: float, y1: float) -> None:
    ax.annotate(
        "", xy=(x1, y1), xytext=(x0, y0),
        arrowprops=dict(arrowstyle="->", lw=1.3, color="#1f2933"),
    )


def _draw_diamond(ax, x: float, y: float, label: str, *,
                  color: str = "#f4a261", text_color: str = "white",
                  radius: float = 0.20) -> None:
    diamond = patches.RegularPolygon(
        (x, y), numVertices=4, radius=radius,
        orientation=np.pi / 4, facecolor=color, edgecolor="#1f2933",
        linewidth=1.0, zorder=5,
    )
    ax.add_patch(diamond)
    ax.text(x, y, label, ha="center", va="center",
            fontsize=7.5, fontweight="bold", color=text_color, zorder=6)


def _draw_dial(ax, cx: float, cy: float, inner_r: float, outer_r: float,
               positions: list[tuple[str, str]],
               default_position: str = "",
               start_top_deg: float = 90.0) -> None:
    n = len(positions)
    wedge_angle = 360.0 / n
    for i, (label, sub) in enumerate(positions):
        theta_end = start_top_deg - i * wedge_angle
        theta_start = theta_end - wedge_angle
        is_default = (label == default_position)
        face = "#f4a261" if is_default else "#e7ecef"
        wedge = Wedge((cx, cy), outer_r, theta_start, theta_end,
                      width=outer_r - inner_r,
                      facecolor=face, edgecolor="#1f2933",
                      linewidth=1.3, zorder=3)
        ax.add_patch(wedge)
        theta_mid = np.deg2rad((theta_start + theta_end) / 2)
        # Label outer
        r_l = inner_r + (outer_r - inner_r) * 0.65
        ax.text(cx + r_l * np.cos(theta_mid), cy + r_l * np.sin(theta_mid),
                label, ha="center", va="center", fontsize=18,
                fontweight="bold",
                color="white" if is_default else "#1f2933", zorder=4)
        # Sub-label inner
        r_s = inner_r + (outer_r - inner_r) * 0.22
        ax.text(cx + r_s * np.cos(theta_mid), cy + r_s * np.sin(theta_mid),
                sub, ha="center", va="center", fontsize=6.8,
                color="white" if is_default else "#1f2933",
                fontweight="bold" if is_default else "normal", zorder=4)


def _draw_halo(ax, cx: float, cy: float, outer_r: float, halo_r: float,
               categories: list[str], header: str,
               sub_header: str = "") -> None:
    halo = Wedge((cx, cy), halo_r, 0, 360, width=halo_r - outer_r - 0.04,
                 facecolor="#fce4e4", edgecolor="#9a1c1c", linewidth=1.4)
    ax.add_patch(halo)
    n_cat = len(categories)
    for i, cat in enumerate(categories):
        theta_deg = 90 - (360 / n_cat) * i
        theta_rad = np.deg2rad(theta_deg)
        r = (outer_r + halo_r) / 2 + 0.01
        ax.text(cx + r * np.cos(theta_rad), cy + r * np.sin(theta_rad),
                cat, ha="center", va="center", fontsize=8.0,
                color="#9a1c1c", fontweight="bold", zorder=5)
    ax.text(cx, halo_r + 0.18, header, ha="center", va="bottom",
            fontsize=12, fontweight="bold", color="#9a1c1c")
    if sub_header:
        ax.text(cx, halo_r + 0.04, sub_header, ha="center", va="bottom",
                fontsize=8.5, color="#9a1c1c", style="italic")


# ───────────────────────────────────────────────────────────────
# Example figures (delete or modify in your build_figures.py)
# ───────────────────────────────────────────────────────────────

def example_pipeline_horizontal(out_path: Path) -> None:
    """좌→우 horizontal flow with N steps + gate diamonds."""
    fig, ax = plt.subplots(figsize=(13, 5), dpi=300)
    ax.set_xlim(0, 13); ax.set_ylim(0, 5); ax.axis("off")

    steps = [("Step 1", "30 min"), ("Step 2", "40 min"),
             ("Step 3", "30 min"), ("Step 4", "50 min")]
    box_w, box_h, spacing, x_start, y_box = 1.6, 1.4, 1.8, 1.0, 2.0
    for i, (label, sub) in enumerate(steps):
        x = x_start + i * spacing
        _draw_box(ax, x, y_box, box_w, box_h, label, sub)
        if i < len(steps) - 1:
            _draw_arrow(ax, x + box_w, y_box + box_h / 2,
                        x_start + (i + 1) * spacing, y_box + box_h / 2)
    fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def example_circular_dial(out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 8), dpi=300)
    ax.set_xlim(-2, 2); ax.set_ylim(-2, 2); ax.axis("off")
    ax.set_aspect("equal")
    positions = [("L0", "manual"), ("L1", "assisted"),
                 ("L2", "default"), ("L3", "supervised")]
    _draw_dial(ax, 0, 0, 0.55, 1.10, positions, default_position="L2")
    _draw_halo(ax, 0, 0, 1.10, 1.40,
               ["category_a", "category_b", "category_c"],
               header="Outer ring (governance)")
    fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ───────────────────────────────────────────────────────────────
# Entry point — replace with your own figure functions
# ───────────────────────────────────────────────────────────────

def main(paper_home: Path | None = None) -> None:
    paper_home = paper_home or Path(__file__).resolve().parents[3]
    out = _ensure_outdir(paper_home)
    example_pipeline_horizontal(out / "figure_example_pipeline.png")
    example_circular_dial(out / "figure_example_dial.png")
    print(f"wrote example figures into {out}")


if __name__ == "__main__":
    main()
