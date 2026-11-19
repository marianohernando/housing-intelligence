import type { ReactNode } from "react";

import GlassCard from "@/components/ui/GlassCard";
import { formatNumber } from "@/lib/format";
import { INVESTOR_METHOD as M } from "@/lib/investorMethod";

import styles from "../../app/(vida)/section.module.css";

/**
 * «Cómo calculamos la ficha para inversores» (D-251): what the parcel search (D-250) and the
 * viability v0 (D-248) do, in plain words and nothing more. Copy from pitch/textos_web.md §11
 * (`metodo.inversores.*`). Every figure comes from lib/investorMethod.ts, generated from the code
 * and the versioned tables by scripts/export_investor_data.py: none is typed here.
 */

/** «1,36», «0,875», «2», «1.109»: Spanish, without trailing zeros after the comma. */
export const n = (value: number) =>
  formatNumber(value, Number.isInteger(value) ? 0 : value < 1 ? 3 : 2)
    .replace(/(,\d*?)0+$/, "$1")
    .replace(/,$/, "");
const pct = (value: number) => `${n(value)} %`;
const grado = (g: number) => `${g}º`;
/** «2, 3, 4, 6, 10 y 11» */
export const listed = (items: readonly (string | number)[]) =>
  items.length < 2 ? items.join("") : `${items.slice(0, -1).join(", ")} y ${items.at(-1)}`;
const lower = (label: string) => label.charAt(0).toLowerCase() + label.slice(1);

function External({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer">
      {children}
      <span className="visually-hidden"> (se abre en una pestaña nueva)</span>
    </a>
  );
}

function Coefficients() {
  const split = M.split;
  return (
    <ul className={styles.text}>
      {M.zonalNorms.map((rule) => {
        const splitValue = rule.nz === split.nz ? rule.coefficients.find((c) => c.grado === split.grado)?.value : undefined;
        return (
          <li key={rule.nz}>
            <strong>
              Norma zonal {rule.nz} ({rule.name}):
            </strong>{" "}
            {rule.coefficients.map((c) => `grado ${grado(c.grado)}, ${n(c.value)}`).join("; ")} m² por cada m² de parcela (
            <External href={rule.url}>art. {rule.article}</External>).
            {splitValue !== undefined &&
              ` En el grado ${grado(split.grado)}, ${n(splitValue)} hasta ${n(split.limitM2)} m² de parcela y ${n(split.excess)} sobre lo que pase de ahí.`}
          </li>
        );
      })}
      <li>
        <strong>Norma zonal 1 (grados {listed(M.nz1.factors.map((f) => grado(f.grado)))}), aproximado:</strong> superficie de la
        parcela × Z × C. Z es la cifra que el plano de condiciones de la edificación de 1997 da a cada manzana; C, un factor de la
        norma por grado ({M.nz1.factors.map((f) => `grado ${grado(f.grado)}, ${n(f.value)}`).join("; ")};{" "}
        <External href={M.nz1.url}>art. {M.nz1.article}</External>). Es aproximado porque la norma lo aplica al fondo edificable o a
        la parcela edificable, no siempre a la parcela entera.
      </li>
    </ul>
  );
}

export default function InvestorMethod() {
  const nz1Grados = M.nz1.factors.map((f) => grado(f.grado));
  const [, optimistic] = M.scenarios;
  const swing = optimistic ? Math.abs(optimistic.pricePct) : 0;
  const costSwing = optimistic ? Math.abs(optimistic.costPct) : 0;
  return (
    <GlassCard as="section" aria-labelledby="inversores" className={styles.card}>
      <h2 id="inversores">Cómo calculamos la ficha para inversores</h2>
      <p className={styles.para}>
        En «Inversores» buscas una parcela de Madrid capital por su referencia catastral, su dirección o en el mapa, y te decimos cómo
        es, qué dice el planeamiento, cuánto se puede construir y si una promoción sale. Cada cifra dice de dónde sale y si es un{" "}
        <strong>dato</strong>, un <strong>supuesto</strong> nuestro o algo que <strong>pones tú</strong>.
      </p>

      <h3>1. De dónde sale cada dato de la parcela</h3>
      <ul className={styles.text}>
        <li>
          <strong>La parcela</strong> (su superficie, su uso, lo que hay construido, el año, si es un solar y, en un edificio con varios
          pisos o locales, cuántos hay de cada uso): datos elaborados por Vida Fácil a partir de los de la Dirección General del
          Catastro (Sede Electrónica del Catastro), con la fecha en que los consultamos. Nunca enseñamos los pisos uno a uno.
        </li>
        <li>
          <strong>El planeamiento</strong> (la norma zonal y su grado, o el ámbito; el uso que le da; el plan en vigor con el enlace a
          su ficha oficial): del Ayuntamiento de Madrid, en el punto de la parcela. Es información urbanística sin valor jurídico: manda
          la ficha oficial.
        </li>
        <li>
          <strong>El barrio:</strong> si el barrio de la parcela es uno de los {M.pilotBarrios} del piloto (dentro de la M-40), la ficha
          del barrio: quién vive, precios, qué falta, comercio y suelo. Si no, las cifras de su distrito o de toda la ciudad, y lo
          decimos.
        </li>
      </ul>

      <h3>2. Cuánto se puede construir</h3>
      <p className={styles.para}>Los m² edificables de partida, en este orden:</p>
      <ol className={styles.text}>
        <li>
          <strong>Dato oficial de la parcela,</strong> si lo hay: el del visor de edificabilidad (VEDA) del Ayuntamiento (
          {n(M.vedaParcels)} parcelas, de vivienda y de otros usos) y, si no, el del Portal del Suelo de la Comunidad de Madrid (
          {M.portalParcels} parcelas de Madrid capital). Va primero la cifra de vivienda; si solo hay de otros usos (industrial o
          terciario), la enseñamos como referencia y no la usamos para la vivienda.
        </li>
        <li>
          <strong>Supuesto con su norma zonal</strong> (la regla del Plan General que dice qué y cuánto se construye en cada zona de la
          ciudad ya hecha): en las que fijan cuántos m² se pueden construir por cada m² de parcela, multiplicamos esa cifra por la
          superficie de la parcela. Es un supuesto: la norma lo aplica a la parcela edificable, que puede ser menor.
          <Coefficients />
        </li>
        <li>
          <strong>Sin dato</strong> en el resto: las normas zonales {listed(M.withoutCoefficient)}, que no fijan una cifra; la
          norma zonal 1 fuera de los grados {listed(nz1Grados)} o sin la Z de su manzana; una norma zonal sin grado o una parcela sin
          superficie; los ámbitos (zonas con su propio plan) sin dato oficial; el suelo dotacional (para equipamientos, zonas verdes o
          servicios públicos), el no urbanizable y el rústico; y cuando el Ayuntamiento no nos da la calificación. Los m² los pones
          tú.
        </li>
      </ol>
      <p className={styles.para}>
        <strong>Puedes cambiar la edificabilidad siempre.</strong> «Sin dato» no es 0. Al lado enseñamos lo construido hoy, que es lo
        que hay, no lo que se puede construir. Las normas: {M.nnuuCitation}.
      </p>

      <h3>3. ¿Sale la promoción? (método residual)</h3>
      <p className={styles.para}>Con lo que pones y lo que traemos:</p>
      <ul className={styles.text}>
        <li>
          <strong>Ingresos:</strong> los m² por el precio de venta del barrio (o de su distrito), que es una estimación: el valor tasado
          de la ciudad repartido según el valor catastral de cada zona. Más la prima de la vivienda nueva, la de toda la ciudad: el
          valor tasado de la vivienda libre de hasta 5 años frente al de toda la vivienda libre.
        </li>
        <li>
          <strong>Coste de construcción:</strong> los m² por el presupuesto de ejecución material (PEM, lo que cuesta la obra en sí) de
          los visados de obra nueva de viviendas en bloque de la Comunidad de Madrid (
          <External href={M.pem.url}>
            {n(M.pem.eurM2)} €/m², {M.pem.year}
          </External>
          ) y por un coeficiente de {n(M.costCoefficient)}: el PEM más, sobre el PEM,{" "}
          {M.costParts.map((p) => `un ${pct(p.pct)} de ${lower(p.label)}`).join("; ")} (supuesto). El presupuesto de los visados suele
          declararse a la baja: ajusta el coeficiente si tienes otro.
        </li>
        <li>
          <strong>Comercialización y otros gastos:</strong> un {pct(M.salesCostsPct)} de las ventas (supuesto:{" "}
          {M.salesCostParts.map((p) => `${pct(p.pct)} de ${lower(p.label)}`).join("; ")}).
        </li>
        <li>
          <strong>Suelo:</strong> lo pones tú, en total o por m² edificable, si lo sabes.
        </li>
        <li>
          <strong>Margen objetivo:</strong> un {pct(M.targetMarginPct)} de las ventas (supuesto).
        </li>
        <li>
          <strong>Sin plazos ni financiación</strong> en esta versión: el margen es antes de los intereses del préstamo y de los
          impuestos.
        </li>
      </ul>
      <p className={styles.para}>
        En la calculadora puedes cambiar los m², el precio, la prima, el alquiler, el PEM, el coeficiente, los gastos, el suelo, el
        margen objetivo y los datos de la comprobación de demanda. No se cambian el suelo del «Ajustar» ({pct(M.adjustFloorPct)}), la
        subida y la bajada de los escenarios ni el umbral de esfuerzo ({pct(M.effortThresholdPct)}).
      </p>
      <p className={styles.para}>Y te decimos:</p>
      <ul className={styles.text}>
        <li>
          <strong>El margen sobre ventas,</strong> solo si pones el precio del suelo: lo que queda de los ingresos tras la construcción,
          los gastos y el suelo, en % de los ingresos.
        </li>
        <li>
          <strong>Lo máximo que se puede pagar por el suelo</strong> (el valor residual: lo que queda para el suelo tras pagar la
          construcción, los gastos y el margen objetivo).
        </li>
        <li>
          <strong>La rentabilidad bruta si se alquila:</strong> el alquiler de un año (el de referencia de un contrato nuevo del barrio
          o del distrito) entre lo que cuestan la construcción y el suelo. Sin precio del suelo, contamos el suelo a lo máximo que se
          puede pagar por él; si ni con el suelo gratis se llega al margen objetivo, no hay rentabilidad que dar.
        </li>
      </ul>
      <p className={styles.para}>
        En tres escenarios: el base; el optimista, con un {pct(swing)} más de precio de venta y de alquiler y un {pct(costSwing)} menos
        de coste; y el pesimista, al revés. <strong>Semáforo (supuesto), solo si pones el precio del suelo:</strong> «Sale» si llega al
        margen objetivo; «Ajustar» entre el {pct(M.adjustFloorPct)} y el objetivo; «No sale» por debajo del {pct(M.adjustFloorPct)}. Si
        pones un margen objetivo por debajo del {pct(M.adjustFloorPct)}, no hay franja de «Ajustar»: sale o no sale. Sin precio del
        suelo no hay veredicto: solo lo máximo que podrías pagar por él.
      </p>
      <p className={styles.para}>
        <strong>¿Lo pueden pagar los hogares del barrio?</strong> Una vivienda tipo de {n(M.homeM2)} m² a precio de vivienda nueva, con
        una hipoteca del {pct(M.ltvPct)} del precio a {M.loanYears} años al {pct(M.loanRatePct)}: la cuota y el alquiler frente al{" "}
        {pct(M.effortThresholdPct)} de la renta media de los hogares del barrio (el umbral de la Ley 12/2023 por el derecho a la
        vivienda). Solo cuenta la cuota o el alquiler, sin gastos ni suministros, así que la cuenta es optimista; y es la renta media:
        no dice cuántos hogares ganan más o menos.
      </p>

      <h3>4. Lo que no te dice</h3>
      <ul className={styles.text}>
        <li>No es una tasación ni un informe vinculante ni una garantía de rentabilidad.</li>
        <li>
          No decimos qué se puede construir con toda la normativa (alturas, ocupación, retranqueos, usos o cargas): solo una
          edificabilidad de partida, con su fuente, para hacer números.
        </li>
        <li>
          La primera búsqueda de una parcela puede tardar unos segundos, porque los servicios oficiales responden más despacio la primera
          vez: les damos como mucho {n(M.lookupBudgetS)} segundos (leer el barrio va aparte). Si el Ayuntamiento no responde, te
          enseñamos la parcela sin el planeamiento; si el Catastro no responde, no podemos enseñarte la ficha, salvo la de las parcelas
          de ejemplo, que tenemos guardadas.
        </li>
      </ul>

      <h3>Palabras que usamos</h3>
      <ul className={styles.text}>
        <li>
          <strong>PEM y PEC:</strong> el presupuesto de ejecución material es lo que cuesta la obra en sí; el de contrata (PEC) le suma
          los gastos generales y el beneficio del constructor.
        </li>
        <li>
          <strong>ICIO:</strong> el impuesto municipal sobre construcciones, instalaciones y obras.
        </li>
        <li>
          <strong>Seguro decenal:</strong> el seguro obligatorio que cubre durante diez años los daños en la estructura.
        </li>
        <li>
          <strong>Ámbito:</strong> una zona de la ciudad con su propio plan, que fija lo que se construye en ella.
        </li>
        <li>
          <strong>Dotacional:</strong> suelo para equipamientos, zonas verdes o servicios públicos, no para vivienda.
        </li>
        <li>
          <strong>Valor residual del suelo:</strong> lo máximo que se puede pagar por el suelo para que la promoción llegue al margen
          objetivo.
        </li>
      </ul>
    </GlassCard>
  );
}
