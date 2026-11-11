import type { Metadata } from "next";
import type { ReactNode } from "react";

import CmCount from "@/components/provenance/CmCount";
import DatasetList from "@/components/provenance/DatasetList";
import SiteFooter from "@/components/shell/SiteFooter";
import GlassCard from "@/components/ui/GlassCard";

import styles from "../section.module.css";

export const metadata: Metadata = { title: "Cómo lo calculamos" };

/*
 * Copy from pitch/metodologia.md, part 1 (line D). Paragraphs marked «pendiente de A» are left
 * out until line A has them (D's rule), and so are the row definitions that no longer match the
 * rows of /gaps after GAP-001; both are listed for D in PR #2.
 */

function Section({ id, title, children }: { id: string; title: string; children: ReactNode }) {
  return (
    <GlassCard as="section" aria-labelledby={id} className={styles.card}>
      <h2 id={id}>{title}</h2>
      {children}
    </GlassCard>
  );
}

// gap-0.2 (D-213), with estado.* and fila.zona_pequena of pitch/textos_web.md; the long definitions
// wait for pitch/metodologia.md (1.4)
const STATUS_ROWS: [string, string][] = [
  ["claramente menos que los municipios de su tipo, y no es por el tamaño de la zona", "FALTA"],
  ["menos que los municipios de su tipo, pero no tanto como para decir que falta", "JUSTO"],
  ["lo mismo o más que los municipios de su tipo", "CUBIERTO"],
  ["tan poca gente que no podemos saber con seguridad si falta (nunca sale FALTA)", "Zona pequeña para comparar"],
  ["un dato que no tenemos", "SIN DATOS"],
];

function GapMethod() {
  return (
    <Section id="que-falta" title="Cómo decidimos qué falta en una zona">
      <p className={styles.para}>
        Para cada servicio contamos cuántos hay en la zona por cada número fijo de vecinos. Después hacemos la misma
        cuenta para los demás municipios de su tipo en la Comunidad de Madrid (rurales o urbanos) y comparamos:
      </p>
      <table className={styles.table}>
        <thead>
          <tr>
            <th scope="col">Si la zona tiene…</th>
            <th scope="col">Sale</th>
          </tr>
        </thead>
        <tbody>
          {STATUS_ROWS.map(([when, status]) => (
            <tr key={status}>
              <td>{when}</td>
              <td>
                <strong>{status}</strong>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className={styles.para}>
        Es una señal para saber dónde mirar primero, no un veredicto: comparamos con zonas parecidas de la región, no con una
        norma oficial que diga cuántos centros debería haber.
      </p>
    </Section>
  );
}

function Reliability() {
  return (
    <Section id="fiabilidad" title="Qué significa la fiabilidad">
      <p className={styles.para}>Cada dato lleva una de estas etiquetas:</p>
      <ul className={styles.text}>
        <li><strong>Dato fiable:</strong> sale de un registro oficial completo.</li>
        <li><strong>Dato aproximado:</strong> es oficial, pero la zona tiene poca población o la fuente no está completa.</li>
        <li><strong>Dato poco seguro:</strong> faltan bastantes datos en la fuente.</li>
        <li><strong>Sin datos:</strong> no lo tenemos.</li>
      </ul>
      <p className={styles.para}>Usamos estas etiquetas según la fiabilidad del dato, que va de 0 a 1:</p>
      <ul className={styles.text}>
        <li><strong>0,8 o más:</strong> dato fiable.</li>
        <li><strong>De 0,5 a menos de 0,8:</strong> dato aproximado.</li>
        <li><strong>Más de 0 y menos de 0,5:</strong> dato poco seguro.</li>
        <li><strong>0:</strong> sin datos.</li>
      </ul>
      <p className={styles.para}>El 0,5 cuenta como aproximado porque es la fiabilidad que reciben siempre las zonas con poca población.</p>
      <p className={styles.para}>La fiabilidad baja en estos casos:</p>
      <ul className={styles.text}>
        <li>
          <strong>Zonas con poca población.</strong> En un pueblo pequeño, un solo centro más o menos cambia mucho la cuenta,
          así que el dato cuenta como aproximado. Pasa con menos de 500 menores de 15 años en colegios, menos de 2.000
          habitantes en centros de salud y menos de 500 personas mayores en residencias.
        </li>
        <li>
          <strong>Fuentes incompletas.</strong> Por ejemplo, si de algunas residencias no se publica cuántas plazas tienen,
          cuanto mayor es esa parte, menos nos fiamos.
        </li>
        <li>
          <strong>Cuentas aproximadas.</strong> Por ejemplo, la fuente agrupa los hogares de «5 o más personas» y los
          contamos como de 5.
        </li>
      </ul>
    </Section>
  );
}

function Limits() {
  return (
    <Section id="limites" title="Lo que estos datos no te dicen">
      <ul className={styles.text}>
        <li>
          <strong>Contamos centros, no plazas.</strong> Un colegio grande y uno pequeño cuentan igual, y un consultorio rural
          cuenta como un centro de salud.
        </li>
        <li>
          <strong>Alquiler:</strong> la Comunidad solo publica el precio medio de los municipios de más de 20.000 habitantes.
          En los demás no tenemos el dato y lo decimos.
        </li>
        <li>
          <strong>No enseñamos pisos en venta ni en alquiler.</strong> Te ayudamos a elegir zona; el piso lo buscas donde
          prefieras.
        </li>
        <li>
          <strong>Todavía no sabemos qué echan en falta los vecinos.</strong> Hoy todo sale de datos oficiales. Más adelante
          queremos sumar lo que la gente diga que necesita, siempre de forma anónima y por zonas.
        </li>
        <li>
          <strong>Cada dato tiene su fecha.</strong> Algunos horarios de transporte son los últimos publicados aunque ya estén
          caducados (el del metro venció en mayo de 2026). Lo avisamos.
        </li>
      </ul>
    </Section>
  );
}

export default function ComoLoCalculamosPage() {
  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Cómo lo calculamos</h1>
      <Section id="principios" title="Tres reglas que seguimos siempre">
        <ul className={styles.text}>
          <li>
            Comparamos cada zona con los demás municipios de la Comunidad de Madrid de su mismo tipo, urbanos o rurales,
            siempre según cuánta gente vive en ella.
          </li>
          <li>Si un dato no existe, lo decimos: «sin datos» no es lo mismo que cero.</li>
          <li>Cada dato dice de dónde sale y cuánto podemos fiarnos de él.</li>
        </ul>
      </Section>
      <Section id="zonas" title="Qué zonas comparamos">
        <p className={styles.para}>
          Los 179 municipios de la Comunidad de Madrid. Madrid capital no va como un solo bloque: la dividimos en sus 21
          distritos, porque no es lo mismo vivir en un distrito que en otro.
        </p>
      </Section>
      <Section id="encaje" title="Cómo sale el % de encaje">
        <p className={styles.para}>
          El % de encaje dice <strong>cuánto se parece una zona a lo que tú buscas</strong>. No es una nota de la zona: la
          misma zona puede encajar mucho con una familia con niños y poco con una persona mayor que vive sola.
        </p>
        <p className={styles.para}>
          <strong>Paso 1. Lo imprescindible.</strong> Miramos tus condiciones en cada zona, por ejemplo tu presupuesto o
            tener un colegio cerca. Cada condición puede salir de tres maneras:
        </p>
        <ul className={styles.text}>
          <li><strong>Cumple.</strong></li>
          <li><strong>No cumple.</strong></li>
          <li><strong>No lo sabemos</strong>, porque falta el dato. En ese caso no la damos por buena.</li>
        </ul>
        <p className={styles.para}>
          Solo te enseñamos como «zonas que encajan» las que cumplen todo. Las que fallan en una sola cosa salen aparte, en
          «Casi encajan», para que decidas tú.
        </p>
        <p className={styles.para}>
          <strong>Debajo del %</strong> van entre 3 y 5 hechos que puedes comprobar, como «Colegio con primaria a 5 min
            andando», y cada uno dice cuánto nos fiamos del dato.
        </p>
      </Section>
      <GapMethod />
      <Reliability />
      <Section id="datos" title="Qué datos usamos">
        <ul className={styles.text}>
          <li>
            <strong>
              <CmCount /> conjuntos de datos del Portal de Datos Abiertos de la Comunidad de Madrid:
            </strong>{" "}
            población, hogares, vivienda, renta, alquiler, colegios, salud, mayores, farmacias y las 6 redes de transporte
            público del Consorcio Regional de Transportes de Madrid, que también se publican en ese portal.
          </li>
          <li>
            <strong>Como apoyo,</strong> el padrón y el panel de distritos del Ayuntamiento de Madrid para la población y los
            hogares de cada distrito de Madrid capital, y el mapa de calles de OpenStreetMap para las distancias a pie.
          </li>
          <li>
            <strong>Antes de usar un conjunto,</strong> pasa un control de calidad: que no haya registros repetidos, que cada
            municipio exista, que los errores queden apartados y que un dato que falta no se convierta en un cero.
          </li>
          <li>
            <strong>Cada resultado</strong> dice de qué conjuntos sale, con el enlace a su ficha en el portal, su versión y
            su licencia.
          </li>
        </ul>
        <DatasetList />
      </Section>
      <Limits />
      <Section id="privacidad" title="Tu privacidad">
        <p className={styles.para}>No te pedimos nombre ni cuenta. Solo trabajamos con datos de zonas, nunca de personas.</p>
      </Section>
      <SiteFooter />
    </div>
  );
}
