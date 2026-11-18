/**
 * Places for «Trabajo en» (pure, unit tested): CRTM stations (metro, Cercanías, Metro Ligero)
 * from /api/v1/places and the zones of the map, found by name without an external geocoder.
 */
import type { ScenarioState } from "@/contracts/scenario_state";
import { speaksToMany, voice } from "@/lib/fit";
import { titleCase } from "@/lib/names";
import type { PlaceFeature } from "@/lib/map/places";
import { homeLabel, type OlderPlaceKind } from "@/lib/scenario";
import { type ZoneCollection, type ZoneGeometry, ringArea, searchable } from "@/lib/map/zones";

/** Station subcategories of /api/v1/places, with the word that goes after their name. */
export const STATION_KINDS: Record<string, string> = { metro: "metro", cercanias: "Cercanías", metro_ligero: "Metro Ligero" };

export interface WorkPlace {
  id: string;
  /** What the search and the zone card call it («Nuevos Ministerios (metro)»). */
  label: string;
  /** Kind of place, shown next to the name in the list («Metro», «Municipio»). */
  kind: string;
  lat: number;
  lon: number;
}

const capitalize = (text: string) => text.charAt(0).toUpperCase() + text.slice(1);

/** One entry per station name and kind: the source repeats a station once per platform or line. */
export function stationPlaces(features: readonly PlaceFeature[]): WorkPlace[] {
  const seen = new Map<string, WorkPlace>();
  for (const f of features) {
    const word = STATION_KINDS[f.properties.subcategory ?? ""];
    const [lon, lat] = f.geometry.coordinates;
    if (!word || lon === undefined || lat === undefined) continue;
    const name = titleCase(f.properties.name);
    const label = `${name} (${word})`;
    if (!seen.has(label)) seen.set(label, { id: `estacion:${label}`, label, kind: capitalize(word), lat, lon });
  }
  return [...seen.values()];
}

/** Centre of mass of the largest polygon: a point inside ordinary zones, for the distance in a straight line. */
export function centroidOf(geometry: ZoneGeometry): [lon: number, lat: number] | null {
  const rings = (geometry.type === "Polygon" ? [geometry.coordinates] : geometry.coordinates).map((p) => p[0] ?? []);
  const ring = rings.reduce<GeoJSON.Position[]>((best, r) => (Math.abs(ringArea(r)) > Math.abs(ringArea(best)) ? r : best), []);
  const area = ringArea(ring);
  if (area === 0) return null;
  let cx = 0;
  let cy = 0;
  for (let i = 0; i < ring.length - 1; i += 1) {
    const [x1 = 0, y1 = 0] = ring[i] ?? [];
    const [x2 = 0, y2 = 0] = ring[i + 1] ?? [];
    const cross = x1 * y2 - x2 * y1;
    cx += (x1 + x2) * cross;
    cy += (y1 + y2) * cross;
  }
  return [cx / (6 * area), cy / (6 * area)];
}

/** The zones of the map as places: municipios, and Madrid's districts with the city in brackets. */
export function zonePlaces(zones: ZoneCollection): WorkPlace[] {
  return zones.features.flatMap((f) => {
    const centre = centroidOf(f.geometry);
    if (!centre) return [];
    const { level, name, municipio_name, zone_key } = f.properties;
    const district = level === "distrito";
    return [
      {
        id: `zona:${zone_key}`,
        label: district ? `${name} (${municipio_name})` : name,
        kind: district ? `Distrito de ${municipio_name}` : "Municipio",
        lon: centre[0],
        lat: centre[1],
      },
    ];
  });
}

/** Places whose name contains what was typed (no accents, any case): names that start with it first. */
export function findPlaces(places: readonly WorkPlace[], query: string, limit = 8): WorkPlace[] {
  const wanted = searchable(query);
  if (wanted.length < 2) return [];
  const scored = places.flatMap((p) => {
    const text = searchable(p.label);
    const at = text.indexOf(wanted);
    return at < 0 ? [] : [{ p, score: at === 0 ? 0 : 1 }];
  });
  scored.sort((a, b) => a.score - b.score || a.p.label.localeCompare(b.p.label, "es"));
  return scored.slice(0, limit).map((s) => s.p);
}

/**
 * The option the arrows move to in a list of `length` (ARIA combobox): -1 is none, down from none
 * goes to the first, up from none to the last, and both wrap around.
 */
export function stepActive(current: number, step: 1 | -1, length: number): number {
  if (length === 0) return -1;
  if (current < 0) return step === 1 ? 0 : length - 1;
  return (current + step + length) % length;
}

/**
 * lugar.* of pitch/textos_web.md (D-244): «Somos mayores» is asked where they want to live, in place
 * of «Trabajo en», in the household's words (`voice`): «¿Cerca de dónde quieres vivir?», «Donde vivo
 * ahora» and «Cerca de mi familia» to one person who lives alone; «queréis», «vivimos» and «nuestra»
 * to more. «Puedes cambiarlo» stays: it speaks to whoever fills in the form, as the rest of it does
 * (D-245 §11).
 */
export function olderPlaceText(scenario: ScenarioState) {
  const v = voice(speaksToMany(scenario.household));
  const tu = capitalize(v.tu);
  return {
    title: `¿Cerca de dónde ${v.quieres} vivir?`,
    // The name of the two options, not the question again (review H7 of PR #79)
    which: `${tu} casa de ahora o ${v.tu} familia`,
    // «Donde vivo ahora» is the label the place takes (homeLabel), so the option and the place say the same
    options: { other: capitalize(homeLabel(scenario)), family: `Cerca de ${v.mi} familia` } satisfies Record<OlderPlaceKind, string>,
    search: { other: `¿Dónde ${v.vives} ahora?`, family: `¿Dónde vive ${v.tu} familia?` } satisfies Record<OlderPlaceKind, string>,
    help: `Miramos cuánto se tarda en transporte público hasta ese sitio, llegando a las 9:00 de un día laborable, y contamos el trayecto como si ${v.fueras} 3 días a la semana. Ponemos 30 min como mucho: puedes cambiarlo o quitarlo.`,
    // A family place picked before this field knew its name (a shared link): said in plain words
    family: `${tu} familia`,
  };
}
