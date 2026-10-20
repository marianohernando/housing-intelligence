"use client";

import "maplibre-gl/dist/maplibre-gl.css";

import {
  Map as MapLibreMap,
  type MapLayerMouseEvent,
  NavigationControl,
  setWorkerUrl,
  type StyleSpecification,
} from "maplibre-gl";
import { useEffect, useRef, useState } from "react";

import {
  type AdminLevel,
  type AdminUnitProperties,
  adminUnitsUrl,
  DEFAULT_API_URL,
  describeLineage,
  describeUnit,
  type Lineage,
} from "@/lib/geo";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_URL;
const WORKER_URL = "/maplibre/maplibre-gl-worker.mjs"; // copied by scripts/copy-maplibre-worker.mjs
const LAYERS: { level: AdminLevel; simplify: number; fill: string; line: string; minzoom: number }[] = [
  { level: "municipio", simplify: 50, fill: "#d9d4c7", line: "#6b6353", minzoom: 0 },
  { level: "barrio", simplify: 10, fill: "#f0a35e", line: "#b5531c", minzoom: 9 },
];
const BLANK_STYLE: StyleSpecification = {
  version: 8,
  sources: {},
  layers: [{ id: "background", type: "background", paint: { "background-color": "#f6f4ef" } }],
};

export default function AdminMap() {
  const container = useRef<HTMLDivElement>(null);
  const [selected, setSelected] = useState<AdminUnitProperties | null>(null);
  const [lineage, setLineage] = useState<Lineage>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!container.current) return;
    setWorkerUrl(WORKER_URL);
    const map = new MapLibreMap({
      container: container.current,
      style: BLANK_STYLE,
      center: [-3.7, 40.42],
      zoom: 8,
      attributionControl: { compact: false, customAttribution: "Comunidad de Madrid — CC BY 4.0" },
    });
    map.addControl(new NavigationControl(), "top-right");

    map.on("load", async () => {
      for (const layer of LAYERS) {
        try {
          const response = await fetch(adminUnitsUrl(API_URL, layer.level, layer.simplify));
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          const body = await response.json();
          setLineage(body.data.lineage as Lineage);
          const id = `admin-${layer.level}`;
          map.addSource(id, { type: "geojson", data: { type: "FeatureCollection", features: body.data.features } });
          map.addLayer({ id: `${id}-fill`, type: "fill", source: id, minzoom: layer.minzoom, paint: { "fill-color": layer.fill, "fill-opacity": 0.45 } });
          map.addLayer({ id: `${id}-line`, type: "line", source: id, minzoom: layer.minzoom, paint: { "line-color": layer.line, "line-width": 0.8 } });
          map.on("click", `${id}-fill`, (event: MapLayerMouseEvent) => {
            const props = event.features?.[0]?.properties as AdminUnitProperties | undefined;
            if (props) setSelected({ ...props, area_km2: Number(props.area_km2), name: props.name || null });
          });
          map.on("mouseenter", `${id}-fill`, () => (map.getCanvas().style.cursor = "pointer"));
          map.on("mouseleave", `${id}-fill`, () => (map.getCanvas().style.cursor = ""));
        } catch (exc) {
          setError(`No se pudo cargar la capa ${layer.level}: ${(exc as Error).message}`);
        }
      }
    });
    return () => map.remove();
  }, []);

  const detail = selected ? describeUnit(selected) : null;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 320px", height: "100vh" }}>
      <div ref={container} role="region" aria-label="Mapa de unidades administrativas de la Comunidad de Madrid" />
      <aside aria-live="polite" style={{ padding: 16, borderLeft: "1px solid #ddd", fontFamily: "system-ui", overflowY: "auto" }}>
        <h1 style={{ fontSize: 18, margin: "0 0 8px" }}>Geografía canónica</h1>
        <p style={{ fontSize: 13, color: "#555", margin: "0 0 16px" }}>
          179 municipios y 131 barrios de Madrid desde el seccionado censal de la Comunidad de Madrid. Haz zoom y pulsa una zona.
        </p>
        {error && <p role="alert" style={{ color: "#a00", fontSize: 13 }}>{error}</p>}
        {detail ? (
          <section>
            <h2 style={{ fontSize: 16, margin: "0 0 8px" }}>{detail.title}</h2>
            <dl style={{ fontSize: 13, display: "grid", gridTemplateColumns: "auto 1fr", gap: "4px 12px" }}>
              {detail.rows.map(([k, v]) => (
                <div key={k} style={{ display: "contents" }}>
                  <dt style={{ color: "#666" }}>{k}</dt>
                  <dd style={{ margin: 0 }}>{v}</dd>
                </div>
              ))}
            </dl>
          </section>
        ) : (
          <p style={{ fontSize: 13 }}>Ninguna zona seleccionada.</p>
        )}
        <footer style={{ marginTop: 24, fontSize: 12, color: "#666" }}>
          <strong>Procedencia:</strong> {describeLineage(lineage) || "cargando…"}
        </footer>
      </aside>
    </div>
  );
}
