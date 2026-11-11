import SearchCard from "@/components/search/SearchCard";
import GlassCard from "@/components/ui/GlassCard";

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
          <p className={styles.lead}>Te decimos qué zonas encajan con tu vida y qué le falta a cada una, con datos oficiales.</p>
        </section>
        <SearchCard />
      </div>
      <GlassCard as="aside" aria-labelledby="como-funciona" className={styles.side}>
        <h2 id="como-funciona">Así funciona</h2>
        <ol className={styles.list}>
          <li>
            <strong>Cuéntanos cómo es tu hogar</strong> y lo que te importa: colegios, salud, transporte…
          </li>
          <li>
            <strong>Mira las zonas que encajan</strong> y por qué, con hechos que puedes comprobar.
          </li>
          <li>
            <strong>Entra en una zona</strong> y mira qué le falta frente al conjunto de la región.
          </li>
        </ol>
      </GlassCard>
    </div>
  );
}
