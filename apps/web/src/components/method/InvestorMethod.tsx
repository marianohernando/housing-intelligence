import type { ReactNode } from "react";

import GlassCard from "@/components/ui/GlassCard";
import { formatNumber } from "@/lib/format";
import { INVESTOR_METHOD as M } from "@/lib/investorMethod";

import styles from "../../app/(vida)/section.module.css";

/**
 * «Cómo calculamos la ficha para inversores» (D-251): what the parcel search (D-250) and the
 * viability v0 (D-248) do, in plain words. Copy from pitch/textos_web.md §11
 * (`metodo.inversores.*`). Every figure comes from lib/investorMethod.ts, generated from the code
 * and the versioned tables by scripts/export_investor_data.py: none is typed here.
 */

/** «1,36», «0,875», «2», «1.109»: Spanish, without trailing zeros after the comma. */
export const n = (value: number) =>
  formatNumber(value, Number.isInteger(value) ? 0 : value < 1 ? 3 : 2)
    .replace(/(,\d*?)0+$/, "$1")
    .replace(/,$/, "");
const pct = (value: number) => `${n(value)} %`;
const signed = (value: number) => `${value > 0 ? "+" : "−"}${pct(Math.abs(value))}`;
const grado = (g: number) => `${g}º`;

function SubTitle({ children }: { children: ReactNode }) {
  return <h3>{children}</h3>;
}

function External({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer">
      {children}
      <span className="visually-hidden"> (se abre en una pestaña nueva)</span>
    </a>
  );
}

function Coefficients() {
  return (
    <ul className={styles.text}>
      {M.zonalNorms.map((rule) => (
        <li key={rule.nz}>
          <strong>
            Norma zonal {rule.nz} ({rule.name}):
          </strong>{" "}
          {rule.coefficients.map((c) => `grado ${grado(c.grado)}, ${n(c.value)}`).join("; ")} m² por cada m² de parcela (
          <External href={rule.url}>art. {rule.article}</External>).
          {rule.nz === 8 &&
            ` En el grado 6º, ${n(rule.coefficients.find((c) => c.grado === 6)?.value ?? 0)} hasta ${n(M.nz8Grado6.limitM2)} m² de parcela y ${n(M.nz8Grado6.excess)} sobre lo que pase de ahí.`}
        </li>
      ))}
      <li>
        <strong>Norma zonal 1 (grados 1º a 4º), aproximado:</strong> superficie de la parcela × Z (del plano de condiciones de la
        edificación de 1997) × C ({M.nz1.factors.map((f) => `grado ${grado(f.grado)}, ${n(f.value)}`).join("; ")};{" "}
        <External href={M.nz1.url}>art. {M.nz1.article}</External>). Es aproximado porque la norma lo aplica al fondo edificable o a
        la parcela edificable, no siempre a la parcela entera.
      </li>
    </ul>
  );
}

export default function InvestorMethod() {
  const [base, ...others] = M.scenarios;
  return (
    <GlassCard as="section" aria-labelledby="inversores" className={styles.card}>
      <h2 id="inversores">Cómo calculamos la ficha para inversores</h2>
      <p className={styles.para}>
        En «Inversores» buscas una parcela de Madrid capital por su referencia catastral, su dirección o en el mapa, y te decimos cómo
        es, qué dice el planeamiento, cuánto se puede construir y si una promoción sale. Cada cifra dice de dónde sale y si es un{" "}
        <strong>dato</strong>, un <strong>supuesto</strong> nuestro o algo que <strong>pones tú</strong>.
      </p>

      <SubTitle>1. De dónde sale cada dato de la parcela</SubTitle>
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
          <strong>El barrio:</strong> si la parcela está dentro de la M-40 (los {M.pilotBarrios} barrios del piloto), la ficha del barrio:
          quién vive, precios, qué falta, comercio y suelo. Fuera del piloto, las cifras de su distrito o de toda la ciudad, y lo
          decimos.
        </li>
      </ul>

      <SubTitle>2. Cuánto se puede construir</SubTitle>
      <p className={styles.para}>Los m² edificables de partida, en este orden:</p>
      <ol className={styles.text}>
        <li>
          <strong>Dato oficial de la parcela,</strong> si lo hay: el del visor de edificabilidad (VEDA) del Ayuntamiento ({n(M.vedaParcels)}{" "}
          parcelas) y, si no, el del Portal del Suelo de la Comunidad de Madrid ({M.portalParcels} parcelas de Madrid capital). Va
          primero la cifra residencial; si solo hay de otros usos (industrial o terciario), la enseñamos como referencia y no la usamos
          para la vivienda.
        </li>
        <li>
          <strong>Supuesto con su norma zonal:</strong> en las normas zonales que fijan cuántos m² se pueden construir por cada m² de
          parcela, multiplicamos esa cifra por la superficie de la parcela. Es un supuesto: la norma lo aplica a la parcela edificable,
          que puede ser menor.
          <Coefficients />
        </li>
        <li>
          <strong>Sin dato</strong> en el resto: las normas zonales que no fijan una cifra (la 2, la 3, la 4 y la 6), los ámbitos sin
          dato oficial, el suelo de uso dotacional, el no urbanizable y el rústico. Los pones tú.
        </li>
      </ol>
      <p className={styles.para}>
        <strong>Siempre la puedes cambiar.</strong> «Sin dato» no es 0. Al lado enseñamos lo construido hoy, que es lo que hay, no lo
        que se puede construir. Las normas: {M.nnuuCitation}.
      </p>

      <SubTitle>3. ¿Sale la promoción? (método residual)</SubTitle>
      <p className={styles.para}>Con lo que pones y lo que traemos, todo editable:</p>
      <ul className={styles.text}>
        <li>
          <strong>Ingresos:</strong> los m² por el precio de venta estimado del barrio (o de su distrito), más la prima de la vivienda
          nueva (el valor tasado de la vivienda de hasta 5 años frente al de toda la vivienda). Datos, con su fuente al lado.
        </li>
        <li>
          <strong>Coste de construcción:</strong> los m² por el presupuesto de ejecución material de los visados de obra nueva de
          viviendas en bloque de la Comunidad de Madrid (<External href={M.pem.url}>{n(M.pem.eurM2)} €/m², {M.pem.year}</External>) y por un
          coeficiente de {n(M.costCoefficient)} (supuesto: {M.costParts.map((p) => `${pct(p.pct)} de ${p.label.charAt(0).toLowerCase()}${p.label.slice(1)}`).join("; ")}). El
          presupuesto de los visados suele declararse a la baja: ajusta el coeficiente si tienes otro.
        </li>
        <li>
          <strong>Comercialización y otros gastos:</strong> un {pct(M.salesCostsPct)} de las ventas (supuesto:{" "}
          {M.salesCostParts.map((p) => `${pct(p.pct)} de ${p.label.charAt(0).toLowerCase()}${p.label.slice(1)}`).join("; ")}).
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
      <p className={styles.para}>Y te decimos:</p>
      <ul className={styles.text}>
        <li>
          <strong>El margen sobre ventas:</strong> lo que queda de los ingresos tras la construcción, los gastos y el suelo, en % de los
          ingresos.
        </li>
        <li>
          <strong>Lo máximo que se puede pagar por el suelo</strong> (valor residual) para llegar al margen objetivo.
        </li>
        <li>
          <strong>La rentabilidad bruta si se alquila:</strong> el alquiler de un año (el de referencia de un contrato nuevo del barrio
          o del distrito) entre lo que cuestan la construcción y el suelo. Sin precio del suelo, contamos el suelo a lo máximo que se
          puede pagar por él.
        </li>
      </ul>
      <p className={styles.para}>
        En tres escenarios: {base?.label.toLowerCase()};{" "}
        {others.map((s) => `${s.key} (${signed(s.pricePct)} de precio y ${signed(s.costPct)} de coste)`).join("; ")}.{" "}
        <strong>Semáforo (supuesto), solo si pones el precio del suelo:</strong> «Sale» si llega al margen objetivo; «Ajustar» entre el{" "}
        {pct(M.adjustFloorPct)} y el objetivo; «No sale» por debajo del {pct(M.adjustFloorPct)}. Sin precio del suelo no hay veredicto:
        solo lo máximo que podrías pagar por él.
      </p>
      <p className={styles.para}>
        <strong>¿Lo pueden pagar los hogares del barrio?</strong> Una vivienda tipo de {n(M.homeM2)} m² a precio de vivienda nueva, con
        una hipoteca del {pct(M.ltvPct)} del precio a {M.loanYears} años al {pct(M.loanRatePct)}: la cuota y el alquiler frente al{" "}
        {pct(M.effortThresholdPct)} de la renta media de los hogares del barrio (el umbral de la Ley 12/2023 por el derecho a la
        vivienda). Solo cuenta la cuota o el alquiler, sin gastos ni suministros, así que la cuenta es optimista; y es la renta media:
        no dice cuántos hogares ganan más o menos.
      </p>

      <SubTitle>4. Lo que no te dice</SubTitle>
      <ul className={styles.text}>
        <li>No es una tasación ni un informe vinculante ni una garantía de rentabilidad.</li>
        <li>
          No decimos qué se puede construir con toda la normativa (alturas, ocupación, retranqueos, usos o cargas): solo una
          edificabilidad de partida, con su fuente, para hacer números.
        </li>
        <li>
          La primera búsqueda de una parcela puede tardar unos segundos, porque los servicios oficiales responden más despacio la primera
          vez; como mucho {n(M.lookupBudgetS)} segundos. Si el Catastro o el Ayuntamiento no responden, lo decimos y te enseñamos el resto.
        </li>
      </ul>
    </GlassCard>
  );
}
