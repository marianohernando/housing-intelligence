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
} from "lucide-react";
import { useId } from "react";

import type { FactKind, FactTopic, SearchResult } from "@/contracts/search_response";
import { confidenceText } from "@/lib/confidence";
import { constraintLabels, failedLabels, hasWalkingFact, rankText, resultScope, WALK_MEDIAN, zoneFit, zoneWord } from "@/lib/fit";
import { SCOPE_LABEL } from "@/lib/scenario";

import styles from "./ZoneCard.module.css";

// Copy from pitch/textos_web.md (zona.puesto, zona.hechos.titulo, zona.cerca_de_encajar.motivo,
// zona.condicion.sin_dato, confianza.aria). «No cumple todo lo que pides» is zona.no_cumple. buySource
// (zona.compra.sin_precio) says why a zone may have no purchase price (D-227, D-234).
const TEXT = {
  facts: "Lo que tienes aquí",
  fails: "No cumple:",
  failsUnnamed: "No cumple todo lo que pides.",
  unknown: "No lo sabemos: nos falta el dato para comprobar lo que pides. No lo damos por bueno.",
  // zona.compra.sin_precio (D-227, D-234): why this zone has no purchase price, by its level. Never
  // a promise of an estimate: with the code deployed before the sync a district has none yet
  buySource: {
    municipio:
      "Sin precio de compra en esta zona: el valor tasado del Ministerio de Vivienda solo se publica para los municipios de más de 25.000 habitantes.",
    madrid: "Sin precio de compra en esta zona: el valor tasado del Ministerio de Vivienda se publica para Madrid entero, no por distrito ni por barrio.",
  },
  // zona.sin_alquiler (D-238): the same for renting in a municipio; districts and barrios bring their own reason
  rentSource: "Con «Alquilar», puede faltar el alquiler: la Comunidad de Madrid solo lo publica para los municipios de más de 20.000 habitantes, y casi ningún pueblo los tiene.",
  // zona.fuera (D-238): a zone of the map outside «¿Dónde?»
  outside: (scope: string) => `Fuera de tu búsqueda (${scope}).`,
  confidence: (label: string) => `Fiabilidad del dato: ${label}`,
};

const TOPIC_ICON: Record<FactTopic, LucideIcon> = {
  coste: Euro,
  transporte: Bus,
  salud: Cross,
  colegios: GraduationCap,
  zonas_verdes: Trees,
  seguridad: Shield,
  // The station the fact measures, not a wheelchair (D-204): the same icon as the chip
  accesibilidad: TrainFront,
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
  const { match, ranked } = zoneFit(result, zoneKey);
  const scope = resultScope(result);
  if (!match) return scope === "all" ? null : <p className={styles.hint}>{TEXT.outside(SCOPE_LABEL[scope])}</p>;
  const fails = failedLabels(match.failed_constraints, constraintLabels(result), ranked?.constraints);
  const buying = result.scenario.budget?.kind === "buy";
  const rentingInMunicipio = result.scenario.budget?.kind === "rent" && zoneKey.startsWith("municipio/");

  return (
    <>
      {match.passes_all && ranked && <p className={styles.rank}>{rankText(ranked.rank, zoneWord(result))}</p>}
      {match.match_pct != null && !match.passes_all && (
        <p className={styles.fails}>
          <CircleX size={18} aria-hidden="true" />
          <span>{fails.length > 0 ? `${TEXT.fails} ${fails.join(" · ")}` : TEXT.failsUnnamed}</span>
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
      {match.match_pct == null && rentingInMunicipio && <p className={styles.unknownWhy}>{TEXT.rentSource}</p>}
      {ranked && ranked.facts.length > 0 && (
        <section className={styles.facts} aria-labelledby={factsId}>
          <h3 id={factsId}>{TEXT.facts}</h3>
          <ul>
            {ranked.facts.map((fact, i) => {
              const Icon = TOPIC_ICON[fact.topic];
              const confidence = confidenceText(fact.confidence);
              return (
                <li key={`${i}-${fact.topic}`} className={KIND_CLASS[fact.kind]}>
                  <Icon size={18} aria-hidden="true" />
                  <span>
                    {fact.text}{" "}
                    <small title={confidence.help}>
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
    </>
  );
}
