import DataCounter from "@/components/provenance/DataCounter";

import styles from "./SiteFooter.module.css";

// Copy from pitch/textos_web.md, section 10 (pie.*). The base map credit (pie.mapa_base) is
// drawn by MapLibre on the map itself, so it is not repeated here.
const ATTRIBUTIONS = [
  { text: "Fuente: Comunidad de Madrid — Portal de Datos Abiertos (datos.comunidad.madrid), CC BY 4.0.", href: "https://datos.comunidad.madrid" },
  { text: "Fuente: Ayuntamiento de Madrid — datos.madrid.es, CC BY 4.0.", href: "https://datos.madrid.es" },
  {
    text: "Powered by CRTM — datos del Consorcio Regional de Transportes de Madrid (www.crtm.es). Datos explotados: paradas y frecuencias calculadas por Vida Fácil a partir de sus horarios.",
    href: "https://www.crtm.es",
  },
  { text: "© OpenStreetMap contributors, ODbL.", href: "https://www.openstreetmap.org/copyright" },
];
const TEXT = {
  independent: "Vida Fácil no es un servicio de la Comunidad de Madrid, del Ayuntamiento ni del CRTM.",
  project: "Vida Fácil · Plataforma Housing Intelligence · Proyecto para DATAMAD 2026",
  code: "Código abierto (Apache-2.0)",
  codeHref: "https://github.com/marianohernando/housing-intelligence",
};

/** Footer of the pages without a map: data counter, attributions each licence asks for, and who we are. */
export default function SiteFooter() {
  return (
    <footer className={styles.footer}>
      <DataCounter className={styles.counter} />
      <ul className={styles.attributions}>
        {ATTRIBUTIONS.map(({ text, href }) => (
          <li key={href}>
            <a href={href} target="_blank" rel="noopener noreferrer">
              {text}
            </a>
          </li>
        ))}
      </ul>
      <p>{TEXT.independent}</p>
      <p>
        {TEXT.project} ·{" "}
        <a href={TEXT.codeHref} target="_blank" rel="noopener noreferrer">
          {TEXT.code}
        </a>
      </p>
    </footer>
  );
}
