"use client";

import "maplibre-gl/dist/maplibre-gl.css";

import {
  Map as MapLibreMap,
  type MapLayerMouseEvent,
  NavigationControl,
  setWorkerUrl,
  type StyleSpecification,
} from "maplibre-gl";
import { useCallback, useEffect, useRef, useState } from "react";

import MapPanel, { PLACE_LAYERS, type PlaceLayer } from "@/components/MapPanel";
import { colorFor, type FeatureInfo, type FeatureValueRow, quantileBreaks } from "@/lib/features";
import { type AdminUnitProperties, adminUnitsUrl, DEFAULT_API_URL, type Lineage } from "@/lib/geo";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_URL;
const WORKER_URL = "/maplibre/maplibre-gl-worker.mjs"; // copied by scripts/copy-maplibre-worker.mjs
const DEFAULT_FEATURE = "renta_per_capita";
const BLANK_STYLE: StyleSpecification = {
  version: 8,
  sources: {},
  layers: [{ id: "background", type: "background", paint: { "background-color": "#f6f4ef" } }],
};

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(new URL(path, API_URL));
  if (!response.ok) throw new Error(`HTTP ${response.status} en ${path}`);
  return (await response.json()) as T;
}

export default function AdminMap() {
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const [ready, setReady] = useState(false);
  const [features, setFeatures] = useState<FeatureInfo[]>([]);
  const [featureId, setFeatureId] = useState(DEFAULT_FEATURE);
  const [values, setValues] = useState<Map<string, FeatureValueRow>>(new Map());
  const [breaks, setBreaks] = useState<number[]>([]);
  const [featureLineage, setFeatureLineage] = useState("");
  const [selected, setSelected] = useState<AdminUnitProperties | null>(null);
  const [lineage, setLineage] = useState<Lineage>({});
  const [layers, setLayers] = useState<Record<PlaceLayer, boolean>>({ education: false, health: false, social: false });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!container.current) return;
    setWorkerUrl(WORKER_URL);
    const map = new MapLibreMap({ container: container.current, style: BLANK_STYLE, center: [-3.7, 40.42], zoom: 8, attributionControl: { compact: false, customAttribution: "Comunidad de Madrid — CC BY 4.0" } });
    map.addControl(new NavigationControl(), "top-right");
    mapRef.current = map;
    map.on("load", async () => {
      try {
        for (const [level, simplify, minzoom] of [["municipio", 50, 0], ["barrio", 10, 10]] as const) {
          const body = await getJson<{ data: { features: GeoJSON.Feature[]; lineage: Lineage } }>(adminUnitsUrl(API_URL, level, simplify));
          setLineage(body.data.lineage);
          map.addSource(level, { type: "geojson", data: { type: "FeatureCollection", features: body.data.features }, promoteId: "admin_unit_id" });
          map.addLayer({ id: `${level}-fill`, type: "fill", source: level, minzoom, paint: { "fill-color": ["coalesce", ["feature-state", "color"], level === "barrio" ? "rgba(0,0,0,0)" : "#e8e4da"], "fill-opacity": 0.8 } });
          map.addLayer({ id: `${level}-line`, type: "line", source: level, minzoom, paint: { "line-color": level === "barrio" ? "#7a4a2a" : "#6b6353", "line-width": level === "barrio" ? 0.4 : 0.7 } });
          map.on("click", `${level}-fill`, (event: MapLayerMouseEvent) => {
            const props = event.features?.[0]?.properties as AdminUnitProperties | undefined;
            if (props) setSelected({ ...props, area_km2: Number(props.area_km2), name: props.name || null });
          });
        }
        setReady(true);
      } catch (exc) {
        setError(`No se pudo cargar la geografía: ${(exc as Error).message}`);
      }
    });
    getJson<{ data: FeatureInfo[] }>("/api/v1/features").then((b) => setFeatures(b.data)).catch((exc: Error) => setError(exc.message));
    return () => map.remove();
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) return;
    getJson<{ data: { values: FeatureValueRow[]; lineage: { dataset_versions?: Record<string, string> } } }>(`/api/v1/features/${featureId}/values`)
      .then((body) => {
        const rows = body.data.values;
        const known = rows.flatMap((r) => (r.value === null ? [] : [r.value]));
        const nextBreaks = quantileBreaks(known);
        for (const row of rows) {
          if (row.admin_unit_id) map.setFeatureState({ source: "municipio", id: row.admin_unit_id }, { color: colorFor(row.value, nextBreaks) });
        }
        setBreaks(nextBreaks);
        setValues(new Map(rows.map((r) => [r.admin_unit_id ?? r.territory_code, r])));
        setFeatureLineage(Object.entries(body.data.lineage.dataset_versions ?? {}).map(([d, v]) => `${d} ${v}`).join(" · "));
      })
      .catch((exc: Error) => setError(`No se pudo cargar el indicador: ${exc.message}`));
  }, [featureId, ready]);

  const toggle = useCallback(async (id: PlaceLayer) => {
    const map = mapRef.current;
    const next = !layers[id];
    setLayers((prev) => ({ ...prev, [id]: next }));
    if (!map) return;
    if (!map.getSource(`places-${id}`)) {
      const body = await getJson<{ data: GeoJSON.FeatureCollection }>(`/api/v1/places?category=${id}`);
      map.addSource(`places-${id}`, { type: "geojson", data: body.data });
      const color = PLACE_LAYERS.find((l) => l.id === id)?.color ?? "#000";
      map.addLayer({ id: `places-${id}`, type: "circle", source: `places-${id}`, paint: { "circle-radius": ["interpolate", ["linear"], ["zoom"], 8, 1.5, 13, 5], "circle-color": color, "circle-stroke-color": "#fff", "circle-stroke-width": 0.5 } });
    }
    map.setLayoutProperty(`places-${id}`, "visibility", next ? "visible" : "none");
  }, [layers]);

  const municipioId = selected ? (selected.level === "municipio" ? selected.admin_unit_id : null) : null;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", height: "100vh" }}>
      <div ref={container} role="region" aria-label="Mapa de la Comunidad de Madrid por municipios y barrios" />
      <MapPanel
        features={features}
        featureId={featureId}
        onFeature={setFeatureId}
        breaks={breaks}
        selected={selected}
        selectedValue={municipioId ? values.get(municipioId) ?? null : null}
        lineage={lineage}
        featureLineage={featureLineage}
        layers={layers}
        onToggle={(id) => void toggle(id)}
        error={error}
      />
    </div>
  );
}
