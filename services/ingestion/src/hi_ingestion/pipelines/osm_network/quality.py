"""QA for the walking graph: not truncated, connected, positive lengths, inside the region."""

import numpy as np

from hi_contracts.catalog.pipeline import OsmWalkNetworkPipeline
from hi_domain.geo.bounds import COMUNIDAD_MADRID_BBOX
from hi_ingestion.pipelines.osm_network.network import TO_25830, NetworkResult
from hi_ingestion.pipelines.places.quality import CheckResult, QualityReport

MIN_NODES_INSIDE_REGION_BBOX = 0.95


def _share_inside_region(result: NetworkResult) -> float:
    network = result.network
    if network.n_nodes == 0:
        return 0.0
    lon, lat = TO_25830.transform(network.node_x, network.node_y, direction="INVERSE")
    box = COMUNIDAD_MADRID_BBOX
    lon, lat = np.asarray(lon), np.asarray(lat)
    inside = (
        (lon >= box.min_lon) & (lon <= box.max_lon) & (lat >= box.min_lat) & (lat <= box.max_lat)
    )
    return float(inside.mean())


def run_network_quality(result: NetworkResult, spec: OsmWalkNetworkPipeline) -> QualityReport:
    network = result.network
    lengths = network.edge_length_m
    component_share = network.main_component_share()
    inside = _share_inside_region(result)
    segments = network.n_edges + len(result.quarantine)
    return QualityReport(
        [
            CheckResult(
                "has_network",
                True,
                network.n_nodes > 0 and network.n_edges > 0,
                {"nodes": network.n_nodes, "edges": network.n_edges},
            ),
            CheckResult(
                "edge_lengths_positive",
                True,
                bool(network.n_edges) and bool((lengths > 0).all()),
                {"max_edge_m": round(float(lengths.max()), 1) if network.n_edges else None},
            ),
            CheckResult(
                "total_length_plausible",
                True,
                network.total_km >= spec.min_total_km,
                {"total_km": round(network.total_km, 1), "min_total_km": spec.min_total_km},
            ),
            CheckResult(
                "main_component_share",
                True,
                component_share >= spec.min_main_component_share,
                {
                    "share_of_length": round(component_share, 4),
                    "min": spec.min_main_component_share,
                },
            ),
            CheckResult(
                "missing_node_locations",
                True,
                len(result.quarantine) <= 0.001 * max(segments, 1),
                {"quarantined_segments": len(result.quarantine), "segments": segments},
            ),
            CheckResult(
                "nodes_inside_region_bbox",
                False,
                inside >= MIN_NODES_INSIDE_REGION_BBOX,
                {
                    "share": round(inside, 4),
                    "note": "the Geofabrik extract is padded beyond the regional limit",
                },
            ),
            CheckResult("length_by_highway", False, True, {"km": network.km_by_highway()}),
        ]
    )
