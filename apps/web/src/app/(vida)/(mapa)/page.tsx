import Legend from "@/components/map/Legend";
import ZoneListLink from "@/components/map/ZoneListLink";
import DataCounter from "@/components/provenance/DataCounter";
import ExampleButton from "@/components/search/ExampleButton";
import SearchCard from "@/components/search/SearchCard";
import SearchResults from "@/components/search/SearchResults";
import GlassCard from "@/components/ui/GlassCard";
import OverviewSide from "@/components/zone/OverviewSide";

import styles from "./page.module.css";

// Copy from pitch/textos_web.md (portada.*)
export default function MapaPage() {
  return (
    <div className={styles.page}>
      <div className={styles.main}>
        <section className={styles.hero} aria-labelledby="titulo">
          <h1 id="titulo" className={styles.title}>
            Encuentra tu sitio <span className={styles.accent}>en Madrid</span>
          </h1>
          <p className={styles.lead}>
            Te decimos en qué zonas de la Comunidad de Madrid puedes vivir con tu presupuesto y con lo que necesitas cerca.
          </p>
          <ExampleButton />
        </section>
        <SearchCard />
      </div>
      <div className={styles.side}>
        <OverviewSide>
          <SearchResults>
            <GlassCard as="aside" aria-labelledby="como-funciona" className={styles.steps}>
              <h2 id="como-funciona">Así funciona</h2>
              <ol className={styles.list}>
                <li>
                  <strong>Cuéntanos cómo es tu hogar</strong> y lo que quieres tener cerca: colegios, centro de salud, transporte…
                </li>
                <li>
                  <strong>Mira las zonas que te convienen</strong> y por qué, con hechos que puedes comprobar.
                </li>
                <li>
                  <strong>Entra en una zona</strong> y mira qué le falta comparada con zonas parecidas.
                </li>
              </ol>
            </GlassCard>
          </SearchResults>
        </OverviewSide>
        <DataCounter />
        <ZoneListLink />
      </div>
      <Legend />
    </div>
  );
}
