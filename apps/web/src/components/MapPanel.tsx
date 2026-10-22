"use client";

import type { AdminUnitProperties, Lineage } from "@/lib/geo";
import { describeLineage, describeUnit } from "@/lib/geo";
import type { FeatureInfo, FeatureValueRow } from "@/lib/features";
import { classColor, describeValue, formatValue, UNKNOWN_COLOR } from "@/lib/features";

export type PlaceLayer = "education" | "health" | "social";
export const PLACE_LAYERS: { id: PlaceLayer; label: string; color: string }[] = [
  { id: "education", label: "Centros educativos", color: "#2b6cb0" },
  { id: "health", label: "Atención primaria y hospitales", color: "#2f855a" },
  { id: "social", label: "Servicios para mayores", color: "#805ad5" },
];

interface Props {
  features: FeatureInfo[];
  featureId: string;
  onFeature: (id: string) => void;
  breaks: number[];
  selected: AdminUnitProperties | null;
  selectedValue: FeatureValueRow | null;
  lineage: Lineage;
  featureLineage: string;
  layers: Record<PlaceLayer, boolean>;
  onToggle: (id: PlaceLayer) => void;
  error: string | null;
}

function legendLabel(index: number, breaks: number[], unit: string): string {
  if (breaks.length === 0) return "";
  if (index === 0) return `< ${formatValue(breaks[0] as number, unit)}`;
  const low = breaks[index - 1];
  return low === undefined ? "" : `≥ ${formatValue(low, unit)}`;
}

export default function MapPanel(props: Props) {
  const info = props.features.find((f) => f.feature_id === props.featureId);
  const unit = props.selected ? describeUnit(props.selected) : null;
  return (
    <aside style={{ padding: 16, borderLeft: "1px solid #ddd", fontFamily: "system-ui", overflowY: "auto", fontSize: 13 }}>
      <h1 style={{ fontSize: 18, margin: "0 0 8px" }}>Comunidad de Madrid</h1>
      <label htmlFor="feature" style={{ display: "block", fontWeight: 600, marginBottom: 4 }}>Indicador por municipio</label>
      <select id="feature" value={props.featureId} onChange={(e) => props.onFeature(e.target.value)} style={{ width: "100%", padding: 6 }}>
        {props.features.filter((f) => f.public_use).map((f) => (
          <option key={f.feature_id} value={f.feature_id}>{f.human_name}</option>
        ))}
      </select>
      {info && (
        <figure aria-label="Leyenda" style={{ margin: "12px 0" }}>
          {Array.from({ length: props.breaks.length + 1 }, (_, i) => {
            const text = legendLabel(i, props.breaks, info.unit);
            const color = classColor(i, props.breaks.length + 1);
            return (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <span aria-hidden style={{ width: 14, height: 14, background: color, display: "inline-block" }} />
                <span>{text}</span>
              </div>
            );
          })}
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span aria-hidden style={{ width: 14, height: 14, background: UNKNOWN_COLOR, display: "inline-block" }} />
            <span>Sin dato publicado (no es cero)</span>
          </div>
          <figcaption style={{ color: "#666", marginTop: 6 }}>{info.limitations[0]}</figcaption>
        </figure>
      )}
      {props.error && <p role="alert" style={{ color: "#a00" }}>{props.error}</p>}
      <section aria-live="polite" style={{ margin: "12px 0" }}>
        {unit ? (
          <>
            <h2 style={{ fontSize: 16, margin: "0 0 6px" }}>{unit.title}</h2>
            {info && props.selectedValue && <p style={{ margin: "0 0 6px" }}><strong>{info.human_name}:</strong> {describeValue(props.selectedValue, info)}</p>}
            <dl style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: "4px 12px", margin: 0 }}>
              {unit.rows.map(([k, v]) => (
                <div key={k} style={{ display: "contents" }}><dt style={{ color: "#666" }}>{k}</dt><dd style={{ margin: 0 }}>{v}</dd></div>
              ))}
            </dl>
          </>
        ) : (
          <p>Pulsa un municipio o un barrio.</p>
        )}
      </section>
      <fieldset style={{ border: "1px solid #ddd", padding: 8 }}>
        <legend>Equipamientos</legend>
        {PLACE_LAYERS.map((layer) => (
          <label key={layer.id} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <input type="checkbox" checked={props.layers[layer.id]} onChange={() => props.onToggle(layer.id)} />
            <span aria-hidden style={{ width: 10, height: 10, borderRadius: 5, background: layer.color, display: "inline-block" }} />
            {layer.label}
          </label>
        ))}
      </fieldset>
      <footer style={{ marginTop: 16, fontSize: 12, color: "#666" }}>
        <strong>Procedencia:</strong> {describeLineage(props.lineage) || "cargando…"}
        {props.featureLineage && <div>Indicador: {props.featureLineage}</div>}
      </footer>
    </aside>
  );
}
