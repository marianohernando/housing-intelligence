import { describe, expect, it } from "vitest";

import {
  type AdminFeature,
  boundsOf,
  buildZoneCollection,
  findZone,
  maskAround,
  regionOf,
  ringArea,
  zoneHref,
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

const municipios = [
  unit("municipio", "28079", "MADRID", null, square(0, 0, 2)),
  unit("municipio", "28092", "MOSTOLES", null, square(-2, -2)),
  unit("municipio", "28127", "ROZAS DE MADRID, LAS", null, square(-2, 2)),
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

  it("uses readable names and remembers the municipio of each district", () => {
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
