#!/usr/bin/env python3
"""Plot Mandel displacements and the finite-deformation Biot response."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle


plt.rcParams.update(
    {
        "pgf.texsystem": "lualatex",
        "pgf.rcfonts": False,
        "font.family": "serif",
        "font.size": 9.0,
        "axes.labelsize": 9.0,
        "axes.titlesize": 9.0,
        "xtick.labelsize": 8.0,
        "ytick.labelsize": 8.0,
        "legend.fontsize": 8.0,
    }
)


ROOT = Path(__file__).resolve().parents[1]
SMALL_LOAD_CSV = ROOT / "validation/mandel_displacement_profiles.csv"
PRESSURE_CSV = ROOT / "validation/mandel_pressure_profiles.csv"
LARGE_DEFORMATION_CSV = ROOT / "validation/mandel_large_deformation.csv"
BIOT_CONTOUR_CSV = ROOT / "validation/mandel_biot_contours.csv"

ROOT_COUNT = 12

LOAD = 1.0e5
K = 1.0e9
G = 0.75e9
KS = 2.5e9
KF = 8.0e9
POROSITY = 0.1
B0 = 1.0 - K / KS
MOBILITY = 1.5e-9
WIDTH = 1.0
HEIGHT = 0.1


def save_figure(figure, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, metadata={"Creator": "plot_mandel_extended_results.py"})
    pgf_output = output.with_suffix(".pgf")
    if pgf_output != output:
        figure.savefig(pgf_output)
    if output.parent.resolve() == ROOT / "figures":
        figure.savefig(output.with_suffix(".png"), dpi=180)
        site_output = ROOT / "docs/assets/img" / output.with_suffix(".png").name
        site_output.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(site_output, dpi=180)


def read_rows(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return [
            {name: float(value) for name, value in row.items()}
            for row in csv.DictReader(stream)
        ]


def read_profile_rows(path: Path) -> list[dict[str, float | str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return [
            {
                "time": float(row["time"]),
                "component": row["component"],
                "coordinate": float(row["coordinate"]),
                "displacement": float(row["displacement"]),
            }
            for row in csv.DictReader(stream)
        ]


def mandel_parameters() -> tuple[float, float, float, float]:
    storage_modulus = 1.0 / ((1.0 - POROSITY) / KS - K / KS**2 + POROSITY / KF)
    undrained_bulk_modulus = K + B0**2 * storage_modulus
    poisson = (3.0 * K - 2.0 * G) / (2.0 * (3.0 * K + G))
    undrained_poisson = (3.0 * undrained_bulk_modulus - 2.0 * G) / (
        2.0 * (3.0 * undrained_bulk_modulus + G)
    )
    diffusivity = (
        2.0
        * G
        * (1.0 - poisson)
        * (undrained_poisson - poisson)
        * MOBILITY
        / (B0**2 * (1.0 - undrained_poisson) * (1.0 - 2.0 * poisson) ** 2)
    )
    skempton = B0 * storage_modulus / undrained_bulk_modulus
    return poisson, undrained_poisson, diffusivity, skempton


def mandel_roots() -> tuple[float, ...]:
    poisson, undrained_poisson, _, _ = mandel_parameters()
    coefficient = (1.0 - poisson) / (undrained_poisson - poisson)
    roots = []
    for index in range(ROOT_COUNT):
        lower = index * math.pi + 1.0e-12
        upper = index * math.pi + 0.5 * math.pi - 1.0e-12
        for _ in range(80):
            midpoint = 0.5 * (lower + upper)
            if math.tan(midpoint) - coefficient * midpoint > 0.0:
                upper = midpoint
            else:
                lower = midpoint
        roots.append(0.5 * (lower + upper))
    return tuple(roots)


def analytical_pressure(coordinate: float, time: float) -> float:
    _, undrained_poisson, diffusivity, skempton = mandel_parameters()
    series = sum(
        (
            math.sin(root) * math.cos(root * coordinate / WIDTH)
            - math.sin(root) * math.cos(root)
        )
        / (root - math.sin(root) * math.cos(root))
        * math.exp(-root**2 * diffusivity * time / WIDTH**2)
        for root in mandel_roots()
    )
    return 2.0 * LOAD * skempton * (1.0 + undrained_poisson) * series / 3.0


def analytical_displacement(component: str, coordinate: float, time: float) -> float:
    poisson, undrained_poisson, diffusivity, _ = mandel_parameters()
    exponentials = [
        math.exp(-root**2 * diffusivity * time / WIDTH**2) for root in mandel_roots()
    ]
    uniform_series = sum(
        math.sin(root)
        * math.cos(root)
        / (root - math.sin(root) * math.cos(root))
        * exponential
        for root, exponential in zip(mandel_roots(), exponentials)
    )
    if component == "ux":
        spatial_series = sum(
            math.cos(root)
            * math.sin(root * coordinate / WIDTH)
            / (root - math.sin(root) * math.cos(root))
            * exponential
            for root, exponential in zip(mandel_roots(), exponentials)
        )
        return (
            LOAD * poisson / (2.0 * G)
            - LOAD * undrained_poisson / G * uniform_series
        ) * coordinate + LOAD * WIDTH / G * spatial_series
    if component == "uy":
        return (
            -LOAD * (1.0 - poisson) / (2.0 * G)
            + LOAD * (1.0 - undrained_poisson) / G * uniform_series
        ) * coordinate
    raise ValueError(f"unknown displacement component: {component}")


def plot_pressure(rows: list[dict[str, float]], output: Path) -> None:
    times = sorted({row["time"] for row in rows})
    colors = plt.get_cmap("viridis")(
        [index / max(len(times) - 1, 1) for index in range(len(times))]
    )
    analytical_coordinates = [WIDTH * index / 400.0 for index in range(401)]
    figure, axis = plt.subplots(figsize=(5.98, 3.88), constrained_layout=True)
    # Instantaneous undrained uniform pressure p0 = P0 B_Sk (1+nu_u)/3.  Its
    # level marks the initial pressure that the early-time profile rises above
    # (the Mandel-Cryer overshoot near the undrained center).
    _, undrained_poisson, _, skempton = mandel_parameters()
    initial_kpa = LOAD * skempton * (1.0 + undrained_poisson) / (3.0 * 1000.0)
    axis.axhline(initial_kpa, color="0.4", linestyle="--", linewidth=1.0)
    axis.text(
        0.01,
        initial_kpa + 0.45,
        r"$p_0$ (initial undrained)",
        fontsize=7.5,
        color="0.2",
    )
    for color, time in zip(colors, times):
        numerical = [row for row in rows if math.isclose(row["time"], time)]
        numerical.sort(key=lambda row: row["x"])
        axis.plot(
            analytical_coordinates,
            [analytical_pressure(coordinate, time) / 1000.0 for coordinate in analytical_coordinates],
            color=color,
            linewidth=1.6,
            label=fr"$t={time:g}$ s",
        )
        stride = max(len(numerical) // 20, 1)
        sampled = numerical[::stride]
        if sampled[-1] is not numerical[-1]:
            sampled.append(numerical[-1])
        axis.plot(
            [row["x"] for row in sampled],
            [row["pressure"] / 1000.0 for row in sampled],
            linestyle="none",
            marker="o",
            markersize=3.4,
            markerfacecolor="white",
            markeredgecolor=color,
            markeredgewidth=0.8,
        )
    time_legend = axis.legend(title="Profile time", loc="lower left", ncol=2)
    axis.add_artist(time_legend)
    axis.legend(
        handles=(
            Line2D([0], [0], color="0.2", linewidth=1.6, label="analytical series"),
            Line2D(
                [0],
                [0],
                color="0.2",
                linestyle="none",
                marker="o",
                markerfacecolor="white",
                markersize=3.5,
                label="Q2/Q1 finite element",
            ),
        ),
        loc="upper right",
    )
    axis.set_xlabel(r"distance from the undrained center, $X$ [m]")
    axis.set_ylabel(r"water pressure, $p$ [kPa]")
    axis.set_xlim(0.0, WIDTH)
    axis.set_ylim(bottom=0.0)
    axis.grid(alpha=0.22)
    save_figure(figure, output)
    plt.close(figure)


def plot_small_load(rows: list[dict[str, float | str]], output: Path) -> None:
    times = sorted({float(row["time"]) for row in rows})
    colors = plt.get_cmap("viridis")(
        [index / max(len(times) - 1, 1) for index in range(len(times))]
    )
    figure, axes = plt.subplots(1, 2, figsize=(5.98, 2.77), constrained_layout=True)
    configurations = (
        (axes[0], "ux", WIDTH, 401, r"distance from the undrained center, $X$ [m]", r"horizontal displacement, $u_x$ [$\mu$m]"),
        (axes[1], "uy", HEIGHT, 81, r"distance from the symmetry plane, $Y$ [m]", r"vertical displacement, $u_y$ [$\mu$m]"),
    )
    for axis, component, length, count, xlabel, ylabel in configurations:
        analytical_coordinates = [length * index / (count - 1) for index in range(count)]
        for color, time in zip(colors, times):
            numerical = [
                row
                for row in rows
                if row["component"] == component and math.isclose(float(row["time"]), time)
            ]
            numerical.sort(key=lambda row: float(row["coordinate"]))
            axis.plot(
                analytical_coordinates,
                [1.0e6 * analytical_displacement(component, coordinate, time) for coordinate in analytical_coordinates],
                color=color,
                linewidth=1.8,
                label=fr"$t={time:g}$ s",
            )
            axis.plot(
                [float(row["coordinate"]) for row in numerical],
                [1.0e6 * float(row["displacement"]) for row in numerical],
                linestyle="none",
                marker="o",
                markersize=3.4,
                markerfacecolor="white",
                markeredgecolor=color,
                markeredgewidth=0.8,
            )
        axis.set_xlabel(xlabel)
        axis.set_ylabel(ylabel)
        axis.set_xlim(0.0, length)
        axis.grid(alpha=0.22)
    axes[0].legend(title="Profile time", fontsize=8.0, title_fontsize=8.5)
    axes[1].legend(
        handles=(
            Line2D([0], [0], color="0.2", linewidth=1.8, label="analytical series"),
            Line2D([0], [0], color="0.2", linestyle="none", marker="o", markerfacecolor="white", markersize=4, label="Q2 finite element"),
        ),
        fontsize=8.0,
    )
    save_figure(figure, output)
    plt.close(figure)


def plot_large_deformation(rows: list[dict[str, float]], output: Path) -> None:
    times = [0.0] + [row["time"] for row in rows]
    side = [0.0] + [100.0 * row["side_displacement"] / WIDTH for row in rows]
    top = [0.0] + [-100.0 * row["top_displacement"] / HEIGHT for row in rows]
    biot_minimum = [B0] + [row["biot_minimum"] for row in rows]
    biot_average = [B0] + [row["biot_average"] for row in rows]
    biot_maximum = [B0] + [row["biot_maximum"] for row in rows]

    figure, axes = plt.subplots(1, 2, figsize=(6.35, 2.87), constrained_layout=True)
    axes[0].plot(times, top, color="#b63679", linewidth=1.8, label="platen compression")
    axes[0].plot(times, side, color="#31688e", linewidth=1.8, label="lateral expansion")
    axes[0].axvline(0.2, color="0.55", linewidth=0.9, linestyle=":")
    axes[0].set_xlabel(r"time, $t$ [s]")
    axes[0].set_ylabel("boundary displacement / specimen dimension [%]")
    axes[0].set_xlim(0.0, max(times))
    axes[0].set_ylim(bottom=0.0)
    axes[0].grid(alpha=0.22)
    axes[0].legend(fontsize=8.0)

    axes[1].fill_between(times, biot_minimum, biot_maximum, color="#35b779", alpha=0.24, label="spatial range")
    axes[1].plot(times, biot_average, color="#1f7a5c", linewidth=1.9, label="spatial average")
    axes[1].axhline(B0, color="0.3", linewidth=1.0, linestyle="--", label=r"$B_0=0.6$")
    axes[1].axvline(0.2, color="0.55", linewidth=0.9, linestyle=":")
    axes[1].set_xlabel(r"time, $t$ [s]")
    axes[1].set_ylabel(r"Biot coefficient, $B$")
    axes[1].set_xlim(0.0, max(times))
    axes[1].grid(alpha=0.22)
    axes[1].legend(fontsize=8.0)

    save_figure(figure, output)
    plt.close(figure)


def plot_spatial_contours(
    rows: list[dict[str, float]],
    value_key: str,
    colorbar_label: str,
    output: Path,
    limits: tuple[float, float] | None = None,
    scale: float = 1.0,
) -> None:
    times = sorted({row["time"] for row in rows})
    x_centers = sorted({row["X"] for row in rows})
    y_centers = sorted({row["Y"] for row in rows})
    x_edges = [WIDTH * index / len(x_centers) for index in range(len(x_centers) + 1)]
    y_edges = [HEIGHT * index / len(y_centers) for index in range(len(y_centers) + 1)]
    values = {
        (row["time"], row["X"], row["Y"]): scale * row[value_key]
        for row in rows
    }
    minimum = min(values.values()) if limits is None else limits[0]
    maximum = max(values.values()) if limits is None else limits[1]
    normalization = Normalize(vmin=minimum, vmax=maximum)

    figure = plt.figure(figsize=(6.35, 3.56), constrained_layout=True)
    grid = figure.add_gridspec(2, 4, width_ratios=(1.0, 1.0, 1.0, 0.08))
    axes = [
        figure.add_subplot(grid[row, column])
        for row in range(2)
        for column in range(3)
    ]
    colorbar_axis = figure.add_subplot(grid[:, 3])
    colormap = plt.get_cmap("viridis")
    for axis, time in zip(axes, times):
        for x_index, x_coordinate in enumerate(x_centers):
            for y_index, y_coordinate in enumerate(y_centers):
                axis.add_patch(
                    Rectangle(
                        (x_edges[x_index], y_edges[y_index]),
                        x_edges[x_index + 1] - x_edges[x_index],
                        y_edges[y_index + 1] - y_edges[y_index],
                        facecolor=colormap(
                            normalization(values[(time, x_coordinate, y_coordinate)])
                        ),
                        edgecolor="none",
                    )
                )
        axis.set_title(fr"$t={time:g}$ s", fontsize=9.0)
        axis.set_xlim(0.0, WIDTH)
        axis.set_ylim(0.0, HEIGHT)
        axis.set_xticks((0.0, 0.5, 1.0))
        axis.set_yticks((0.0, 0.05, 0.1))
        axis.set_box_aspect(0.38)
    figure.supxlabel(r"reference coordinate, $X$ [m]", fontsize=10)
    figure.supylabel(r"reference coordinate, $Y$ [m]", fontsize=10)
    color_edges = [
        minimum + (maximum - minimum) * index / 90.0 for index in range(91)
    ]
    for lower, upper in zip(color_edges, color_edges[1:]):
        colorbar_axis.add_patch(
            Rectangle(
                (0.0, lower),
                1.0,
                upper - lower,
                facecolor=colormap(normalization(0.5 * (lower + upper))),
                edgecolor="none",
            )
        )
    colorbar_axis.set_xlim(0.0, 1.0)
    colorbar_axis.set_ylim(minimum, maximum)
    colorbar_axis.set_xticks(())
    colorbar_axis.yaxis.tick_right()
    colorbar_axis.yaxis.set_label_position("right")
    colorbar_axis.set_ylabel(colorbar_label)
    save_figure(figure, output)
    plt.close(figure)


def plot_normalized_biot_contours(rows: list[dict[str, float]], output: Path) -> None:
    plot_spatial_contours(
        rows,
        "biot_coefficient",
        r"normalized Biot coefficient, $B/B_0$",
        output,
        limits=(0.965, 1.01),
        scale=1.0 / B0,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pressure-csv", type=Path, default=PRESSURE_CSV)
    parser.add_argument("--small-load-csv", type=Path, default=SMALL_LOAD_CSV)
    parser.add_argument("--large-deformation-csv", type=Path, default=LARGE_DEFORMATION_CSV)
    parser.add_argument("--biot-contour-csv", type=Path, default=BIOT_CONTOUR_CSV)
    parser.add_argument("--pressure-output", type=Path, default=ROOT / "figures/mandel_pressure_profiles.pdf")
    parser.add_argument("--displacement-output", type=Path, default=ROOT / "figures/mandel_displacements.pdf")
    parser.add_argument("--finite-deformation-output", type=Path, default=ROOT / "figures/mandel_finite_deformation.pdf")
    parser.add_argument("--normalized-biot-contour-output", type=Path, default=ROOT / "figures/mandel_normalized_biot_contours.pdf")
    args = parser.parse_args()

    pressure_rows = read_rows(args.pressure_csv)
    small_rows = read_profile_rows(args.small_load_csv)
    large_rows = read_rows(args.large_deformation_csv)
    contour_rows = read_rows(args.biot_contour_csv)
    plot_pressure(pressure_rows, args.pressure_output)
    plot_small_load(small_rows, args.displacement_output)
    plot_large_deformation(large_rows, args.finite_deformation_output)
    plot_normalized_biot_contours(contour_rows, args.normalized_biot_contour_output)

    print(args.pressure_output)
    print(args.displacement_output)
    print(args.finite_deformation_output)
    print(args.normalized_biot_contour_output)
    print(f"maximum platen compression: {max(-row['top_displacement'] / HEIGHT for row in large_rows):.6f}")
    print(f"maximum lateral expansion: {max(row['side_displacement'] / WIDTH for row in large_rows):.6f}")
    print(f"final average Biot coefficient: {large_rows[-1]['biot_average']:.9f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
