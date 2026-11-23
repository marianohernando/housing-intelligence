import type { Metadata } from "next";
import type { ReactNode } from "react";

import InvestorMethod from "@/components/method/InvestorMethod";
import MethodSteps from "@/components/method/MethodSteps";
import CmCount from "@/components/provenance/CmCount";
import DatasetList from "@/components/provenance/DatasetList";
import SiteFooter from "@/components/shell/SiteFooter";
import GlassCard from "@/components/ui/GlassCard";
import { ENVIRONMENT_METHOD } from "@/lib/environment";
import { bandRanges } from "@/lib/match";
import { CONTEXT_METHOD } from "@/lib/zoneContext";

import styles from "../section.module.css";

export const metadata: Metadata = { title: "Cómo lo calculamos" };

/*
 * Copy from pitch/metodologia.md, part 1 (line D; §1.4–1.8 of 12 nov, gap-0.3 and D-218). Paragraphs
 * marked «pendiente de A» (security, green areas, step-free access) are left out until line A has
 * them, as D's rule says.
 */

function Section({ id, title, children }: { id: string; title: string; children: ReactNode }) {
  return (
    <GlassCard as="section" aria-labelledby={id} className={styles.card}>
      <h2 id={id}>{title}</h2>
      {children}
    </GlassCard>
  );
}

/**
 * pitch/metodologia.md §1.3 with the fit-0.9 method (FORMULA_DECISION: option A with the 1 h cap, chosen by Mariano in F5
 * on 15 nov; «Textos que cambian» of FORMULA_ANALISIS §F4.7). Line D carries the same text to metodologia.md.
 */
function FitMethod() {
  return (
    <Section id="encaje" title="Cómo sale el % de encaje">
      <p className={styles.para}>
        El % de encaje dice <strong>cuánto se parece una zona a lo que tú buscas</strong>. No es una nota de la zona: la
        misma zona puede encajar mucho con una familia con niños y poco con una persona mayor que vive sola.
      </p>
      <p className={styles.para}>
        <strong>Paso 1. Lo imprescindible.</strong> Miramos tus condiciones en cada zona, por ejemplo tu presupuesto, tener
        un colegio cerca o tardar como mucho 45 minutos en llegar al trabajo. Cada condición puede salir de tres maneras:
      </p>
      <ul className={styles.text}>
        <li><strong>Cumple.</strong></li>
        <li><strong>No cumple.</strong></li>
        <li><strong>No lo sabemos</strong>, porque falta el dato. En ese caso no la damos por buena.</li>
      </ul>
      <p className={styles.para}>
        Solo te enseñamos como «zonas que te convienen» las que cumplen todo. Las que fallan en una sola cosa salen aparte,
        en «Casi valen», para que decidas tú. En vez de su %, te decimos lo que les falta: por ejemplo, «Se pasa unos 90 € al
        mes de tu presupuesto» o «Tarda unos 12 min más de lo que pides».
      </p>
      <p className={styles.para}>
        <strong>Paso 2. Lo que te importa.</strong> Entre las zonas que cumplen, cada cosa que te importa recibe una nota de
        0 a 1, y pesa más lo que marcaste primero. Con 5 cosas, la primera cuenta un 33&nbsp;%, la segunda un 27&nbsp;%, la tercera un
        20&nbsp;%, la cuarta un 13&nbsp;% y la quinta un 7&nbsp;%. El % de encaje es la media de esas notas con sus pesos.
      </p>
      <p className={styles.para}>
        <strong>Lo imprescindible también puntúa.</strong> Un servicio que marcas como imprescindible deja fuera las zonas
        que no lo cumplen y, además, cuenta en el %: no es lo mismo tener la escuela infantil a 2 minutos que a 9.
      </p>
      <p className={styles.para}>Así se pone cada nota:</p>
      <ul className={styles.text}>
        <li>
          <strong>Cada minuto a pie cuenta.</strong> Un servicio a pie (escuela infantil, colegio, centro de salud, parada…)
          vale 1 en la puerta de casa, 0,9 justo a la distancia que consideramos cerca, y baja hasta 0 al triple de ese
          tiempo. Para un colegio, cerca son 10 min: a 5 min vale 0,95; a 10, 0,9; a 20, 0,45, y a 30 o más, 0. Para el
          centro de salud, cerca son 15 min, y para la parada, 5. Si pides otros minutos, cerca son los tuyos.
        </li>
        <li>
          <strong>Cercanía y plazas.</strong> Un servicio no vale solo por estar cerca: también cuenta si hay bastante para
          tanta gente, con la misma cifra de «Qué falta» (lo que hay a 15 minutos andando, repartido entre quienes lo
          comparten, frente a zonas parecidas). La nota del servicio es un 60&nbsp;% cercanía y un 40&nbsp;% plazas. Las plazas valen
          1 si la zona tiene lo mismo o más que las zonas parecidas, y bajan hasta 0 cuando tiene el 40&nbsp;% o menos. En un
          barrio de Madrid usamos la cifra de su distrito, porque «Qué falta» es por distrito. Las paradas no tienen plazas:
          solo cuenta lo cerca que están.
        </li>
        <li>
          <strong>El trabajo:</strong> contamos los minutos reales en transporte público para llegar a las 9:00, con los
          horarios que publica el Consorcio Regional de Transportes: metro, Metro Ligero, Cercanías y autobuses. Es el tiempo
          de puerta a puerta, contando lo que se anda hasta la parada. Aquí también cuenta cada minuto: vale 1 si lo tienes
          al lado, 0,9 a los 30 minutos y baja hasta 0 a los 90. Si pones un límite («Tardar como mucho»), esos 30 minutos
          son los tuyos y el 0 llega al triple. Si vas 1 o 2 días a la semana, el trayecto pesa la mitad, y con teletrabajo
          total no cuenta.
        </li>
        <li>
          <strong>El presupuesto:</strong> vale 1 si la zona te cuesta el 75&nbsp;% de tu presupuesto o menos, y baja hasta 0,6
          si te lo comes entero: una zona que cabe no sale «Poco recomendable» solo por eso. Si te pasas, ya no encaja. En
          «Casi valen» te decimos cuánto te pasas, y su nota sigue bajando hasta 0 cuando te pasas un 25&nbsp;%, para que salgan
          antes las que se pasan menos.
        </li>
        <li>
          <strong>«Sin escaleras», zonas verdes y ocio</strong> (solo si los marcas): los minutos andando hasta la estación
          accesible, el parque o el ocio que elijas, con la misma regla de los minutos.
        </li>
        <li>
          <strong>Si a una zona le falta un dato,</strong> nunca cuenta como 0: sale «sin datos» y baja la fiabilidad del %.
        </li>
      </ul>
      <p className={styles.para}>
        <strong>Tres topes, para que el % no diga una cosa y la tarjeta otra:</strong>
      </p>
      <ul className={styles.text}>
        <li>
          <strong>Si falta lo que has marcado.</strong> Si en «Qué falta» la zona sale FALTA en un servicio que has marcado,
          su encaje no pasa del 89&nbsp;%: nunca sale «Muy buena opción».
        </li>
        <li>
          <strong>Más de 1 h de trayecto: como mucho 74&nbsp;%.</strong> Si vas 3 días o más a la semana a un lugar que has
          puesto (el trabajo o tu familia) y tardas más de 1 h en llegar, la zona se queda como mucho en un 74&nbsp;%: nunca
          sale «Buena opción».
        </li>
        <li>
          <strong>Si no llegas.</strong> Si tardas 1 h 30 o más, o con los horarios publicados no se llega a las 9:00, el
          encaje se queda en la mitad. También solo si vas 3 días o más a la semana.
        </li>
      </ul>
      <p className={styles.para}>
        La 1 h y la 1 h 30 valen cuando no pones un límite de tiempo. Si pones el tuyo, se cuentan sobre él: el doble y el
        triple. Con «Tardar como mucho 45 min», serían 1 h 30 y 2 h 15.
      </p>
      <p className={styles.para}>
        <strong>El % en palabras.</strong> Junto a cada % te decimos, en palabras, si la zona es buena opción para ti:
      </p>
      <table className={styles.table}>
        <thead>
          <tr>
            <th scope="col">Si el % es…</th>
            <th scope="col">Sale</th>
          </tr>
        </thead>
        <tbody>
          {/* resultados.banda.*: the thresholds and words of lib/match.ts, the same as the API's `match_band` */}
          {bandRanges().map(([from, band]) => (
            <tr key={band}>
              <td>{from}</td>
              <td>
                <strong>{band}</strong>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className={styles.para}>
        <strong>A igual %.</strong> Las zonas van de más a menos %. A igual %, va primero la que tiene más cerca los servicios
        del día a día (escuela infantil, colegio, centro de salud, farmacia, centro de mayores y transporte), los hayas
        marcado o no: cuenta cada minuto andando, no cuántos servicios hay. Con quién empata cada zona te lo dice su tarjeta,
        en «Ver más sobre…» («Igual de buena que Latina (94&nbsp;%)»), y si más de 10 son igual de buenas, la lista te avisa para que
        marques qué quieres tener cerca o dónde trabajas.
      </p>
      <p className={styles.para}>
        <strong>Debajo del %</strong> van entre 3 y 5 hechos que puedes comprobar, como «Colegio con primaria a 5 min
        andando», y cada uno dice cuánto nos fiamos del dato. Si un tope baja el %, la tarjeta también lo dice, por ejemplo
        «Faltan escuelas infantiles: como mucho 89&nbsp;%».
      </p>
      {/* The fit-0.9 answer to the demo case (golden_family of data/fixtures/golden, D-243 §9; API on the lote 4 data, 15 nov) */}
      <p className={styles.para}>
        <strong>Ejemplo real.</strong> Una pareja con 2 hijos de 4 y 8 años trabaja en la Castellana, puede pagar 1.500 € al
        mes y quiere un colegio a 10 min andando como mucho. Le importan, por este orden, los colegios, el transporte y la
        salud. De las 199 zonas, 42 cumplen todo: 12 salen «Muy buena opción», 5 «Buena opción», 13 «Opción regular» y 12
        «Poco recomendable».
      </p>
      <p className={styles.para}>
        Arriba empatan dos al 94&nbsp;%: Puente de Vallecas y Latina. Va primera Puente de Vallecas porque, a igual %, tiene más
        cerca los servicios del día a día. Detrás van Usera y Moratalaz (93&nbsp;%); Tetuán, Ciudad Lineal y Villaverde (92&nbsp;%), y
        Carabanchel, Coslada y Leganés (90&nbsp;%).
      </p>
      <p className={styles.para}>
        En Latina hay colegio a unos 6 min, parada a unos 2 y centro de salud a unos 10, se tarda 39 min en transporte
        público hasta la Castellana llegando a las 9:00, y el alquiler sale a unos 1.101 € al mes por 77 m². Pierde unos 6
        puntos: 3 por esos 39 minutos de trayecto, y 1,1 por el colegio, 1,1 por la parada y 0,9 por el centro de salud, casi
        todo por los minutos a pie. Las plazas apenas le quitan: de colegios tiene más que las zonas parecidas y de centros
        de salud, casi lo mismo. El alquiler no le quita nada, porque no llega al 75&nbsp;% de lo que puede pagar.
      </p>
      <p className={styles.para}>
        Casi valen Chamartín, Arganzuela, Centro, Chamberí y Retiro: las cinco se pasan del presupuesto. Lo que más zonas
        le quita es el colegio a 10 min: con 5 min más aparecen 49 zonas más, y con 150 € más al mes, 3.
      </p>
    </Section>
  );
}

// pitch/metodologia.md §1.4 (line D, gap-0.3 and D-218): estado.* and fila.zona_pequena of pitch/textos_web.md
const STATUS_ROWS: [string, string][] = [
  ["menos del 80\u00a0% de lo que tienen los municipios de su tipo, y la diferencia no se explica por el tamaño de la zona", "FALTA"],
  ["menos de lo que tienen los municipios de su tipo, pero sin llegar a FALTA", "JUSTO"],
  ["lo mismo o más", "CUBIERTO"],
  ["tan poca gente que, ni junto con sus vecinos, podemos saber con seguridad si falta", "Zona pequeña para comparar (nunca sale FALTA)"],
  ["no tenemos el dato", "SIN DATOS"],
];

// What each row counts as capacity and for whom (D-217 §3), as a list in every size (metodologia §1.4):
// with three columns, a phone fitted two or three words per line (review of PR #17)
const ROW_CAPACITY: [string, string, string][] = [
  ["Escuelas infantiles", "niños de 0 a 4 años", "cada escuela, pública o privada, cuenta como una, porque nadie publica sus plazas."],
  [
    "Colegios",
    "niños de 5 a 14 años",
    "aulas de primaria públicas y concertadas. La Comunidad publica cuántas tiene cada municipio, no cada colegio, así que las repartimos a partes iguales entre sus colegios.",
  ],
  [
    "Centros de salud",
    "todos los vecinos",
    "cada centro de salud del Servicio Madrileño de Salud (SERMAS) cuenta como uno. Los consultorios locales son del mismo equipo médico: cuentan para los minutos a pie, no como más capacidad.",
  ],
  ["Mayores", "personas de 65 años o más", "plazas autorizadas en hogares, clubes y centros de día. Las residencias van aparte."],
  ["Farmacias", "todos los vecinos", "cada farmacia cuenta como una."],
  [
    "Vivienda (solo contexto)",
    "hogares de 4 o más personas",
    "no va a pie y nunca sale FALTA. Contamos las viviendas de más de 90 m² por cada 100 de esos hogares y lo enseñamos como dato para conocer la zona, con la cifra de los municipios parecidos.",
  ],
];

function GapMethod() {
  return (
    <Section id="que-falta" title="Cómo decidimos qué falta en una zona">
      <p className={styles.para}>
        <strong>Lo que tienes a 15 minutos andando, repartido entre quienes lo comparten.</strong> Para cada servicio miramos
        qué tiene la gente de la zona a 15 minutos andando: un kilómetro por la calle, a paso tranquilo (4 km/h). No basta
        con que esté cerca: si mucha gente vive alrededor de un colegio, sus aulas se reparten entre más niños. Por eso
        hacemos dos pasos:
      </p>
      <ol className={styles.text}>
        <li>Para cada centro, repartimos lo que ofrece entre todas las personas que viven a 15 minutos andando o menos de él.</li>
        <li>Para cada calle, sumamos lo que le toca de cada centro que tiene a 15 minutos.</li>
      </ol>
      <p className={styles.para}>
        La zona tiene la media de sus calles, según cuánta gente vive en cada una. Así, un colegio en el límite de dos
        distritos sirve a los dos, y quien vive a más de 15 minutos de todos no suma nada en esa fila.
      </p>
      <p className={styles.para}>
        <strong>Qué cuenta en cada servicio.</strong> Solo lo que se publica; nunca nos lo inventamos centro a centro.
      </p>
      <ul className={styles.text}>
        {ROW_CAPACITY.map(([row, who, what]) => (
          <li key={row}>
            <strong>{row},</strong> para {who}: {what}
          </li>
        ))}
      </ul>
      <p className={styles.para}>
        <strong>Con qué comparamos.</strong> Hacemos la misma cuenta en <strong>los demás municipios de su mismo tipo</strong>{" "}
        en la Comunidad de Madrid: los rurales con los rurales y los urbanos con los urbanos. Rural es lo que dice la ley de
        medio rural: menos de 30.000 habitantes y menos de 100 por km². Los distritos de Madrid son urbanos. Una zona nunca se
        compara consigo misma: un distrito de Madrid se compara con los demás municipios urbanos, sin contar Madrid.
      </p>
      <p className={styles.para}>
        ¿Por qué no con toda la región? Porque un pueblo pequeño suele tener su escuela infantil y pocos niños: a pie y por
        niño, los municipios rurales tienen más del doble de escuelas infantiles que los urbanos (unas 12 por cada 1.000
        niños, frente a menos de 5). Con la media de toda la región, a cualquier ciudad le faltaría de todo.
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
        <strong>¿Por qué el tamaño importa?</strong> En una zona con poca gente, un centro más o menos cambia mucho la
        cuenta. Por eso, para decir FALTA pedimos además que la diferencia sea demasiado grande para ser casualidad. Es la
        misma prueba que usan los indicadores de salud pública de Inglaterra.
      </p>
      <p className={styles.para}>
        <strong>Los pueblos pequeños, junto con sus vecinos.</strong> Si en un municipio vive tan poca gente que no se puede
        comparar solo, lo juntamos con sus vecinos más cercanos del mismo tipo, a 15 km como mucho en línea recta, hasta
        tener un grupo con el que sí se puede. Es más o menos el tamaño de las zonas de salud rurales de la Comunidad, con
        las que esos pueblos ya se organizan. Su estado es entonces el del grupo, y la fila lo dice: «Comparado con
        municipios parecidos de la zona», con los nombres de esos vecinos. Si ni así se llega, sale{" "}
        <strong>zona pequeña para comparar</strong>. Por ejemplo, La Acebeda, con 70 habitantes, no tiene ninguna farmacia a
        15 minutos andando, pero ni junto con sus vecinos hay gente suficiente para decir que le falta. Los distritos de
        Madrid no se juntan: tienen gente de sobra para compararlos solos.
      </p>
      <p className={styles.para}>
        <strong>Ejemplo real.</strong> En Puente de Vallecas la escuela infantil más cercana está a unos 6 minutos andando,
        pero son pocas para tantos niños: 2,8 al alcance a pie por cada 1.000 niños de 0 a 4 años, frente a 4,9 en los demás
        municipios urbanos. Con tantos niños, no es casualidad: sale <strong>FALTA</strong>. En Centro la cifra es parecida,
        pero con menos niños la diferencia podría ser casualidad: sale <strong>JUSTO</strong>.
      </p>
      <p className={styles.para}>
        <strong>El hospital.</strong> En la fila de centros de salud verás también los minutos a pie hasta el hospital
        general más cercano, público o privado. Es una pista de dónde pueden quedar las urgencias, no un dato de urgencias:
        ninguna fuente abierta dice qué hospitales las tienen abiertas las 24 horas. No cuenta para el estado de la fila: a un
        hospital no se va andando a elegir. En «Todos los centros» de cada zona verás el nombre y las camas instaladas de los
        hospitales que hemos podido identificar en el Catálogo Nacional de Hospitales del Ministerio de Sanidad; de unos
        pocos solo sabemos el tipo y el municipio.
      </p>
      <p className={styles.para}>
        <strong>Dónde invertir primero.</strong> En «Qué falta» sumamos la gente que vive en las zonas en FALTA de cada
        servicio: los niños de 0 a 4 años para las escuelas infantiles, los de 5 a 14 para los colegios, las personas de 65
        años o más para los mayores, todos los vecinos para los centros de salud y las farmacias, y los hogares de 4 o más
        personas para la vivienda. Es la misma gente con la que hacemos la cuenta: el censo y, en los distritos de Madrid, el
        padrón. Las zonas van de más a menos gente afectada. Contamos a toda la gente de la zona, aunque
        dentro de ella unas calles estén mejor servidas que otras.
      </p>
      <p className={styles.para}>
        Es una señal para saber dónde mirar primero, no un veredicto: comparamos con zonas parecidas, no con una norma oficial
        que diga cuánto debería haber.
      </p>
    </Section>
  );
}

// pitch/metodologia.md §1.5
function WalkingTimes() {
  return (
    <Section id="a-pie" title="Distancias a pie">
      <p className={styles.para}>
        Medimos lo que tardarías andando por las calles de verdad, no en línea recta, a un paso tranquilo de 4 km/h, con el
        mapa de calles de OpenStreetMap. Desde cada calle donde vive gente calculamos cuánto se tarda hasta lo más cercano:
        escuela infantil, colegio con primaria (público o concertado), centro de salud o consultorio, farmacia, centro de
        mayores, hospital general y parada de autobús, metro o Cercanías. En cada fila de «Qué falta» verás lo que tarda la
        mitad de la zona: unos vecinos lo tienen más cerca y otros más lejos. Son los mismos 15 minutos de la sección anterior: lo que
        queda más lejos no cuenta como «al alcance a pie». A ese paso, 10 minutos son unos 670 metros. Si en una zona no hay
        calles en el mapa, sale «sin datos», nunca cero. Usamos el mismo paso que el estudio «El Madrid de los 15 minutos»
        del Ayuntamiento.
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
          así que el dato cuenta como aproximado. Pasa con menos de 200 niños de 0 a 4 años en escuelas infantiles, menos
          de 300 niños de 5 a 14 años en colegios, menos de 2.000 habitantes en centros de salud y en farmacias, menos de
          300 personas mayores en mayores y menos de 100 hogares de 4 o más personas en vivienda.
        </li>
        <li>
          <strong>Aulas repartidas.</strong> En colegios el dato es aproximado como mucho, porque las aulas de cada municipio
          se reparten a partes iguales entre sus colegios. Esto mide cuánto nos fiamos del dato; si la zona es demasiado
          pequeña para comparar, se ve aparte (en «Cómo decidimos qué falta en una zona»).
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
          <strong>Solo usamos la capacidad que se publica.</strong> De las escuelas infantiles, los centros de salud y las
          farmacias no se publican plazas ni médicos, así que cada uno cuenta como uno. Las aulas de primaria son las del
          municipio repartidas entre sus colegios, y las plazas de mayores son autorizadas: no sabemos cuántas están libres.
        </li>
        <li>
          <strong>Medimos lo que tienes andando.</strong> No lo que tienes en coche o en autobús, que en los pueblos también
          cuenta. Y quien vive a más de 15 minutos de cualquier centro no suma nada en esa fila.
        </li>
        <li>
          <strong>Colocamos a la gente por calles.</strong> Sabemos cuánta gente vive en cada municipio y en cada distrito de
          Madrid, no en cada portal: la repartimos entre sus calles según su longitud.
        </li>
        <li>
          <strong>Las camas de hospital no cuentan en la lista.</strong> Las enseñamos en los hospitales que hemos podido
          identificar, pero no deciden si a una zona le falta algo: para eso haría falta medir el viaje en coche o en
          transporte público.
        </li>
        <li>
          <strong>Vivienda:</strong> comparamos las viviendas grandes con los hogares grandes, no el mercado, y solo como
          contexto: en muchos pueblos las segundas residencias hacen que haya más viviendas grandes que hogares grandes, así
          que la cifra no dice si falta vivienda y no la juzgamos. No sabemos cuántas están libres ni a qué precio.
        </li>
        <li>
          <strong>Alquiler:</strong> la Comunidad publica el precio medio de 37 municipios (los de más de 20.000 habitantes
          con contratos suficientes) y el de los códigos postales de Madrid capital. En el resto no tenemos el dato y lo
          decimos. Para cada distrito de Madrid hacemos la media de sus códigos postales, y cada código pesa según cuántos
          colegios, centros de salud y centros sociales del distrito están en él, porque eso aproxima dónde vive la gente. Es
          una aproximación, así que cuenta con menos fiabilidad. Cuadra con la cifra oficial: con los distritos sale 14,5 € el
          metro cuadrado, y la Comunidad publica 15,1 para todo Madrid. Esa media es de todos los contratos en vigor, así que
          la ajustamos a lo que se pagó en los contratos firmados en 2024 en la misma zona, según la Agencia Tributaria: entre
          un 5&nbsp;% y un 26&nbsp;% más. Aun así, un anuncio de hoy puede pedir más. Donde la Comunidad no publica el alquiler (los
          pueblos), partimos de la referencia del Ministerio de Vivienda (SERPAVI, 2024): la mediana por metro cuadrado de
          los alquileres de vivienda habitual declarados a Hacienda, con el Catastro. La subimos ligeramente para llevarla al
          nivel de la cifra de la Comunidad, porque una mediana se queda algo por debajo de una media, y la ajustamos a un
          contrato firmado en 2024 igual que la de la Comunidad. Es una elaboración nuestra y un dato aproximado; en la
          tarjeta te decimos entre qué precios está la mitad de los contratos. Si en un pueblo se alquilan muy pocas viviendas,
          no se publica y sale «sin datos».
        </li>
        <li>
          <strong>Compra:</strong> usamos el valor tasado medio de la vivienda libre por metro cuadrado (Ministerio de
          Vivienda, en el portal de la Comunidad), por los metros que suponemos para tu hogar. Es lo que tasan las sociedades
          de tasación, no el precio de un anuncio. Solo se publica para los municipios de más de 25.000 habitantes: en los
          municipios pequeños sale «sin datos» y no inventamos un precio. En los distritos y barrios de Madrid el precio es una
          estimación, y lo decimos: repartimos el valor tasado de toda la ciudad según el valor catastral por metro cuadrado
          de cada zona (Catastro, publicado por el Ayuntamiento). La media de los distritos coincide con el valor tasado de
          Madrid. El valor catastral sale de valoraciones antiguas, así que es un dato aproximado, no un precio real: frente
          a los precios de los anuncios, ordena los distritos casi igual, pero los caros salen algo más baratos y los baratos
          algo más caros.
        </li>
        <li>
          {/* D-235: the same words the card's tests check (no alarm or wealth words) */}
          <strong>{CONTEXT_METHOD.lead}</strong> {CONTEXT_METHOD.text}
        </li>
        <li>
          <strong>Vivienda nueva y lo que viene:</strong> en cada zona contamos cuántas compraventas del último año fueron
          de obra nueva, cuánto se tasa una vivienda de menos de 5 años frente a una más antigua, las viviendas del Plan Vive
          y, en Madrid capital, el suelo para vivienda del Plan General que aún no está terminado. También el suelo público
          para vivienda: las parcelas de uso residencial que la Comunidad de Madrid y los ayuntamientos ofrecen en venta o en
          concesión en el Portal del Suelo 4.0 (portal de datos abiertos de la Comunidad, se actualiza cada día), con sus
          metros edificables; en Madrid capital, cada parcela va a su distrito por su sitio en el mapa de la Comunidad. Son
          datos para conocer la zona: no cambian el encaje ni el orden. Dicen dónde se vende o se prepara vivienda nueva y
          dónde hay suelo para construirla, no cuántos pisos quedan libres, cuántos caben ni cuándo estarán.
        </li>
        <li>
          {/* D-237, R-07 of PR #65: street level, not the façade, and not the share of neighbours */}
          <strong>{ENVIRONMENT_METHOD.lead}</strong> {ENVIRONMENT_METHOD.text}
        </li>
        <li>
          <strong>Ocio:</strong> los bares, restaurantes, gimnasios, museos, bibliotecas, teatros y cines salen de
          OpenStreetMap, un mapa hecho por voluntarios. En las ciudades está bastante completo; en los pueblos pequeños falta
          algún local, así que un pueblo puede tener un bar que no vemos. Por eso el ocio solo cuenta si lo marcas y no deja
          fuera ninguna zona salvo que marques «Solo zonas que lo tengan».
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
      <Section id="en-cinco-pasos" title="Cómo decidimos qué falta, en cinco pasos">
        <MethodSteps />
        <a href="#que-falta" className={styles.more}>
          Ver el detalle
        </a>
      </Section>
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
      <FitMethod />
      <GapMethod />
      <WalkingTimes />
      <Reliability />
      <InvestorMethod />
      <Section id="datos" title="Qué datos usamos">
        <ul className={styles.text}>
          <li>
            <strong>
              <CmCount /> conjuntos de datos del Portal de Datos Abiertos de la Comunidad de Madrid:
            </strong>{" "}
            población, hogares, vivienda, renta, alquiler, colegios y sus aulas, salud y camas de hospital de la región,
            mayores, farmacias y las 6 redes de transporte público del Consorcio Regional de Transportes de Madrid, que
            también se publican en ese portal.
          </li>
          <li>
            <strong>Como apoyo,</strong> sin contarlos como datos de la Comunidad:
            <ul>
              <li>
                el padrón y el panel de distritos del Ayuntamiento de Madrid, para la población y los hogares de cada distrito
                de Madrid capital;
              </li>
              <li>
                el mapa de OpenStreetMap: sus calles, para las distancias a pie, y sus locales de ocio (bares, restaurantes,
                gimnasios y cultura), que solo cuentan si marcas «Ocio»;
              </li>
              <li>
                la estadística de viviendas declaradas en el IRPF de la Agencia Tributaria (ejercicio 2024), para acercar el
                alquiler al de los contratos firmados ese año;
              </li>
              <li>
                los catálogos de hospitales y de centros de atención primaria del Ministerio de Sanidad, para el nombre de los
                centros de salud y el nombre y las camas de los hospitales;
              </li>
              <li>
                el geocodificador oficial CartoCiudad del IGN, solo para colocar los pocos centros que el registro publica sin
                coordenadas o con coordenadas que contradicen su dirección.
              </li>
            </ul>
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
        <p className={styles.para}>
          Contamos las visitas de forma agregada y sin cookies (Vercel Web Analytics), solo para saber cuánta gente usa la
          web. No sabemos quién eres ni guardamos lo que buscas.
        </p>
      </Section>
      <SiteFooter />
    </div>
  );
}
