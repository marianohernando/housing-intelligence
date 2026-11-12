import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import type { ZoneGapList } from "@/contracts/zone_gap_list_response";

import {
  type AdminFeature,
  boundsOf,
  buildZoneCollection,
  edgeWall,
  findZone,
  isWholeCity,
  maskAround,
  outlinePoints,
  regionOf,
  ringArea,
  wholeCities,
  type ZoneCollection,
  zoneDirectory,
  type ZoneFeature,
  zoneHref,
  zonePropertiesOf,
} from "../map/zones";

function square(x: number, y: number, size = 1): GeoJSON.Polygon {
  return {
    type: "Polygon",
    coordinates: [
      [
        [x, y],
        [x + size, y],
        [x + size, y + size],
        [x, y + size],
        [x, y],
      ],
    ],
  };
}

function unit(level: string, code: string, name: string, parent: string | null, geometry: GeoJSON.Geometry): AdminFeature {
  const id = `ES.28.${level === "municipio" ? "MUN" : "DIS"}.${code}`;
  return {
    type: "Feature",
    id,
    geometry: geometry as AdminFeature["geometry"],
    properties: { admin_unit_id: id, level, code, name, parent, area_km2: 1 },
  };
}

// Names as /api/v1/geo/admin-units returns them since 12c834a: already readable.
const municipios = [
  unit("municipio", "28079", "Madrid", null, square(0, 0, 2)),
  unit("municipio", "28092", "Mostoles", null, square(-2, -2)),
  unit("municipio", "28127", "Las Rozas de Madrid", null, square(-2, 2)),
];
const distritos = [
  unit("distrito", "2807901", "Centro", "ES.28.MUN.28079", square(0, 0)),
  unit("distrito", "2807905", "Chamartín", "ES.28.MUN.28079", square(1, 1)),
  unit("distrito", "2809201", "Mostoles — distrito censal 01", "ES.28.MUN.28092", square(-2, -2)),
];

describe("buildZoneCollection", () => {
  const zones = buildZoneCollection(municipios, distritos);

  it("splits Madrid capital into its districts and keeps the other municipios whole", () => {
    expect(zones.features.map((f) => f.properties.zone_key)).toEqual([
      "municipio/28092",
      "municipio/28127",
      "distrito/2807901",
      "distrito/2807905",
    ]);
  });

  it("splits the municipios named by admin_unit_id (the ids asked with ?parent=)", () => {
    const keys = buildZoneCollection(municipios, distritos, ["ES.28.MUN.28092"]).features.map((f) => f.properties.zone_key);
    expect(keys).toEqual(["municipio/28079", "municipio/28127", "distrito/2809201"]);
  });

  it("keeps the API's readable names and remembers the municipio of each district", () => {
    expect(findZone(zones, "municipio", "28127")?.properties.name).toBe("Las Rozas de Madrid");
    const chamartin = findZone(zones, "distrito", "2807905");
    expect(chamartin?.properties).toMatchObject({ name: "Chamartín", municipio_name: "Madrid" });
  });

  it("keeps admin_unit_id as the feature id (promoteId of the map layers)", () => {
    expect(zones.features.every((f) => f.id === f.properties.admin_unit_id)).toBe(true);
  });

  it("returns undefined for an unknown zone", () => {
    expect(findZone(zones, "distrito", "2807999")).toBeUndefined();
  });
});

describe("zone helpers", () => {
  it("lists the points of every outer ring, to frame the whole zone (holes do not matter)", () => {
    const hole = [
      [0.4, 0.4],
      [0.6, 0.4],
      [0.6, 0.6],
      [0.4, 0.4],
    ];
    const multi: GeoJSON.MultiPolygon = {
      type: "MultiPolygon",
      coordinates: [[...square(0, 0).coordinates, hole], square(5, 5).coordinates],
    };
    expect(outlinePoints(multi)).toHaveLength(10);
    expect(outlinePoints(square(1, 2))).toContainEqual([2, 3]);
  });

  it("links a zone to its screen", () => {
    expect(zoneHref({ level: "distrito", code: "2807905" })).toBe("/zona/distrito/2807905");
  });

  it("computes the bounds of polygons and multipolygons", () => {
    expect(boundsOf(square(1, 2, 3))).toEqual([1, 2, 4, 5]);
    const multi: GeoJSON.MultiPolygon = { type: "MultiPolygon", coordinates: [square(0, 0).coordinates, square(5, 5).coordinates] };
    expect(boundsOf(multi)).toEqual([0, 0, 6, 6]);
  });

  it("builds a mask whose holes wind opposite to its outer ring", () => {
    const multi: GeoJSON.MultiPolygon = { type: "MultiPolygon", coordinates: [square(0, 0).coordinates, square(5, 5).coordinates] };
    const mask = maskAround(multi);
    const [outer, ...holes] = mask.coordinates;
    expect(holes).toHaveLength(2);
    for (const hole of holes) expect(Math.sign(ringArea(hole))).toBe(-Math.sign(ringArea(outer ?? [])));
  });
});

describe("regionOf", () => {
  it("joins every zone into one multipolygon, to fade what lies outside the region", () => {
    const zones = buildZoneCollection(municipios, distritos);
    const region = regionOf(zones);
    expect(region.type).toBe("MultiPolygon");
    expect(region.coordinates).toHaveLength(zones.features.length);
    expect(maskAround(region).coordinates).toHaveLength(zones.features.length + 1);
  });
});

describe("edgeWall", () => {
  // A ~1 km square near Madrid, in both windings
  const ccw = square(-3.7, 40.45, 0.01);
  const cw: GeoJSON.Polygon = { type: "Polygon", coordinates: [[...(ccw.coordinates[0] ?? [])].reverse()] };

  function inside([x, y]: GeoJSON.Position, ring: GeoJSON.Position[]): boolean {
    let hit = false;
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i, i += 1) {
      const [xi = 0, yi = 0] = ring[i] ?? [];
      const [xj = 0, yj = 0] = ring[j] ?? [];
      if (yi > (y ?? 0) !== yj > (y ?? 0) && (x ?? 0) < ((xj - xi) * ((y ?? 0) - yi)) / (yj - yi) + xi) hit = !hit;
    }
    return hit;
  }

  /** Middle of the wall's far side: the two offset corners of each quad. */
  function farMiddle(quad: GeoJSON.Polygon): GeoJSON.Position {
    const [, , c = [], d = []] = quad.coordinates[0] ?? [];
    return [((c[0] ?? 0) + (d[0] ?? 0)) / 2, ((c[1] ?? 0) + (d[1] ?? 0)) / 2];
  }

  it("builds one thin quad per side of the outline", () => {
    const wall = edgeWall(ccw, 20);
    expect(wall.features).toHaveLength(4);
    for (const quad of wall.features) expect(quad.geometry.coordinates[0]).toHaveLength(5);
  });

  it("puts the wall just outside the zone, whatever the ring winding", () => {
    for (const zone of [ccw, cw]) {
      const ring = zone.coordinates[0] ?? [];
      for (const quad of edgeWall(zone, 20).features) expect(inside(farMiddle(quad.geometry), ring)).toBe(false);
    }
  });

  it("offsets the wall by its width in metres", () => {
    const [quad] = edgeWall(ccw, 20).features;
    const [a = [], , , d = []] = quad?.geometry.coordinates[0] ?? [];
    const metres = Math.hypot(((d[0] ?? 0) - (a[0] ?? 0)) * 111320 * Math.cos((40.45 * Math.PI) / 180), ((d[1] ?? 0) - (a[1] ?? 0)) * 111320);
    expect(metres).toBeCloseTo(20, 0);
  });

  it("walls every part of a multipolygon", () => {
    const multi: GeoJSON.MultiPolygon = { type: "MultiPolygon", coordinates: [ccw.coordinates, square(-3.6, 40.45, 0.01).coordinates] };
    expect(edgeWall(multi, 20).features).toHaveLength(8);
  });
});

describe("zoneDirectory", () => {
  const zones = buildZoneCollection(
    [...municipios, unit("municipio", "28006", "Alcobendas", null, square(3, 3))],
    distritos,
  );

  it("lists Madrid's districts and the other municipios apart, each by name", () => {
    const { distritos: d, municipios: m } = zoneDirectory(zones, "");
    expect(d.map((z) => z.name)).toEqual(["Centro", "Chamartín"]);
    expect(m.map((z) => z.name)).toEqual(["Alcobendas", "Las Rozas de Madrid", "Mostoles"]);
  });

  it("filters by name ignoring case and accents", () => {
    expect(zoneDirectory(zones, "chamartin").distritos.map((z) => z.name)).toEqual(["Chamartín"]);
    expect(zoneDirectory(zones, "  ROZAS ").municipios.map((z) => z.name)).toEqual(["Las Rozas de Madrid"]);
    expect(zoneDirectory(zones, "zzz")).toEqual({ distritos: [], municipios: [] });
  });
});

describe("whole cities (Madrid capital, shown by its districts)", () => {
  const district = (code: string): ZoneFeature => ({
    type: "Feature",
    id: code,
    geometry: { type: "Polygon", coordinates: [] },
    properties: { admin_unit_id: `d${code}`, level: "distrito", code, name: code, municipio_name: "Madrid", zone_key: `distrito/${code}` },
  });

  it("names the split municipio after its districts and knows its id", () => {
    const zones: ZoneCollection = { type: "FeatureCollection", features: [district("2807901"), district("2807905")] };
    expect(wholeCities(zones)).toEqual([{ admin_unit_id: "ES.28.MUN.28079", code: "28079", name: "Madrid" }]);
    expect(isWholeCity("ES.28.MUN.28079")).toBe(true);
    expect(isWholeCity("ES.28.MUN.28092")).toBe(false);
    expect(isWholeCity(null)).toBe(false);
  });

  it("gives none when the districts are not loaded", () => {
    expect(wholeCities({ type: "FeatureCollection", features: [] })).toEqual([]);
  });
});

describe("zonePropertiesOf (the zone screen before the outlines)", () => {
  // Test fixtures published by line A with the contract (data/fixtures/contracts), not demo data.
  const fixture = (name: string) =>
    JSON.parse(readFileSync(new URL(`../../../../../data/fixtures/contracts/${name}.fixture.json`, import.meta.url), "utf8")) as ZoneGapList;

  it("names a municipio and a Madrid district as the outlines would", () => {
    expect(zonePropertiesOf(fixture("zone_gap_list.el_alamo").zone)).toEqual({
      admin_unit_id: "ES.28.MUN.28004",
      level: "municipio",
      code: "28004",
      name: "El Álamo",
      municipio_name: "El Álamo",
      zone_key: "municipio/28004",
    });
    const district = { level: "distrito", code: "2807905", name: "Chamartín", admin_unit_id: "ES.28.DIS.2807905", municipio_name: "Madrid" };
    expect(zonePropertiesOf(district)).toMatchObject({ municipio_name: "Madrid", level: "distrito" });
    expect(zonePropertiesOf(district)?.zone_key).toBe(`${district.level}/${district.code}`);
  });

  it("is null for levels the map has not, or without an id to ask for its places", () => {
    expect(zonePropertiesOf({ level: "seccion_censal", code: "2807905001", name: "x", admin_unit_id: "ES.28.SEC.2807905001" })).toBeNull();
    expect(zonePropertiesOf({ level: "municipio", code: "28004", name: "El Álamo" })).toBeNull();
    expect(zonePropertiesOf({ level: "distrito", code: "2807905", name: "Chamartín", admin_unit_id: "ES.28.DIS.2807905" })).toBeNull();
  });
});
