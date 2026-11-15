import {
  Briefcase,
  Bus,
  CircleQuestionMark,
  CircleX,
  Cross,
  Euro,
  GraduationCap,
  Info,
  type LucideIcon,
  Shield,
  TrainFront,
  Trees,
  Wine,
} from "lucide-react";
import { useId } from "react";

import type { FactKind, FactTopic, SearchResult } from "@/contracts/search_response";
import { useDatasets } from "@/components/provenance/useDatasets";
import Help from "@/components/ui/Help";
import { type ConfidenceText, confidenceText } from "@/lib/confidence";
import {
  constraintLabels,
  factText,
  hasWalkingFact,
  rankText,
  rentReferenceAvailable,
  resultScope,
  WALK_MEDIAN,
  zoneFit,
  zoneWord,
} from "@/lib/fit";
import { tieText } from "@/lib/match";
import { SCOPE_LABEL } from "@/lib/scenario";
import { FAILS_UNNAMED, joinShortfalls, shortfalls } from "@/lib/shortfall";

import styles from "./ZoneCard.module.css";

// Copy from pitch/textos_web.md (zona.puesto, zona.empate in lib/match.ts, zona.hechos.titulo, resultados.casi.* and
// zona.no_cumple in lib/shortfall.ts, zona.condicion.sin_dato, confianza.aria). buySource (zona.compra.sin_precio) says
// why a zone may have no purchase price (D-227, D-234).
const TEXT = {
  facts: "Lo que tienes aquí",
  unknown: "No lo sabemos: nos falta el dato para comprobar lo que pides. No lo damos por bueno.",
  // zona.compra.sin_precio (D-227, D-234): why this zone has no purchase price, by its level. Never
  // a promise of an estimate: with the code deployed before the sync a district has none yet
  buySource: {
    municipio:
      "Sin precio de compra en esta zona: el valor tasado del Ministerio de Vivienda solo se publica para los municipios de más de 25.000 habitantes.",
    madrid: "Sin precio de compra en esta zona: el valor tasado del Ministerio de Vivienda se publica para Madrid entero, no por distrito ni por barrio.",
  },
  // zona.sin_alquiler (D-238, D-242): the same for renting in a municipio; districts and barrios bring their own reason.
  // With the Ministry's reference published (D-242), only the municipios with very few rented homes lack it
  rentSource: {
    reference: "Con «Alquilar», puede faltar el alquiler: en los municipios con muy pocas viviendas alquiladas no se publica su precio.",
    cm: "Con «Alquilar», puede faltar el alquiler: la Comunidad de Madrid solo lo publica para los municipios de más de 20.000 habitantes, y casi ningún pueblo los tiene.",
  },
  // zona.fuera (D-238): a zone of the map outside «¿Dónde?»
  outside: (scope: string) => `Fuera de tu búsqueda (${scope}).`,
  confidence: (label: string) => `Fiabilidad del dato: ${label}`,
  // confianza.ayuda: what «Dato fiable» and the others mean, behind a button instead of a tooltip
  confidenceHelp: "¿Qué quiere decir «Dato fiable»?",
  confidenceAbout: "Lo que tienes aquí",
};

/** The confidence words of the facts, once each, in the order they appear. */
function confidenceLevels(confidences: readonly number[]): ConfidenceText[] {
  return [...new Map(confidences.map((c) => confidenceText(c)).map((t) => [t.label, t])).values()];
}

const TOPIC_ICON: Record<FactTopic, LucideIcon> = {
  coste: Euro,
  transporte: Bus,
  salud: Cross,
  colegios: GraduationCap,
  zonas_verdes: Trees,
  seguridad: Shield,
  // The station the fact measures, not a wheelchair (D-204): the same icon as the chip
  accesibilidad: TrainFront,
  ocio: Wine, // the same icon as the chip «Ocio» (D-236)
  trayecto: Briefcase,
  otro: Info,
};

const KIND_CLASS: Record<FactKind, string | undefined> = {
  strength: styles.strength,
  weakness: styles.weakness,
  unknown: styles.unknownFact,
};

/**
 * What the search says about the zone: its place in the ranking, the conditions it fails or
 * cannot be checked, and its facts with their confidence in words. Everything comes from the API.
 */
export default function FitDetails({ result, zoneKey }: { result: SearchResult; zoneKey: string }) {
  const factsId = useId();
  const { data: datasets } = useDatasets();
  const { match, ranked } = zoneFit(result, zoneKey);
  const scope = resultScope(result);
  if (!match) return scope === "all" ? null : <p className={styles.hint}>{TEXT.outside(SCOPE_LABEL[scope])}</p>;
  // F5 of fit-0.9: what it lacks in plain words («Se pasa unos 120 € al mes de tu presupuesto»), as in «Casi valen»
  const fails = joinShortfalls(
    shortfalls({ failed_constraints: match.failed_constraints, constraints: ranked?.constraints }, constraintLabels(result), result.scenario),
  );
  const word = zoneWord(result);
  const tie = match.passes_all ? tieText(match, result.all_zones, word, result.results) : null;
  const buying = result.scenario.budget?.kind === "buy";
  const rentingInMunicipio = result.scenario.budget?.kind === "rent" && zoneKey.startsWith("municipio/");

  return (
    <>
      {match.passes_all && ranked && <p className={styles.rank}>{rankText(ranked.rank, word)}</p>}
      {tie && <p className={styles.tie}>{tie}</p>}
      {match.match_pct != null && !match.passes_all && (
        <p className={styles.fails}>
          <CircleX size={18} aria-hidden="true" />
          {fails ? (
            <span>
              <span aria-hidden="true">{fails.text}</span>
              <span className="visually-hidden">{fails.aria}</span>
            </span>
          ) : (
            <span>{FAILS_UNNAMED}</span>
          )}
        </p>
      )}
      {match.match_pct == null && (
        <p className={styles.unknown}>
          <CircleQuestionMark size={18} aria-hidden="true" />
          <span>{TEXT.unknown}</span>
        </p>
      )}
      {/* Buying, only a zone with no price says why (D-234): one with its price may be unknown for another condition */}
      {match.match_pct == null && buying && match.estimated_cost_eur == null && (
        <p className={styles.unknownWhy}>{zoneKey.startsWith("municipio/") ? TEXT.buySource.municipio : TEXT.buySource.madrid}</p>
      )}
      {match.match_pct == null && rentingInMunicipio && <p className={styles.unknownWhy}>{rentReferenceAvailable(datasets?.datasets) ? TEXT.rentSource.reference : TEXT.rentSource.cm}</p>}
      {ranked && ranked.facts.length > 0 && (
        <section className={styles.facts} aria-labelledby={factsId}>
          <h3 id={factsId}>{TEXT.facts}</h3>
          <ul>
            {ranked.facts.map((fact, i) => {
              // A fact with a topic or kind this web does not know yet (fit-0.9 and later) still shows, with the «otro» icon
              const Icon = TOPIC_ICON[fact.topic] ?? Info;
              const confidence = confidenceText(fact.confidence);
              return (
                <li key={`${i}-${fact.topic}`} className={KIND_CLASS[fact.kind]}>
                  <Icon size={18} aria-hidden="true" />
                  <span>
                    {factText(fact, buying)}{" "}
                    <small>
                      <span aria-hidden="true">· {confidence.label}</span>
                      <span className="visually-hidden">{TEXT.confidence(confidence.label)}</span>
                    </small>
                  </span>
                </li>
              );
            })}
          </ul>
          {hasWalkingFact(ranked.facts) && <p className={styles.hint}>{WALK_MEDIAN}</p>}
        </section>
      )}
      {/* After the facts, outside their list: what each confidence word means */}
      {ranked && ranked.facts.length > 0 && (
        <Help about={TEXT.confidenceAbout} label={TEXT.confidenceHelp}>
          <ul>
            {confidenceLevels(ranked.facts.map((f) => f.confidence)).map((level) => (
              <li key={level.label}>
                <strong>{level.label}:</strong> {level.help}
              </li>
            ))}
          </ul>
        </Help>
      )}
    </>
  );
}
