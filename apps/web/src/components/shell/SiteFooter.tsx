import DataCounter from "@/components/provenance/DataCounter";
import SourceAttributions from "@/components/provenance/SourceAttributions";

import styles from "./SiteFooter.module.css";

// pie.* of pitch/textos_web.md, section 10. The citations each licence asks for come from the
// source catalogue (attribution_text of /datasets); the base map credit (pie.mapa_base) is drawn
// by MapLibre on the map itself, so it is not repeated here.
const TEXT = {
  independent:
    "Vida Fácil no es un servicio de la Comunidad de Madrid, del Ayuntamiento, del CRTM, del Ministerio de Sanidad ni de la Agencia Tributaria.", // pie.independiente (13 nov)
  project: "Vida Fácil · Proyecto para DATAMAD 2026", // pie.proyecto (13 nov): one visible name
  code: "Código abierto (Apache-2.0)",
  codeHref: "https://github.com/marianohernando/housing-intelligence",
  // For screen readers only: the links open in a new tab (review of PR #16)
  newTab: " (se abre en una pestaña nueva)",
};

/** Footer of the pages without a map: data counter, attributions each licence asks for, and who we are. */
export default function SiteFooter() {
  return (
    <footer className={styles.footer}>
      <DataCounter className={styles.counter} />
      <SourceAttributions className={styles.attributions} />
      <p>{TEXT.independent}</p>
      <p>
        {TEXT.project} ·{" "}
        <a href={TEXT.codeHref} target="_blank" rel="noopener noreferrer">
          {TEXT.code}
          <span className="visually-hidden">{TEXT.newTab}</span>
        </a>
      </p>
    </footer>
  );
}
