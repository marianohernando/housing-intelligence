/**
 * The single ScenarioState of the search (CLAUDE.md §13: chips, filters and map share one
 * state). Pure helpers, unit tested; the shape is the generated contract type.
 */
import type { Anchor, BudgetKind, NearbyNeed, NeedKey, PriorityKey, ScenarioState, SearchScope } from "@/contracts/scenario_state";

/**
 * «¿Dónde?» (D-238): the whole region, or one of its three parts by the statistical zoning of the
 * Comunidad de Madrid (Madrid capital, its four metropolitan zones, the rest).
 */
export const SCOPES: readonly SearchScope[] = ["all", "madrid", "alrededores", "pueblos"];

/** donde.toda, donde.madrid, donde.alrededores, donde.pueblos */
export const SCOPE_LABEL: Record<SearchScope, string> = {
  all: "Toda la Comunidad",
  madrid: "Madrid capital",
  alrededores: "Alrededores de Madrid",
  pueblos: "Pueblos",
};

export function scopeOf(s: Pick<ScenarioState, "scope">): SearchScope {
  return s.scope ?? "all";
}

/**
 * «Toda la Comunidad» leaves `scope` out: a search without it means the whole region, so the
 * example, a shared link and an API that does not know the field all keep working.
 */
export function setScope(s: ScenarioState, scope: SearchScope): ScenarioState {
  const next: ScenarioState = { ...s, scope };
  if (scope === "all") delete next.scope;
  return next;
}

/**
 * Slider ranges, inside the contract ranges (RENT_RANGE_EUR, BUY_RANGE_EUR). Each starts at one
 * of its quick amounts, so the button of that amount shows as chosen.
 */
export const BUDGET_RANGE: Record<BudgetKind, { min: number; max: number; step: number; initial: number }> = {
  rent: { min: 300, max: 5_000, step: 50, initial: 1_200 },
  buy: { min: 50_000, max: 2_000_000, step: 10_000, initial: 250_000 },
};

/**
 * The amounts offered with one tap (UX mobile audit, A1: a 94-step slider is hard to hit with an
 * unsteady finger). The slider stays, and «Otra cantidad» takes any amount of its range.
 */
export const QUICK_BUDGETS: Record<BudgetKind, readonly number[]> = {
  rent: [600, 900, 1_200, 1_500],
  buy: [150_000, 250_000, 400_000, 600_000],
};

const LIMITS = { minors: 8, seniors: 4 } as const;
const WALK_LIMITS = { min: 1, max: 60, initial: 10 } as const;
const PRIORITY_KEYS: readonly PriorityKey[] = ["transporte", "salud", "colegios", "zonas_verdes", "seguridad", "sin_escaleras", "ocio"];

export function defaultScenario(): ScenarioState {
  return {
    schema_version: 2,
    budget: { kind: "rent", amount_eur: BUDGET_RANGE.rent.initial },
    // «Lo normal para tu hogar», said as in the example, so going back to it is the same search
    min_floor_area_m2: null,
    household: { adults: 1, minors: 0, minor_ages: [], seniors_in_care: 0 },
    anchors: [],
    nearby: [],
    priorities: [],
  };
}

const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value));

function household(s: ScenarioState) {
  return { adults: 1, minors: 0, minor_ages: [], seniors_in_care: 0, ...s.household };
}

export function peopleAtHome(s: ScenarioState): number {
  const h = household(s);
  return h.adults + h.minors + h.seniors_in_care;
}

export function setAdults(s: ScenarioState, adults: 1 | 2): ScenarioState {
  return relabelHome({ ...s, household: { ...household(s), adults } });
}

export function setMinors(s: ScenarioState, minors: number): ScenarioState {
  // Ages must list every child or be empty: a new count forgets the old ages.
  return relabelHome({ ...s, household: { ...household(s), minors: clamp(Math.round(minors), 0, LIMITS.minors), minor_ages: [] } });
}

export function setSeniors(s: ScenarioState, seniors: number): ScenarioState {
  return relabelHome({ ...s, household: { ...household(s), seniors_in_care: clamp(Math.round(seniors), 0, LIMITS.seniors) } });
}

/** «Somos mayores» (D-244): the adults of the household are 65 or older. */
export function isOlderHousehold(s: Pick<ScenarioState, "household">): boolean {
  return s.household?.seniors === true;
}

/** What «Somos mayores» marks in «¿Qué quieres tener cerca?» (D-244), in this order; each one can be taken away. */
export const OLDER_PRIORITIES: readonly PriorityKey[] = ["salud", "sin_escaleras", "transporte"];

/**
 * Marks or unmarks «Somos mayores» (D-244). It adds no one to the household (unlike the people
 * looked after, `seniors_in_care`). Marked, OLDER_PRIORITIES join what matters, after what was
 * already marked, and a search of the whole region with no place to go starts in Madrid capital
 * (without a place, small well-served villages would come first, D-243 §13). Unmarked, the field
 * leaves the scenario, as it was before, and so does «Donde vivimos ahora» (an `other` place only
 * this flow makes, which no field shows without it: it would filter unseen, review H1 of PR #79).
 * What stays, in view for the person to change: Madrid capital, what it marked and a family place,
 * which «Más opciones» shows.
 */
export function setOlderHousehold(s: ScenarioState, on: boolean): ScenarioState {
  const home = { ...household(s) };
  if (!on) {
    delete home.seniors;
    return { ...s, household: home, anchors: (s.anchors ?? []).filter((a) => kindOf(a) !== "other") };
  }
  const priorities = s.priorities ?? [];
  const older: ScenarioState = {
    ...s,
    household: { ...home, seniors: true },
    priorities: [...priorities, ...OLDER_PRIORITIES.filter((p) => !priorities.includes(p))],
  };
  const noPlace = (s.anchors ?? []).length === 0;
  return noPlace && scopeOf(s) === "all" ? setScope(older, "madrid") : older;
}

/**
 * Marks or unmarks a priority; the order of marking is the order of importance. «Ocio» (D-236)
 * comes with its groups: marked, it starts with LEISURE_INITIAL; unmarked, it takes them all away.
 */
export function togglePriority(s: ScenarioState, key: PriorityKey): ScenarioState {
  const current = s.priorities ?? [];
  const on = !current.includes(key);
  const priorities = on ? [...current, key] : current.filter((p) => p !== key);
  if (key !== "ocio") return { ...s, priorities };
  const others = (s.nearby ?? []).filter((n) => !isLeisure(n.need));
  const groups = on ? LEISURE_INITIAL.map((need) => leisureNeed(need, LEISURE_DEFAULT)) : [];
  return { ...s, priorities, nearby: [...others, ...groups] };
}

/** The groups of «Ocio» (importa.ocio.*), in the order of its boxes: the leisure NeedKeys of the contract. */
export const LEISURE_KEYS = ["bares", "restaurantes", "gimnasios", "cultura"] as const satisfies readonly NeedKey[];
export type LeisureKey = (typeof LEISURE_KEYS)[number];
/** What most people asked for, ticked when «Ocio» is marked; the person can change it. */
const LEISURE_INITIAL: readonly LeisureKey[] = ["bares", "restaurantes"];
/** Minutes offered for «Ocio»; one value for all its groups. */
export const LEISURE_MINUTES: readonly number[] = [5, 10, 15];

export interface LeisureConfig {
  groups: LeisureKey[];
  minutes: number;
  required: boolean;
}
/** «Me importa» ranks and never filters: «Imprescindible» is opt-in, since OSM misses places in small villages (D-236). */
const LEISURE_DEFAULT: Omit<LeisureConfig, "groups"> = { minutes: 10, required: false };

function isLeisure(need: NeedKey): need is LeisureKey {
  return (LEISURE_KEYS as readonly NeedKey[]).includes(need);
}

function leisureNeed(need: LeisureKey, { minutes, required }: Omit<LeisureConfig, "groups">): NearbyNeed {
  return { need, max_walk_minutes: minutes, required };
}

/** What the «Ocio» configurator shows: the ticked groups and the minutes and «Imprescindible» they share. */
export function leisureConfig(s: ScenarioState): LeisureConfig {
  const chosen = (s.nearby ?? []).filter((n) => isLeisure(n.need));
  const [first] = chosen;
  return {
    groups: LEISURE_KEYS.filter((key) => chosen.some((n) => n.need === key)),
    minutes: first?.max_walk_minutes ?? LEISURE_DEFAULT.minutes,
    required: first?.required ?? LEISURE_DEFAULT.required,
  };
}

/** The scenario with this «Ocio»: its groups go to `nearby`, after the other services and in the order of the boxes. */
function withLeisure(s: ScenarioState, config: LeisureConfig): ScenarioState {
  const others = (s.nearby ?? []).filter((n) => !isLeisure(n.need));
  const groups = LEISURE_KEYS.filter((key) => config.groups.includes(key)).map((key) => leisureNeed(key, config));
  return { ...s, nearby: [...others, ...groups] };
}

export function toggleLeisureGroup(s: ScenarioState, key: LeisureKey): ScenarioState {
  const config = leisureConfig(s);
  const groups = config.groups.includes(key) ? config.groups.filter((g) => g !== key) : [...config.groups, key];
  return withLeisure(s, { ...config, groups });
}

export function setLeisureMinutes(s: ScenarioState, minutes: number): ScenarioState {
  return withLeisure(s, { ...leisureConfig(s), minutes: clamp(Math.round(minutes), WALK_LIMITS.min, WALK_LIMITS.max) });
}

export function setLeisureRequired(s: ScenarioState, required: boolean): ScenarioState {
  return withLeisure(s, { ...leisureConfig(s), required });
}

/** The services of «Lo quiero a un paseo»: every NeedKey but the groups of «Ocio», which have their own boxes. */
export type ServiceKey = Exclude<NeedKey, LeisureKey>;
export type NearbyService = NearbyNeed & { need: ServiceKey };

export function nearbyServices(s: ScenarioState): NearbyService[] {
  return (s.nearby ?? []).filter((n): n is NearbyService => !isLeisure(n.need));
}

export function setBudgetKind(s: ScenarioState, kind: BudgetKind): ScenarioState {
  if (s.budget?.kind === kind) return s;
  return { ...s, budget: { kind, amount_eur: BUDGET_RANGE[kind].initial } };
}

export function setBudgetAmount(s: ScenarioState, amount: number): ScenarioState {
  const kind = s.budget?.kind ?? "rent";
  const { min, max, step } = BUDGET_RANGE[kind];
  return { ...s, budget: { kind, amount_eur: clamp(Math.round(amount / step) * step, min, max) } };
}

/**
 * «Otra cantidad»: the euros the person types («900», «1.250», «1 250 €»), as they are, or null
 * when it is not a whole number inside the slider's range (the field then says which range).
 */
export function typedBudget(text: string, kind: BudgetKind): number | null {
  const digits = text.replace(/[.\s€]/g, "");
  if (!/^\d+$/.test(digits)) return null;
  const amount = Number(digits);
  const { min, max } = BUDGET_RANGE[kind];
  return amount >= min && amount <= max ? amount : null;
}

/** A typed amount goes as typed, not rounded to the slider's step; `typedBudget` has checked its range. */
export function setTypedBudget(s: ScenarioState, amount: number): ScenarioState {
  return { ...s, budget: { kind: s.budget?.kind ?? "rent", amount_eur: amount } };
}

/**
 * What the API assumes with `min_floor_area_m2: null` (D-214): the median useful floor area of the
 * homes of households of each size in the Comunidad de Madrid (Censo 2021), 5 or more people as
 * 5. A copy of MEDIAN_FLOOR_AREA_M2 in hi_domain/affordability.py, checked by a test.
 */
export const HOUSEHOLD_FLOOR_AREA_M2: Readonly<Record<1 | 2 | 3 | 4 | 5, number>> = { 1: 61, 2: 68, 3: 71, 4: 77, 5: 77 };

/** m² offered in «Para unos 68 m² (cámbialo)»; a value from a shared link outside them is offered too. */
export const FLOOR_AREA_RANGE = { min: 40, max: 150, step: 5 } as const;
/** Contract range of `min_floor_area_m2` (hi_contracts ScenarioState). */
const FLOOR_AREA_LIMITS = { min: 15, max: 400 } as const;

/** The m² the search prices a home at: the person's, or the usual for their household (`household` true). */
export interface FloorArea {
  m2: number;
  household: boolean;
}

export function floorArea(s: Pick<ScenarioState, "household" | "min_floor_area_m2">): FloorArea {
  if (s.min_floor_area_m2 != null) return { m2: s.min_floor_area_m2, household: false };
  const h = s.household ?? {};
  const people = clamp((h.adults ?? 1) + (h.minors ?? 0) + (h.seniors_in_care ?? 0), 1, 5) as 1 | 2 | 3 | 4 | 5;
  return { m2: HOUSEHOLD_FLOOR_AREA_M2[people], household: true };
}

export function floorAreaOptions(current: number | null | undefined): number[] {
  const { min, max, step } = FLOOR_AREA_RANGE;
  const steps = Array.from({ length: (max - min) / step + 1 }, (_, i) => min + i * step);
  return [...new Set([...steps, ...(current == null ? [] : [current])])].sort((a, b) => a - b);
}

/** The m² of the home; null is «Lo normal para tu hogar», what the API derives from the household. */
export function setFloorArea(s: ScenarioState, m2: number | null): ScenarioState {
  const min_floor_area_m2 = m2 === null ? null : clamp(Math.round(m2), FLOOR_AREA_LIMITS.min, FLOOR_AREA_LIMITS.max);
  return { ...s, min_floor_area_m2 };
}

/** presupuesto.sin_limite (`budget: null`); turned off, the budget starts again as renting. */
export function setNoBudgetLimit(s: ScenarioState, noLimit: boolean): ScenarioState {
  if (noLimit) return { ...s, budget: null };
  return s.budget ? s : { ...s, budget: { kind: "rent", amount_eur: BUDGET_RANGE.rent.initial } };
}

/** «Lo quiero a un paseo» (cerca.*): services the household wants within walking minutes. */
export const NEED_KEYS: readonly ServiceKey[] = ["escuela_infantil", "colegio", "centro_salud", "farmacia", "mayores", "transporte"];
/** Contract range of a work commute (Anchor.max_minutes). */
const COMMUTE_LIMITS = { min: 5, max: 120 } as const;
/** Minutes offered in the selector; a value from the API outside them is offered too. */
export const WALK_MINUTES: readonly number[] = [5, 10, 15, 20, 30];

export function walkMinutesOptions(current: number | undefined, offered: readonly number[] = WALK_MINUTES): number[] {
  const all = new Set([...offered, ...(current === undefined ? [] : [current])]);
  return [...all].sort((a, b) => a - b);
}

/** A new service starts at 10 min and as a must («Imprescindible»), the contract defaults. */
export function addNearby(s: ScenarioState, need: NeedKey): ScenarioState {
  const nearby = s.nearby ?? [];
  if (nearby.some((n) => n.need === need)) return s;
  return { ...s, nearby: [...nearby, { need, max_walk_minutes: WALK_LIMITS.initial, required: true }] };
}

export function removeNearby(s: ScenarioState, need: NeedKey): ScenarioState {
  return { ...s, nearby: (s.nearby ?? []).filter((n) => n.need !== need) };
}

function changeNearby(s: ScenarioState, need: NeedKey, change: (n: NearbyNeed) => NearbyNeed): ScenarioState {
  return { ...s, nearby: (s.nearby ?? []).map((n) => (n.need === need ? change(n) : n)) };
}

export function setNearbyMinutes(s: ScenarioState, need: NeedKey, minutes: number): ScenarioState {
  const max_walk_minutes = clamp(Math.round(minutes), WALK_LIMITS.min, WALK_LIMITS.max);
  return changeNearby(s, need, (n) => ({ ...n, max_walk_minutes }));
}

export function setNearbyRequired(s: ScenarioState, need: NeedKey, required: boolean): ScenarioState {
  return changeNearby(s, need, (n) => ({ ...n, required }));
}

/** A place picked for «Trabajo en» or «Cerca de mi familia o amigos»: a name and a point. */
export interface Place {
  label: string;
  lat: number;
  lon: number;
}

/**
 * The places the search asks for: where the person works and, optionally, where family or friends
 * live; with «Somos mayores», where they live now (`other`, D-244).
 */
export type PlaceKind = "work" | "family" | "other";

/** Their order in `anchors`: the earlier a place, the more its trip weighs in the fit (the work place first). */
const PLACE_KINDS: readonly PlaceKind[] = ["work", "family", "other"];
const kindOf = (a: Anchor) => a.kind ?? "work";
/** Position of a place in `anchors`; kinds the web does not edit (from a shared link) go last. */
const placeOrder = (a: Anchor) => (PLACE_KINDS as readonly string[]).indexOf(kindOf(a)) + 1 || PLACE_KINDS.length + 1;
const LABEL_MAX = 80;

/** The place of a kind, if the search has one. */
export function placeOf(s: ScenarioState, kind: PlaceKind): Anchor | null {
  return (s.anchors ?? []).find((a) => kindOf(a) === kind) ?? null;
}

function changePlace(s: ScenarioState, kind: PlaceKind, change: (a: Anchor) => Anchor): ScenarioState {
  return { ...s, anchors: (s.anchors ?? []).map((a) => (kindOf(a) === kind ? change(a) : a)) };
}

/**
 * Sets (or with null, removes) the place of a kind. It goes without a minutes limit (`max_minutes:
 * null`, «Sin límite») until the person picks one in «Tardar como mucho». The zone card says how far
 * each zone is either way, except for a work place with «Teletrabajo total» and no limit: that trip
 * neither scores nor limits, so it is not shown (D-240).
 */
export function setPlace(s: ScenarioState, kind: PlaceKind, place: Place | null): ScenarioState {
  const kept = (s.anchors ?? []).filter((a) => kindOf(a) !== kind);
  const picked: Anchor[] = place ? [{ kind, label: place.label.slice(0, LABEL_MAX), lat: place.lat, lon: place.lon, max_minutes: null }] : [];
  return { ...s, anchors: [...picked, ...kept].sort((a, b) => placeOrder(a) - placeOrder(b)) };
}

/** Minutes offered in «Tardar como mucho» (trabajo.max_min); a value from a shared link outside them is offered too. */
export const COMMUTE_MINUTES: readonly number[] = [30, 45, 60, 90];

export function commuteMinutesOptions(current: number | null | undefined): number[] {
  const all = new Set([...COMMUTE_MINUTES, ...(current == null ? [] : [current])]);
  return [...all].sort((a, b) => a - b);
}

/** The trip limit of a place; null is «Sin límite». Without the place there is nothing to limit. */
export function setPlaceMaxMinutes(s: ScenarioState, kind: PlaceKind, minutes: number | null): ScenarioState {
  const max_minutes = minutes === null ? null : clamp(Math.round(minutes), COMMUTE_LIMITS.min, COMMUTE_LIMITS.max);
  return changePlace(s, kind, (a) => ({ ...a, max_minutes }));
}

/** «Trabajo en», if the search has one. */
export const workPlace = (s: ScenarioState) => placeOf(s, "work");
export const setWorkPlace = (s: ScenarioState, place: Place | null) => setPlace(s, "work", place);
export const setWorkMaxMinutes = (s: ScenarioState, minutes: number | null) => setPlaceMaxMinutes(s, "work", minutes);

/** Days offered in «¿Cuántos días vas a la oficina?» (trabajo.dias); 0 is «Teletrabajo total». */
export const OFFICE_DAYS: readonly number[] = [5, 4, 3, 2, 1, 0];
/** Up to this many days a week the trip to work weighs half in the fit (FEW_DAYS_PER_WEEK of hi_domain/fit.py, D-240). */
export const FEW_OFFICE_DAYS = 2;
const DAYS_LIMITS = { min: 0, max: 7, usual: 5 } as const;

/** Days a week the person goes to the work place; the contract default (5) until they say otherwise. */
export function officeDays(anchor: Anchor): number {
  return anchor.days_per_week ?? DAYS_LIMITS.usual;
}

/** The days offered, most first; a value from a shared link outside them (6 or 7) is offered too. */
export function officeDaysOptions(current: number): number[] {
  return [...new Set([...OFFICE_DAYS, current])].sort((a, b) => b - a);
}

/**
 * Days a week at the work place (`days_per_week`, D-240). The limit stays as it was: with 0
 * («Teletrabajo total») the trip is not scored, but a limit the person set still applies.
 */
export function setWorkDays(s: ScenarioState, days: number): ScenarioState {
  const days_per_week = clamp(Math.round(days), DAYS_LIMITS.min, DAYS_LIMITS.max);
  return changePlace(s, "work", (a) => ({ ...a, days_per_week }));
}

/**
 * The demo case (portada.ejemplo.boton): a couple with 2 children who work on the Castellana.
 * Same as line A's golden profile (data/fixtures/contracts/scenario_state.familia_castellana.fixture.json),
 * checked by a test, with the work place without a limit (`max_minutes: null`): its figures are the pitch's.
 */
export function exampleScenario(): ScenarioState {
  return {
    schema_version: 2,
    budget: { kind: "rent", amount_eur: 1500 },
    min_floor_area_m2: null,
    household: { adults: 2, minors: 2, minor_ages: [4, 8], seniors_in_care: 0 },
    anchors: [{ kind: "work", label: "Paseo de la Castellana (Azca)", lon: -3.693, lat: 40.45, days_per_week: 4, max_minutes: null }],
    nearby: [{ need: "colegio", max_walk_minutes: 10, required: true }],
    priorities: ["colegios", "transporte", "salud"],
  };
}

/**
 * The second example of the portada (D-244, Mariano's design): a retired couple renting up to
 * 1.200 € a month who want to live near their family in Ciudad Lineal, 30 min by public transport
 * as most, in Madrid capital, with what «Somos mayores» marks. The point is the Ciudad Lineal metro
 * station of GET /api/v1/places, a public place, never a home address.
 */
export function retiredExampleScenario(): ScenarioState {
  return {
    schema_version: 2,
    scope: "madrid",
    budget: { kind: "rent", amount_eur: 1_200 },
    min_floor_area_m2: null,
    household: { adults: 2, minors: 0, minor_ages: [], seniors_in_care: 0, seniors: true },
    anchors: [{ kind: "family", label: "Ciudad Lineal (metro)", lon: -3.63816, lat: 40.43805, ...OLDER_TRIP }],
    nearby: [],
    priorities: [...OLDER_PRIORITIES],
  };
}

/**
 * «¿Cerca de dónde queréis vivir?» (D-244), in place of «Trabajo en» for «Somos mayores»: where
 * they live now (`other`, said as HOME_LABEL, never the place's own name) or near their family.
 * The trip goes with 30 min as a limit the person can change, and 3 days a week, so it weighs as
 * a place they go to often.
 */
export type OlderPlaceKind = "other" | "family";
/**
 * Lower case: the API says it inside a sentence («27 min en transporte público hasta donde vivo
 * ahora…», H7). In the household's words, as `voice` of lib/fit.ts: «vivo» when one person lives at
 * home, «vivimos» when more (speaksToMany, the same count as peopleAtHome).
 */
export const HOME_LABEL = { one: "donde vivo ahora", many: "donde vivimos ahora" } as const;
export const OLDER_TRIP = { max_minutes: 30, days_per_week: 3 } as const;

/** The label of «Donde vivo ahora» / «Donde vivimos ahora» for this household. */
export function homeLabel(s: ScenarioState): string {
  return peopleAtHome(s) > 1 ? HOME_LABEL.many : HOME_LABEL.one;
}

const HOME_LABELS: readonly string[] = Object.values(HOME_LABEL);

/**
 * Once the household changes, or a shared link is opened (decodeScenario), «donde vivo ahora» says
 * «vivimos» (and back), so the field, the facts and «¿Quieres ver más zonas?» of the API keep the
 * household's words. Only the labels this flow
 * gives: another `other` place (from a shared link) keeps its own.
 */
function relabelHome(s: ScenarioState): ScenarioState {
  const label = homeLabel(s);
  const stale = (a: Anchor) => kindOf(a) === "other" && HOME_LABELS.includes(a.label) && a.label !== label;
  if (!(s.anchors ?? []).some(stale)) return s;
  return { ...s, anchors: (s.anchors ?? []).map((a) => (stale(a) ? { ...a, label } : a)) };
}

/** The place of «¿Cerca de dónde queréis vivir?», if the search has one. */
export function olderPlace(s: ScenarioState): { kind: OlderPlaceKind; anchor: Anchor } | null {
  for (const kind of ["other", "family"] as const) {
    const anchor = placeOf(s, kind);
    if (anchor) return { kind, anchor };
  }
  return null;
}

/** Sets (or with null, removes) the place of «¿Cerca de dónde queréis vivir?»: one place, of one of its two kinds. */
export function setOlderPlace(s: ScenarioState, kind: OlderPlaceKind, place: Place | null): ScenarioState {
  const kept = (s.anchors ?? []).filter((a) => kindOf(a) !== "other" && kindOf(a) !== "family");
  if (!place) return { ...s, anchors: kept };
  const label = kind === "other" ? homeLabel(s) : place.label.slice(0, LABEL_MAX);
  const picked: Anchor = { kind, label, lat: place.lat, lon: place.lon, ...OLDER_TRIP };
  return { ...s, anchors: [...kept, picked].sort((a, b) => placeOrder(a) - placeOrder(b)) };
}

/**
 * The same point as the other kind: «Donde vivimos ahora» or near the family, keeping the limit.
 * `familyLabel` names the family's place (the place picked, if the field still knows it).
 */
export function setOlderPlaceKind(s: ScenarioState, kind: OlderPlaceKind, familyLabel: string): ScenarioState {
  const current = olderPlace(s);
  if (!current || current.kind === kind) return s;
  const label = kind === "other" ? homeLabel(s) : familyLabel.slice(0, LABEL_MAX);
  const moved: Anchor = { ...current.anchor, kind, label };
  const kept = (s.anchors ?? []).filter((a) => a !== current.anchor);
  return { ...s, anchors: [...kept, moved].sort((a, b) => placeOrder(a) - placeOrder(b)) };
}

function toBase64Url(text: string): string {
  let binary = "";
  for (const byte of new TextEncoder().encode(text)) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function fromBase64Url(text: string): string {
  const binary = atob(text.replace(/-/g, "+").replace(/_/g, "/"));
  return new TextDecoder().decode(Uint8Array.from(binary, (c) => c.charCodeAt(0)));
}

export function encodeScenario(s: ScenarioState): string {
  return toBase64Url(JSON.stringify(s));
}

function isScenario(value: unknown): value is ScenarioState {
  if (typeof value !== "object" || value === null) return false;
  const s = value as ScenarioState;
  const h = s.household;
  return (
    s.schema_version === 2 &&
    (h === undefined || (Number.isInteger(h.adults) && Number.isInteger(h.minors ?? 0))) &&
    (s.priorities ?? []).every((p) => PRIORITY_KEYS.includes(p)) &&
    (s.scope === undefined || SCOPES.includes(s.scope)) &&
    (s.budget == null || ((s.budget.kind === "rent" || s.budget.kind === "buy") && Number.isFinite(s.budget.amount_eur)))
  );
}

/** The scenario in a shared link, or null if the text is not a valid one (the API validates again). */
export function decodeScenario(text: string): ScenarioState | null {
  try {
    const value: unknown = JSON.parse(fromBase64Url(text));
    // A link made before «donde vivo ahora» (or by hand) says the place in the household's words too
    return isScenario(value) ? relabelHome(value) : null;
  } catch {
    return null;
  }
}
