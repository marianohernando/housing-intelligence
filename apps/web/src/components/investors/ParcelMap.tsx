"use client";

import "maplibre-gl/dist/maplibre-gl.css";

// MapLibre loads after the page (import() below), as in VidaMap: only its types are imported here.
import type { GeoJSONSource, Map as MapLibreMap } from "maplibre-gl";
import { useEffect, useRef, useState } from "react";

import { baseStyle, MAP_PALETTE_TOKENS, mapGlyphsUrl, mapTilesSource, type MapPalette } from "@/lib/map/style";
import { SEARCH_TEXT as TEXT } from "@/lib/parcels";

import styles from "./Parcels.module.css";

const WORKER_URL = "/maplibre/maplibre-gl-worker.mjs"; // copied by scripts/copy-maplibre-worker.mjs
const MAP_TILES_URL = process.env.NEXT_PUBLIC_MAP_TILES_URL;
const MAP_GLYPHS_URL = process.env.NEXT_PUBLIC_MAP_GLYPHS_URL;
/** Madrid capital: where the map opens and how far it may go (the search covers the city only) */
const CENTER: [number, number] = [-3.7038, 40.4168];
const BOUNDS: [[number, number], [number, number]] = [
  [-4.0, 40.25],
  [-3.4, 40.7],
];
const PICK = "parcel-pick";

function readPalette(): MapPalette {
  const css = getComputedStyle(document.documentElement);
  const entries = Object.entries(MAP_PALETTE_TOKENS).map(([key, token]) => [key, css.getPropertyValue(`--${token}`).trim()]);
  return Object.fromEntries(entries) as MapPalette;
}

function point(lon: number, lat: number): GeoJSON.FeatureCollection {
  return { type: "FeatureCollection", features: [{ type: "Feature", properties: {}, geometry: { type: "Point", coordinates: [lon, lat] } }] };
}

interface Props {
  /** A click on the map: the point the person chose */
  onPick: (lat: number, lon: number) => void;
}

/**
 * «En el mapa» (D-250): a small map of Madrid capital with the app's base style; a click marks the
 * point and hands it over. The basemap's citation goes in a line under it, at the size of the text.
 */
export default function ParcelMap({ onPick }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const pickRef = useRef(onPick);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    pickRef.current = onPick;
  }, [onPick]);

  useEffect(() => {
    const element = container.current;
    if (!element) return;
    let map: MapLibreMap | null = null;
    let cancelled = false;
    import("maplibre-gl")
      .then((lib) => {
        if (cancelled) return;
        try {
          lib.setWorkerUrl(WORKER_URL);
          map = new lib.Map({
            container: element,
            style: baseStyle(readPalette(), mapTilesSource(MAP_TILES_URL, window.location.origin), mapGlyphsUrl(MAP_GLYPHS_URL, window.location.origin)),
            center: CENTER,
            zoom: 11.5,
            minZoom: 10,
            maxBounds: BOUNDS,
            attributionControl: false,
            locale: { "Map.Title": TEXT.mapAria },
          });
        } catch {
          setFailed(true);
          return;
        }
        const created = map;
        created.on("load", () => {
          const palette = readPalette();
          created.addSource(PICK, { type: "geojson", data: { type: "FeatureCollection", features: [] } });
          created.addLayer({
            id: PICK,
            type: "circle",
            source: PICK,
            paint: {
              "circle-radius": 9,
              "circle-color": palette.violetStrong,
              "circle-stroke-color": "#ffffff",
              "circle-stroke-width": 3,
            },
          });
        });
        created.on("click", (event) => {
          const { lng, lat } = event.lngLat;
          (created.getSource(PICK) as GeoJSONSource | undefined)?.setData(point(lng, lat));
          pickRef.current(lat, lng);
        });
      })
      .catch(() => setFailed(true));
    return () => {
      cancelled = true;
      map?.remove();
    };
  }, []);

  if (failed) return <p className={styles.mapFailed}>{TEXT.mapNoWebgl}</p>;
  return (
    <div className={styles.mapBox}>
      <div ref={container} className={styles.map} />
      <p className={styles.mapCredits}>
        Mapa:{" "}
        <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">
          © OpenStreetMap<span className="visually-hidden"> (se abre en una pestaña nueva)</span>
        </a>{" "}
        ·{" "}
        <a href="https://openfreemap.org" target="_blank" rel="noopener noreferrer">
          OpenFreeMap<span className="visually-hidden"> (se abre en una pestaña nueva)</span>
        </a>
      </p>
    </div>
  );
}
