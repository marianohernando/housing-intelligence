import { describe, expect, it } from "vitest";

import type { PlaceFeature } from "../map/places";
import type { ZoneCollection, ZoneFeature, ZoneLevel } from "../map/zones";
import { centroidOf, findPlaces, stationPlaces, stepActive, zonePlaces } from "../workPlaces";

function station(name: string, subcategory: string, lon = -3.69, lat = 40.45): PlaceFeature {
  return {
    type: "Feature",
    geometry: { type: "Point", coordinates: [lon, lat] },
    properties: { name, category: "transport", subcategory, municipio: "28079", seccion: null },
  };
}

function zone(level: ZoneLevel, code: string, name: string, municipio: string): ZoneFeature {
  return {
    type: "Feature",
    geometry: square,
    properties: { admin_unit_id: code, level, code, name, municipio_name: municipio, zone_key: `${level}/${code}` },
  };
}

const square: GeoJSON.Polygon = {
  type: "Polygon",
  coordinates: [
    [
      [0, 0],
      [2, 0],
      [2, 2],
      [0, 2],
      [0, 0],
    ],
  ],
};

describe("stationPlaces", () => {
  it("names each station readably with its kind, once per name and kind", () => {
    const places = stationPlaces([
      station("NUEVOS MINISTERIOS", "metro"),
      station("NUEVOS MINISTERIOS", "metro"),
      station("Nuevos Ministerios", "cercanias"),
      station("BERNA", "metro_ligero"),
      station("Parada 123", "autobus"),
    ]);
    expect(places.map((p) => [p.label, p.kind])).toEqual([
      ["Nuevos Ministerios (metro)", "Metro"],
      ["Nuevos Ministerios (Cercanías)", "Cercanías"],
      ["Berna (Metro Ligero)", "Metro Ligero"],
    ]);
  });
});

describe("centroidOf and zonePlaces", () => {
  it("puts the point at the centre of mass of the largest polygon", () => {
    const small: GeoJSON.Position[] = [
      [10, 10],
      [10.1, 10],
      [10.1, 10.1],
      [10, 10],
    ];
    expect(centroidOf(square)).toEqual([1, 1]);
    expect(centroidOf({ type: "MultiPolygon", coordinates: [[small], square.coordinates] })).toEqual([1, 1]);
    expect(centroidOf({ type: "Polygon", coordinates: [] })).toBeNull();
  });

  it("turns the zones of the map into places, districts with their city", () => {
    const zones: ZoneCollection = {
      type: "FeatureCollection",
      features: [zone("distrito", "2807905", "Chamartín", "Madrid"), zone("municipio", "28006", "Alcobendas", "Alcobendas")],
    };
    expect(zonePlaces(zones).map((p) => [p.label, p.kind, p.lon, p.lat])).toEqual([
      ["Chamartín (Madrid)", "Distrito de Madrid", 1, 1],
      ["Alcobendas", "Municipio", 1, 1],
    ]);
  });
});

describe("findPlaces", () => {
  const places = stationPlaces([
    station("SANTIAGO BERNABEU", "metro"),
    station("BERNA", "metro_ligero"),
    station("Chamartín", "cercanias"),
  ]);

  it("finds by any part of the name, without accents or case, names that start with it first", () => {
    expect(findPlaces(places, "berna").map((p) => p.label)).toEqual(["Berna (Metro Ligero)", "Santiago Bernabeu (metro)"]);
    expect(findPlaces(places, "CHAMARTIN").map((p) => p.label)).toEqual(["Chamartín (Cercanías)"]);
  });

  it("waits for two letters and keeps the list short", () => {
    expect(findPlaces(places, "b")).toEqual([]);
    expect(findPlaces(places, "a", 1)).toEqual([]);
    expect(findPlaces(places, "ber", 1)).toHaveLength(1);
  });
});

describe("stepActive (arrows in the list of places)", () => {
  it("starts from none: down goes to the first, up to the last", () => {
    expect(stepActive(-1, 1, 3)).toBe(0);
    expect(stepActive(-1, -1, 3)).toBe(2);
  });

  it("wraps around at both ends and is none in an empty list", () => {
    expect(stepActive(2, 1, 3)).toBe(0);
    expect(stepActive(0, -1, 3)).toBe(2);
    expect(stepActive(1, 1, 3)).toBe(2);
    expect(stepActive(0, 1, 0)).toBe(-1);
  });
});
