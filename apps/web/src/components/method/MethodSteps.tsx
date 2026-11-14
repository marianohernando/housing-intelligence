import { ArrowDown, ArrowRight, Database, Footprints, ListChecks, type LucideIcon, Scale, Users } from "lucide-react";
import type { ReactNode } from "react";

import GapBadge from "@/components/zone/GapBadge";

import styles from "./MethodSteps.module.css";

// Line D's copy (pitch/textos_web.md §5c, metodo.paso*): pitch/metodologia.md §1.4 in five steps (fase de mejora: «un gráfico, no solo texto»).
const STEPS: { icon: LucideIcon; title: string; text: ReactNode }[] = [
  {
    icon: Database,
    title: "Datos abiertos",
    text: "Dónde está cada centro y cuánta gente vive en cada zona, de la Comunidad de Madrid y otras fuentes oficiales.",
  },
  { icon: Footprints, title: "Lo que hay a 15 min andando", text: "Por las calles de verdad, a paso tranquilo: un kilómetro." },
  {
    icon: Users,
    title: "Repartido entre quienes lo comparten",
    text: "Si mucha gente vive alrededor de un centro, lo que ofrece toca a menos.",
  },
  {
    icon: Scale,
    title: "Comparado con municipios parecidos",
    text: "Urbanos con urbanos y rurales con rurales. Un distrito de Madrid, con las demás ciudades.",
  },
  {
    icon: ListChecks,
    title: "FALTA, JUSTO o CUBIERTO",
    text: (
      <>
        <span className={styles.badges}>
          <GapBadge status="FALTA" />
          <GapBadge status="JUSTO" />
          <GapBadge status="CUBIERTO" />
        </span>
        FALTA solo si la diferencia es clara y no es casualidad.
      </>
    ),
  },
];

const TEXT = {
  label: "Cómo decidimos qué falta, en cinco pasos",
  example:
    "Ejemplo, con los datos del 12 de noviembre de 2026: en Puente de Vallecas hay 2,8 escuelas infantiles al alcance a pie por cada 1.000 niños de 0 a 4 años, frente a 4,9 en los municipios parecidos. Es decir, aquí hay 57 por cada 100: FALTA.",
};

/** «Cómo lo calculamos» as a picture: open data → 15 min on foot → shared → compared → status. HTML, so it reads on a phone. */
export default function MethodSteps() {
  return (
    <figure className={styles.figure}>
      <ol className={styles.steps} aria-label={TEXT.label}>
        {STEPS.map(({ icon: Icon, title, text }, i) => (
          <li key={title} className={styles.step}>
            <span className={styles.icon} aria-hidden="true">
              <Icon size={22} />
            </span>
            <strong className={styles.title}>{title}</strong>
            <span className={styles.text}>{text}</span>
            {i < STEPS.length - 1 && (
              <span className={styles.arrow} aria-hidden="true">
                <ArrowRight className={styles.right} size={20} />
                <ArrowDown className={styles.down} size={20} />
              </span>
            )}
          </li>
        ))}
      </ol>
      <figcaption className={styles.example}>{TEXT.example}</figcaption>
    </figure>
  );
}
