"""Gate 1/2 evidence artifacts for the admin boundaries pipeline."""

import json
from pathlib import Path
from typing import Any

import geopandas as gpd

from hi_ingestion.pipelines.admin_boundaries.h3map import H3Mapping
from hi_ingestion.pipelines.admin_boundaries.transform import to_wgs84


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n")


def render_sample(
    path: Path, units: gpd.GeoDataFrame, mapping: H3Mapping, zones: list[dict[str, Any]]
) -> None:
    """Visual QA: municipalities, Madrid barrios, H3 r8 around the centre and golden points."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    u = to_wgs84(units)
    fig, (ax_region, ax_city) = plt.subplots(1, 2, figsize=(14, 7))
    u[u["level"] == "municipio"].boundary.plot(ax=ax_region, linewidth=0.3, color="#555")
    u[u["level"] == "barrio"].boundary.plot(ax=ax_region, linewidth=0.2, color="#c33")
    barrios = u[u["level"] == "barrio"]
    barrios.boundary.plot(ax=ax_city, linewidth=0.4, color="#c33")
    r8 = mapping.cells[mapping.cells["resolution"] == 8]
    if not barrios.empty:
        minx, miny, maxx, maxy = barrios.total_bounds
        window = r8.cx[minx:maxx, miny:maxy]
        window.boundary.plot(ax=ax_city, linewidth=0.15, color="#36c")
        ax_city.set_xlim(minx, maxx)
        ax_city.set_ylim(miny, maxy)
    for zone in zones:
        for ax in (ax_region, ax_city):
            ax.plot(zone["lon"], zone["lat"], "k*", markersize=7)
        ax_region.annotate(zone["zone_id"], (zone["lon"], zone["lat"]), fontsize=6)
    ax_region.set_title("Comunidad de Madrid — municipios (gris) y barrios de Madrid (rojo)")
    ax_city.set_title("Madrid capital — barrios + H3 r8 (azul) + puntos golden")
    for ax in (ax_region, ax_city):
        ax.set_aspect("equal")
        ax.set_axis_off()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
