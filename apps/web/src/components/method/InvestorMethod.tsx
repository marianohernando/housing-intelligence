import type { ReactNode } from "react";

import GlassCard from "@/components/ui/GlassCard";
import { formatNumber } from "@/lib/format";
import { CALCULATOR_TEXT } from "@/lib/investors";
import { INVESTOR_METHOD as M } from "@/lib/investorMethod";
import { SERVICES_TEXT, SHEET_TEXT, USE_TEXT } from "@/lib/parcels";

import styles from "../../app/(vida)/section.module.css";

/**
 * «Cómo calculamos la ficha para inversores» (D-251): what the parcel search (D-250) and the
 * viability v0 (D-248) do, in plain words and nothing more. Copy from pitch/textos_web.md §11
 * (`metodo.inversores.*`). Every figure comes from lib/investorMethod.ts, generated from the code
 * and the versioned tables by scripts/export_investor_data.py: none is typed here.
 */

/** «1,36», «0,875», «2», «1.109»: Spanish, without trailing zeros after the comma. */
export const n = (value: number) =>
  formatNumber(value, Number.isInteger(value) ? 0 : 4)
    .replace(/(,\d*?)0+$/, "$1")
    .replace(/,$/, "");
const pct = (value: number) => `${n(value)} %`;
const grado = (g: number) => `${g}º`;
/** «2, 3, 4, 6, 10 y 11» */
export const listed = (items: readonly (string | number)[]) =>
  items.length < 2 ? items.join("") : `${items.slice(0, -1).join(", ")} y ${items.at(-1)}`;
const lower = (label: string) => label.charAt(0).toLowerCase() + label.slice(1);
/** «574 de uso residencial, 51 de uso terciario y 484 de uso industrial» */
const byUse = (counts: Partial<Record<keyof typeof USE_TEXT, number>>) =>
  listed(
    (Object.entries(counts) as [keyof typeof USE_TEXT, number][]).map(([kind, count]) =>
      kind === "otro" ? `${n(count)} de otros usos` : `${n(count)} de uso ${USE_TEXT[kind].label.toLowerCase()}`,
    ),
  );

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
  const best = M.scenarios.find((s) => s.key === "optimista");
  const worst = M.scenarios.find((s) => s.key === "pesimista");
  const crg = M.costReferences.crg;
  const block = crg.types.find((t) => t.key === "bloque_abierto");
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
          <strong>La parcela</strong> (su superficie, su uso, lo que hay construido, el año, si está sin edificar según su uso en el Catastro y, en un edificio con varios
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
          terciario), la enseñamos como referencia y no la usamos para la vivienda. Si la parcela está en un ámbito que el
          Ayuntamiento no da por terminado (planeamiento, gestión o urbanización sin acabar, según el estado de desarrollo de los
          ámbitos o según VEDA), la cifra oficial también es una referencia y la de partida queda «sin dato».
        </li>
        <li>
          <strong>Supuesto con su norma zonal</strong> (la regla del Plan General que dice qué y cuánto se construye en cada zona de la
          ciudad ya hecha): en las que fijan cuántos m² se pueden construir por cada m² de parcela, multiplicamos esa cifra por la
          superficie de la parcela. Es un supuesto: la norma lo aplica a la parcela edificable, que puede ser menor. Si el plan le da a
          la parcela otro uso que vivienda (por ejemplo, industrial en la norma zonal 9, de actividades económicas), esos m² son de ese
          uso: los enseñamos como referencia y la de partida queda «sin dato».
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
        <strong>Por uso, según el plan.</strong> El Ayuntamiento publica, para muchas parcelas urbanísticas (la parcela que dibuja el
        plan), los m² de su uso principal y de sus otros usos, en m² o en m² por m² de parcela; en m² por m², los multiplicamos por la
        superficie de la parcela urbanística y lo marcamos como supuesto. Es lo que el plan permite en total, no lo que queda por
        construir, y la parcela urbanística puede no coincidir con la catastral. Cuando no la publica, lo decimos. Salvo excepciones,
        los usos asociados y complementarios no pueden pasar del 50 % de lo edificado, ni del 25 % en una parcela dotacional (Normas Urbanísticas, art.
        7.2.8). Público o privado solo existe en el dotacional: el básico y el singular son de titularidad pública, y el privado, de
        titularidad privada (art. 7.7.2). El terciario no se divide así (art. 7.6.1): un «terciario público» no existe en el plan, y los
        servicios de la Administración son dotacionales.
      </p>
      <p className={styles.para}>
        <strong>Por uso, según cada fuente de la parcela catastral.</strong> VEDA y el Portal del Suelo publican una sola cifra por
        parcela, con un solo uso: de las {n(M.vedaParcels)} de VEDA, {byUse(M.vedaByUse)}; de las {M.portalParcels} del Portal del
        Suelo, {byUse(M.portalByUse)}. En la ficha enseñamos cada cifra con su uso y su fuente, y nunca la repartimos entre usos.
      </p>
      <p className={styles.para}>
        <strong>La calculadora calcula solo vivienda,</strong> porque sus precios y alquileres son de vivienda: parte de la cifra
        residencial. Si solo hay cifra de otros usos, o la parcela no está lista (un ámbito sin terminar, un uso del plan que no es
        vivienda), la edificabilidad de partida queda «sin dato» y pones tú los m² de vivienda que quieras estudiar.
      </p>
      <p className={styles.para}>Y antes de las cifras, la ficha avisa:</p>
      <ul className={styles.text}>
        <li>si el plan da a la parcela otro uso que vivienda;</li>
        <li>
          si el ámbito no está terminado: si es suelo urbano no consolidado o urbanizable, la ley pide ceder gratis al Ayuntamiento el
          suelo para el 10 % de la edificabilidad del ámbito y costear las obras de urbanización (Ley 9/2001 del Suelo de la Comunidad
          de Madrid, arts. 18.2.c, 18.2.d y 21.1), y nada de eso entra en la cuenta;
        </li>
        <li>
          si es vivienda con protección pública: tiene un precio máximo legal de venta por m² útil que fija la Comunidad por orden
          (Decreto 74/2009, art. 12), así que el precio libre del barrio no vale;
        </li>
        <li>si es vivienda unifamiliar: el coste de partida es el de un bloque de pisos y el precio, el de la vivienda del barrio en general;</li>
        <li>y, si es suelo público del Portal del Suelo, quién lo ofrece, en qué régimen y si está urbanizado según el Portal.</li>
      </ul>
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
          <strong>Coste de construcción:</strong> los m² por un presupuesto de ejecución material (PEM, lo que cuesta la obra en sí) de{" "}
          {n(crg.defaultPem)} €/m², el punto medio del bloque abierto en Madrid ({block ? `${n(block.low)}–${n(block.high)}` : ""} €/m²)
          de los{" "}
          <External href={crg.url}>Costes de Referencia General de la Comunidad de Madrid</External>, actualizados al año {crg.year}{" "}
          (supuesto: los costes han subido desde entonces). Por un coeficiente de {n(M.costCoefficient)}: el PEM más, sobre el PEM,{" "}
          {M.costParts.map((p) => `un ${pct(p.pct)} de ${lower(p.label)}`).join("; ")} (supuesto; el ICIO de Madrid es del{" "}
          {pct(M.icioPct)}: ordenanza fiscal del ICIO, art. 25, en el Libro de Ordenanzas Fiscales 2024, p. 154; vigente en 2025).
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
      <p className={styles.para} id="inversores-coste">
        <strong>{CALCULATOR_TEXT.costReferencesTitle}.</strong> El coste de construcción es el dato que más cambia la cuenta:
      </p>
      <ul className={styles.text}>
        {CALCULATOR_TEXT.costReferences().map((ref) => (
          <li key={ref.href}>
            {ref.text} <External href={ref.href}>{ref.link}</External>
          </li>
        ))}
      </ul>
      <p className={styles.para}>
        <strong>{CALCULATOR_TEXT.costScopeTitle}.</strong> {CALCULATOR_TEXT.costIncludes(M.costParts.map((p) => lower(p.label)))}{" "}
        {CALCULATOR_TEXT.costExcludesTitle}
      </p>
      <ul className={styles.text}>
        {CALCULATOR_TEXT.costExcludes.map((line) => (
          <li key={line}>{line}</li>
        ))}
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
          construcción, los gastos y el margen objetivo), redondeado a tres cifras y antes de financiación, impuestos de compra del
          suelo, urbanización y derribo.
        </li>
        <li>
          <strong>Hasta cuánto puede costar la construcción</strong> (el punto de equilibrio): el coste por m² construido (PEM ×
          coeficiente) con el que la promoción llega justo al margen objetivo. Es lo que queda de los ingresos tras quitar el margen
          objetivo, los gastos de la venta y el suelo, entre los m², y en cada escenario con su subida o bajada del coste. Con el
          precio del suelo que pones y, si lo pones, también con el suelo gratis. Te lo damos también como PEM, con tu coeficiente, y
          como coeficiente, sobre tu PEM: si el presupuesto de tu obra queda por debajo, la promoción llega al margen objetivo.
        </li>
        <li>
          <strong>La rentabilidad bruta si se alquila:</strong> el alquiler de un año (el de referencia de un contrato nuevo del barrio
          o del distrito) entre lo que cuestan la construcción y el suelo. Sin precio del suelo, contamos el suelo a lo máximo que se
          puede pagar por él; si ni con el suelo gratis se llega al margen objetivo, no hay rentabilidad que dar.
        </li>
      </ul>
      <p className={styles.para}>
        En tres escenarios: el base; el optimista, con un {pct(Math.abs(best?.pricePct ?? 0))} más de precio de venta y de alquiler y
        un {pct(Math.abs(best?.costPct ?? 0))} menos de coste; y el pesimista, con un {pct(Math.abs(worst?.pricePct ?? 0))} menos de
        precio y un {pct(Math.abs(worst?.costPct ?? 0))} más de coste, porque las referencias de coste se separan un 15 % o más.{" "}
        <strong>Semáforo (supuesto), solo si pones el precio del suelo:</strong> «Sale» si llega al
        margen objetivo; «Ajustar» entre el {pct(M.adjustFloorPct)} y el objetivo; «No sale» por debajo del {pct(M.adjustFloorPct)}. La
        tasación hipotecaria pide al promotor un margen mínimo del {pct(M.appraisalMinMarginPct)} en vivienda de primera residencia,
        sin financiación ni Impuesto sobre Sociedades (Orden ECO/805/2003, disposición adicional sexta). Si
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

      <h3 id="inversores-servicios">4. Servicios y suministros</h3>
      <p className={styles.para}>{SERVICES_TEXT.solar}</p>
      <ul className={styles.text}>
        <li>
          <strong>Señal del planeamiento.</strong> En una norma zonal: {lower(SERVICES_TEXT.zonal.replace(/^Norma zonal: /, ""))} En
          un ámbito, el estado de sus obras de urbanización según el Ayuntamiento (el estado de desarrollo de los ámbitos); si no están
          terminadas y el planeamiento y la gestión del ámbito sí: {lower(SERVICES_TEXT.worksPending)} Si el planeamiento o la
          gestión no lo están: {lower(SERVICES_TEXT.planningFirst)} Si es suelo del Portal del Suelo, si lo da por urbanizado.
        </li>
        <li>
          <strong>Potencia (supuesto).</strong> Las viviendas, como los m² edificables de partida entre {n(M.homeM2)} m² (la vivienda
          tipo); la potencia, {n(M.supplies.kwPerHome)} kW por vivienda (electrificación básica) por el coeficiente de simultaneidad de
          la tabla 1 de la ITC-BT-10 del Reglamento de Baja Tensión: de {n(M.supplies.simultaneityOne)} con una vivienda a{" "}
          {n(M.supplies.simultaneityMax)} con {M.supplies.tableHomes}, y {n(M.supplies.stepPastTable)} más por cada una a partir de
          ahí. Sin servicios comunes ni garaje, que se suman aparte, así que es un mínimo. Por encima de {n(M.supplies.transformerKw)}{" "}
          kW: {lower(SERVICES_TEXT.transformer.replace(/^Por encima de 100 kW, /, ""))}
        </li>
        <li>
          <strong>Capacidad de la red.</strong> {SERVICES_TEXT.capacity} {SERVICES_TEXT.cnmc} Solo enlazamos su mapa: no copiamos sus
          cifras.
        </li>
        <li>
          <strong>Agua.</strong> {SERVICES_TEXT.canal}
        </li>
        <li>
          <strong>Edificio catalogado.</strong> Leemos el catálogo de edificios protegidos del Plan General en el punto de la parcela
          (Ayuntamiento de Madrid, datos abiertos). En los niveles 1 y 2 (singular, integral, estructural y volumétrico) el edificio
          está protegido en su conjunto y ni siquiera en ruina puede tener orden o licencia de demolición; en el nivel 3 (parcial y
          ambiental), en ruina se puede rehabilitar o derribar, pero la licencia puede obligar a mantener los elementos protegidos
          (Normas Urbanísticas, arts. 4.3.4 y 4.3.7). En los dos casos, la cuenta de obra nueva no vale tal cual: en un edificio
          catalogado, la calculadora empieza sin superficie («Sin dato») y avisa de que hace falta un estudio de rehabilitación.
        </li>
        <li>
          <strong>Lo que hay construido.</strong> Si el Catastro dice que hay un edificio, la ficha lo recuerda: la calculadora es de
          obra nueva sobre suelo libre y no cuenta el derribo, el desalojo ni la compra a los propietarios.
        </li>
      </ul>

      <h3>5. Lo que no te dice</h3>
      <ul className={styles.text}>
        <li>No es una tasación ni un informe vinculante ni una garantía de rentabilidad. {SHEET_TEXT.firstFilter}</li>
        <li>
          {SHEET_TEXT.sections.study}: {SHEET_TEXT.studyItems.map((item) => lower(item).replace(/\.$/, "")).join("; ")}. {SHEET_TEXT.takeIt}
        </li>
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
        {(Object.keys(USE_TEXT) as (keyof typeof USE_TEXT)[]).map((kind) => (
          <li key={kind}>
            <strong>{USE_TEXT[kind].label}:</strong> {lower(USE_TEXT[kind].plain)}
          </li>
        ))}
        {SERVICES_TEXT.words.map((w) => (
          <li key={w.term}>
            <strong>{w.term}:</strong> {lower(w.text)}
          </li>
        ))}
        <li>
          <strong>Parcela urbanística:</strong> la parcela que dibuja el plan; puede no coincidir con la del Catastro.
        </li>
        <li>
          <strong>Punto de equilibrio:</strong> el coste de construcción con el que la promoción llega justo al margen objetivo.
        </li>
        <li>
          <strong>Valor residual del suelo:</strong> lo máximo que se puede pagar por el suelo para que la promoción llegue al margen
          objetivo.
        </li>
      </ul>
    </GlassCard>
  );
}
