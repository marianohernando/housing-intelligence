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
import { constraintLabels, failedLabels, hasWalkingFact, rankText, WALK_MEDIAN, zoneFit } from "@/lib/fit";

import styles from "./ZoneCard.module.css";

// Copy from pitch/textos_web.md (zona.puesto, zona.hechos.titulo, zona.cerca_de_encajar.motivo,
// zona.condicion.sin_dato, confianza.aria). «No cumple todo lo que pides» is zona.no_cumple. buySource
// is B's draft for D after fit-0.5 (D-227): why a zone may have no purchase price.
const TEXT = {
  facts: "Lo que tienes aquí",
  fails: "No cumple:",
  failsUnnamed: "No cumple todo lo que pides.",
  unknown: "No lo sabemos: nos falta el dato para comprobar lo que pides. No lo damos por bueno.",
  buySource: "Con «Comprar», puede faltar el precio: el oficial (valor tasado del Ministerio de Vivienda) solo se publica para los municipios de más de 25.000 habitantes, no para los distritos de Madrid ni para los pueblos.",
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
  if (!match) return null;
  const fails = failedLabels(match.failed_constraints, constraintLabels(result));
  const buying = result.scenario.budget?.kind === "buy";

  return (
    <>
      {match.passes_all && ranked && <p className={styles.rank}>{rankText(ranked.rank)}</p>}
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
      {/* The usual reason when buying, said as a possibility: another condition may be the unknown one (D-227 §3) */}
      {match.match_pct == null && buying && <p className={styles.unknownWhy}>{TEXT.buySource}</p>}
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
